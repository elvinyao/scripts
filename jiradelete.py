from jira import JIRA
import logging
import sys
from typing import List, Optional

class JiraTicketManager:
    def __init__(self, server_url: str, username: str, api_token: str):
        """
        初始化Jira连接
        
        Args:
            server_url: Jira服务器URL
            username: 用户名
            api_token: API令牌
        """
        self.logger = self._setup_logging()
        try:
            self.jira = JIRA(
                server=server_url,
                basic_auth=(username, api_token)
            )
            self.logger.info("Successfully connected to Jira")
        except Exception as e:
            self.logger.error(f"Failed to connect to Jira: {str(e)}")
            raise

    def _setup_logging(self) -> logging.Logger:
        """设置日志配置"""
        logger = logging.getLogger('JiraTicketManager')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        return logger

    def get_tickets_by_filter(self, jql_filter: str) -> List[str]:
        """
        根据JQL过滤器获取tickets
        
        Args:
            jql_filter: JQL查询字符串
        
        Returns:
            符合条件的ticket key列表
        """
        try:
            issues = self.jira.search_issues(jql_filter, maxResults=False)
            ticket_keys = [issue.key for issue in issues]
            self.logger.info(f"Found {len(ticket_keys)} tickets matching filter")
            return ticket_keys
        except Exception as e:
            self.logger.error(f"Error searching for tickets: {str(e)}")
            raise

    def delete_tickets(self, ticket_keys: List[str]) -> None:
        """
        删除指定的tickets
        
        Args:
            ticket_keys: 要删除的ticket key列表
        """
        successful_deletions = 0
        failed_deletions = 0

        for key in ticket_keys:
            try:
                self.jira.issue(key).delete()
                successful_deletions += 1
                self.logger.info(f"Successfully deleted ticket: {key}")
            except Exception as e:
                failed_deletions += 1
                self.logger.error(f"Failed to delete ticket {key}: {str(e)}")

        self.logger.info(f"Deletion complete. Successfully deleted: {successful_deletions}, Failed: {failed_deletions}")

def main():
    # 配置信息
    SERVER_URL = "https://your-jira-instance.com"
    USERNAME = "your-username"
    API_TOKEN = "your-api-token"
    JQL_FILTER = "project = DEMO AND status = Closed"  # 替换为你的JQL过滤器

    try:
        # 创建Jira管理器实例
        jira_manager = JiraTicketManager(SERVER_URL, USERNAME, API_TOKEN)

        # 获取符合条件的tickets
        tickets = jira_manager.get_tickets_by_filter(JQL_FILTER)

        if not tickets:
            print("No tickets found matching the filter criteria.")
            return

        # 确认删除
        confirmation = input(f"Found {len(tickets)} tickets. Do you want to proceed with deletion? (y/n): ")
        if confirmation.lower() != 'y':
            print("Operation cancelled by user.")
            return

        # 执行删除
        jira_manager.delete_tickets(tickets)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()