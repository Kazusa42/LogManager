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
import sys
import math
import json
import time
import socket
import argparse
import platform

import serial.tools.list_ports

from utils.logAnalyst import LogAnalyst
from utils.device import Device
# from .logAnalyst import LogAnalyst

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE FUNCTIONS HERE

#------------------------- FUNCTIONS FOR LOG ANALYST -----------------------------

def logAnalyst_arg_parser(parser: argparse.ArgumentParser):
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-f', '--file', type=str, default=None)
    parser.add_argument('-d', '--physicalDistance', type=float, default=float('inf'))
    parser.add_argument('-w', '--warmupSamples', type=int, default=10)
    parser.add_argument('-n', '--analysisSamples', type=int, default=250)

    args = parser.parse_args()

    return {
        '-a': args.all,
        '-f': args.file,
        '-w': args.warmupSamples,
        '-n': args.analysisSamples,
        '-d': args.physicalDistance
    }

def chose_log_file(directory: str) -> str:
    # list all log files under 'logs' directory and let user chose on of them
    # return the choosed log file name
    log_files = [f for f in os.listdir(directory) if f.endswith('.log')]
    if not log_files:
        print('No log files found in the "log" folder.')
        return None
    print(f"{' Index':<7} {' File name':<20}\n" + '-' * 20)
    for idx, log_file in enumerate(log_files):
        print(f" {(idx + 1):<7} {log_file:<20}")
    
    try:
        user_input = input('Enter the index for a log file.')
        if user_input.startswith('exit'):
            sys.exit('Exiting by user input...')

        choice = int(user_input) - 1
        if choice == 'exit':
            sys.exit()
        elif 0 <= choice < len(log_files):
            return log_files[choice]
        else:
            print('Invalid choice.')
            return None
    except ValueError:
        print('Invalid input. Please input a number.')
        return None

def construct_save_file_path(log_file_name: str, result_dir: str, ext=r'xlsx') -> str:
    filename = log_file_name.split('.log')[0]
    res_filename = f"{filename}_analysis.{ext}"
    return os.path.join(result_dir, res_filename)

def parse_phy_distance(phy_distance: float, filename: str) -> float:
    if math.isinf(phy_distance):
        match = re.search(r"(\d+(\.\d+)?)(cm|m)", filename)
        if match:
            unit = match.group(3)
            phy_dist = float(match.group(1)) if unit == 'cm' else float(match.group(1)) * 100
        else:
            phy_dist = float('inf')
    else:
        phy_dist = phy_distance
    return phy_dist

def analysis(analyst: LogAnalyst, log_file_path: str, phy_distance: float, visual=True):
    file_type = analyst.read_log_file(log_file_path)
    print(f"log format: {file_type}")
    if file_type is None:
        raise ValueError('Unsupported log file format.')
    
    analyst.extract_distance(file_type)
    for device_id in analyst.distances.keys():
        analyst.analysis(phy_distance, device_id)  # analysis
        if visual:
            analyst.show_result(device_id)  # show results on terminal
    

#------------------------ FUNCTIONS FOR RANGING DEMO -----------------------------

def rangingDemo_arg_parser(parser: argparse.ArgumentParser):
    parser.add_argument('-r', '--role', type=str, default=None)
    parser.add_argument('-c', '--comPort', type=str, default=None)
    parser.add_argument('-d', '--distance', type=float, default=float('inf'))
    parser.add_argument('-p', '--power', type=int, default=5)
    parser.add_argument('-t', '--time', type=int, default=600)
    
    args = parser.parse_args()

    return {
        '-r': args.role,
        '-d': args.distance,
        '-p': args.power,
        '-t': args.time,
        '-c': args.comPort,
    }

def welcome_menu_for_rangingdemo():
    """
    Displays a welcome message and user menu.
    """
    os.system('cls') if platform.system() == 'Windows' else os.system('clear')
    print("----------------------------------------------------------------------------------")
    print("- UWB RANGING DEMO AUTOMATION TOOL FOR FIRA AND DEBBY")
    print("- INTERNAL USE ONLY @ RENESAS/A&C/CONN/ACENG")
    print("- Created on Sep.30, 2024.")
    print('-')
    print("--------------------------------- COMMANDS LIST ----------------------------------")
    print("- \'run\'              : Start the ranging demo.")
    print("- \'set power=[value]\': Set the transmission power of current device.")
    print("-                      : The transmission power of current device is default to 5.")
    print("----------------------------------------------------------------------------------")

def load_commands(cmd_file_path: str, role: str) -> dict:
    with open(cmd_file_path, 'r', encoding='utf-8') as f:
        commands = json.load(f)
    return commands[role]

def select_com_port() -> str:
    ports = list(serial.tools.list_ports.comports())
    usb_serial_ports = [port for port in ports if 'USB Serial' in port.description]

    if usb_serial_ports:
        print("Available USB serial COM ports:")
        for port in usb_serial_ports:
            print(f" -- {port.device}")

        selected_port = input("Please select a COM port (e.g., 'com3'): ").lower()
        while not any(p.device.lower() == selected_port for p in usb_serial_ports):
            selected_port = input("Invalid COM port. Please select a valid COM port: ").lower()
        return selected_port
    else:
        sys.exit('No USB serial port found. Check connection.\nExiting...')
        return None

def set_role(role_mapping) -> str:
    role = input("Please enter the device role ('rx' for responder or 'tx' for initiator): ").strip().lower()
    while role not in role_mapping.keys():
        role = input("Invalid role. Please input a vaild role ('rx' for responder or 'tx' for initiator).")
    return role_mapping[role]

def find_available_tcp_port(start_port=20020, host=r'127.0.0.1'):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                port += 1

def init_device(args_dict: dict, cmd_file_path: str) -> Device:
    # init roll
    role_mapping = {'tx': 'initiator', 'rx': 'responder'}
    if args_dict['-r'] is not None:
        role = role_mapping[args_dict['-r']]
    else:
        role = set_role(role_mapping)

    # inti commands
    cmds = load_commands(cmd_file_path, role)

    # init COM port
    if args_dict['-c'] is not None:
        com_port = args_dict['-c']
    else:
        com_port = select_com_port()
    
    # init TCP port
    tcp_port = find_available_tcp_port()

    device = Device(role, cmds, com_port, tcp_port)
    return device

def name_log_file(device_role: str, distance: float) -> str:
    if device_role == 'initiator':
        return None

    if not math.isinf(distance):
        return f"{str(int(distance))}cm.log"
    else:
        user_input = input('Create log file with name: ')
        if user_input.isnumeric():
            return f"{str(user_input)}cm.log"
        else:
            return f"{str(user_input)}.log"

def run_ranging_demo(device: Device, ranging_time: int, cliserver_path: str, log_file=None):
    # establish TCP connection
    device.establish_tcp_conn(cliserver_path)

    # send all commands to start ranging demo
    device.send_cmds()

    # receive ranging demo message within ranging_time * 0.1s
    for i in range(0, ranging_time + 1):
        device.receive(log_file=log_file)
        sys.stdout.flush()
        print(f"Ranging progress: {float(i * 100 / ranging_time):.2f}%", end='\r')
        time.sleep(0.1)
    print('Ranging completed.')

    # close TCP connection for current device
    device.close_tcp_conn()

    # close log file
    if log_file is not None:
        log_file.close()

# END OF FILE
#---------------------------------------------------------------------------------