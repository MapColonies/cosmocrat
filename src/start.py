#!/usr/bin/env python3
import os
import re
import pause
import constants

from config.configuration_handler import ConfigurationHandler
from datetime import timedelta
from region import Region
from entities.polygon import Polygon
from osm_tools.osmconvert import get_osm_file_timestamp
from helper_functions import get_current_datetime, datetime_to_string, string_to_datetime
from constants import log

regions_to_update = []

def initialize_environment():
    # TODO: load configuration better
    config = ConfigurationHandler(constants.CONFIGURATION_PATH)
    regions_to_update.extend(config.regions)

def sleep_til_next_update(closest_update):
    if not closest_update:
        closest_update = get_current_datetime() + timedelta(seconds=constants.DEFAULT_INTERVAL)
    log.info(f'going to sleep until {datetime_to_string(closest_update)}')
    pause.until(closest_update)

# TODO: work with unix times
def main():
    log.info(f'{constants.app_name} started')
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