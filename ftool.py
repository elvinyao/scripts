import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

def parse_log_line(line):
    try:
        log_entry = json.loads(line)
        if log_entry.get('level') == 'info':
            timestamp = datetime.fromisoformat(log_entry['time'].replace('Z', '+00:00'))
            return timestamp.replace(tzinfo=None)  # 移除时区信息以简化处理
    except json.JSONDecodeError:
        pass
    except KeyError:
        pass
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
    plt.title('Frequency of INFO Level Log Entries (Per Minute)')
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
log_file_path = 'path_to_your_json_log_file.log'  # 替换为实际的JSON日志文件路径
timestamps = process_log_file(log_file_path)
plot_log_activity(timestamps)
