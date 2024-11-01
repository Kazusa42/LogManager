# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/10/13
#
# FILE: main.py
# Description: main loop entry of the project
#---------------------------------------------------------------------------------

import os
import argparse

import utils.logAnalyst as logAnalyst
import utils.functions as funcs
import utils.component as comps


def main():

    comps.Const.RESULT_DIR = os.path.join(os.path.dirname(__file__), 'analysis_results')
    comps.Const.LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

    parser = argparse.ArgumentParser(description='Process a log file and analyze distance measurements.')
    args_dict = funcs.logAnalyst_arg_parser(parser=parser)

    analyst = logAnalyst.LogAnalyst(
        warm_up_samples=args_dict['-w'],
        analysis_samples=args_dict['-n'],
        save_dir=comps.Const.RESULT_DIR
    )

    if args_dict['-a']:
        # Process all log files under log folder
        log_files = [f for f in os.listdir(comps.Const.LOG_DIR) if f.endswith('.log')]
        for curr in log_files:
            funcs.analysis(
                analyst=analyst,
                log_file_name=curr,
                log_dir=comps.Const.LOG_DIR,
                phy_distance=args_dict['-d']
            )
            # analyst.show_result()
        pass
    else:  # process single file at once
        # get file name from input args 
        log_file_name = funcs.get_filename(args_dict['-f'])
        if log_file_name is not None and log_file_name.endswith('.log'):  # reveived a log file
            funcs.analysis(
                analyst=analyst,
                log_file_name=log_file_name,
                log_dir=comps.Const.LOG_DIR,
                phy_distance=args_dict['-d']
            )
            print(f'The analysis results of {log_file_name} is: ')
            analyst.show_result()
        else:
            # list all log files in 'logs' directory to let user choose one or more
            print("Failure to receive a valid log file from command. Display all log files under folder 'logs'")
            while True:
                log_file_name = funcs.chose_log_file(directory=comps.Const.LOG_DIR)
                funcs.analysis(
                    analyst=analyst,
                    log_file_name=log_file_name,
                    log_dir=comps.Const.LOG_DIR,
                    phy_distance=args_dict['-d']
                )
                print(f'The analysis results of {log_file_name} is: ')
                analyst.show_result()
            

if __name__ == "__main__":
    main()

