import os
import constants

from datetime import timedelta
from osm_tools.osmosis import clip_polygon, apply_changes_by_polygon, create_delta
from osm_tools.osmupdate import get_changes_from_file, get_changes_from_timestamp
from osm_tools.osmconvert import get_osm_file_timestamp, set_osm_file_timestamp, drop_author
from helper_functions import deconstruct_file_path, string_to_datetime, datetime_to_string, grant_permissions

class Region:
    def __init__(self, name, polygon, interval, sub_regions=[]):
        self.name = name
        self.polygon = polygon
        self.interval = interval
        self.ancestors = []
        self.sub_regions = []
        self.latest_state_path = None
        self.second_latest_state_path = None
        self.next_update = None

    def set_state(self, state_path, timestamp):
        self.second_latest_state_path = self.latest_state_path
        self.latest_state_path = state_path
        self.last_update = timestamp
        self.set_next_update()
        self.clip_sub_regions()

    def clip_sub_regions(self):
        timestamp_str = datetime_to_string(self.last_update)
        for sub_region in self.sub_regions:
            clipped_polygon_path = clip_polygon(
                input_path=self.latest_state_path, 
                polygon_path=sub_region.polygon.path,
                input_timestamp=timestamp_str,
                output_base_path=os.path.join(self.get_ancestors_path(constants.RESULTS_PATH), sub_region.polygon.name),
                exist_ok=True)
            clipped_polygon_path = set_osm_file_timestamp(clipped_polygon_path, timestamp_str)
            grant_permissions(clipped_polygon_path)
            sub_region.set_state(clipped_polygon_path, self.last_update)
    
    def get_changes(self, based_on_file):
        compressed_format = constants.FORMATS_MAP['OSC_GZ']
        if (based_on_file):
            return get_changes_from_file(input_path=self.latest_state_path,
                                         change_format=compressed_format)
        return get_changes_from_timestamp(
            input_timestamp=datetime_to_string(self.last_update),
            change_format=compressed_format)
    
    def update(self, based_on_file=True):
        # get the changes from global using osm-update
        try:
            changes_path = self.get_changes(based_on_file)
        except:
            return False

        # apply the changes on the last state and bound by polygon using osmosis
        updated_path = apply_changes_by_polygon(base_output_path=self.get_ancestors_path(constants.RESULTS_PATH),
                                                input_path=self.latest_state_path,
                                                change_path=changes_path,
                                                polygon_path=self.polygon.path,
                                                is_compressed=True)

        # set the updated timestamp on the new state based on the changes
        changes_timestamp = get_osm_file_timestamp(changes_path)
        updated_path = set_osm_file_timestamp(updated_path, changes_timestamp)

        grant_permissions(changes_path)
        grant_permissions(updated_path)

        # set the updated state of the region, this will also set the state of the sub-regions and clip their polygons
        self.set_state(updated_path, string_to_datetime(changes_timestamp))
        return True

    def create_states_delta(self):
        delta_path = create_delta(delta_path=self.get_ancestors_path(constants.DELTAS_PATH),
                    delta_name=self.get_delta_name(),
                    first_input_pbf_path=self.second_latest_state_path,
                    second_input_pbf_path=self.latest_state_path,
                    should_compress=False)
        
        drop_author(delta_path)
        grant_permissions(delta_path)
        
        for sub_region in self.sub_regions:
            sub_region.create_states_delta()

    def get_delta_name(self):
        (_, name1, timestamp1, _) = deconstruct_file_path(self.latest_state_path)
        (_, name2, timestamp2, _) = deconstruct_file_path(self.second_latest_state_path)

        if not timestamp1:
            timestamp1 = get_osm_file_timestamp(self.latest_state_path)
        if not timestamp2:
            timestamp2 = get_osm_file_timestamp(self.second_latest_state_path)
    
        if name1 is name2:
            return f'{name2}.{timestamp2}.{name1}.{timestamp1}'
        return f'{name2}.{timestamp2}.{timestamp1}'

    def set_next_update(self):
        self.next_update = self.last_update + timedelta(seconds=self.interval)

    def calculate_closest_next_update(self, min=None):
        for sub_region in self.sub_regions:
            min = sub_region.calculate_closest_next_update(min)
        if not min or min > self.next_update:
            min = self.next_update
        return min
    
    def add_sub_region(self, sub_region):
        self.sub_regions.append(sub_region)
        sub_region.ancestors.extend(self.ancestors)
        sub_region.ancestors.append(self.name)
        
    def get_ancestors_path(self, base=''):
        path = base
        for ancestor in self.ancestors:
            path = os.path.join(path, ancestor)
        return os.path.join(path, self.name)