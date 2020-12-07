import config

from datetime import timedelta
from osm_tools.osmosis import clip_polygon, apply_changes_by_polygon, create_delta
from osm_tools.osmupdate import get_changes_from_file, get_changes_from_timestamp
from osm_tools.osmconvert import get_osm_file_timestamp, set_osm_file_timestamp, drop_author
from helper_functions import deconstruct_file_path, string_to_datetime

class Region:
    def __init__(self, name, polygon, interval, sub_regions=[]):
        self.name = name
        self.polygon = polygon
        self.interval = interval
        self.sub_regions = sub_regions
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
        timestamp = self.last_update
        for sub_region in self.sub_regions:
            clipped_polygon_path = clip_polygon(
                input_path=self.latest_state_path, 
                polygon_path=sub_region.polygon.path,
                input_timestamp=timestamp,
                output_base_path=config.RESULTS_PATH,
                exist_ok=True)
            clipped_polygon_path = set_osm_file_timestamp(clipped_polygon_path, timestamp)
            sub_region.set_state(clipped_polygon_path, timestamp)
    
    def get_changes(self, based_on_file):
        if (based_on_file):
            return get_changes_from_file(input_path=self.latest_state_path,
                                         change_format='osc.gz')
        return get_changes_from_timestamp(
            input_timestamp=datetime_to_string(self.last_update),
            change_format='osc.gz')
    
    def update(self, based_on_file=True):
        # get the changes from global using osm-update
        try:
            changes_path = self.get_changes(based_on_file)
        except:
            return False

        # apply the changes on the last state and bound by polygon using osmosis
        updated_path = apply_changes_by_polygon(self.latest_state_path, changes_path, self.polygon.path, True)

        # set the updated timestamp on the new state based on the changes
        changes_timestamp = get_osm_file_timestamp(changes_path)
        updated_path = set_osm_file_timestamp(updated_path, changes_timestamp)

        # set the updated state of the region, this will also set the state of the sub-regions and clip their polygons
        self.set_state(updated_path, changes_timestamp)
        return True

    def create_states_delta(self):
        delta_path = create_delta(delta_name=self.get_delta_name(),
                     first_input_pbf_path=self.second_latest_state_path,
                     second_input_pbf_path=self.latest_state_path,
                     should_compress=False)
        
        drop_author(delta_path)
        
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
        self.next_update = string_to_datetime(self.last_update) + timedelta(seconds=self.interval)

    def calculate_closest_next_update(self, min=None):
        for sub_region in self.sub_regions:
            min = sub_region.calculate_closest_next_update(min)
        if not min or min > self.next_update:
            min = self.next_update
        return min
