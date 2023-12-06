import json
import logging
import socket
import struct
import uuid

from src.utils.handler import DataWriter

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class ForzaBrigde():
    def __init__(self, udp_ip: str, udp_port: int) -> None:
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        
        self.server = None
        self.setup_server()
        pass

    def setup_server(self):
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)
        sock.bind((self.udp_ip, 
                self.udp_port))
        logging.info(f"Has been created new client: IP: {self.udp_ip} PORT: {self.udp_port}")
        self.server = sock
        return None
    

class RaceRecord(ForzaBrigde):
    def __init__(self, udp_ip: str, udp_port: int, frequency: int, mode: str = "dash") -> None:
        super().__init__(udp_ip, udp_port)
        self.mode = mode
        self.frequency = frequency
        self.filename = str(uuid.uuid1())
        pass
    
    @property
    def data_format(self):
        with open("header.json", 'r') as f:
            file = json.loads(f.read())
        return file[self.mode]["format"]
    
    @property
    def list_columns(self):
        with open("header.json", 'r') as f:
            file = json.loads(f.read())
        list_columns = file[self.mode]["columns"]
        return ",".join([column["name"] for column in list_columns])

    @property
    def file_path(self):
        return f"./data/{self.filename}.csv"

    @property
    def frequency_time(self):
        return 1000 / self.frequency

    def create_record(self):
        writer = DataWriter(path=self.file_path)
        writer.insert(self.list_columns)
        logging.info(f"Inserting data into {self.file_path}")
        return None
    
    def prepare_to_insert(self, data: tuple):
        char_list = ["(",")"]
        for char in char_list:
            data = str(data).replace(char,"")
        return data + '\n'        

    def delta_time(self, actual_record, last_record):
        return actual_record - last_record

    def start(self):
        n = 0
        last_record = 0
        writer = DataWriter(path=self.file_path)
        while True:
            data, addr = self.server.recvfrom(1024)
            unpacked_data = struct.unpack(self.data_format, data)
            
            actual_record = unpacked_data[1]
            logging.debug(f"Result: {actual_record - last_record}")

            if self.delta_time(actual_record, last_record) > self.frequency_time:
                last_record = actual_record
                data_to_insert = self.prepare_to_insert(unpacked_data)
                writer.insert(data_to_insert)
                n+=1
            
            if n==100:
                logging.info(f"Has been inserted {n} records.")
                n=0  
        
        return None