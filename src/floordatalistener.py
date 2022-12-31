import numpy as np
import threading
import socket
import re
from floordataconverter import FloorDataConverter

class FloorDataListener:
    
    def __init__(self):
        self.floor_data_converter = FloorDataConverter()
        self.UDP_PORT = 11111
        self.UDP_IP = "192.168.100.110"
        self.splited_numbers = 4
        # self.latest_image = np.zeros((self.floor_data_converter.cells.shape[0], 
        #                             self.floor_data_converter.cells.shape[1]))
        # self.splited_latest_image = np.zeros((self.splited_numbers, 9, 18))
        self.cop = np.zeros((self.splited_numbers, 2))
        self.thread = threading.Thread(target = self.run_update_thread)
        self.thread.start()
        # self.thread.join()
        
    def run_update_thread(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((self.UDP_IP, self.UDP_PORT))
        print(f'Start listening to {self.UDP_IP}:{self.UDP_PORT}')
        # floor_data_converter = FloorDataConverter()
        
        while True:
            indata, addr = udp_socket.recvfrom(65535)     
            data = re.split('\n', indata.decode())
            self.latest_image = self.floor_data_converter.convert(data[-1])
            self.splited_latest_image = self.floor_data_converter.split_cells(self.latest_image, 4)
            # print(self.splited_latest_image)
            self.cop = list(map(self.floor_data_converter.calculate_cop, self.splited_latest_image))
            
        
    def get_latest_floor_image(self):
        return self.latest_image
    
    def get_cop(self):
        return self.cop
