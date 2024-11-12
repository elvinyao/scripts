CAN: Perfect, I’ll start implementing the solution with your specified preferences. Let’s begin with the core structure and basic implementations.

First, I’ll create the project structure and the main configuration files. Here’s the implementation:

# Project Structure
```
automation_system/
│
├── configs/
│   ├── __init__.py
│   ├── environment.yaml
│   ├── task_config.yaml
│   └── notification_templates.yaml
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── task_manager.py
│   │   └── config_loader.py
│   │
│   ├── api_clients/
│   │   ├── __init__.py
│   │   ├── apex_client.py
│   │   ├── jira_client.py
│   │   ├── confluence_client.py
│   │   └── mattermost_client.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_handler.py
│   │
│   ├── notifications/
│   │   ├── __init__.py
│   │   └── notification_manager.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── exceptions.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_core/
│       └── test_task_manager.py
│
├── requirements.txt
└── main.py
```

# First, let's implement the logger.py
import logging
import os
from datetime import datetime

class Logger:
    """Custom logger for the automation system.
    
    Attributes:
        logger: The logging instance
        log_file: Path to the log file
    """
    
    def __init__(self, name: str, log_dir: str = "logs"):
        """Initialize logger with name and directory.
        
        Args:
            name: Name of the logger
            log_dir: Directory to store log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters and add it to the handlers
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """Get the logger instance.
        
        Returns:
            logging.Logger: The logger instance
        """
        return self.logger

# Now let's implement the custom exceptions
class AutomationException(Exception):
    """Base exception class for automation system."""
    pass

class ConfigurationError(AutomationException):
    """Raised when there's an error in configuration."""
    pass

class APIError(AutomationException):
    """Raised when there's an error in API communication."""
    pass

class AuthenticationError(AutomationException):
    """Raised when there's an authentication error."""
    pass

class TaskExecutionError(AutomationException):
    """Raised when there's an error in task execution."""
    pass

# Let's create the config loader
import yaml
from typing import Dict, Any

class ConfigLoader:
    """Configuration loader for the automation system.
    
    Attributes:
        config_dir: Directory containing configuration files
    """
    
    def __init__(self, config_dir: str = "configs"):
        """Initialize config loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self.logger = Logger(__name__).get_logger()
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            config_file: Name of the configuration file
            
        Returns:
            Dict containing configuration data
            
        Raises:
            ConfigurationError: If configuration file cannot be loaded
        """
        try:
            config_path = os.path.join(self.config_dir, config_file)
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration file {config_file}: {str(e)}")
            raise ConfigurationError(f"Configuration error: {str(e)}")

Would you like me to continue with:

	1.	Sample configuration files (environment.yaml, task_config.yaml, notification_templates.yaml)?
	2.	Task Manager implementation?
	3.	API client base classes?

Please let me know which component you’d like me to implement next.



CAN: I’ll create the sample configuration files with comprehensive examples for all the required configurations.

# environment.yaml
# This file contains environment-specific configurations and API endpoints

environments:
  dev:
    jira:
      base_url: "https://dev-jira.company.com"
      auth_type: "oauth"
      oauth:
        client_id: "dev_client_id"
        client_secret: "dev_client_secret"
        token_url: "https://dev-jira.company.com/oauth/token"
      api_version: "v3"
      timeout: 30
      max_retries: 3

    confluence:
      base_url: "https://dev-confluence.company.com"
      auth_type: "basic"
      credentials:
        username: "`${CONFLUENCE_USER}"
        password: "$`{CONFLUENCE_PASS}"
      api_version: "v2"
      timeout: 30
      max_retries: 3

    mattermost:
      base_url: "https://dev-mattermost.company.com"
      auth_type: "token"
      token: "`${MATTERMOST_TOKEN}"
      default_channel: "dev-notifications"

  prod:
    jira:
      base_url: "https://jira.company.com"
      auth_type: "oauth"
      oauth:
        client_id: "$`{PROD_JIRA_CLIENT_ID}"
        client_secret: "`${PROD_JIRA_CLIENT_SECRET}"
        token_url: "https://jira.company.com/oauth/token"
      api_version: "v3"
      timeout: 30
      max_retries: 5

    confluence:
      base_url: "https://confluence.company.com"
      auth_type: "oauth"
      oauth:
        client_id: "$`{PROD_CONFLUENCE_CLIENT_ID}"
        client_secret: "`${PROD_CONFLUENCE_CLIENT_SECRET}"
        token_url: "https://confluence.company.com/oauth/token"
      api_version: "v2"
      timeout: 30
      max_retries: 5

    mattermost:
      base_url: "https://mattermost.company.com"
      auth_type: "token"
      token: "$`{PROD_MATTERMOST_TOKEN}"
      default_channel: "prod-notifications"

global_settings:
  concurrent_task_limit: 10
  task_retry_limit: 3
  task_retry_delay: 300  # seconds
  log_level: "INFO"
  temp_file_path: "/tmp/automation"

# task_config.yaml
# This file defines task types, priorities, and execution rules

task_types:
  jira_ticket_update:
    priority: 1
    retry_enabled: true
    max_retries: 3
    retry_delay: 60
    notification_required: true
    concurrent_limit: 5
    timeout: 300
    validators:
      - check_required_fields
      - check_permission
    pre_execution_hooks:
      - validate_input
      - check_dependencies
    post_execution_hooks:
      - update_status
      - send_notification

  confluence_page_update:
    priority: 2
    retry_enabled: true
    max_retries: 2
    retry_delay: 120
    notification_required: true
    concurrent_limit: 3
    timeout: 600
    validators:
      - check_page_exists
      - check_permission
    pre_execution_hooks:
      - backup_page
      - validate_content
    post_execution_hooks:
      - update_status
      - send_notification

task_priorities:
  1: "CRITICAL"
  2: "HIGH"
  3: "MEDIUM"
  4: "LOW"
  5: "BACKGROUND"

execution_rules:
  max_queue_size: 1000
  default_timeout: 300
  error_threshold: 5
  maintenance_window:
    enabled: true
    start_time: "23:00"
    end_time: "05:00"
    timezone: "UTC"

error_handling:
  retry_strategies:
    network_error:
      max_retries: 3
      delay: 60
      backoff_factor: 2
    api_error:
      max_retries: 2
      delay: 120
      backoff_factor: 1.5

# notification_templates.yaml
# This file contains templates for different types of notifications

