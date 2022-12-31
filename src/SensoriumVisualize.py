import socket
import numpy as np
import matplotlib.pyplot as plt
import sys  
import cv2
import re
import time
import threading
import math
import json
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import streamlit as st
from matplotlib.animation import FuncAnimation

np.set_printoptions(threshold=np.inf)

C_ADC2KG = 53279

class FloorDataConverter:
    
    def isJsonl(self, data):
        #jsonl is started with "{", .dat is started with a number, typically "1"
        if data[0] == "{":
            return True
        else:
            return False

    def jsonl2dat(self, jsonl_data):
#         example in:
#   epoch: 167020402408,
#  floor: [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
#  example out:
#  "167020402408:1,2,3;4,5,6;7,8,9;"
        dat = ""
        json_dict = json.loads(jsonl_data)

        #epoch:
        # dat+=str(json_dict["epoch"])
        # dat+=":"

        #floor:
        values = json_dict["floor"]

        for line in values:
            for v in line:
                dat+=str(v)
                dat+=","
            dat = dat[0:-1]
            dat+=";"
        return dat
        
    def convert(self, raw_data):
        
        #if raw_data is .jsonl, convert it to .dat
        if self.isJsonl(raw_data):
            print('send data is json format')
            raw_data = self.jsonl2dat(raw_data)
        tmp_data = re.split(':', raw_data)
        str_rows = re.split(';', tmp_data[1])[:-1]
        floor_image = [
            [int(value) for value in re.split(',', str_row)]
            for str_row in str_rows]
        cells = np.array(floor_image, dtype=int)
        # print('cells=', cells)
        
        return cells
        
    def calculate_cop(self, cells): 
        x = np.arange(0, cells.shape[1])
        y = np.arange(0, cells.shape[0])
        weight = np.sum(cells)
        CoP_x = np.dot(x, np.sum(cells, axis=0))
        CoP_y = np.dot(y, np.sum(cells, axis=1))
        
        if weight == 0:
            return 0, 0
        else:
            return CoP_x/weight, CoP_y/weight
    
    def calculate_weight(self, cells):
            
        return np.sum(cells)

    def split_cells(self, cells, pixel_size=2):
        splited_cells = np.concatenate([
            np.split(cells[:cells.shape[0]//2], 2, axis=1),
            np.split(cells[cells.shape[0]//2:], 2, axis=1),
            ], axis=0)
            
        return splited_cells

#  ピンポイントでセルを抽出できる関数作成
    # def 
    
class FloorDataListener:
    
    def __init__(self):
        self.UDP_PORT = 12346
        self.UDP_IP = "192.168.100.110"
        self.splited_numbers = 4
        self.latest_image = np.zeros((88, 48))
        # self.latest_image = np.zeros((6, 24))

        self.splited_latest_image = np.zeros((self.splited_numbers, 44, 24))
        self.cop = np.zeros((self.splited_numbers, 4))
        self.thread = threading.Thread(target = self.run_update_thread)
        self.thread.start()
        # self.thread.join()
        
    def run_update_thread(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((self.UDP_IP, self.UDP_PORT))
        print(f'Start listening to {self.UDP_IP}:{self.UDP_PORT}')
        floor_data_converter = FloorDataConverter()
        
        while True:
            indata, addr = udp_socket.recvfrom(65535)     
            data = re.split('\n', indata.decode())
            self.latest_image = floor_data_converter.convert(data[-1])
            # print('self.latest_image=', self.latest_image)
            # print(self.latest_image.shape)
            self.splited_latest_image = floor_data_converter.split_cells(self.latest_image, 4)
            # print(self.splited_latest_image)
            self.cop = list(map(floor_data_converter.calculate_cop, self.splited_latest_image))
            
        
    def get_latest_floor_image(self):
        return self.latest_image
    
    def get_cop(self):
        return self.cop


class Plotter:
    
    def __init__(self):
        self.fig = go.Figure()
        self.udp_listener = FloorDataListener()

    def plot_cop(self, cop, latest_image):
        
        if cop[0][0] != 0:
            self.fig.add_scatter(cop[0][0], cop[0][1], c='r', s=50)

        if cop[1][0] != 0:
            self.fig.add_scatter(cop[1][0]+latest_image.shape[1]/2,
                        cop[1][1], c='r', s=50)
        if cop[2][0] != 0:
            self.fig.add_scatter(cop[2][0], 
                        cop[2][1]+latest_image.shape[0]/2, c='r', s=50)
        if cop[3][0] != 0:
            self.fig.add_scatter(cop[3][0]+latest_image.shape[1]/2,
                        cop[3][1]+latest_image.shape[0]/2, c='r', s=50)
        
    def update(self, *fargs):
        # self.fig.clear()
        latest_image = self.udp_listener.get_latest_floor_image()
        print('self.latest_image=', latest_image)
        # self.fig.imshow(latest_image, interpolation='nearest')
        self.fig.add_trace(go.Heatmap(latest_image))
        # pio.show(plotter.update, renderer='browser')
        # self.fig.grid()
        # self.fig.set_xlim(0, self.udp_listener.latest_image.shape[1])
        # self.fig.set_ylim(0, self.udp_listener.latest_image.shape[0])
        # self.fig.hlines(self.udp_listener.latest_image.shape[0]/2, 
        #                 0, self.udp_listener.latest_image.shape[1], linestyles='dashed')
        # self.fig.vlines(self.udp_listener.latest_image.shape[1]/2, 
        #                 0, self.udp_listener.latest_image.shape[0], linestyles='dashed')
        cop = self.udp_listener.get_cop()
        # self.fig.invert_yaxis()
        # print(cop)
        # self.plot_cop(cop, latest_image)
        

if __name__ == "__main__":
    plotter = Plotter()
    plotter.update()
    plotter.fig.show()