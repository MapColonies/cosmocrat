import os
import definitions

from entities.region import Region
from entities.polygon import Polygon
from osm_tools.osmconvert import get_osm_file_timestamp
from helper_functions import string_to_datetime, read_file, dictionary_has_non_none_key, handle_subprocess_exit_code

# TODO: support inner states?
# TODO: support remote files
# TODO: validate polygon
# TODO: support polygon in geojson
# TODO: determine polygon name?
# TODO: should update the configuration in every interval
class Configuration():
    def __init__(self, path):
        self.path = path
        self.interval = definitions.DEFAULT_INTERVAL_SECONDS
        self.regions = []
        self.load_config()

    def load_config(self):
        try:
            data = read_file(file_path=self.path, throw_not_found=True)
        except FileNotFoundError:
            raise FileNotFoundError()
        except:
            raise Exception()
        self.interval = data['interval_seconds']
        for region in data['regions']:
            (region_entity, state_path) = self.create_region_entity(region)
            state_timestamp = get_osm_file_timestamp(state_path)
            region_entity.set_state(state_path, string_to_datetime(state_timestamp))
            self.regions.append(region_entity)

    def create_region_entity(self, data):
        name = data['name']
        if dictionary_has_non_none_key(data, 'state'):
            state_path = data['state']
        else:
            state_path = None
        polygon_path = data['polygon']
        polygon_entity = Polygon(name, polygon_path)
        region_entity = Region(name, polygon_entity, self.interval)
        if dictionary_has_non_none_key(data, 'regions'):
            for sub_region in data['regions']:
                (sub_region_entity, _) = self.create_region_entity(sub_region)
                region_entity.add_sub_region(sub_region_entity)
        return (region_entity, state_path)
        