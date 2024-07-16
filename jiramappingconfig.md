如何使用python程序，做一个操作jira的API的工具。 因为要使用不同环境里的jira， jira的 issue type可能名称不同，而且 jira的field的名称可能不同，且非必需的jira field各个环境数量不一致，可能不会一一对应。怎么设计一个共用的field mapping逻辑，来适应不同环境的jira下，这个程序，都可以正常运行。 
为了创建一个操作Jira API的Python工具，并适应不同环境下的Jira配置（如issue type名称不同、field名称不同、非必需field不一致等），需要设计一个灵活的field mapping逻辑。以下是设计思路和实现方法：

### 设计思路

1. **配置文件**：使用配置文件（如JSON或YAML）来定义不同环境下的field mapping。这可以确保工具的灵活性和可扩展性。
2. **抽象化**：抽象出Jira API的操作，使其适应不同的field mapping。
3. **统一接口**：提供统一的接口，让用户可以使用相同的方法处理不同环境下的Jira。
4. **错误处理**：处理不同环境下的field缺失或不匹配的情况。

### 实现步骤

1. **配置文件**：定义不同环境的field mapping。
2. **Jira操作类**：封装Jira API操作，适应不同的field mapping。
3. **主程序**：加载配置文件并初始化Jira操作类，执行相应的操作。

### 1. 配置文件

使用JSON或YAML文件来定义不同环境的field mapping，例如：

```yaml
# config.yaml
environments:
  env1:
    base_url: "https://jira-env1.example.com"
    username: "user1"
    api_token: "token1"
    issue_type_mapping:
      task: "Task"
      bug: "Bug"
    field_mapping:
      summary: "Summary"
      description: "Description"
      custom_field_1: "Custom Field 1"
  env2:
    base_url: "https://jira-env2.example.com"
    username: "user2"
    api_token: "token2"
    issue_type_mapping:
      task: "Story"
      bug: "Defect"
    field_mapping:
      summary: "Summary"
      description: "Description"
      custom_field_1: "Custom Field A"
```

### 2. Jira操作类

封装Jira API操作，使其适应不同的field mapping。

```python
import requests
import yaml

class JiraClient:
    def __init__(self, base_url, username, api_token, issue_type_mapping, field_mapping):
        self.base_url = base_url
        self.username = username
        self.api_token = api_token
        self.issue_type_mapping = issue_type_mapping
        self.field_mapping = field_mapping

    def _make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}/rest/api/2/{endpoint}"
        auth = (self.username, self.api_token)
        headers = {'Content-Type': 'application/json'}
        response = requests.request(method, url, json=data, auth=auth, headers=headers)
        response.raise_for_status()
        return response.json()

    def create_issue(self, issue_type, fields):
        mapped_fields = {self.field_mapping.get(k, k): v for k, v in fields.items()}
        issue_data = {
            "fields": {
                "issuetype": {"name": self.issue_type_mapping[issue_type]},
                **mapped_fields
            }
        }
        return self._make_request("POST", "issue", data=issue_data)

    def get_issue(self, issue_key):
        return self._make_request("GET", f"issue/{issue_key}")

    def update_issue(self, issue_key, fields):
        mapped_fields = {self.field_mapping.get(k, k): v for k, v in fields.items()}
        issue_data = {"fields": mapped_fields}
        return self._make_request("PUT", f"issue/{issue_key}", data=issue_data)

# Load configuration
def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Initialize JiraClient
def get_jira_client(env_name):
    config = load_config()
    env_config = config['environments'][env_name]
    return JiraClient(
        base_url=env_config['base_url'],
        username=env_config['username'],
        api_token=env_config['api_token'],
        issue_type_mapping=env_config['issue_type_mapping'],
        field_mapping=env_config['field_mapping']
    )

# Example usage
if __name__ == "__main__":
    env_name = "env1"  # or "env2" depending on the environment you want to use
    jira_client = get_jira_client(env_name)
    
    # Create an issue
    issue_fields = {
        "summary": "Test issue",
        "description": "This is a test issue.",
        "custom_field_1": "Custom value"
    }
    issue = jira_client.create_issue(issue_type="task", fields=issue_fields)
    print("Created issue:", issue)

    # Get an issue
    issue_key = issue['key']
    fetched_issue = jira_client.get_issue(issue_key)
    print("Fetched issue:", fetched_issue)

    # Update an issue
    update_fields = {
        "summary": "Updated test issue",
        "description": "This is an updated test issue."
    }
    updated_issue = jira_client.update_issue(issue_key, fields=update_fields)
    print("Updated issue:", updated_issue)
```

### 3. 设计思路

1. **配置文件**：存储不同环境的Jira连接信息和field mapping。
2. **Jira操作类**：根据配置文件的内容动态映射field名称。
3. **主程序**：加载配置文件并初始化Jira操作类，提供统一的接口进行Jira操作。

### 总结

