import os 
import pytz

from enum import Enum
from MapColoniesJSONLogger.logger import generate_logger

app_name = 'cosmocrat'

OSMOSIS_PATH='/home/amito/src/osmosis/bin/osmosis'
OSMUPDATE_PATH='/home/amito/src/osmupdate/osmctools/src/a.out'
OSMCONVERT_PATH='/home/amito/src/osmconvert/osmconvert'

DEFAULT_SLEEP_INTERVAL=300
DEFAULT_FILE_PERMISSIONS=0o644
APP_PATH = '/home/amito/src/cosmocrat'
DATA_PATH = os.path.join(APP_PATH, 'data')
POLYGONS_PATH = os.path.join(DATA_PATH, 'polygons')
REGIONS_PATH = os.path.join(DATA_PATH, 'regions')
SUB_REGIONS_PATH = os.path.join(REGIONS_PATH, 'sub-regions')
OSMCHANGES_PATH = os.path.join(DATA_PATH, 'osm-changes')
RESULTS_PATH = os.path.join(DATA_PATH, 'results')
DELTAS_PATH = os.path.join(DATA_PATH, 'deltas')
OSMUPDATE_CACHE_PATH = os.path.join(DATA_PATH, 'osmupdate_temp', 'temp')
TIME_UNITS_IN_USE = ['hour', 'day']
FORMATS_MAP = {
    'OSM_PBF': 'osm.pbf',
    'OSM': 'osm',
    'OSC': 'osc',
    'OSC_GZ': 'osc.gz',
    'POLY': 'poly'
}
TIMESTAMP_REGEX = r'\b[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2}Z\b'
Time_Unit = Enum('Time_Unit', 'minute hour day')

# TODO: where should it be
log_file_extention = '.log'
base_log_path = os.path.join(APP_PATH, 'log', app_name)
service_logs_path = os.path.join(base_log_path, app_name + log_file_extention)
osm_tools_logs_path = os.path.join(base_log_path, 'osm_tools' + log_file_extention)
os.makedirs(base_log_path, exist_ok=True)
log = generate_logger(app_name, log_level='INFO', handlers=[{'type': 'rotating_file', 'path': service_logs_path},{ 'type': 'stream', 'output': 'stderr' }])
process_log = generate_logger('osm_tools', log_level='INFO', handlers=[{'type': 'rotating_file', 'path': osm_tools_logs_path}, { 'type': 'stream', 'output': 'stderr' }])