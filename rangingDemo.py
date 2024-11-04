# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/11/04
#
# FILE: rangingDemo.py
# Description: option supported script for ranging demo
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import os
import argparse

import utils.component as comps
import utils.functions as funcs

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

def main():
    comps.Const.COMMAND_FILE = os.path.join(os.path.dirname(__file__), 'command.json')
    comps.Const.CLISERVER = os.path.join(os.path.dirname(__file__), 'Cliserver.exe')
    comps.Const.LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

    parser = argparse.ArgumentParser(description='Ranging demo')
    args_dict = funcs.rangingDemo_arg_parser(parser=parser)

    funcs.welcome_menu_for_rangingdemo()

    device = funcs.init_device(args_dict, comps.Const.COMMAND_FILE)
    print('Device initialized successfully.')
    print(f"Device info: {device}")

    log_file_name = funcs.name_log_file(device.role, args_dict['-d'])
    if log_file_name:
        log_file = open(os.path.join(comps.Const.LOG_DIR, log_file_name), 'w')
    else:
        log_file =None

    while True:
        user_input = input("Waiting for command: ").lower().strip()
        if user_input.startswith('set power'):
            device.tx_power = int(user_input.split('=')[1])
        elif user_input.startswith('run'):
            funcs.run_ranging_demo(device, args_dict['-t'], comps.Const.CLISERVER, log_file)
        else:
            print('Unsupported command.')
    

if __name__ == "__main__":
    # Example usage
    main()

# END OF FILE
#---------------------------------------------------------------------------------