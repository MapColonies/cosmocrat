import os
import re
import constants
import subprocess
import pytz
import requests

from datetime import datetime, timedelta, timezone
from osmeterium.run_command import run_command
from constants import log, process_log

def get_current_datetime():
    return datetime.now(tz=timezone.utc)

def datetime_to_string(datetime):
    return datetime.strftime(r'%Y-%m-%dT%H:%M:%SZ')

def string_to_datetime(string):
    datetime_str = datetime.strptime(string, r'%Y-%m-%dT%H:%M:%SZ')
    return datetime_to_utc(datetime_str)

def datetime_to_utc(datetime):
    time_zone_dt = pytz.timezone('UTC').localize(datetime)
    return time_zone_dt.astimezone(pytz.utc)

def handle_subprocess_exit_code(exit_code):
    log.error(fr'The subprocess raised an error: {exit_code}')
    raise

def subprocess_get_stdout_output(args, remove_new_lines=True):
    completed_process = subprocess.run(args=args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True)
                                        
    if completed_process.returncode is not 0:
        raise
    output = completed_process.stdout
    if remove_new_lines: 
        return output.replace('\n', '')
    return output

def run_command_wrapper(command):
    run_command(command,
                process_log.info,
                process_log.info,
                handle_subprocess_exit_code,
                (lambda: log.info('subprocess finished successfully.')))

# def get_file_name_from_path(input, suffix, remove_datetime = False):
#     format_removed = input[:input.rfind(suffix)]
#     result = format_removed[format_removed.rfind('/') + 1:]
#     if remove_datetime:
#         result = remove_datetime_from_string(result)
#     return remove_dots_from_edges_of_string(result)
    
def remove_datetime_from_string(input):
    return re.sub(constants.TIMESTAMP_REGEX, '', input)
    
def remove_dots_from_edges_of_string(input):
    output = re.sub(r'(^[.])|([.]$)', '', input)
    if input is not output:
        output = remove_dots_from_edges_of_string(output)
    return output

def get_file_format(input):
    format = ''
    successful = False
    rest = input
    for format_value in constants.FORMATS_MAP.values():
        index = input.find(format_value)
        if index is not -1 and len(format) < len(format_value):
            format = format_value
            successful = True
    if successful:
        rest = input[:input.rfind(format)]
    return (successful, format, rest)

def get_file_dir(input):
    index = input.rfind('/')
    if index is -1:
        return (False, None, input)
    path = input[:index]
    rest = input[index + 1:]
    return (True, path, rest)

def get_file_timestamps(input):
    timestamps = []
    success = False
    for match in re.finditer(constants.TIMESTAMP_REGEX, input):
        success = True
        timestamp = match.group(0)
        timestamps.append(timestamp)
    rest = remove_datetime_from_string(input)
    return (success, timestamps, rest)

# TODO: create path class
def deconstruct_file_path(string):
    (_, format, string) = get_file_format(string)
    (_, dir, string) = get_file_dir(string)
    (_, timestamps, string) = get_file_timestamps(string)
    if len(timestamps) is 1:
        timestamps = timestamps[0]
    name = remove_dots_from_edges_of_string(string)
    return (dir, name, timestamps, format)

def get_compression_method(compression, default_format=''):
    compression_type = 'none'
    compression_format = default_format
    if compression:
        compression_type = 'gzip'
        compression_format += '.gz'
    return (compression_type, compression_format)

def grant_permissions(path, permissions=constants.DEFAULT_FILE_PERMISSIONS):
    os.chmod(path, permissions)

def request_file_from_url(server_url, path):
    url = '/'.join([server_url, path])
    result = requests.get(url)
    return (result.ok, result.text)