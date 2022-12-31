import numpy as np
import json
import re
from plotter import main


class FloorDataConverter:
    
    def isJsonl(self, data):
        # jsonl is started with "{", .dat is started with a number, typically "1"
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

        # epoch:
        # dat+=str(json_dict["epoch"])
        # dat+=":"

        # floor:
        values = json_dict["floor"]

        for line in values:
            for v in line:
                dat += str(v)
                dat += ","
            dat = dat[0:-1]
            dat += ";"

        return dat
        
    def convert(self, raw_data):
        
        # if raw_data is .jsonl, convert it to .dat
        if self.isJsonl(raw_data):
            raw_data = self.jsonl2dat(raw_data)
        # timestamps
        tmp_data = re.split(':', raw_data)
        str_rows = re.split(';', tmp_data[1])[:-1]
        floor_image = [
            [int(value) for value in re.split(',', str_row)]
            for str_row in str_rows]
        cells = np.array(floor_image, dtype=int)
        
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

        # splited_cells = np.concatenate([
        #     np.split(cells[:])
        # ])
            
        return splited_cells

#  ピンポイントでセルを抽出できる関数作成
    # def 
    