# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/11/02
#
# FILE: logProcessing.py
# Description: option supported script for logAnalyst
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import os
import argparse

import utils.logAnalyst as logAnalyst
import utils.functions as funcs
import utils.component as comps

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

def main():

    comps.Const.RESULT_DIR = os.path.join(os.path.dirname(__file__), 'analysis_results')
    comps.Const.LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

    parser = argparse.ArgumentParser(description='Process a log file and analyze distance measurements.')
    args_dict = funcs.logAnalyst_arg_parser(parser=parser)

    analyst = logAnalyst.LogAnalyst(
        warmup_samples=args_dict['-w'],
        analysis_samples=args_dict['-n'],
    )

    if args_dict['-a']:
        # Process all log files under 'logs' folder
        # option '-a' has the heighest priority
        log_files = [f for f in os.listdir(comps.Const.LOG_DIR) if f.endswith('.log')]
        for filename in log_files:
            print(f"Processing {filename}.")
            log_file_path = os.path.join(comps.Const.LOG_DIR, filename)
            phy_distance = funcs.parse_phy_distance(args_dict['-d'], filename)

            funcs.analysis(analyst, log_file_path, phy_distance, visual=False)

            save_file_path = funcs.construct_save_file_path(filename, comps.Const.RESULT_DIR)
            analyst.save_result(save_file_path)
    else: 
        # process single file at once, get file name from input args 
        if args_dict['-f'] is None:
            # list all log files in 'logs' directory to let user choose one or more
            print("Failure to receive a valid log file from command. Display all log files under folder 'logs'.")
            while True:
                filename = funcs.chose_log_file(directory=comps.Const.LOG_DIR)
                if filename:
                    log_file_path = os.path.join(comps.Const.LOG_DIR, filename)
                    phy_distance = funcs.parse_phy_distance(args_dict['-d'], filename)

                    funcs.analysis(analyst, log_file_path, phy_distance)
                    save_file_path = funcs.construct_save_file_path(filename, comps.Const.RESULT_DIR)
                    analyst.save_result(save_file_path)

        elif os.path.isabs(args_dict['-f']):  # received an absolute path
            filename = os.path.basename(args_dict['-f'])
            phy_distance = funcs.parse_phy_distance(args_dict['-d'], filename)

            funcs.analysis(analyst, args_dict['-f'], phy_distance)

            save_file_path = funcs.construct_save_file_path(filename, comps.Const.RESULT_DIR)
            analyst.save_result(save_file_path)
        
        else:  # received a relative path from option
            filename = os.path.basename(args_dict['-f'])
            log_file_path = os.path.join(comps.Const.LOG_DIR, filename)
            phy_distance = funcs.parse_phy_distance(args_dict['-d'], filename)

            funcs.analysis(analyst, log_file_path, phy_distance)

            save_file_path = funcs.construct_save_file_path(filename, comps.Const.RESULT_DIR)
            analyst.save_result(save_file_path)


if __name__ == "__main__":
    main()

# END OF FILE
#---------------------------------------------------------------------------------