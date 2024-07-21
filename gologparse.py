import json
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil import parser

def parse_log_file(log_file_path):
    logs = []
    # 尝试多种可能的编码
    encodings = ['utf-8', 'cp932', 'shift_jis', 'euc-jp', 'iso2022_jp']
    
    for encoding in encodings:
        try:
            with open(log_file_path, 'r', encoding=encoding) as file:
                for line in file:
                    try:
                        log_data = json.loads(line)
                        if "msg" in log_data and "execution_time" in log_data:
                            msg = log_data["msg"]
                            execution_time = parser.isoparse(log_data["execution_time"])
                            logs.append((msg, execution_time))
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            # 如果成功读取文件，跳出循环
            print(f"File successfully read with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            # 如果当前编码失败，尝试下一个
            continue
    else:
        # 如果所有编码都失败
        raise ValueError("Unable to decode the file with any of the attempted encodings.")

    return logs
def calculate_time_diffs_between_done(logs):
    time_diffs = []
    last_done_time = None
    for msg, time in logs:
        if msg == "got data,done":
            if last_done_time is not None:
                time_diff = (time - last_done_time).total_seconds()
                time_diffs.append((time, time_diff))
            last_done_time = time
    return time_diffs
def calculate_time_diffs(logs):
    time_diffs = []
    start_time = None
    for msg, time in logs:
        if msg == "go to ticker.C":
            start_time = time
        elif msg == "got data,done" and start_time is not None:
            time_diff = (time - start_time).total_seconds()
            time_diffs.append((start_time, time_diff))
            start_time = None
    return time_diffs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_time_diffs_between_done(time_diffs, output_file):
    if not time_diffs:
        print("No valid time differences to plot.")
        return
    
    done_times, diffs = zip(*time_diffs)
    
    # 将datetime对象转换为matplotlib可以使用的数值形式
    dates = mdates.date2num(done_times)
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, diffs, marker='o')
    
    plt.title('Time Differences Between Consecutive "got data,done" Messages')
    plt.xlabel('Time of "got data,done"')
    plt.ylabel('Time Difference to Previous "got data,done" (seconds)')
    
    # 设置x轴为日期时间格式
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    
    plt.gcf().autofmt_xdate()  # 自动格式化x轴日期标签
    plt.tight_layout()
    plt.grid(True)
    
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

    # 可选：显示图表
    # plt.show()
def plot_time_diffs(time_diffs, output_file):
    if not time_diffs:
        print("No valid time differences to plot.")
        return
    
    times, diffs = zip(*time_diffs)
    plt.figure(figsize=(12, 6))
    plt.plot(times, diffs, marker='o')
    plt.title('Time Differences Between "go to ticker.C" and "got data,done"')
    plt.xlabel('Time')
    plt.ylabel('Time Difference (seconds)')
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

def main(log_file_path, output_file):
    logs = parse_log_file(log_file_path)
    time_diffs = calculate_time_diffs(logs)
    plot_time_diffs(time_diffs, output_file)

if __name__ == "__main__":
    log_file_path = "path/to/your/golang/log/file.log"  # 替换为实际的日志文件路径
    output_file = "time_diff_plot.png"  # 输出的图表文件名
    main(log_file_path, output_file)

def main(log_file_path, output_file1, output_file2):
    logs = parse_log_file(log_file_path)
    
    # 原来的时间差计算和绘图
    time_diffs1 = calculate_time_diffs(logs)
    plot_time_diffs(time_diffs1, output_file1)
    
    # 新的时间差计算和绘图
    time_diffs2 = calculate_time_diffs_between_done(logs)
    plot_time_diffs_between_done(time_diffs2, output_file2)

if __name__ == "__main__":
    log_file_path = "path/to/your/golang/log/file.log"  # 替换为实际的日志文件路径
    output_file1 = "time_diff_plot1.png"  # 输出的第一个图表文件名
    output_file2 = "time_diff_plot2.png"  # 输出的第二个图表文件名
    main(log_file_path, output_file1, output_file2)
