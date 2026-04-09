"""Static catalog of developer tools managed by forge setup."""

from forge.core.models import HowToStep, MCPServerConfig, SetupTool

SETUP_TOOLS: list[SetupTool] = [
    SetupTool(
        id="claude-code",
        kind="cli",
        display_name="Claude Code CLI",
        description="Anthropic's official CLI for Claude.",
        check_command=["claude", "--version"],
        install_commands={
            "macos": ["npm install -g @anthropic-ai/claude-code"],
            "linux": ["npm install -g @anthropic-ai/claude-code"],
            "windows": ["npm install -g @anthropic-ai/claude-code"],
        },
        auth_steps=[
            HowToStep(
                step=1,
                description="Run claude and follow the OAuth flow in your browser.",
                command="claude",
            ),
        ],
    ),
    SetupTool(
        id="github-mcp",
        kind="mcp-server",
        display_name="GitHub MCP Server",
        description="MCP server for GitHub API access from Claude Code.",
        mcp_key="github",
        mcp_config=MCPServerConfig(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": "<your-github-token>"},
        ),
        env_vars_required=["GITHUB_TOKEN"],
        auth_steps=[
            HowToStep(
                step=1,
                description="Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic).",
            ),
            HowToStep(
                step=2,
                description="Generate a new token with scopes: repo, read:org.",
            ),
            HowToStep(
                step=3,
                description="Copy the token — you will not see it again.",
            ),
            HowToStep(
                step=4,
                description="Open ~/.claude/settings.json and replace <your-github-token> with your token under mcpServers.github.env.GITHUB_TOKEN.",
            ),
        ],
    ),
    SetupTool(
        id="github-cli",
        kind="cli",
        display_name="GitHub CLI",
        description="Official GitHub CLI (gh) for repo and PR management.",
        check_command=["gh", "--version"],
        install_commands={
            "macos": ["brew install gh"],
            "linux": [
                "sudo apt install gh  # Debian/Ubuntu",
                "sudo dnf install gh  # Fedora/RHEL",
            ],
            "windows": ["winget install --id GitHub.cli"],
        },
        auth_steps=[
            HowToStep(
                step=1,
                description="Run the interactive auth login.",
                command="gh auth login",
            ),
            HowToStep(
                step=2,
                description="Choose GitHub.com, HTTPS, and authenticate via browser.",
            ),
        ],
    ),
    SetupTool(
        id="aws-cli",
        kind="cli",
        display_name="AWS CLI",
        description="Amazon Web Services command-line interface.",
        check_command=["aws", "--version"],
        install_commands={
            "macos": ["brew install awscli"],
            "linux": [
                'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip',
                "unzip awscliv2.zip",
                "sudo ./aws/install",
            ],
            "windows": ["msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi"],
        },
        post_install_steps=[
            HowToStep(
                step=1,
                description="Configure a named profile (replace 'myprofile' with your desired profile name).",
                command="aws configure --profile myprofile",
            ),
            HowToStep(
                step=2,
                description="Enter your AWS Access Key ID when prompted.",
            ),
            HowToStep(
                step=3,
                description="Enter your AWS Secret Access Key when prompted.",
            ),
            HowToStep(
                step=4,
                description="Enter your default region (e.g. us-east-1).",
            ),
            HowToStep(
                step=5,
                description="Enter output format — json is recommended.",
            ),
            HowToStep(
                step=6,
                description="Verify your setup.",
                command="aws sts get-caller-identity --profile myprofile",
            ),
        ],
        auth_steps=[
            HowToStep(
                step=1,
                description="Get your credentials at: https://console.aws.amazon.com/iam/ → Security credentials → Access keys.",
            ),
        ],
    ),
    SetupTool(
        id="postman-mcp",
        kind="mcp-server",
        display_name="Postman MCP Server",
        description="MCP server for Postman API collection access from Claude Code.",
        mcp_key="postman",
        mcp_config=MCPServerConfig(
            command="npx",
            args=["-y", "@postman/mcp-server"],
            env={"POSTMAN_API_KEY": "<your-postman-api-key>"},
        ),
        env_vars_required=["POSTMAN_API_KEY"],
        auth_steps=[
            HowToStep(
                step=1,
                description="Log in to Postman at https://www.postman.com/",
            ),
            HowToStep(
                step=2,
                description="Go to your Profile → Settings → API Keys.",
            ),
            HowToStep(
                step=3,
                description="Click 'Generate API Key', give it a name, and copy the key.",
            ),
            HowToStep(
                step=4,
                description="Open ~/.claude/settings.json and replace <your-postman-api-key> with your key under mcpServers.postman.env.POSTMAN_API_KEY.",
            ),
        ],
    ),
]

SETUP_TOOLS_BY_ID: dict[str, SetupTool] = {t.id: t for t in SETUP_TOOLS}
