import argparse

from src.utils.game_link import RaceRecord

parser = argparse.ArgumentParser(
                    prog='ForzaMotorsport',
                    description='Race data ingestion')

parser.add_argument('-i', '--ip', type=str)
parser.add_argument('-p', '--port', type=int)
parser.add_argument('-m', '--mode', type=str)
parser.add_argument('-f', '--frequency', type=int)

args = parser.parse_args()

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

try:
    race.start()
except KeyboardInterrupt:
    print("\nClose connection!")
    pass