- **灵活性**：通过配置文件实现不同环境的field mapping，适应不同的Jira配置。
- **可扩展性**：通过简单地修改配置文件，可以轻松适应新的Jira环境。
- **统一接口**：提供统一的接口，简化Jira操作逻辑，提高代码可读性和可维护性。

这种设计使得工具能够适应不同的Jira环境，并且能够根据不同的field mapping动态调整，使操作更加灵活和方便。
如何修改这个程序，是程序在初始运行时，输出当前的config信息。

为了在程序初始运行时输出当前的配置信息，可以在加载配置文件后直接打印配置内容。我们可以在`get_jira_client`函数中添加打印配置的逻辑，这样在初始化`JiraClient`之前就会输出当前的配置信息。

### 修改后的代码

1. **加载配置文件后打印配置**：在`get_jira_client`函数中添加打印配置的逻辑。
2. **优化代码结构**：确保配置文件路径可以通过参数传递，增强灵活性。

### 代码实现

#### 配置文件（`config.yaml`）

```yaml
# config.yaml
environments:
  env1:
    base_url: "https://jira-env1.example.com"
    username: "user1"
    api_token: "token1"
    issue_type_mapping:
      task: "Task"
      bug: "Bug"
    field_mapping:
      summary: "Summary"
      description: "Description"
      custom_field_1: "Custom Field 1"
  env2:
    base_url: "https://jira-env2.example.com"
    username: "user2"
    api_token: "token2"
    issue_type_mapping:
      task: "Story"
      bug: "Defect"
    field_mapping:
      summary: "Summary"
      description: "Description"
      custom_field_1: "Custom Field A"
```

#### `config_loader.py`

保持不变，负责从文件加载配置：
```python
import yaml

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
```

#### `sender.py`

在加载配置文件后打印配置信息：
```python
import requests
import yaml

class JiraClient:
    def __init__(self, base_url, username, api_token, issue_type_mapping, field_mapping):
        self.base_url = base_url
        self.username = username
        self.api_token = api_token
        self.issue_type_mapping = issue_type_mapping
        self.field_mapping = field_mapping

    def _make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}/rest/api/2/{endpoint}"
        auth = (self.username, self.api_token)
        headers = {'Content-Type': 'application/json'}
        response = requests.request(method, url, json=data, auth=auth, headers=headers)
        response.raise_for_status()
        return response.json()

    def create_issue(self, issue_type, fields):
        mapped_fields = {self.field_mapping.get(k, k): v for k, v in fields.items()}
        issue_data = {
            "fields": {
                "issuetype": {"name": self.issue_type_mapping[issue_type]},
                **mapped_fields
            }
        }
        return self._make_request("POST", "issue", data=issue_data)

    def get_issue(self, issue_key):
        return self._make_request("GET", f"issue/{issue_key}")

    def update_issue(self, issue_key, fields):
        mapped_fields = {self.field_mapping.get(k, k): v for k, v in fields.items()}
        issue_data = {"fields": mapped_fields}
        return self._make_request("PUT", f"issue/{issue_key}", data=issue_data)

# Load configuration
def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Initialize JiraClient
def get_jira_client(env_name, config_path='config.yaml'):
    config = load_config(config_path)
    env_config = config['environments'][env_name]
    
    # Print current configuration
    print("Current configuration:")
    print(f"Environment: {env_name}")
    print(f"Base URL: {env_config['base_url']}")
    print(f"Username: {env_config['username']}")
    print(f"Issue Type Mapping: {env_config['issue_type_mapping']}")
    print(f"Field Mapping: {env_config['field_mapping']}")

    return JiraClient(
        base_url=env_config['base_url'],
        username=env_config['username'],
        api_token=env_config['api_token'],
        issue_type_mapping=env_config['issue_type_mapping'],
        field_mapping=env_config['field_mapping']
    )

# Example usage
if __name__ == "__main__":
    env_name = "env1"  # or "env2" depending on the environment you want to use
    config_path = 'path/to/config.yaml'
    
    jira_client = get_jira_client(env_name, config_path)
    
    # Create an issue
    issue_fields = {
        "summary": "Test issue",
        "description": "This is a test issue.",
        "custom_field_1": "Custom value"
    }
    issue = jira_client.create_issue(issue_type="task", fields=issue_fields)
    print("Created issue:", issue)

    # Get an issue
    issue_key = issue['key']
    fetched_issue = jira_client.get_issue(issue_key)
    print("Fetched issue:", fetched_issue)

    # Update an issue
    update_fields = {
        "summary": "Updated test issue",
        "description": "This is an updated test issue."
    }
    updated_issue = jira_client.update_issue(issue_key, fields=update_fields)
    print("Updated issue:", updated_issue)
```

### 总结

- **自动加载和打印配置**：在初始化JiraClient时自动加载并打印配置文件的内容。
- **增强灵活性**：通过传递配置文件路径和环境名称，灵活初始化JiraClient实例。
- **保持原有功能**：保留原有的Jira API操作逻辑，确保功能完整。

这样设计的程序在初始运行时能够输出当前的配置信息，方便用户了解当前环境的配置内容。
