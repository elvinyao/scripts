import re
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

def parse_log_line(line):
    # 使用正则表达式匹配日期时间格式和特定消息
    pattern = r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) ===\[focalboard\] boardId is not target\. block\.boardid=\d+'
    match = re.match(pattern, line)
    if match:
        # 如果匹配成功，将字符串转换为datetime对象
        return datetime.strptime(match.group(1), '%Y/%m/%d %H:%M:%S')
    return None

def process_log_file(file_path):
    timestamps = []
    with open(file_path, 'r') as file:
        for line in file:
            timestamp = parse_log_line(line)
            if timestamp:
                timestamps.append(timestamp)
    return timestamps

def plot_log_activity(timestamps):
    # 按小时统计日志条目
    hourly_counts = defaultdict(int)
    for timestamp in timestamps:
        hourly_counts[timestamp.replace(minute=0, second=0)] += 1

    # 准备绘图数据
    hours = sorted(hourly_counts.keys())
    counts = [hourly_counts[hour] for hour in hours]

    # 创建图表
    plt.figure(figsize=(12, 6))
    plt.plot(hours, counts, marker='o')
    plt.title('Frequency of "boardId is not target" Messages Over Time')
    plt.xlabel('Time')
    plt.ylabel('Number of Occurrences')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.show()

# 主程序
log_file_path = 'path_to_your_log_file.log'  # 替换为实际的日志文件路径
timestamps = process_log_file(log_file_path)
plot_log_activity(timestamps)




import re
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.dates as mdates

def parse_log_line(line):
    pattern = r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) ===\[focalboard\] boardId is not target\. block\.boardid=\d+'
    match = re.match(pattern, line)
    if match:
        return datetime.strptime(match.group(1), '%Y/%m/%d %H:%M:%S')
    return None

def round_to_minute(dt):
    return dt.replace(second=0, microsecond=0)

def process_log_file(file_path):
    timestamps = []
    with open(file_path, 'r') as file:
        for line in file:
            timestamp = parse_log_line(line)
            if timestamp:
                timestamps.append(round_to_minute(timestamp))
    return timestamps

def plot_log_activity(timestamps):
    # 按分钟统计日志条目
    minute_counts = defaultdict(int)
    for timestamp in timestamps:
        minute_counts[timestamp] += 1

    # 准备绘图数据
    time_intervals = sorted(minute_counts.keys())
    counts = [minute_counts[interval] for interval in time_intervals]

    # 创建图表
    plt.figure(figsize=(20, 8))
    plt.plot(time_intervals, counts, marker='.', linestyle='-', markersize=3)
    plt.title('Frequency of "boardId is not target" Messages (Per Minute)')
    plt.xlabel('Time')
    plt.ylabel('Number of Occurrences')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 设置x轴
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(0, 60, 15)))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # 如果数据跨越多天，添加顶部的日期标签
    if (time_intervals[-1].date() - time_intervals[0].date()).days > 0:
        ax2 = plt.gca().twiny()
        ax2.set_xlim(plt.gca().get_xlim())
        ax2.set_xticks(mdates.date2num([time_intervals[0].date(), time_intervals[-1].date()]))
        ax2.set_xticklabels([time_intervals[0].strftime('%Y-%m-%d'), time_intervals[-1].strftime('%Y-%m-%d')])
        ax2.tick_params(axis='x', which='major', pad=15)

    plt.show()

# 主程序
log_file_path = 'path_to_your_log_file.log'  # 替换为实际的日志文件路径
timestamps = process_log_file(log_file_path)
plot_log_activity(timestamps)


import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

def parse_log_line(line):
    pattern = r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) ===\[focalboard\] boardId is not target\. block\.boardid=\d+'
    match = re.match(pattern, line)
    if match:
        return datetime.strptime(match.group(1), '%Y/%m/%d %H:%M:%S')
    return None

def round_to_minute(dt):
    return dt.replace(second=0, microsecond=0)

def process_log_file(file_path):
    timestamps = []
    with open(file_path, 'r') as file:
        for line in file:
            timestamp = parse_log_line(line)
            if timestamp:
                timestamps.append(round_to_minute(timestamp))
    return timestamps

def plot_log_activity(timestamps):
    # 按分钟统计日志条目
    minute_counts = defaultdict(int)
    for timestamp in timestamps:
        minute_counts[timestamp] += 1

    # 准备绘图数据
    time_intervals = sorted(minute_counts.keys())
    counts = [minute_counts[interval] for interval in time_intervals]

    # 创建图表
    plt.figure(figsize=(20, 8))
    plt.bar(time_intervals, counts, width=0.001, align='center', color='skyblue', edgecolor='navy')
    plt.title('Frequency of "boardId is not target" Messages (Per Minute)')
    plt.xlabel('Time')
    plt.ylabel('Number of Occurrences')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, axis='y')

    # 设置x轴
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(0, 60, 15)))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # 如果数据跨越多天，添加顶部的日期标签
    if (time_intervals[-1].date() - time_intervals[0].date()).days > 0:
        ax2 = plt.gca().twiny()
        ax2.set_xlim(plt.gca().get_xlim())
        ax2.set_xticks(mdates.date2num([time_intervals[0].date(), time_intervals[-1].date()]))
        ax2.set_xticklabels([time_intervals[0].strftime('%Y-%m-%d'), time_intervals[-1].strftime('%Y-%m-%d')])
        ax2.tick_params(axis='x', which='major', pad=15)

    plt.show()

# 主程序
log_file_path = 'path_to_your_log_file.log'  # 替换为实际的日志文件路径
timestamps = process_log_file(log_file_path)
plot_log_activity(timestamps)
