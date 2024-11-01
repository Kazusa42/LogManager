import os
import sys
import time
import socket
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.functions as funcs


class Device:
    """ UWB device, (Debby, Fina etc.)"""
    def __init__(self, role: str, com_port: str, cmds: dict, tcp_port=r'20020', tx_power=5) -> None:
        self.role = role
        self.info = {
            'com_port': com_port,
            'tcp_port': tcp_port,
            'ip_addr': r'127.0.0.1'
        }
        self.cmd = cmds
        self.tx_power = tx_power

        self.tcp_conn = None

    def set_tx_power(self, power: int):
        self.tx_power = power

    def start_tcp_conn(self, cliserver_path=r'Cliserver.exe'):
        try:
            subprocess.Popen(
                [cliserver_path, self.info['ip_addr'], self.info['tcp_port'], self.info['com_port']],
                shell=True, stdout=subprocess.PIPE
            )
            self.tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_conn.connect((self.info['ip_addr'], int(self.info['tcp_port'])))
            print('TCP connection established successfully.')
        except Exception as e:
            print(f'Fialed to establish connection: {e}')
            sys.exit(1)

    def close_tcp_conn(self):
        if self.tcp_conn is not None:
            self.tcp_conn.close()
    
    # must be used after tcp connection is established
    def send_cmd(self, cmd):
        if self.tcp_conn is None:
            print('TCP connection is not established yet.')
            return
        
        if cmd == 'setpower':
            full_cmd = f"{self.cmd[cmd]}{self.tx_power}"
        else: full_cmd = self.cmd[cmd]
        
        self.tcp_conn.send(full_cmd.encode())
        # time.sleep(0.5)
        self.recv()

    def recv(self, log_file=None, buffsize=2048):
        resp = self.tcp_conn.recv(buffsize).decode()
        if log_file is None:
            print(f"{resp}")
        else:
            log_file.write(f"{resp}")


if __name__ == '__main__':
    # where 'Cliserver.exe' is
    cliserver_path = r'C:\Users\a5149517\Desktop\Automation_tools\Cliserver.exe'

    # where 'command.json' file is
    cmd_path = r'C:\Users\a5149517\Desktop\Automation_tools\command.json'

    # log file dir
    log_file = open(r'C:\Users\a5149517\Desktop\Automation_tools\logs\test_log.log', 'w')
    # for initiator, there is no need to record log, so set the log_file to None
    # log_file = None

    # example usage to instance a UWB device as responder
    role = r'responder'  # role of current device
    tx_power = 4         # transmission power of current device
    com_port = 'com7'    # COM port of current device
    ranging_time = 600   # ranging time

    # example usage to instance a UWB device as initiator
    # role = r'initiator'
    # cmds = funcs.load_commands(cmd_path, role)
    cmds = funcs.load_commands(cmd_path, role)
    device = Device(role=role, com_port=com_port, cmds=cmds)

    # example usage to set tx power
    device.set_tx_power(tx_power)

    # example usage to start tcp connection
    device.start_tcp_conn(cliserver_path=cliserver_path)

    device.send_cmd('reset')     # example usage to reset device
    device.send_cmd('boot')      # example usage to boot device
    device.send_cmd('setpower')  # example usage of set tx power of current device
    device.send_cmd('start')     # example usage to start ranging demo

    for _ in range(0, ranging_time):  # receive ranging results in about 1 min
        device.recv(log_file=log_file)
        time.sleep(0.1)
    
    device.send_cmd('reset')

    if log_file is not None:
        log_file.close()