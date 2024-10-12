# -*- coding:utf-8 -*-
# !/usr/bin/env python
#---------------------------------------------------------------------------------
# Author: Zhang
#
# Create Date: 2024/10/09
# Last Update on: 2024/10/11
#
# FILE: component.py
# Description: Basic classes are defined here
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# IMPORT REQUIRED PACKAGES HERE

import os
import math
import re

import numpy as np
import pandas as pd

# END OF PACKAGE IMPORT
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# DEFINE CLASS HERE


class LogManager:
    """
    A class designed to read, extract, and analyze distance measurement results from a log file.
    """
    
    def __init__(self, log_file_path: str, real_distance: float):
        """
        Initialize LogManager with log file path and real distance.
        
        Parameters:
        -----------
        log_file_path : str
            The path to the log file that contains distance measurements.
        real_distance : float
            The actual real distance that the measurements are expected to approximate.
        """
        self.log_file_path = log_file_path
        self.real_distance = real_distance
        self.distance_results = []  # Store parsed distance results

    def _extract_data(self, warm_up_samples: int, analysis_samples: int) -> None:
        """
        Extract range data from the log file and save it in the distance_results attribute.
        
        Parameters:
        -----------
        warm_up_samples : int
            Number of samples to skip as warm-up.
        analysis_samples : int
            Number of samples to include for analysis.
        """
        if not os.path.isfile(self.log_file_path):
            raise FileNotFoundError(f"The log file {self.log_file_path} does not exist.")

        file_ext = os.path.splitext(self.log_file_path)[1]
        
        # Open the file and process based on file extension
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                if file_ext == '.log':
                    self._parse_log_file(file, warm_up_samples, analysis_samples)
                else:
                    raise ValueError("Unsupported file type. Only .log file is supported.")
        except Exception as e:
            # Raise exception after logging for better debugging
            raise RuntimeError(f"Error reading file: {e}") from e

    def _parse_log_file(self, file, warm_up_samples: int, analysis_samples: int, log_type: str = 'tera') -> None:
        """
        Parse the log file and extract distance results.
        
        Parameters:
        -----------
        file : file object
            The opened log file object.
        warm_up_samples : int
            Number of samples to skip as warm-up.
        analysis_samples : int
            Number of samples to analyze after warm-up.
        log_type : str
            The type of log file ('gui' or 'tera').
        """
        # Select appropriate regex pattern based on log type
        if log_type == 'tera':
            pattern = re.compile(r'>> RAD RESULT:( Time Out|([\d.]+)m)')  # Mobis tera term log pattern
        elif log_type == 'gui':
            pattern = re.compile(r"Distance\s*:\s*(\d+)")  # GUI log pattern
        else:
            raise ValueError("Unsupported log type provided.")

        content = file.read()
        matches = pattern.findall(content)

        # Extract valid distance results based on log type
        extracted_distances = []
        if log_type == 'tera':
            extracted_distances = [
                float('NaN') if match[0] == ' Time Out' else float(match[1])
                for match in matches
            ]
        elif log_type == 'gui':
            extracted_distances = [float(match) for match in matches]

        # Handle case where insufficient data is available
        if len(extracted_distances) < (warm_up_samples + analysis_samples):
            print('Not enough log data for the specified warm-up and analysis length.')
            print('Extracting all available log data.')
            self.distance_results = extracted_distances
        else:
            self.distance_results = extracted_distances[warm_up_samples:(warm_up_samples + analysis_samples)]

    def analysis(self, warm_up_samples: int = 10, analysis_samples: int = 250) -> dict:
        """
        Perform analysis on the extracted data.
        
        Parameters:
        -----------
        warm_up_samples : int, optional
            Number of initial samples to skip (default is 10).
        analysis_samples : int, optional
            Number of samples to include in the analysis (default is 250).
        
        Returns:
        --------
        dict
            A dictionary containing analysis results.
        """
        self._extract_data(warm_up_samples=warm_up_samples, analysis_samples=analysis_samples)

        if not self.distance_results:
            raise ValueError("No data available for analysis.")
        
        valid_distances = [d for d in self.distance_results if not math.isnan(d)]
        total_measurements = len(self.distance_results)

        if valid_distances:
            avg_distance = np.mean(valid_distances)
            standard_error = np.std(valid_distances, ddof=0)  # Population standard deviation
        else:
            avg_distance, standard_error = float('NaN'), float('NaN')

        offset = avg_distance - self.real_distance if not math.isnan(avg_distance) else float('NaN')
        success_count = len(valid_distances)
        timeout_count = total_measurements - success_count
        success_rate = success_count / total_measurements if total_measurements > 0 else 0.0

        # Return the analysis results in a structured dictionary
        return {
            "N (total measurements)": total_measurements,
            "Ave. distance": avg_distance,
            "Std. error": standard_error,
            "Offset": offset,
            "Ranging successful count": success_count,
            "Time out count": timeout_count,
            "RSR (ranging success ratio)": success_rate
        }

    @staticmethod
    def print_result(result: dict) -> None:
        """
        Print the analysis results with two columns, left-aligned.
        
        Parameters:
        -----------
        result : dict
            The dictionary containing analysis results.
        """
        print(f"{' Metric':<35}{' Value':<10}")
        print("-" * 46)
        
        # Iterate and print result metrics
        for metric, value in result.items():
            if isinstance(value, float):
                print(f" {metric:<35}{value:<10.2f}")
            else:
                print(f" {metric:<35}{value:<10}")

    def save_results(self, file_name: str) -> None:
        """
        Save the distance results and analysis data into an Excel file.
        
        Parameters:
        -----------
        file_name : str
            The name of the Excel file to save the results into. Should end with ".xlsx".
        """
        if not self.distance_results:
            raise ValueError("No data available to save. Please run extract_data() first.")
        
        # Ensure analysis is performed before saving
        analysis_results = self.analysis()

        measurement_index = list(range(1, len(self.distance_results) + 1))
        distance_results = self.distance_results
        
        metrics = list(analysis_results.keys())
        values = list(analysis_results.values())

        max_length = max(len(measurement_index), len(metrics))
        
        # Pad lists to ensure equal length for DataFrame
        measurement_index += [''] * (max_length - len(measurement_index))
        distance_results += [''] * (max_length - len(distance_results))
        metrics += [''] * (max_length - len(metrics))
        values += [''] * (max_length - len(values))

        # Create DataFrame for saving results
        df = pd.DataFrame({
            "Index": measurement_index,
            "Ranging Results": distance_results,
            "Metric": metrics,
            "Value": values
        })

        df.to_excel(file_name, sheet_name='Results', index=False)
        print(f"Results successfully saved to {file_name}")
