import os
import constants

from uuid import uuid4
from helper_functions import run_command_wrapper
from osm_tools.osmconvert import get_osm_file_timestamp

def limit_time_units(time_units=constants.TIME_UNITS_IN_USE):
    result = ''
    for time_unit in time_units:
        if time_unit not in constants.Time_Unit._member_names_:
            raise
        result += f'--{time_unit} '
    return result
    
def get_changes_from_timestamp(input_timestamp, change_format=constants.FORMATS_MAP['OSC']):
    temp_output_name = f'{uuid4()}.{change_format}'
    output_path = os.path.join(constants.OSMCHANGES_PATH, change_format, temp_output_name)

    run_command_wrapper(f'{constants.OSMUPDATE_PATH} \
                    {input_timestamp} \
                    {output_path} \
                    {limit_time_units()} \
                    --tempfiles={constants.OSMUPDATE_CACHE_PATH} \
                    --keep-tempfiles \
                    --trust-tempfiles \
                    -v')

    output_timestamp = get_osm_file_timestamp(output_path)
    output_name = f'{input_timestamp}.{output_timestamp}.{change_format}'
    new_output_path = os.path.join(constants.OSMCHANGES_PATH, change_format, output_name)
    os.rename(output_path, new_output_path)
    return new_output_path

def get_changes_from_file(input_path, change_format=constants.FORMATS_MAP['OSC']):
    temp_output_name = f'{uuid4()}.{change_format}'

    output_path = os.path.join(constants.OSMCHANGES_PATH, change_format, temp_output_name)
    
    run_command_wrapper(f'{constants.OSMUPDATE_PATH} \
                    {input_path} \
                    {output_path} \
                    {limit_time_units()} \
                    --tempfiles={constants.OSMUPDATE_CACHE_PATH} \
                    --keep-tempfiles \
                    --trust-tempfiles \
                    -v')
    input_timestamp = get_osm_file_timestamp(input_path)
    output_timestamp = get_osm_file_timestamp(output_path)
    output_name = f'{input_timestamp}.{output_timestamp}.{change_format}'
    new_output_path = os.path.join(constants.OSMCHANGES_PATH, change_format, output_name)
    os.rename(output_path, new_output_path)
    return new_output_path