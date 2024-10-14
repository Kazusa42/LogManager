# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/10/10
#
# FILE: functions.py
# Description: functions which will be used in main loop are defined here
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import os
import re
import math
import argparse

from .logAnalyst import LogAnalyst

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE FUNCTIONS HERE

def generate_result_file_path(log_file_path: str, curr_path: str, ext=r'.xlsx') -> str:
    name, _ = os.path.splitext(os.path.basename(log_file_path))
    result_file_name = name + r'_analysis_results' + ext
    save_dir = os.path.join(curr_path, 'analysis_results')
    return os.path.join(save_dir, result_file_name)

def arg_parse(parser: argparse.ArgumentParser):
    parser.add_argument('-a', '--all', action='store_true', help='Process all log files under log folder.')
    parser.add_argument('-f', '--file', type=str, default='', help='The path to the interest log file (can be empty).')

    parser.add_argument('-w', '--warmupSamples', type=int, default=10, help='The number of data will be ignore the at first.')
    parser.add_argument('-n', '--analysisSamples', type=int, default=250, help='The number of data which will be used to analyze.')
    parser.add_argument('-d', '--physicalDistance', type=float, default=float('NaN'), help='Physical distance (cm) for comparison.')

    args = parser.parse_args()

    return {
        '-a': args.all,
        '-f': args.file,
        '-w': args.warmupSamples,
        '-n': args.analysisSamples,
        '-d': args.physicalDistance
    }

def parse_filename_for_measurement(filename: str) -> float: 
    match = re.search(r"(\d+(\.\d+)?)(cm|m)", filename)
    if match:
        unit = match.group(3)
        # change the unit of distance to cm
        distance = float(match.group(1)) if unit == 'cm' else float(match.group(1)) * 100
        return distance
    return float('NaN')

def get_filename(filename: str) -> str:
    return os.path.basename(filename) if filename else None

def chose_log_file(directory: str) -> str:
    # list all log files under 'directory' directory
    # and let user chose on of them
    # return the choosed file name
    log_files = [f for f in os.listdir(directory) if f.endswith('.log')]
    if not log_files:
        print('No log files found in the "log" folder.')
        return None
    print(f"{' Index':<7} {' File name':<20}")
    print('-' * 20)
    for idx, log_file in enumerate(log_files):
        print(f" {(idx + 1):<7} {log_file:<20}")
    
    try: 
        choice = int(input('Enter the index for a log file.')) - 1
        if 0 <= choice < len(log_files):
            return log_files[choice]
        else:
            print('Invalid choice.')
            return None
    except ValueError:
        print('Invalid input. Please input a number.')
        return None


def analysis(analyst: LogAnalyst, log_file_name: str, log_dir: str, phy_distance: float):
    if math.isnan(phy_distance):
        true_distance = parse_filename_for_measurement(log_file_name)
    else:
        true_distance = phy_distance
    
    analyst.analysis(
        log_file_path=os.path.join(log_dir, log_file_name),
        true_distance=true_distance
    )
