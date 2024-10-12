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

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE FUNCTIONS HERE

def generate_result_file_path(log_file_path: str, curr_path: str, ext=r'.xlsx') -> str:
    name, _ = os.path.splitext(os.path.basename(log_file_path))
    result_file_name = name + r'_analysis_results' + ext
    save_dir = os.path.join(curr_path, 'analysis_results')
    return os.path.join(save_dir, result_file_name)