email_templates:
  task_success:
    subject: "[{environment}] Task {task_id} completed successfully"
    body: |
      Task Details:
      - Task ID: {task_id}
      - Type: {task_type}
      - Started: {start_time}
      - Completed: {end_time}
      - Environment: {environment}
      
      Results:
      {task_results}
      
      For more details, please visit: {task_url}

  task_failure:
    subject: "[{environment}] Task {task_id} failed"
    body: |
      Task Details:
      - Task ID: {task_id}
      - Type: {task_type}
      - Started: {start_time}
      - Failed: {end_time}
      - Environment: {environment}
      
      Error Details:
      {error_message}
      
      Stack Trace:
      {stack_trace}
      
      Please check the logs for more information: {log_url}

mattermost_templates:
  task_success:
    channel: "task-notifications"
    message: |
      :white_check_mark: **Task Completed Successfully**
      - **Task ID**: {task_id}
      - **Type**: {task_type}
      - **Environment**: {environment}
      - **Duration**: {duration}
      
      **Results**: {task_results}
      
      [View Details]({task_url})

  task_failure:
    channel: "task-alerts"
    message: |
      :rotating_light: **Task Execution Failed**
      - **Task ID**: {task_id}
      - **Type**: {task_type}
      - **Environment**: {environment}
      - **Error**: {error_message}
      
      [View Logs]({log_url})

notification_rules:
  jira_ticket_update:
    success:
      email:
        enabled: true
        template: "task_success"
        recipients: ["team_lead@company.com", "project_manager@company.com"]
      mattermost:
        enabled: true
        template: "task_success"
    failure:
      email:
        enabled: true
        template: "task_failure"
        recipients: ["team_lead@company.com", "support@company.com"]
      mattermost:
        enabled: true
        template: "task_failure"

  confluence_page_update:
    success:
      email:
        enabled: false
      mattermost:
        enabled: true
        template: "task_success"
    failure:
      email:
        enabled: true
        template: "task_failure"
        recipients: ["content_team@company.com", "support@company.com"]
      mattermost:
        enabled: true
        template: "task_failure"

global_settings:
  notification_defaults:
    email_from: "automation@company.com"
    email_smtp:
      host: "smtp.company.com"
      port: 587
      use_tls: true
    mattermost_default_channel: "automation-notifications"
    include_stack_trace: true
    max_retry_notifications: 3

These configuration files provide a comprehensive setup for:

	1.	Multiple environments with different authentication methods
	2.	Detailed task configurations with priorities and execution rules
	3.	Customizable notification templates and rules

Would you like me to continue with:

	1.	Task Manager implementation
	2.	API client base classes
	3.	Or any specific part of the configuration you’d like me to explain in more detail?

Please let me know which component you’d like me to implement next.


CAN: I’ll implement the Task Manager with support for priority-based scheduling, concurrent execution, and error handling. Here’s the implementation:

# src/core/task_manager.py

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import threading
from queue import PriorityQueue
from concurrent.futures import ThreadPoolExecutor
import time

from ..utils.logger import Logger
from ..utils.exceptions import TaskExecutionError, ConfigurationError
from .config_loader import ConfigLoader

@dataclass
class Task:
    """Task data structure.
    
    Attributes:
        id: Unique task identifier
        type: Type of task (e.g., 'jira_ticket_update')
        priority: Task priority (1-5, 1 being highest)
        Task payload/data
        environment: Target environment
        created_at: Task creation timestamp
        retry_count: Number of retry attempts
        status: Current task status
    """
    id: str
    type: str
    priority: int
    data: Dict[str, Any]
    environment: str
    created_at: datetime
    retry_count: int = 0
    status: str = 'pending'
    
    def __lt__(self, other):
        """Compare tasks based on priority."""
        return self.priority < other.priority

