# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/10/10
#
# FILE: main.py
# Description: main loop entry of the project
#---------------------------------------------------------------------------------

import os
import argparse

import utils.component as comps
import utils.functions as funcs


def main():
    parser = argparse.ArgumentParser(description='Process a log file and analyze distance measurements.')

    parser.add_argument('-d', '--distance', type=float, required=True, help='The real distance for comparison')
    parser.add_argument('-f', '--file', type=str, default='', help='The path to the log file (can be empty)')
    parser.add_argument('-n', '--numOfData', type=int, default=250, help='The number of data which will be used to analyze.')
    parser.add_argument('-w', '--warmUpSamples', type=int, default=10, help='The number of data will be ignore the at first')

    args = parser.parse_args()

    real_distance = args.distance
    log_file_path = args.file
    analysis_samples = args.numOfData
    warm_up_samples = args.warmUpSamples

    curr_path = os.path.dirname(__file__)

    if log_file_path == '':
        log_folder = os.path.join(curr_path, 'log')
        log_files = [f for f in os.listdir(log_folder) if f.endswith('.log')]

        if not log_files:
            print("No .log files found in the 'log' folder.")
            return

        print("Please choose a log file from the list below:")
        for idx, log_file in enumerate(log_files):
            print(f"{idx + 1}. {log_file}")
        
        try:
            choice = int(input("Enter the number corresponding to your choice: ")) - 1
            if 0 <= choice < len(log_files):
                log_file_path = os.path.join(log_folder, log_files[choice])
            else:
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
    else:
        if not os.path.isabs(log_file_path):
            log_file_path = os.path.join(os.path.join(curr_path, 'log'), log_file_path)

    if not os.path.isfile(log_file_path):
        print(f"The file {log_file_path} does not exist.")
        return

    log_manager = comps.LogManager(log_file_path, real_distance)
    analysis_result = log_manager.analysis(warm_up_samples=warm_up_samples, analysis_samples=analysis_samples)

    log_manager.print_result(analysis_result)

    save_path = funcs.generate_result_file_path(
        log_file_path=log_file_path,
        curr_path=curr_path
    )
    log_manager.save_results(save_path)

if __name__ == "__main__":
    if_terminal = True  # if do not want to run script in trminal mode, change the value to False
    
    if if_terminal:
        main()
    else:
        real_distance = 0.5  # physical distance (m)
        log_file_path = r'your_log_file.log'  # absolute path of log file (including file name)
        save_path = r'save_path.xlsx'  # absolute path of result file (including file name, must be excel file)
        warm_up = 10  # the number of ranging results will be ignored at first
        data_len = 250  # the number of data will be used to analyze

        log_manager = comps.LogManager(log_file_path, real_distance)
        analysis_result = log_manager.analysis(warm_up=warm_up, data_len=data_len)
        log_manager.print_result(analysis_result)
        log_manager.save_results(save_path)
