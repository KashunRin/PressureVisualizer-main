import numpy as np
import matplotlib.pyplot as plt
import sys  
import time
from matplotlib.animation import FuncAnimation

from floordatalistener import FloorDataListener
from floordataconverter import FloorDataConverter

np.set_printoptions(threshold=np.inf)

class Plotter:
    
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(6,11))
        # self.fig, self.ax = plt.subplots()

        self.udp_listener = FloorDataListener()

    def plot_cop(self, cop, latest_image):
        
        if cop[0][0] != 0:
            self.ax.scatter(cop[0][0], cop[0][1], c='r', s=50)

        if cop[1][0] != 0:
            self.ax.scatter(cop[1][0]+latest_image.shape[1]/2,
                        cop[1][1], c='r', s=50)
        if cop[2][0] != 0:
            self.ax.scatter(cop[2][0], 
                        cop[2][1]+latest_image.shape[0]/2, c='r', s=50)
        if cop[3][0] != 0:
            self.ax.scatter(cop[3][0]+latest_image.shape[1]/2,
                        cop[3][1]+latest_image.shape[0]/2, c='r', s=50)
        
    def update(self, frame, *fargs):
        self.ax.clear()
        self.latest_image = self.udp_listener.get_latest_floor_image()
        self.ax.imshow(self.latest_image, aspect='equal')
        self.ax.grid()
        self.ax.set_xlim(0, self.udp_listener.latest_image.shape[1]-1)
        self.ax.set_ylim(0, self.udp_listener.latest_image.shape[0]-1)
        self.ax.hlines(self.udp_listener.latest_image.shape[0]/2, 
                        0, self.udp_listener.latest_image.shape[1], linestyles='dashed')
        self.ax.vlines(self.udp_listener.latest_image.shape[1]/2, 
                        0, self.udp_listener.latest_image.shape[0], linestyles='dashed')
        cop = self.udp_listener.get_cop()
        self.ax.invert_yaxis()
        self.plot_cop(cop, self.latest_image)


if __name__ == "__main__":
    plotter = Plotter()
    floordataconverter = FloorDataConverter()
    floordatalistener = FloorDataListener()

    outfile = open('Plantar.dat', 'w')
    ani = FuncAnimation(plotter.fig, plotter.update, frames=None, interval=10)
    # ani.save('Plantar_test.gif', writer='pillow')
    # ani.save('Planter_test.mp4', writer='ffmpeg')
    
    outfile.close() 
    
    plt.show()