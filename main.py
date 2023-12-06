import argparse

from datetime import datetime
from src.utils.handler import BucketManager
from src.utils.game_link import RaceRecord

def get_race(path: str):
    with open(path, "r") as f:
        data = f.read()
    return data

parser = argparse.ArgumentParser(
                    prog='TelemetryForzaMotorsport',
                    description='Race data ingestion')

parser.add_argument('--ip', type=str, help='IP to connect with Forza Motorsport')
parser.add_argument('--port', type=int, help='Port to connect with Forza Motorsport')
parser.add_argument('--mode', type=str, help='Choose between: dash or sled')
parser.add_argument('--frequency', type=int, help='Frequency to record the data (Hz)')

args = parser.parse_args()

# Checking if all arguments are set
for arg in [args.ip, args.port, args.mode, args.frequency]:
 if arg is None:
    raise Exception("One of args has not been set.")

UDP_IP = args.ip
UDP_PORT = args.port
MODE = args.mode
FREQUENCY = args.frequency

race = RaceRecord(udp_ip=UDP_IP, 
                  udp_port=UDP_PORT, 
                  frequency=FREQUENCY, 
                  mode=MODE)

bucket_manager = BucketManager()

try:
    race.start()
except KeyboardInterrupt:
    file_path = race.file_path
    filename = race.filename
    date = datetime.now()
    data = get_race(path=file_path)
    bucket_manager.put_object(bucket_name="brass-bucket-telemetry-forza",
                              data=data,
                              path=f'year={date.year}/month={date.month}/day={date.day}/{filename}.csv')
    print("Close connection!")
    pass