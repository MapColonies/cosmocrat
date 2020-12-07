import os
import config

from uuid import uuid4
from helper_functions import subprocess_get_stdout_output, run_command_wrapper, deconstruct_file_path

def convert_changefile_format(input_path, input_format, output_format):
    if input_format is output_format:
        return
    input_name = get_file_name_from_path(input_path, input_format)
    output_path = os.path.join(config.OSMCHANGES_PATH, output_format, f'{input_name}.{output_format}')
    run_command_wrapper(f'{config.OSMCONVERT_PATH} \
                    {input_path} \
                    -o={output_path} \
                    --verbose')

def get_osm_file_timestamp(file_path):
    command = [config.OSMCONVERT_PATH, '--out-timestamp', file_path, '--verbose']
    try:
        return subprocess_get_stdout_output(command)
    except:
        raise

def set_osm_file_timestamp(input_path, new_timestamp):
    (dir, name, _, input_format) = deconstruct_file_path(input_path)
    temp_path = os.path.join(dir, f'{str(uuid4())}.{input_format}')
    run_command_wrapper(f'{config.OSMCONVERT_PATH} \
                    {input_path} \
                    --timestamp={new_timestamp} \
                    -o={temp_path} \
                    --verbose')
    output_name = f'{name}.{new_timestamp}.{input_format}'
    output_path = os.path.join(dir, output_name)
    os.rename(temp_path, output_path)
    return output_path

def drop_author(input_path):
    (dir, _, _, input_format) = deconstruct_file_path(input_path)
    temp_path = os.path.join(dir, f'{str(uuid4())}.{input_format}')
    run_command_wrapper(f'{config.OSMCONVERT_PATH} \
                    --drop-author \
                    {input_path} \
                    -o={temp_path} \
                    --verbose')
    os.rename(temp_path, input_path)
    