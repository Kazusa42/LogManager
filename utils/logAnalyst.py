# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/10/12
#
# FILE: logAnalyst.py
# Description: Classes logAnalyst is defined here
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import os
import math
import re
import statistics

import pandas as pd

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE CLASS HERE


class LogAnalyst(object):
    def __init__(self, warm_up_samples: int, analysis_samples: int, save_dir: str) -> None:
        self._warm_up_samples = warm_up_samples
        self._analysis_samples = analysis_samples

        self.save_dir = save_dir
        self.distances = []
        self.log_content = None
        self.analysis_result = None
    
    def _read_log(self, log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as f:
            self.log_content = f.read()
    
    def _decide_log_type(self):
        if self.log_content:
            lines = [line.strip() for line in self.log_content.splitlines() if line.strip()]

            if not lines:  # no valid data
                return None

            for line in lines:
                if "PORT" in line and "TimeStamp" in line:
                    return 'gui'
                elif "Status" in line and "BlockIndex" in line:
                    return 'teraterm'
                elif "RAD RESULT" in line:
                    return 'non_gui'
                else: continue 
        return None  # can not recognize the log type
    
    def _extract_distance(self):
        log_type = self._decide_log_type()
        if log_type == 'gui':
            pattern = re.compile(r"Distance\s*:\s*(\d+)")
        elif log_type == 'teraterm':
            pattern = re.compile(r"Distance\[cm\]: (\d+|-)")
        elif log_type == 'non_gui':
            # pattern for Mobis
            pattern = re.compile(r'>> RAD RESULT:( Time Out|([\d.]+)m)')
        else: raise TypeError('Can not recognize log file type.')

        matches = pattern.findall(self.log_content)
        if log_type == 'gui':
            self.distances = [
                float('NaN') if str(match) == '65535' else float(match)
                for match in matches 
            ]
        elif log_type == 'teraterm':
            self.distances = [
                float('NaN') if str(match) == '-' else float(match)
                for match in matches 
            ]
        elif log_type == 'non_gui':
            self.distances = [
                float('NaN') if match[0] == ' Time Out' else float(match[1])
                for match in matches
            ]
        else: pass
    
    @staticmethod
    def _decide_unit(valid_distance) -> str:
        count = sum(1 for x in valid_distance if x > 10)

        if count > len(valid_distance) / 2:
            return 'cm'
        else: return 'm'

    def _get_save_file_name(self, log_file_path, ext='xlsx'):
        filename = os.path.splitext(os.path.basename(log_file_path))[0]
        new_filename = f'{filename}_analysis.{ext}'
        return os.path.join(self.save_dir, new_filename)
    
    def _save_result(self, result: dict, distance, log_file_path):
        save_path = self._get_save_file_name(log_file_path)
        
        keys, values = list(result.keys()), list(result.values())
        max_len = max(len(distance), len(keys))

        data = {
            'ranging results': distance + [None] * (max_len - len(distance)),
            'Metrics': keys + [None] * (max_len - len(keys)),
            'Values': values + [None] * (max_len - len(values))
        }
        df = pd.DataFrame(data)
        df.to_excel(save_path, index=False)

    def analysis(self, log_file_path, true_distance: float):
        self._read_log(log_file_path)
        self._extract_distance()
        
        # decide which part of data will be used to analysis
        total_distances_num = len(self.distances)
        if total_distances_num <= self._warm_up_samples:
            distances_used_to_analysis = self.distances

        elif self._warm_up_samples < total_distances_num <= (self._warm_up_samples + self._analysis_samples):
            distances_used_to_analysis = self.distances[self._warm_up_samples:]

        elif (self._warm_up_samples + self._analysis_samples) < total_distances_num:
            distances_used_to_analysis = self.distances[self._warm_up_samples:self._warm_up_samples + self._analysis_samples]
        
        valid_distances = [d for d in distances_used_to_analysis if not math.isnan(d)]
        if not valid_distances:
            raise ValueError('No valid data for analysis.')
        
        # guess the unit by parse ranging results in log file.
        unit = self._decide_unit(valid_distances)
        
        # get statistics with unit 'cm'
        min_distance = min(valid_distances) if unit == 'cm' else min(valid_distances) * 100
        max_distance = max(valid_distances) if unit == 'cm' else max(valid_distances) * 100
        ave_distance = statistics.mean(valid_distances) if unit == 'cm' else statistics.mean(valid_distances) * 100
        median_distance = statistics.median(valid_distances) if unit == 'cm' else statistics.median(valid_distances) * 100

        if math.isnan(true_distance):
            offset = 'None (True distance is not provided)'
        else:
            offset = (true_distance - ave_distance)

        stdev = statistics.stdev(valid_distances)

        success_count = len(valid_distances)
        fail_count = len(distances_used_to_analysis) - success_count
        success_rate = success_count / len(distances_used_to_analysis)

        self.analysis_result = {
            'min distance (cm)': min_distance,
            'max distance (cm)': max_distance,
            'average distance (cm)': round(ave_distance, 2),
            'median distance (cm)': round(median_distance, 2),
            'offset (real - ave.) (cm)': round(offset, 2),
            'std. deviation': round(stdev, 2),
            'success count': success_count,
            'fail count': fail_count,
            'success rate': round(success_rate, 2)
        }
        self._save_result(self.analysis_result, distances_used_to_analysis, log_file_path)
    
    def show_result(self):
        print(f"{' Metric':<30}{' Value':<10}")
        print('-' * 41)

        for key, value in self.analysis_result.items():
            print(f" {key:<30}{value:<10}")
        print('-' * 41, end='\n\n')

# END OF CLASS DEFINITION
#---------------------------------------------------------------------------------


if __name__ == '__main__':
    save_dir = r'C:\Users\a5149517\Desktop\Automation_tools\analysis_results'
    
    warm_up_samples, analysis_samples = 10, 100

    log_file = r'C:\Users\a5149517\Desktop\Automation_tools\logs\140cm.log'
    true_distance = 0.5
    
    analyst = LogAnalyst(warm_up_samples, analysis_samples, save_dir)
    analyst.analysis(log_file, true_distance)
    print(f'The analysis results of {log_file} is: ')
    analyst.show_result()
