import threading
import time
import queue
import random

# APEX API 配置读取模块
class ApexConfigReader:
    def __init__(self):
        self.immediate_tasks = queue.Queue()
        self.scheduled_tasks = queue.Queue()

    def read_immediate_tasks(self):
        # 模拟读取即时任务
        print("Reading immediate tasks from APEX API")
        self.immediate_tasks.put(("ImmediateTask", time.time()))

    def read_scheduled_tasks(self):
        # 模拟读取定时任务
        print("Reading scheduled tasks from APEX API")
        self.scheduled_tasks.put(("ScheduledTask", time.time() + 10))  # 10秒后执行

# API 客户端
class ApiClient:
    def __init__(self):
        self.retry_delay = 1

    def call_api(self, api_name):
        try:
            # 模拟API调用
            if random.random() < 0.3:  # 30%概率发生异常
                raise Exception("API call failed")
            print(f"Calling {api_name} API")
            self.retry_delay = 1
        except Exception as e:
            print(f"Error calling {api_name} API: {str(e)}")
            time.sleep(self.retry_delay)
            self.retry_delay = min(self.retry_delay * 2, 5)
            return False
        return True

# Jira 操作模块
class JiraOperator:
    def __init__(self, api_client):
        self.api_client = api_client

    def create_issue(self):
        return self.api_client.call_api("Jira Create Issue")

    def update_issue(self):
        return self.api_client.call_api("Jira Update Issue")

# Confluence 操作模块
class ConfluenceOperator:
    def __init__(self, api_client):
        self.api_client = api_client

    def update_page(self):
        return self.api_client.call_api("Confluence Update Page")

# Mattermost 操作模块
class MattermostOperator:
    def __init__(self, api_client):
        self.api_client = api_client

    def send_notification(self):
        return self.api_client.call_api("Mattermost Send Notification")

# 任务执行器
class TaskExecutor:
    def __init__(self, jira_op, confluence_op, mattermost_op):
        self.jira_op = jira_op
        self.confluence_op = confluence_op
        self.mattermost_op = mattermost_op

    def execute_task(self, task):
        print(f"Executing task: {task[0]}")
        self.jira_op.create_issue()
        self.jira_op.update_issue()
        self.confluence_op.update_page()
        self.mattermost_op.send_notification()
        print(f"Task {task[0]} completed")

# 主程序
class MainProgram:
    def __init__(self):
        self.api_client = ApiClient()
        self.jira_op = JiraOperator(self.api_client)
        self.confluence_op = ConfluenceOperator(self.api_client)
        self.mattermost_op = MattermostOperator(self.api_client)
        self.task_executor = TaskExecutor(self.jira_op, self.confluence_op, self.mattermost_op)
        self.config_reader = ApexConfigReader()
        self.running = True

    def read_config(self):
        while self.running:
            self.config_reader.read_immediate_tasks()
            self.config_reader.read_scheduled_tasks()
            time.sleep(3)

    def execute_tasks(self):
        while self.running:
            # 检查并执行即时任务
            while not self.config_reader.immediate_tasks.empty():
                task = self.config_reader.immediate_tasks.get()
                threading.Thread(target=self.task_executor.execute_task, args=(task,)).start()

            # 检查并执行定时任务
            while not self.config_reader.scheduled_tasks.empty():
                task = self.config_reader.scheduled_tasks.get()
                if task[1] <= time.time():
                    threading.Thread(target=self.task_executor.execute_task, args=(task,)).start()
                else:
                    self.config_reader.scheduled_tasks.put(task)
                    break

            time.sleep(1)

    def run(self):
        config_thread = threading.Thread(target=self.read_config)
        execute_thread = threading.Thread(target=self.execute_tasks)

        config_thread.start()
        execute_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping program...")
            self.running = False

        config_thread.join()
        execute_thread.join()

if __name__ == "__main__":
    program = MainProgram()
    program.run()
