# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/11/03
#
# FILE: device.py
# Description: Classe Device is defined here
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import os
import sys
import time
import socket
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils.functions as funcs

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE CLASS HERE

class Device(object):
    """ UWB device, (Debby, Fina, etc,.)"""
    def __init__(self, role, cmds_dict, com_port, tcp_port=r'20020') -> None:
        self.role = role             # initiator or responder
        self.tx_power = 5            # transmission power, default to 5

        self._cmds_dict = cmds_dict  # all commands used to start ranging demo
        
        self._com_port = com_port    # USB serial port
        self._tcp_port = tcp_port    # TCP port
        self.tcp_connection = None   # TCP connection

    def __setattr__(self, name, value) -> None:
        if name == 'tx_power':
            if not (1 <= value <= 9):
                print(f"{name} is out-of-range. Assignment ignored.")
                return
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return f"Device(role={self.role}, com_port={self._com_port}, tcp_port={self._tcp_port},)"
    
    def establish_tcp_conn(self, cliserver_path=r'Cliserver.exe', host=r'127.0.0.1'):
        try:
            subprocess.Popen(
                [cliserver_path, host, self._tcp_port, self._com_port],
                shell=True, stdout=subprocess.PIPE
            )
            self.tcp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_connection.connect((host, int(self._tcp_port)))
        except Exception as e:
            print('Failed to establish TCP connection: {e}')
            sys.exit("Exiting...")

    def receive(self, log_file=None, buff_size=2048, visual=False):
        if self.tcp_connection is None:
            print('TCP connection is not established.')
            return
        resp = self.tcp_connection.recv(buff_size).decode()
        if log_file is not None:
            log_file.write(f"{resp}")
        if visual:
            print(f"{resp}")

    def send_cmds(self):
        if self.tcp_connection is None:
            print('TCP connection is not established.')
            return
        
        for key in self._cmds_dict.keys():
            if key == 'setpower':
                command = f"{self._cmds_dict[key]}{self.tx_power}"
            else:
                command = self._cmds_dict[key]
            self.tcp_connection.send(command.encode())
            self.receive()

# END OF CLASS DEFINATION
#---------------------------------------------------------------------------------

if __name__ == '__main__':
    # where 'Cliserver.exe' is
    cliserver_path = r'C:\Users\a5149517\Desktop\Automation_tools\Cliserver.exe'

    # where 'command.json' file is
    cmd_path = r'C:\Users\a5149517\Desktop\Automation_tools\command.json'

    # log file
    log_file = open(r'C:\Users\a5149517\Desktop\Automation_tools\logs\test_log.log', 'w')
    # for initiator, there is no need to record log, so set the log_file to None
    # log_file = None

    # example usage to instance a UWB device as responder
    role = r'responder'  # role of current device
    com_port = 'com7'    # COM port of current device
    ranging_time = 600   # ranging time with unit 0.1s

    # example usage to instance a UWB device as initiator
    # role = r'initiator'

    cmds = funcs.load_commands(cmd_path, role)
    device = Device(role, cmds, com_port)

    # example usage to set tx power
    device.tx_power = 5

    # example usage to start tcp connection
    device.establish_tcp_conn(cliserver_path=cliserver_path)

    # example usage to start ranging demo 
    device.send_cmds()

    # receive ranging demo message within ranging_time * 0.1s
    for _ in range(0, ranging_time + 1):
        device.receive(log_file=log_file)
        time.sleep(0.1)
    
    device.tcp_connection.close()

    if log_file is not None:
        log_file.close()

# END OF FILE
#---------------------------------------------------------------------------------