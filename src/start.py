#!/usr/bin/env python3
import os
import re
import pause
import definitions

from config.configuration import Configuration
from datetime import timedelta
from entities.region import Region
from entities.polygon import Polygon
from osm_tools.osmconvert import get_osm_file_timestamp
from helper_functions import get_current_datetime, datetime_to_string, string_to_datetime, log_and_exit
from definitions import log

def load_config():
    try:
        return Configuration(definitions.CONFIGURATION_PATH)
    except FileNotFoundError:
        log_and_exit(f'Could not locate configuration in the given path {definitions.CONFIGURATION_PATH}')
    except:
        log_and_exit('An Error occurred while loading the configuration.')

def sleep_til_next_update(closest_update, default_interval):
    if not closest_update:
        closest_update = get_current_datetime() + timedelta(seconds=default_interval)
    log.info(f'going to sleep until {datetime_to_string(closest_update)}')
    pause.until(closest_update)

def main():
    log.info(f'{definitions.app_name} started')
    config = load_config()
    while True:
        closest_update = None
        for region in config.regions:
            if region.update():
                region.create_states_delta()
            next_region_update = region.calculate_closest_next_update()
            if not closest_update or closest_update > next_region_update:
                closest_update = next_region_update
        sleep_til_next_update(closest_update, default_interval=config.interval)

if __name__ == '__main__':
    main()