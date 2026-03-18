#!/usr/bin/env bash
set -euo pipefail

# Install this repo's Claude Code skills into the user's Claude skills directory.
# This makes the skills available in Claude Code (VS Code) without needing to open this repo as the workspace.

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_HOME/skills"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC_SKILLS_DIR="$REPO_ROOT/.claude/skills"

if [ ! -d "$SRC_SKILLS_DIR" ]; then
  echo "Error: expected skills directory not found: $SRC_SKILLS_DIR"
  exit 1
fi

mkdir -p "$SKILLS_DIR"

echo "Installing skills into: $SKILLS_DIR"

for skill_path in "$SRC_SKILLS_DIR"/*; do
  skill_name="$(basename "$skill_path")"
  dest="$SKILLS_DIR/$skill_name"

  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    echo "Warning: destination already exists and is not a symlink: $dest"
    echo "  (leave it, remove it, or rename it before re-running)"
    continue
  fi

  ln -sfn "$skill_path" "$dest"
  echo "  -> $skill_name"
done

# Ensure MCP settings include required servers (merge, but never remove existing config)
MCP_SETTINGS="$CLAUDE_HOME/mcp_settings.json"
if [ ! -f "$MCP_SETTINGS" ]; then
  cat > "$MCP_SETTINGS" <<'EOF'
{
  "mcpServers": {
    "virtual-fly-brain": {
      "type": "http",
      "url": "https://vfb3-mcp.virtualflybrain.org",
      "tools": ["*"]
    },
    "artl-mcp": {
      "command": "uvx",
      "args": ["artl-mcp"],
      "tools": ["*"]
    },
    "ols4": {
      "type": "http",
      "url": "https://www.ebi.ac.uk/ols4/api/mcp",
      "tools": ["*"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "tools": ["*"]
    }
  }
}
EOF
  echo "Created default MCP settings at $MCP_SETTINGS"
else
  echo "MCP settings already exist at $MCP_SETTINGS (not modified)"
fi

cat <<'EOF'

✅ Done.

Next steps:
  1) Run: ./setup_venv.sh
  2) Open Claude Code and verify the skills show up as slash commands:
       /vfb-connectivity  /flybase-combo-pubs  /flybase-stocks

If you want to install the skills into a different Claude config directory, set:
  export CLAUDE_HOME=/path/to/your/claude/config

EOF
