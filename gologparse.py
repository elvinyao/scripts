import json
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil import parser

def parse_log_line(line):
    try:
        log_data = json.loads(line)
        if "msg" in log_data and "execution_time" in log_data:
            msg = log_data["msg"]
            execution_time = parser.isoparse(log_data["execution_time"])
            return msg, execution_time
    except (json.JSONDecodeError, KeyError, ValueError):
        pass
    return None, None

def calculate_time_diff(logs):
    time_diffs = []
    for i in range(0, len(logs), 2):
        if i + 1 < len(logs):
            time_diff = (logs[i+1][1] - logs[i][1]).total_seconds()
            time_diffs.append((f"{logs[i][0]}-{logs[i+1][0]}", time_diff))
    return time_diffs

def plot_time_diffs(time_diffs):
    if not time_diffs:
        print("No valid time differences to plot.")
        return
    
    labels, diffs = zip(*time_diffs)
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(labels)), diffs, marker='o')
    plt.title('Time Differences Between Paired Messages')
    plt.xlabel('Message Pairs')
    plt.ylabel('Time Difference (seconds)')
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def main(log_file_path):
    logs = []
    with open(log_file_path, 'r') as file:
        for line in file:
            msg, execution_time = parse_log_line(line)
            if msg and execution_time:
                logs.append((msg, execution_time))
    
    if not logs:
        print("No valid log entries found.")
        return

    time_diffs = calculate_time_diff(logs)
    plot_time_diffs(time_diffs)

if __name__ == "__main__":
    log_file_path = "path/to/your/golang/log/file.log"  # 替换为实际的日志文件路径
    main(log_file_path)
