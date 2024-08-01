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
