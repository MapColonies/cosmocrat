import os
import constants

from region import Region
from entities.polygon import Polygon
from osm_tools.osmconvert import get_osm_file_timestamp
from helper_functions import string_to_datetime, read_file, dictionary_has_key, handle_subprocess_exit_code

# TODO: create config_map
# TODO: support inner states?
# TODO: handle exceptions
# TODO: support remote files
# TODO: validate polygon
# TODO: support polygon in geojson
# TODO: polygon name?
# TODO: file system object and calculate latest state
# TODO: should update the configuration in every interval
class ConfigurationHandler():
    def __init__(self, path, exception_func):
        self.path = os.path.join(constants.DATA_PATH)
        self.interval = constants.DEFAULT_INTERVAL
        self.regions = []
        self.exception_func = exception_func
        self.load_config()

    def load_config(self):
        try:
            data = read_file(file_path=self.path, is_json=True, throw_not_found=True)
        except:
            # legit?
            self.exception_func('Failed while reading configuration.')
        self.interval = data['interval_seconds']
        for region in data['regions']:
            (region_entity, state_path) = self.create_region_entity(region)
            state_timestamp = get_osm_file_timestamp(state_path)
            region_entity.set_state(state_path, string_to_datetime(state_timestamp))
            self.regions.append(region_entity)

    def create_region_entity(self, data):
        name = data['name']
        if dictionary_has_key(data, 'state'):
            state_path = data['state']
        else:
            state_path = None
        polygon_path = data['polygon']
        polygon_entity = Polygon(name, polygon_path)
        region_entity = Region(name, polygon_entity, self.interval)
        if dictionary_has_key(data, 'regions'):
            for sub_region in data['regions']:
                (sub_region_entity, _) = self.create_region_entity(sub_region)
                region_entity.add_sub_region(sub_region_entity)
        return (region_entity, state_path)
        