#!/usr/bin/env python3
import os
import re
import pause
import config

from datetime import timedelta
from region import Region
from osm_tools.osmconvert import get_osm_file_timestamp
from helper_functions import get_current_datetime, datetime_to_string
from config import log

regions_to_update = []

class Polygon:
    def __init__(self, name, path):
        self.name = name
        self.path = path

def initialize_environment():
    # polygons
    tel_aviv_polygon = Polygon('Tel Aviv', os.path.join(config.POLYGONS_PATH, 'telaviv.poly'))
    jerusalem_polygon = Polygon('Jerusalem', os.path.join(config.POLYGONS_PATH, 'jerusalem.poly'))
    israel_polygon = Polygon('Israel', os.path.join(config.POLYGONS_PATH, 'israel-and-palestine.poly'))

    # regions
    tel_aviv = Region(name='Tel Aviv', polygon=tel_aviv_polygon, interval=3600)
    jerusalem = Region(name='Jerusalem', polygon=jerusalem_polygon, interval=3600)
    israel = Region(name='Israel', polygon=israel_polygon, interval=3600, sub_regions=[tel_aviv, jerusalem])

    # TODO: file system object and calculate latest state
    starting_state = os.path.join(config.RESULTS_PATH, 'israel-and-palestine-latest.2020-12-02T15:00:00Z.osm.pbf')
    israel.set_state(starting_state, get_osm_file_timestamp(starting_state))
    regions_to_update.append(israel)

def sleep_til_next_update(closest_update):
    if not closest_update:
            closest_update = get_current_datetime() + timedelta(seconds=config.DEFAULT_SLEEP_INTERVAL)
    log.info(f'going to sleep until {datetime_to_string(closest_update)}')
    pause.until(closest_update)

def main():
    log.info(f'{config.app_name} started')
    initialize_environment()
    while True:
        closest_update = None
        for region in regions_to_update:
            if region.update():
                region.create_states_delta()
            next_region_update = region.calculate_closest_next_update()
            if not closest_update or closest_update > next_region_update:
                closest_update = next_region_update
            # TODO: determine when to set a region state and create its deltas
        sleep_til_next_update(closest_update)

if __name__ == '__main__':
    main()