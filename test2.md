import shutil
import anyio

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)

async def main():
    claude_path = shutil.which("claude")
    print("Using Claude:", claude_path)

    options = ClaudeAgentOptions(
        cli_path=claude_path,
        cwd="/path/to/your/project",
    )

    async for message in query(
        prompt="分析一下这个项目",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

anyio.run(main)
