def show_result(analysis_result: dict):
        print(f"{' Metric':<30}{' Value':<10}")
        print('-' * 41)

        for key, value in analysis_result.items():
            print(f" {key:<30}{value:<10}")


analysis_result = {
    'min distance': 10,
    'max distance': 20,
    'average distance': round(11.35556, 2),
    'median distance': 15,
    'std. error': round(0.1543761, 2),
    'offset (real - ave.)': -2.1,
    'success count': 97,
    'fail count': 3,
    'success rate': round(0.97, 2)
}

# show_result(analysis_result)
import os

def chose_log_file(directory: str) -> str:
    # list all log files under 'directory' directory
    # and let user chose on of them
    # return the choosed file name
    log_files = [f for f in os.listdir(directory) if f.endswith('.log')]
    if not log_files:
        print('No log files found in the "log" folder.')
        return None
    print('Please choose a log file from the list blow:')
    print(f"{' Index':<7} {' File name':<20}")
    print('-' * 20)
    for idx, log_file in enumerate(log_files):
        print(f" {(idx + 1):<7} {log_file:<20}")

chose_log_file(r'C:\Users\lyin0\Desktop\LogManager\logs')

