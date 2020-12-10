import json
import constants

from region import Region
from entities.polygon import Polygon
from osm_tools.osmconvert import get_osm_file_timestamp
from helper_functions import string_to_datetime

# TODO: remove helper functions
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
    def __init__(self, path):
        self.path = path
        self.interval = constants.DEFAULT_INTERVAL
        self.regions = []
        self.load_config()

    def load_config(self):
        data = read_json(self.path)
        self.interval = data['interval_seconds']
        for region in data['regions']:
            (region_entity, state_path) = self.create_region_entity(region)
            state_timestamp = get_osm_file_timestamp(state_path)
            region_entity.set_state(state_path, string_to_datetime(state_timestamp))
            self.regions.append(region_entity)

    def create_region_entity(self, data):
        name = data['name']
        if has_key(data, 'state'):
            state_path = data['state']
        else:
            state_path = None
        polygon_path = data['polygon']
        polygon_entity = Polygon(name, polygon_path)
        region_entity = Region(name, polygon_entity, self.interval)
        if has_key(data, 'regions'):
            for sub_region in data['regions']:
                (sub_region_entity, _) = self.create_region_entity(sub_region)
                region_entity.add_sub_region(sub_region_entity)
        return (region_entity, state_path)
        

def has_key(dictionary, key):
    return key in dictionary and dictionary[key]

def read_json(path):
    with open(path, 'r') as json_file:
        return json.load(json_file)