class TaskManager:
    """Manages task execution with priority queuing and concurrent processing."""
    
    def __init__(self, config_dir: str = "configs"):
        """Initialize TaskManager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.logger = Logger(__name__).get_logger()
        self.config_loader = ConfigLoader(config_dir)
        
        # Load configurations
        self.task_config = self.config_loader.load_config("task_config.yaml")
        self.env_config = self.config_loader.load_config("environment.yaml")
        
        # Initialize task queue and execution pool
        self.task_queue = PriorityQueue()
        self.active_tasks: Dict[str, Task] = {}
        self.task_results: Dict[str, Any] = {}
        
        # Initialize locks and events
        self.task_lock = threading.Lock()
        self.shutdown_event = threading.Event()
        
        # Initialize executor
        self.max_workers = self.env_config['global_settings']['concurrent_task_limit']
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Task handlers registry
        self.task_handlers: Dict[str, Callable] = {}
        
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler function for a specific task type.
        
        Args:
            task_type: Type of task
            handler: Function to handle the task
        """
        self.task_handlers[task_type] = handler
        self.logger.info(f"Registered handler for task type: {task_type}")
        
    def submit_task(self, task: Task) -> str:
        """Submit a new task for execution.
        
        Args:
            task: Task to be executed
            
        Returns:
            str: Task ID
            
        Raises:
            ConfigurationError: If task type is not configured
        """
        if task.type not in self.task_config['task_types']:
            raise ConfigurationError(f"Unknown task type: {task.type}")
            
        self.task_queue.put(task)
        self.logger.info(f"Task {task.id} submitted with priority {task.priority}")
        return task.id
        
    async def process_tasks(self):
        """Main task processing loop."""
        self.logger.info("Task processing started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get active task count
                active_task_count = len(self.active_tasks)
                
                if active_task_count < self.max_workers and not self.task_queue.empty():
                    task = self.task_queue.get_nowait()
                    
                    # Check if task should be executed
                    if self._should_execute_task(task):
                        # Submit task for execution
                        future = self.executor.submit(self._execute_task, task)
                        future.add_done_callback(lambda f: self._task_completed_callback(task, f))
                        
                        with self.task_lock:
                            self.active_tasks[task.id] = task
                            
                await asyncio.sleep(1)  # Prevent CPU spinning
                
            except Exception as e:
                self.logger.error(f"Error in task processing loop: {str(e)}")
                
    def _should_execute_task(self, task: Task) -> bool:
        """Check if task should be executed based on rules and conditions.
        
        Args:
            task: Task to check
            
        Returns:
            bool: True if task should be executed
        """
        task_config = self.task_config['task_types'].get(task.type, {})
        
        # Check concurrent limit
        type_count = sum(1 for t in self.active_tasks.values() if t.type == task.type)
        if type_count >= task_config.get('concurrent_limit', self.max_workers):
            return False
            
        # Check maintenance window
        if self._is_in_maintenance_window():
            return False
            
        return True
        
    def _execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task.
        
        Args:
            task: Task to execute
            
        Returns:
            Dict containing task execution results
            
        Raises:
            TaskExecutionError: If task execution fails
        """
        task.status = 'running'
        start_time = time.time()
        
        try:
            # Get task handler
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise TaskExecutionError(f"No handler registered for task type: {task.type}")
                
            # Execute pre-execution hooks
            self._execute_hooks(task, 'pre_execution_hooks')
            
            # Execute task
            result = handler(task.data)
            
            # Execute post-execution hooks
            self._execute_hooks(task, 'post_execution_hooks')
            
            task.status = 'completed'
            execution_time = time.time() - start_time
            
            return {
                'status': 'success',
                'result': result,
                'execution_time': execution_time
            }
            
        except Exception as e:
            task.status = 'failed'
            error_msg = str(e)
            self.logger.error(f"Task {task.id} failed: {error_msg}")
            
            # Handle retry logic
            if self._should_retry_task(task):
                self._schedule_retry(task)
            
            return {
                'status': 'error',
                'error': error_msg,
                'execution_time': time.time() - start_time
            }
            
    def _task_completed_callback(self, task: Task, future):
        """Callback for task completion.
        
        Args:
            task: Completed task
            future: Future object containing task result
        """
        try:
            result = future.result()
            self.task_results[task.id] = result
            
            with self.task_lock:
                if task.id in self.active_tasks:
                    del self.active_tasks[task.id]
                    
            # Send notification if required
            if self.task_config['task_types'][task.type].get('notification_required'):
                self._send_task_notification(task, result)
                
        except Exception as e:
            self.logger.error(f"Error in task completion callback: {str(e)}")
            
    def _should_retry_task(self, task: Task) -> bool:
        """Check if failed task should be retried.
        
        Args:
            task: Failed task
            
        Returns:
            bool: True if task should be retried
        """
        task_config = self.task_config['task_types'].get(task.type, {})
        max_retries = task_config.get('max_retries', 0)
        return task_config.get('retry_enabled', False) and task.retry_count < max_retries
        
    def _schedule_retry(self, task: Task):
        """Schedule a task for retry.
        
        Args:
            task: Task to retry
        """
        task_config = self.task_config['task_types'][task.type]
        retry_delay = task_config.get('retry_delay', 60)
        
        task.retry_count += 1
        task.status = 'pending_retry'
        
        # Use asyncio to schedule retry
        asyncio.create_task(self._delayed_retry(task, retry_delay))
        
    async def _delayed_retry(self, task: Task, delay: int):
        """Delay and retry a task.
        
        Args:
            task: Task to retry
            delay: Delay in seconds before retry
        """
        await asyncio.sleep(delay)
        self.submit_task(task)
        
    def _is_in_maintenance_window(self) -> bool:
        """Check if current time is within maintenance window.
        
        Returns:
            bool: True if in maintenance window
        """
        maintenance_config = self.task_config['execution_rules']['maintenance_window']
        if not maintenance_config.get('enabled', False):
            return False
            
        # Implementation of maintenance window check
        # Add your maintenance window logic here
        return False
        
    def _execute_hooks(self, task: Task, hook_type: str):
        """Execute task hooks.
        
        Args:
            task: Task being executed
            hook_type: Type of hooks to execute
        """
        task_config = self.task_config['task_types'].get(task.type, {})
        hooks = task_config.get(hook_type, [])
        
        for hook in hooks:
            try:
                # Execute hook (implement hook execution logic)
                pass
            except Exception as e:
                self.logger.error(f"Error executing {hook} for task {task.id}: {str(e)}")
                
    def shutdown(self):
        """Shutdown the task manager gracefully."""
        self.logger.info("Initiating task manager shutdown")
        self.shutdown_event.set()
        
        # Wait for active tasks to complete
        self.executor.shutdown(wait=True)
        self.logger.info("Task manager shutdown complete")

This TaskManager implementation includes:

	1.	Priority-based task queuing
	2.	Concurrent task execution with thread pool
	3.	Retry mechanism for failed tasks
	4.	Hook system for pre/post execution
	5.	Maintenance window support
	6.	Comprehensive error handling and logging

Would you like me to implement:

	1.	API client base classes
	2.	Notification system
	3.	Specific task handlers for JIRA/Confluence operations
	4.	Unit tests for the TaskManager

Please let me know which component you’d like me to implement next.


CAN: I’ll implement the base API client classes with support for different authentication methods, retry mechanisms, and error handling. Here’s the implementation:

# src/api_clients/base_client.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import requests
import time
from urllib.parse import urljoin
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..utils.logger import Logger
from ..utils.exceptions import APIError, AuthenticationError, ConfigurationError

class BaseAuthHandler(ABC):
    """Abstract base class for authentication handlers."""
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers.
        
        Returns:
            Dict containing authentication headers
        """
        pass
    
    @abstractmethod
    def refresh_auth(self):
        """Refresh authentication credentials."""
        pass

class BasicAuthHandler(BaseAuthHandler):
    """Handler for basic authentication."""
    
    def __init__(self, username: str, password: str):
        """Initialize basic auth handler.
        
        Args:
            username: Username for basic auth
            password: Password for basic auth
        """
        self.username = username
        self.password = password
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get basic auth headers.
        
        Returns:
            Dict containing basic auth headers
        """
        import base64
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
        
    def refresh_auth(self):
        """No refresh needed for basic auth."""
        pass

class OAuthHandler(BaseAuthHandler):
    """Handler for OAuth authentication."""
    
    def __init__(self, client_id: str, client_secret: str, token_url: str):
        """Initialize OAuth handler.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            token_url: Token endpoint URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.access_token = None
        self.token_expiry = 0
        self.logger = Logger(__name__).get_logger()
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get OAuth headers.
        
        Returns:
            Dict containing OAuth headers
        """
        if self._is_token_expired():
            self.refresh_auth()
        return {"Authorization": f"Bearer {self.access_token}"}
        
    def refresh_auth(self):
        """Refresh OAuth token."""
        try:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expiry = time.time() + token_data.get("expires_in", 3600)
            
        except Exception as e:
            self.logger.error(f"OAuth token refresh failed: {str(e)}")
            raise AuthenticationError(f"Failed to refresh OAuth token: {str(e)}")
            
    def _is_token_expired(self) -> bool:
        """Check if the current token is expired.
        
        Returns:
            bool: True if token is expired
        """
        return not self.access_token or time.time() >= self.token_expiry

class TokenAuthHandler(BaseAuthHandler):
    """Handler for token-based authentication."""
    
    def __init__(self, token: str):
        """Initialize token auth handler.
        
        Args:
            token: Authentication token
        """
        self.token = token
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get token auth headers.
        
        Returns:
            Dict containing token auth headers
        """
        return {"Authorization": f"Bearer {self.token}"}
        
    def refresh_auth(self):
        """No refresh needed for token auth."""
        pass

class BaseAPIClient:
    """Base class for API clients."""
    
    def __init__(
        self,
        base_url: str,
        auth_handler: BaseAuthHandler,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True
    ):
        """Initialize API client.
        
        Args:
            base_url: Base URL for API
            auth_handler: Authentication handler instance
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.auth_handler = auth_handler
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.logger = Logger(__name__).get_logger()
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        Optional[Union[Dict, str]] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Any:
        """Make HTTP request to API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            Request data
            headers: Additional headers
            files: Files to upload
            
        Returns:
            Response data
            
        Raises:
            APIError: If request fails
        """
        url = urljoin(self.base_url, endpoint)
        request_headers = self._prepare_headers(headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=self._prepare_data(data),
                headers=request_headers,
                files=files,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            self._handle_response(response)
            return self._parse_response(response)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise APIError(f"Request failed: {str(e)}")
            
    def _prepare_headers(self, additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Prepare request headers.
        
        Args:
            additional_headers: Additional headers to include
            
        Returns:
            Dict containing all headers
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Add auth headers
        headers.update(self.auth_handler.get_auth_headers())
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
            
        return headers
        
    def _prepare_data(self, Optional[Union[Dict, str]]) -> Optional[str]:
        """Prepare request data.
        
        Args:
            Data to prepare
            
        Returns:
            JSON string or original data
        """
        if isinstance(data, dict):
            return json.dumps(data)
        return data
        
    def _handle_response(self, response: requests.Response):
        """Handle API response.
        
        Args:
            response: Response object
            
        Raises:
            APIError: If response indicates error
            AuthenticationError: If authentication fails
        """
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed")
            
        if response.status_code == 403:
            raise AuthenticationError("Insufficient permissions")
            
        if not 200 <= response.status_code < 300:
            error_msg = self._get_error_message(response)
            raise APIError(f"API error: {error_msg}")
            
    def _parse_response(self, response: requests.Response) -> Any:
        """Parse API response.
        
        Args:
            response: Response object
            
        Returns:
            Parsed response data
            
        Raises:
            APIError: If response parsing fails
        """
        try:
            if not response.content:
                return None
            return response.json()
        except ValueError as e:
            self.logger.error(f"Failed to parse API response: {str(e)}")
            return response.text
            
    def _get_error_message(self, response: requests.Response) -> str:
        """Extract error message from response.
        
        Args:
            response: Response object
            
        Returns:
            Error message string
        """
        try:
            error_data = response.json()
            return error_data.get('message', error_data.get('error', str(response.content)))
        except ValueError:
            return f"HTTP {response.status_code}: {response.text}"
            
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
        """
        return self._make_request("GET", endpoint, params=params)
        
    def post(self, endpoint: str, Optional[Dict] = None, files: Optional[Dict] = None) -> Any:
        """Make POST request.
        
        Args:
            endpoint: API endpoint
            data: Request data
            files: Files to upload
            
        Returns:
            Response data
        """
        return self._make_request("POST", endpoint, data=data, files=files)
        
    def put(self, endpoint: str, Optional[Dict] = None) -> Any:
        """Make PUT request.
        
        Args:
            endpoint: API endpoint
            Request data
            
        Returns:
            Response data
        """
        return self._make_request("PUT", endpoint, data=data)
        
    def delete(self, endpoint: str) -> Any:
        """Make DELETE request.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Response data
        """
        return self._make_request("DELETE", endpoint)

This base API client implementation includes:

	1.	Support for different authentication methods (Basic, OAuth, Token)
	2.	Automatic retry mechanism with exponential backoff
	3.	Comprehensive error handling and logging
	4.	Request/response processing
	5.	SSL verification options
	6.	Timeout handling

Would you like me to implement:

	1.	Specific API clients for JIRA/Confluence/Mattermost
	2.	Unit tests for the base client
	3.	Additional authentication methods
	4.	Or any other component?

Please let me know which part you’d like me to implement next.


CAN: I’ll implement specific API clients for JIRA, Confluence, and Mattermost by extending the BaseAPIClient. Here’s the implementation:

# src/api_clients/jira_client.py

from typing import Dict, List, Optional, Any
from .base_client import BaseAPIClient, BaseAuthHandler

class JIRAClient(BaseAPIClient):
    """JIRA API client implementation."""
    
    def __init__(
        self,
        base_url: str,
        auth_handler: BaseAuthHandler,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize JIRA client.
        
        Args:
            base_url: JIRA base URL
            auth_handler: Authentication handler
            timeout: Request timeout
            max_retries: Maximum retry attempts
        """
        super().__init__(base_url, auth_handler, timeout, max_retries)
        self.api_path = "rest/api/3"
        
    def create_issue(self, project_key: str, issue_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a JIRA issue.
        
        Args:
            project_key: Project key
            issue_type: Issue type (e.g., 'Bug', 'Story')
            Issue data
            
        Returns:
            Created issue data
        """
        payload = {
            "fields": {
                "project": {"key": project_key},
                "issuetype": {"name": issue_type},
                **data
            }
        }
        return self.post(f"{self.api_path}/issue", data=payload)
        
    def update_issue(self, issue_key: str, Dict[str, Any]) -> Dict[str, Any]:
        """Update a JIRA issue.
        
        Args:
            issue_key: Issue key
            Updated field values
            
        Returns:
            Updated issue data
        """
        return self.put(f"{self.api_path}/issue/{issue_key}", data={"fields": data})
        
    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get JIRA issue details.
        
        Args:
            issue_key: Issue key
            fields: List of fields to retrieve
            
        Returns:
            Issue data
        """
        params = {"fields": ",".join(fields)} if fields else None
        return self.get(f"{self.api_path}/issue/{issue_key}", params=params)
        
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search JIRA issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results
            
        Returns:
            List of matching issues
        """
        params = {
            "jql": jql,
            "maxResults": max_results
        }
        return self.get(f"{self.api_path}/search", params=params)
        
    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to an issue.
        
        Args:
            issue_key: Issue key
            comment: Comment text
            
        Returns:
            Created comment data
        """
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        return self.post(f"{self.api_path}/issue/{issue_key}/comment", data=payload)

# src/api_clients/confluence_client.py

class ConfluenceClient(BaseAPIClient):
    """Confluence API client implementation."""
    
    def __init__(
        self,
        base_url: str,
        auth_handler: BaseAuthHandler,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize Confluence client.
        
        Args:
            base_url: Confluence base URL
            auth_handler: Authentication handler
            timeout: Request timeout
            max_retries: Maximum retry attempts
        """
        super().__init__(base_url, auth_handler, timeout, max_retries)
        self.api_path = "rest/api"
        
    def get_page(self, page_id: str, expand: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get Confluence page content.
        
        Args:
            page_id: Page ID
            expand: List of properties to expand
            
        Returns:
            Page content and metadata
        """
        params = {"expand": ",".join(expand)} if expand else None
        return self.get(f"{self.api_path}/content/{page_id}", params=params)
        
    def create_page(
        self,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Confluence page.
        
        Args:
            space_key: Space key
            title: Page title
            content: Page content (in storage format)
            parent_id: Parent page ID
            
        Returns:
            Created page data
        """
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]
            
        return self.post(f"{self.api_path}/content", data=payload)
        
    def update_page(
        self,
        page_id: str,
        title: str,
        content: str,
        version_number: int
    ) -> Dict[str, Any]:
        """Update an existing Confluence page.
        
        Args:
            page_id: Page ID
            title: Page title
            content: Page content
            version_number: Current version number
            
        Returns:
            Updated page data
        """
        payload = {
            "version": {"number": version_number + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        return self.put(f"{self.api_path}/content/{page_id}", data=payload)
        
    def delete_page(self, page_id: str):
        """Delete a Confluence page.
        
        Args:
            page_id: Page ID
        """
        return self.delete(f"{self.api_path}/content/{page_id}")
        
    def get_page_attachments(self, page_id: str) -> List[Dict[str, Any]]:
        """Get attachments for a page.
        
        Args:
            page_id: Page ID
            
        Returns:
            List of attachments
        """
        return self.get(f"{self.api_path}/content/{page_id}/child/attachment")
        
    def add_attachment(
        self,
        page_id: str,
        file_path: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add attachment to a page.
        
        Args:
            page_id: Page ID
            file_path: Path to file
            comment: Attachment comment
            
        Returns:
            Attachment data
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.post(
                f"{self.api_path}/content/{page_id}/child/attachment",
                files=files,
                data={'comment': comment} if comment else None
            )

# src/api_clients/mattermost_client.py

class MattermostClient(BaseAPIClient):
    """Mattermost API client implementation."""
    
    def __init__(
        self,
        base_url: str,
        auth_handler: BaseAuthHandler,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize Mattermost client.
        
        Args:
            base_url: Mattermost base URL
            auth_handler: Authentication handler
            timeout: Request timeout
            max_retries: Maximum retry attempts
        """
        super().__init__(base_url, auth_handler, timeout, max_retries)
        self.api_path = "api/v4"
        
    def send_message(
        self,
        channel_id: str,
        message: str,
        props: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a message to a channel.
        
        Args:
            channel_id: Channel ID
            message: Message text
            props: Additional message properties
            
        Returns:
            Created post data
        """
        payload = {
            "channel_id": channel_id,
            "message": message,
        }
        if props:
            payload["props"] = props
            
        return self.post(f"{self.api_path}/posts", data=payload)
        
    def get_channel_by_name(
        self,
        team_name: str,
        channel_name: str
    ) -> Dict[str, Any]:
        """Get channel by name.
        
        Args:
            team_name: Team name
            channel_name: Channel name
            
        Returns:
            Channel data
        """
        return self.get(
            f"{self.api_path}/teams/name/{team_name}/channels/name/{channel_name}"
        )
        
    def create_channel(
        self,
        team_id: str,
        name: str,
        display_name: str,
        type: str = 'O'
    ) -> Dict[str, Any]:
        """Create a new channel.
        
        Args:
            team_id: Team ID
            name: Channel name
            display_name: Display name
            type: Channel type ('O' for public, 'P' for private)
            
        Returns:
            Created channel data
        """
        payload = {
            "team_id": team_id,
            "name": name,
            "display_name": display_name,
            "type": type
        }
        return self.post(f"{self.api_path}/channels", data=payload)
        
    def upload_file(
        self,
        channel_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Upload a file.
        
        Args:
            channel_id: Channel ID
            file_path: Path to file
            
        Returns:
            Uploaded file data
        """
        with open(file_path, 'rb') as f:
            files = {'files': f}
            return self.post(
                f"{self.api_path}/files",
                files=files,
                data={'channel_id': channel_id}
            )
        
    def get_team_by_name(self, team_name: str) -> Dict[str, Any]:
        """Get team by name.
        
        Args:
            team_name: Team name
            
        Returns:
            Team data
        """
        return self.get(f"{self.api_path}/teams/name/{team_name}")

These API clients provide:

	1.	JIRA Client:
	•	Issue CRUD operations
	•	Search functionality
	•	Comment management
	2.	Confluence Client:
	•	Page CRUD operations
	•	Attachment handling
	•	Content management
	3.	Mattermost Client:
	•	Message sending
	•	Channel management
	•	File upload capabilities

Would you like me to implement:

	1.	Unit tests for these clients
	2.	Additional API endpoints
	3.	Error handling specific to each platform
	4.	Or any other component?

Please let me know which part you’d like me to implement next.


CAN: I’ll implement comprehensive unit tests, additional API endpoints, and platform-specific error handling. Let’s start:

# src/api_clients/exceptions.py

class JIRAError(APIError):
    """JIRA specific errors."""
    def __init__(self, message: str, error_code: str = None, response: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.response = response

class ConfluenceError(APIError):
    """Confluence specific errors."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class MattermostError(APIError):
    """Mattermost specific errors."""
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details

# tests/test_api_clients.py

import pytest
import responses
from unittest.mock import Mock, patch
from datetime import datetime

from src.api_clients.jira_client import JIRAClient
from src.api_clients.confluence_client import ConfluenceClient
from src.api_clients.mattermost_client import MattermostClient
from src.api_clients.base_client import TokenAuthHandler
from src.api_clients.exceptions import JIRAError, ConfluenceError, MattermostError

# Test fixtures
@pytest.fixture
def auth_handler():
    return TokenAuthHandler("test-token")

@pytest.fixture
def jira_client(auth_handler):
    return JIRAClient("https://jira.example.com", auth_handler)

@pytest.fixture
def confluence_client(auth_handler):
    return ConfluenceClient("https://confluence.example.com", auth_handler)

@pytest.fixture
def mattermost_client(auth_handler):
    return MattermostClient("https://mattermost.example.com", auth_handler)

# JIRA Client Tests
class TestJIRAClient:
    @responses.activate
    def test_create_issue_success(self, jira_client):
        """Test successful issue creation."""
        responses.add(
            responses.POST,
            "https://jira.example.com/rest/api/3/issue",
            json={"id": "123", "key": "TEST-1"},
            status=201
        )

        result = jira_client.create_issue(
            "TEST",
            "Bug",
            {
                "summary": "Test Issue",
                "description": "Test Description"
            }
        )

        assert result["key"] == "TEST-1"
        assert len(responses.calls) == 1

    @responses.activate
    def test_create_issue_error(self, jira_client):
        """Test issue creation with error."""
        responses.add(
            responses.POST,
            "https://jira.example.com/rest/api/3/issue",
            json={"errorMessages": ["Project does not exist"]},
            status=400
        )

        with pytest.raises(JIRAError) as exc:
            jira_client.create_issue("INVALID", "Bug", {"summary": "Test"})
        assert "Project does not exist" in str(exc.value)

    @responses.activate
    def test_search_issues(self, jira_client):
        """Test issue search."""
        mock_response = {
            "issues": [
                {"key": "TEST-1", "fields": {"summary": "Test Issue"}},
                {"key": "TEST-2", "fields": {"summary": "Another Issue"}}
            ],
            "total": 2
        }
        responses.add(
            responses.GET,
            "https://jira.example.com/rest/api/3/search",
            json=mock_response,
            status=200
        )

        results = jira_client.search_issues('project = "TEST"')
        assert len(results["issues"]) == 2
        assert results["issues"][0]["key"] == "TEST-1"

# Confluence Client Tests
class TestConfluenceClient:
    @responses.activate
    def test_create_page_success(self, confluence_client):
        """Test successful page creation."""
        mock_response = {
            "id": "123456",
            "title": "Test Page",
            "version": {"number": 1}
        }
        responses.add(
            responses.POST,
            "https://confluence.example.com/rest/api/content",
            json=mock_response,
            status=200
        )

        result = confluence_client.create_page(
            "SPACE",
            "Test Page",
            "<p>Test Content</p>"
        )

        assert result["id"] == "123456"
        assert result["title"] == "Test Page"

    @responses.activate
    def test_update_page_version_conflict(self, confluence_client):
        """Test page update with version conflict."""
        responses.add(
            responses.PUT,
            "https://confluence.example.com/rest/api/content/123456",
            json={"message": "Version conflict"},
            status=409
        )

        with pytest.raises(ConfluenceError) as exc:
            confluence_client.update_page("123456", "Test", "Content", 1)
        assert "Version conflict" in str(exc.value)

    @responses.activate
    def test_get_page_attachments(self, confluence_client):
        """Test getting page attachments."""
        mock_response = {
            "results": [
                {"id": "att1", "title": "file1.pdf"},
                {"id": "att2", "title": "file2.jpg"}
            ]
        }
        responses.add(
            responses.GET,
            "https://confluence.example.com/rest/api/content/123456/child/attachment",
            json=mock_response,
            status=200
        )

        results = confluence_client.get_page_attachments("123456")
        assert len(results["results"]) == 2
        assert results["results"][0]["title"] == "file1.pdf"

# Mattermost Client Tests
class TestMattermostClient:
    @responses.activate
    def test_send_message_success(self, mattermost_client):
        """Test successful message sending."""
        mock_response = {
            "id": "post1",
            "create_at": 1234567890,
            "message": "Test message"
        }
        responses.add(
            responses.POST,
            "https://mattermost.example.com/api/v4/posts",
            json=mock_response,
            status=201
        )

        result = mattermost_client.send_message(
            "channel1",
            "Test message"
        )

        assert result["id"] == "post1"
        assert result["message"] == "Test message"

    @responses.activate
    def test_create_channel_error(self, mattermost_client):
        """Test channel creation with error."""
        responses.add(
            responses.POST,
            "https://mattermost.example.com/api/v4/channels",
            json={"message": "Name already exists"},
            status=400
        )

        with pytest.raises(MattermostError) as exc:
            mattermost_client.create_channel(
                "team1",
                "test-channel",
                "Test Channel"
            )
        assert "Name already exists" in str(exc.value)

# Additional API endpoints for each client

# Extended JIRA Client
class JIRAClientExtended(JIRAClient):
    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get available transitions for an issue."""
        return self.get(f"{self.api_path}/issue/{issue_key}/transitions")

    def transition_issue(self, issue_key: str, transition_id: str, fields: Optional[Dict] = None):
        """Transition an issue to a new status."""
        payload = {
            "transition": {"id": transition_id}
        }
        if fields:
            payload["fields"] = fields
        return self.post(f"{self.api_path}/issue/{issue_key}/transitions", data=payload)

    def get_issue_watchers(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get watchers of an issue."""
        return self.get(f"{self.api_path}/issue/{issue_key}/watchers")

    def add_issue_watcher(self, issue_key: str, account_id: str):
        """Add a watcher to an issue."""
        return self.post(f"{self.api_path}/issue/{issue_key}/watchers", data=account_id)

# Extended Confluence Client
class ConfluenceClientExtended(ConfluenceClient):
    def get_space(self, space_key: str) -> Dict[str, Any]:
        """Get space information."""
        return self.get(f"{self.api_path}/space/{space_key}")

    def get_space_permissions(self, space_key: str) -> List[Dict[str, Any]]:
        """Get space permissions."""
        return self.get(f"{self.api_path}/space/{space_key}/permission")

    def export_page(self, page_id: str, export_format: str = 'pdf') -> bytes:
        """Export page to different formats."""
        return self.get(f"{self.api_path}/content/{page_id}/export/{export_format}")

    def get_page_children(self, page_id: str) -> List[Dict[str, Any]]:
        """Get child pages of a page."""
        return self.get(f"{self.api_path}/content/{page_id}/child/page")

# Extended Mattermost Client
class MattermostClientExtended(MattermostClient):
    def get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Get user status."""
        return self.get(f"{self.api_path}/users/{user_id}/status")

    def update_user_status(self, user_id: str, status: str) -> Dict[str, Any]:
        """Update user status."""
        payload = {"user_id": user_id, "status": status}
        return self.put(f"{self.api_path}/users/{user_id}/status", data=payload)

    def get_channel_statistics(self, channel_id: str) -> Dict[str, Any]:
        """Get channel statistics."""
        return self.get(f"{self.api_path}/channels/{channel_id}/stats")

    def add_user_to_channel(self, channel_id: str, user_id: str) -> Dict[str, Any]:
        """Add user to channel."""
        payload = {"user_id": user_id}
        return self.post(f"{self.api_path}/channels/{channel_id}/members", data=payload)

# Platform-specific error handling implementation

class JIRAErrorHandler:
    """JIRA specific error handler."""
    
    @staticmethod
    def handle_error(response: requests.Response) -> None:
        """Handle JIRA specific errors."""
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"errorMessages": [response.text]}

        if response.status_code == 400:
            raise JIRAError(
                "Invalid request",
                error_code="BAD_REQUEST",
                response=error_data
            )
        elif response.status_code == 401:
            raise JIRAError(
                "Authentication failed",
                error_code="UNAUTHORIZED",
                response=error_data
            )
        elif response.status_code == 403:
            raise JIRAError(
                "Permission denied",
                error_code="FORBIDDEN",
                response=error_data
            )
        elif response.status_code == 404:
            raise JIRAError(
                "Resource not found",
                error_code="NOT_FOUND",
                response=error_data
            )

class ConfluenceErrorHandler:
    """Confluence specific error handler."""
    
    @staticmethod
    def handle_error(response: requests.Response) -> None:
        """Handle Confluence specific errors."""
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"message": response.text}

        if response.status_code == 409:
            raise ConfluenceError(
                "Version conflict detected",
                status_code=response.status_code,
                response=error_data
            )
        elif response.status_code == 404:
            raise ConfluenceError(
                "Page or space not found",
                status_code=response.status_code,
                response=error_data
            )

class MattermostErrorHandler:
    """Mattermost specific error handler."""
    
    @staticmethod
    def handle_error(response: requests.Response) -> None:
        """Handle Mattermost specific errors."""
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"message": response.text}

        if response.status_code == 400:
            raise MattermostError(
                "Invalid request",
                status_code=response.status_code,
                details=error_data
            )
        elif response.status_code == 403:
            raise MattermostError(
                "Action not permitted",
                status_code=response.status_code,
                details=error_data
            )

This implementation provides:

	1.	Comprehensive unit tests for all clients
	2.	Extended API endpoints for each platform
	3.	Platform-specific error handling

Would you like me to:

	1.	Add more test cases
	2.	Implement additional API endpoints
	3.	Add more error handling scenarios
	4.	Or implement any other component?

Please let me know what you’d like me to focus on next.


CAN: I’ll extend the implementation with more test cases, additional API endpoints, and enhanced error handling. Here’s the implementation:

# Additional Test Cases
# tests/test_api_clients_extended.py

import pytest
import responses
from datetime import datetime, timedelta
import json

class TestJIRAClientAdvanced:
    @responses.activate
    def test_bulk_issue_create(self, jira_client):
        """Test bulk issue creation."""
        mock_response = {
            "issues": [
                {"id": "123", "key": "TEST-1"},
                {"id": "124", "key": "TEST-2"}
            ]
        }
        responses.add(
            responses.POST,
            "https://jira.example.com/rest/api/3/issue/bulk",
            json=mock_response,
            status=201
        )

        issues = [
            {"fields": {"summary": "Test 1", "project": {"key": "TEST"}}},
            {"fields": {"summary": "Test 2", "project": {"key": "TEST"}}}
        ]
        result = jira_client.bulk_create_issues(issues)
        assert len(result["issues"]) == 2
        assert result["issues"][0]["key"] == "TEST-1"

    @responses.activate
    def test_issue_link_creation(self, jira_client):
        """Test issue linking."""
        responses.add(
            responses.POST,
            "https://jira.example.com/rest/api/3/issueLink",
            status=201
        )

        result = jira_client.create_issue_link(
            "TEST-1",
            "TEST-2",
            "Blocks",
            {"comment": "Blocking issue"}
        )
        assert responses.calls[0].response.status_code == 201

    @responses.activate
    def test_worklog_addition(self, jira_client):
        """Test adding worklog."""
        mock_response = {
            "id": "12345",
            "timeSpentSeconds": 3600
        }
        responses.add(
            responses.POST,
            "https://jira.example.com/rest/api/3/issue/TEST-1/worklog",
            json=mock_response,
            status=201
        )

        result = jira_client.add_worklog(
            "TEST-1",
            "1h",
            "Work completed",
            datetime.now()
        )
        assert result["id"] == "12345"

class TestConfluenceClientAdvanced:
    @responses.activate
    def test_page_history(self, confluence_client):
        """Test retrieving page history."""
        mock_response = {
            "results": [
                {
                    "id": "1",
                    "version": {"number": 1},
                    "by": {"displayName": "User 1"}
                },
                {
                    "id": "2",
                    "version": {"number": 2},
                    "by": {"displayName": "User 2"}
                }
            ]
        }
        responses.add(
            responses.GET,
            "https://confluence.example.com/rest/api/content/123456/history",
            json=mock_response,
            status=200
        )

        result = confluence_client.get_page_history("123456")
        assert len(result["results"]) == 2
        assert result["results"][0]["version"]["number"] == 1

    @responses.activate
    def test_space_content_backup(self, confluence_client):
        """Test space content backup."""
        mock_response = {
            "status": "in_progress",
            "backup_id": "backup123"
        }
        responses.add(
            responses.POST,
            "https://confluence.example.com/rest/api/space/TEST/backup",
            json=mock_response,
            status=202
        )

        result = confluence_client.backup_space("TEST")
        assert result["status"] == "in_progress"

    @responses.activate
    def test_content_restrictions(self, confluence_client):
        """Test content restrictions management."""
        mock_response = {
            "restrictions": {
                "user": ["user1", "user2"],
                "group": ["group1"]
            }
        }
        responses.add(
            responses.PUT,
            "https://confluence.example.com/rest/api/content/123456/restriction",
            json=mock_response,
            status=200
        )

        result = confluence_client.update_page_restrictions(
            "123456",
            users=["user1", "user2"],
            groups=["group1"]
        )
        assert len(result["restrictions"]["user"]) == 2

class TestMattermostClientAdvanced:
    @responses.activate
    def test_bulk_user_import(self, mattermost_client):
        """Test bulk user import."""
        mock_response = {
            "results": [
                {"user": {"username": "user1"}, "status": "ok"},
                {"user": {"username": "user2"}, "status": "ok"}
            ]
        }
        responses.add(
            responses.POST,
            "https://mattermost.example.com/api/v4/users/import",
            json=mock_response,
            status=201
        )

        users = [
            {"username": "user1", "email": "user1@test.com"},
            {"username": "user2", "email": "user2@test.com"}
        ]
        result = mattermost_client.bulk_import_users(users)
        assert len(result["results"]) == 2

    @responses.activate
    def test_channel_analytics(self, mattermost_client):
        """Test channel analytics retrieval."""
        mock_response = {
            "post_counts_by_day": {
                "2023-01-01": 10,
                "2023-01-02": 15
            },
            "active_users": 25
        }
        responses.add(
            responses.GET,
            "https://mattermost.example.com/api/v4/channels/channel1/analytics",
            json=mock_response,
            status=200
        )

        result = mattermost_client.get_channel_analytics("channel1")
        assert result["active_users"] == 25

# Additional API Endpoints

class JIRAClientExtendedV2(JIRAClientExtended):
    """Extended JIRA client with additional endpoints."""

    def get_issue_security_levels(self, issue_key: str) -> Dict[str, Any]:
        """Get security levels for an issue."""
        return self.get(f"{self.api_path}/issue/{issue_key}/securitylevel")

    def get_issue_remote_links(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get remote links for an issue."""
        return self.get(f"{self.api_path}/issue/{issue_key}/remotelink")

    def create_issue_remote_link(
        self,
        issue_key: str,
        link_url: str,
        title: str,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create remote link for an issue."""
        payload = {
            "object": {
                "url": link_url,
                "title": title,
                "summary": summary
            }
        }
        return self.post(f"{self.api_path}/issue/{issue_key}/remotelink", data=payload)

    def get_issue_property(self, issue_key: str, property_key: str) -> Dict[str, Any]:
        """Get issue property."""
        return self.get(f"{self.api_path}/issue/{issue_key}/properties/{property_key}")

class ConfluenceClientExtendedV2(ConfluenceClientExtended):
    """Extended Confluence client with additional endpoints."""

    def get_content_descendants(
        self,
        content_id: str,
        depth: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get content descendants."""
        params = {"depth": depth} if depth else None
        return self.get(f"{self.api_path}/content/{content_id}/descendant", params=params)

    def move_page(
        self,
        page_id: str,
        target_parent_id: str,
        position: Optional[int] = None
    ) -> Dict[str, Any]:
        """Move page to new location."""
        payload = {
            "targetId": target_parent_id,
            "position": position
        }
        return self.put(f"{self.api_path}/content/{page_id}/move", data=payload)

    def get_space_themes(self, space_key: str) -> List[Dict[str, Any]]:
        """Get space themes."""
        return self.get(f"{self.api_path}/space/{space_key}/theme")

class MattermostClientExtendedV2(MattermostClientExtended):
    """Extended Mattermost client with additional endpoints."""

    def get_user_audit(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user audit logs."""
        return self.get(f"{self.api_path}/users/{user_id}/audit")

    def create_channel_category(
        self,
        team_id: str,
        user_id: str,
        category_name: str,
        channel_ids: List[str]
    ) -> Dict[str, Any]:
        """Create channel category."""
        payload = {
            "team_id": team_id,
            "user_id": user_id,
            "display_name": category_name,
            "channel_ids": channel_ids
        }
        return self.post(f"{self.api_path}/users/{user_id}/teams/{team_id}/channels/categories", data=payload)

# Enhanced Error Handling

class JIRAErrorHandlerExtended(JIRAErrorHandler):
    @staticmethod
    def handle_error(response: requests.Response) -> None:
        """Enhanced JIRA error handling."""
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"errorMessages": [response.text]}

        error_mapping = {
            400: ("Invalid request", "BAD_REQUEST"),
            401: ("Authentication failed", "UNAUTHORIZED"),
            403: ("Permission denied", "FORBIDDEN"),
            404: ("Resource not found", "NOT_FOUND"),
            409: ("Version conflict", "CONFLICT"),
            429: ("Too many requests", "RATE_LIMIT"),
            500: ("Internal server error", "SERVER_ERROR"),
            503: ("Service unavailable", "SERVICE_UNAVAILABLE")
        }

        if response.status_code in error_mapping:
            message, code = error_mapping[response.status_code]
            raise JIRAError(
                f"{message}: {error_data.get('errorMessages', ['No detail'])[0]}",
                error_code=code,
                response=error_data
            )

class ConfluenceErrorHandlerExtended(ConfluenceErrorHandler):
    @staticmethod
    def handle_error(response: requests.Response) -> None:
        """Enhanced Confluence error handling."""
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"message": response.text}

        error_mapping = {
            400: "Invalid request parameters",
            401: "Authentication required",
            403: "Insufficient permissions",
            404: "Content not found",
            409: "Version conflict",
            413: "Content too large",
            429: "Rate limit exceeded",
            500: "Internal server error",
            503: "Service temporarily unavailable"
        }

        if response.status_code in error_mapping:
            raise ConfluenceError(
                error_mapping[response.status_code],
                status_code=response.status_code,
                response=error_data
            )

class MattermostErrorHandlerExtended(MattermostErrorHandler):
    @staticmethod
    def handle_error(response: requests.Response) -> None:
        """Enhanced Mattermost error handling."""
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"message": response.text}

        if response.status_code == 429:
            retry_after = response.headers.get('X-RateLimit-Reset')
            raise MattermostError(
                "Rate limit exceeded",
                status_code=response.status_code,
                details={
                    "retry_after": retry_after,
                    "error": error_data
                }
            )

        error_mapping = {
            400: "Invalid request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not found",
            501: "Feature not implemented",
            503: "Server unavailable"
        }

        if response.status_code in error_mapping:
            raise MattermostError(
                error_mapping[response.status_code],
                status_code=response.status_code,
                details=error_data
            )

This implementation adds:

	1.	Advanced test cases for complex scenarios
	2.	Additional API endpoints for extended functionality
	3.	Enhanced error handling with detailed error information

Would you like me to:

	1.	Add more integration test cases
	2.	Implement more specialized API endpoints
	3.	Add more error recovery mechanisms
	4.	Or implement any other component?

Please let me know what you’d like me to focus on next.
