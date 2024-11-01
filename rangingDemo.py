import os
import sys
import json
import socket
import argparse

import utils.component as comps
import utils.functions as funcs


def main():
    comps.Const.COMMAND_FILE = os.path.join(os.path.dirname(__file__), 'command.json')
    comps.Const.CLISERVER = os.path.join(os.path.dirname(__file__), 'Cliserver.exe')
    comps.Const.LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

    parser = argparse.ArgumentParser(description='Ranging demo')
    args_dict = funcs.rangingDemo_arg_parser(parser=parser)

    funcs.welcome_menu_for_rangingdemo()

    device = funcs.init_device(
        args_dict=args_dict,
        cmd_file_path=comps.Const.COMMAND_FILE,
        tcp_port=args_dict['-tp']
    )
    print('Device initialized successfully.')

    while True:
        user_input = input("Waiting for command: ").lower().strip()
        if user_input == 'exit':
            sys.exit("Exiting...")
        elif user_input.startswith('set power'):
            power = int(user_input.split('=')[1])
            if 1 <= power <= 9:
                device.set_tx_power(power)
            else:
                print('Invalid power. Please input power between 1-9.')
        elif user_input.startswith('run'):
            log_file_name = funcs.name_log_file(device_role=device.role, distance=args_dict['-d'])
            if log_file_name:
                log_file = open(os.path.join(comps.Const.LOG_DIR, log_file_name), 'w')
            else: log_file =None

            funcs.run_ranging_demo(
                device=device,
                ranging_time=args_dict['-t'],
                cliserver_path=comps.Const.CLISERVER,
                log_file=log_file,
            )
        else:
            print('Unsupported command.')
            continue
    

if __name__ == "__main__":
    # Example execution
    main()
    # demo.init_device()
    # demo.run()