import requests
import json
from datetime import datetime

# JIRA API配置
jira_url = "https://your-jira-instance.com"
api_endpoint = "/rest/api/2/issue/ISSUE-123"  # 替换为您的issue key
auth = ("your_username", "your_api_token")  # 使用API令牌或密码

# 准备要更新的字段数据
update_data = {
    "fields": {
        # 文本字段 (String)
        "customfield_10001": "这是一个文本字段的新值",
        
        # 数字字段 (Number)
        "customfield_10002": 42.5,
        
        # 日期时间字段 (DateTime) - 使用ISO 8601格式
        "customfield_10003": "2025-04-23T14:30:00.000+0000",
        
        # 标签字段 (Labels) - 使用数组
        "labels": ["标签1", "标签2", "新标签"],
        
        # 选择列表字段 (Select/Option)
        "customfield_10004": {"value": "选项1"},
        
        # 多选列表字段 (Multi-select)
        "customfield_10005": [
            {"value": "选项A"},
            {"value": "选项B"}
        ],
        
        # 用户选择器字段 (User Picker)
        "customfield_10006": {"name": "username"},
        
        # 多用户选择器 (Multi-User Picker)
        "customfield_10007": [
            {"name": "user1"},
            {"name": "user2"}
        ],
        
        # 级联选择字段 (Cascading Select)
        "customfield_10008": {
            "value": "父选项",
            "child": {"value": "子选项"}
        },
        
        # 复选框字段 (Checkbox)
        "customfield_10009": [{"value": "选中的值"}],
        
        # 单选按钮字段 (Radio Buttons)
        "customfield_10010": {"value": "所选选项"},
        
        # URL字段
        "customfield_10011": "https://example.com",
        
        # 文本区域字段 (TextArea)
        "customfield_10012": "这是\n多行\n文本内容"
    }
}

# 发送PUT请求更新问题
headers = {
    "Content-Type": "application/json"
}

response = requests.put(
    jira_url + api_endpoint,
    auth=auth,
    headers=headers,
    data=json.dumps(update_data)
)

# 检查响应
if response.status_code == 204:  # JIRA API成功更新返回204状态码
    print("问题已成功更新!")
else:
    print(f"更新失败: {response.status_code}")
    print(response.text)
