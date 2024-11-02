# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/11/02
#
# FILE: logAnalyst.py
# Description: Classes logAnalyst is defined here
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import math
import re
import statistics

import pandas as pd

from collections import defaultdict

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE CLASS HERE


class LogAnalyst(object):
    def __init__(self, warmup_samples: int, analysis_samples: int) -> None:
        self._warmup_samples = warmup_samples
        self._analysis_samples = analysis_samples
        self._content = None

        self._distance_pattern = {
            'gui': r"Distance\s*:\s*(\d+)",
            'teraterm': r"Distance\[cm\]: (\d+|-)",
            'mobis': r">> RAD RESULT:( Time Out|([\d.]+))"
        }

        self._ranging_failed_flag = {
            'gui': r"65535",
            'teraterm': r"-",
            'mobis': r" Time Out"
        }

        # ranging results used to analysis (intercepted)
        # with unit cm
        # self.distances = defaultdict(list)  
        self.analysis_results = {}  # analysis results

    def read_log_file(self, log_file_path: str) -> str:
        """ guess log file type from content """
        with open(log_file_path, 'r', encoding='utf-8') as f:
            # read log file line by line and remove empty line
            self._content = [line.strip() for line in f.readlines() if line.strip()]
        
        if not self._content:  # empty log file
            return None
        
        for line in self._content:
            if "PORT" in line and "TimeStamp" in line:
                return 'gui'
            elif "Status" in line and "BlockIndex" in line:
                return 'teraterm'
            elif "RAD RESULT" in line:
                return 'mobis'
            else: continue 
        return None
    
    def extract_distance(self, log_file_type, device_info_pattern=r"PORT\s*(\d+)"):
        self.distances = defaultdict(list)

        distance_pattern = self._distance_pattern[log_file_type]
        ranging_failed_flag = self._ranging_failed_flag[log_file_type]

        for line in self._content:
            device_id = '0'
            security_status_code = 0

            if log_file_type == 'gui':
                # extract port information for gui log
                device_id = re.search(device_info_pattern, line).group(1)
                # extract secutrity status code
                security_status_code = int(line.split(',')[9])
            
            # search distance information in current line
            match = re.search(distance_pattern, line)
            # only deal lines contains distance information
            if match:
                if not security_status_code:
                    tmp = match.group(1)
                    curr_dist = float(tmp) if tmp != ranging_failed_flag else float('inf')
                else:
                    # security code is not 0
                    # un-secured results, regarded as ranging failed
                    curr_dist = float('inf')
                
                if log_file_type == 'mobis' and not math.isinf(curr_dist):
                    # change the unit to cm
                    curr_dist = round(curr_dist * 100)
                self.distances[device_id].append(curr_dist)

        # intercept useful distances
        for device_id in self.distances.keys():
            length = len(self.distances[device_id])
            if length <= self._warmup_samples:
                self.distances[device_id] = self.distances[device_id]
            elif self._warmup_samples < length <= (self._warmup_samples + self._analysis_samples):
                self.distances[device_id] = self.distances[device_id][self._warmup_samples:]
            elif (self._warmup_samples + self._analysis_samples) < length:
                self.distances[device_id] = \
                    self.distances[device_id][self._warmup_samples:self._warmup_samples + self._analysis_samples]
            else: pass

    def analysis(self, physical_distance: float, device_id: str):
        success_dists = [d for d in self.distances[device_id] if not math.isinf(d)]  # successful ranging results
        if not success_dists:
            raise ValueError('All ranging failed. No valied ranging results to analysis.')
            
        min_dist = min(success_dists)
        max_dist = max(success_dists)
        ave_dist = statistics.mean(success_dists)
        median_dist = statistics.median(success_dists)
        stdev = statistics.stdev(success_dists)

        if math.isinf(physical_distance):
            offset = 'None (True distance is not provided)'
        else:
            offset = (physical_distance - ave_dist)
            
        successed_cnt = len(success_dists)
        failed_cnt = len(self.distances[device_id]) - successed_cnt
        ranging_success_rate = successed_cnt / len(self.distances[device_id])

        self.analysis_results[device_id] = {
            'min distance (cm)': min_dist,
            'max distance (cm)': max_dist,
            'average distance (cm)': round(ave_dist, 2),
            'median distance (cm)': round(median_dist, 2),
            'offset (real - ave.) (cm)': round(offset, 2),
            'std. deviation': round(stdev, 2),
            'success count': successed_cnt,
            'fail count': failed_cnt,
            'success rate': round(ranging_success_rate, 2)
        }
    
    def show_result(self, device_id):
        print(f"Ranging results from device @ port {device_id}:")
        print(f"{' Metric':<30}{' Value':<10}\n" + '-' * 41)
        for key, value in self.analysis_results[device_id].items():
            print(f" {key:<30}{value:<10}")
        print('-' * 41, end='\n\n')
    
    def save_result(self, save_file_path):
        with pd.ExcelWriter(save_file_path, engine='openpyxl') as writer:
            for device_id, results in self.analysis_results.items():
                dists = self.distances[device_id]

                max_len = max(len(dists), len(results))
                data = {
                    'Ranging result': dists + [None] * (max_len - len(dists)),
                    'Metric': list(results.keys()) + [None] * (max_len - len(results)),
                    'Value': list(results.values()) + [None] * (max_len - len(results))
                }

                df = pd.DataFrame(data)
                df.fillna('nan')
                df.to_excel(writer, sheet_name=f"device@port{device_id}", index=False)

# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------


if __name__ == '__main__':
    # interest log file (log file name)
    log_file_path = r'C:\Users\lyin0\Desktop\LogManager\logs\8.0m.log'

    # where to store the analysis results (save file name)
    save_file_path = r'C:\Users\lyin0\Desktop\LogManager\analysis_results\test.xlsx'

    # physical distance with unit cm
    physical_distance = 800
    
    # igonre the first warmup_samples ranging results
    # use analysis_samples ranging results to analysis
    warmup_samples, analysis_samples = 10, 250

    # initial an instance of LogAnalyst
    myAnalyst = LogAnalyst(warmup_samples, analysis_samples)

    # decide log file type, gui, teraterm or mobis
    file_type = myAnalyst.read_log_file(log_file_path)

    # parse log file, extract ranging results
    myAnalyst.extract_distance(file_type)

    for device_id in myAnalyst.distances.keys():
        myAnalyst.analysis(physical_distance, device_id)  # analysis
        myAnalyst.show_result(device_id)  # show results on terminal

    myAnalyst.save_result(save_file_path)  # save all results to one excel file

    
# END OF FILE
#---------------------------------------------------------------------------------