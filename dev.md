# Development Notes

This file covers installing this local checkout as a `uv` tool so the package
can be tested the same way an end user runs the `aiornot` CLI and
`aiornot-mcp` MCP server.

Run these commands from the repository root.

## Install As A Local Tool

Install the local directory in editable mode with the MCP extra:

```bash
uv tool install --force --editable ".[mcp]" --python 3.12
```

This installs both console scripts from `pyproject.toml`:

- `aiornot`
- `aiornot-mcp`

Use Python 3.10 or newer for MCP. The base library still supports Python 3.9,
but the `mcp` package does not.

If the commands are not on your shell `PATH`, run:

```bash
uv tool update-shell
```

Then restart your shell, or use the absolute executable path from:

```bash
command -v aiornot
command -v aiornot-mcp
```

## Smoke Test The CLI

```bash
aiornot --help
aiornot token --help
aiornot image single --help
aiornot text single --help
```

To test authenticated calls, set an API key:

```bash
export AIORNOT_API_KEY="your_api_key"
aiornot token check
```

The CLI also accepts `AIORNOT_API_TOKEN`, or a saved token from:

```bash
aiornot token config
```

## Smoke Test The MCP Server

Verify the source checkout imports the MCP extra and registers tools:

```bash
uv run --extra mcp python -c "from aiornot.mcp_server import create_server; s = create_server(); print('\n'.join(sorted(s._tool_manager._tools)))"
```

Expected tools:

- `aiornot_check_token`
- `aiornot_analyze_image_file`
- `aiornot_analyze_text`
- `aiornot_analyze_text_file`
- `aiornot_analyze_video_file`
- `aiornot_analyze_voice_file`
- `aiornot_analyze_music_file`
- `aiornot_batch_csv`
- `aiornot_batch_scan`

For the installed tool, use the executable inside the `uv` tool environment:

```bash
export AIORNOT_MCP="$(uv tool dir)/aiornot/bin/aiornot-mcp"
test -x "$AIORNOT_MCP" && echo "$AIORNOT_MCP"
```

## Add To Claude Code

After installing the local tool, run this from the project where you use Claude
Code:

```bash
export AIORNOT_API_KEY="your_api_key"
export AIORNOT_MCP="$(uv tool dir)/aiornot/bin/aiornot-mcp"
claude mcp add --transport stdio --scope local --env AIORNOT_API_KEY="$AIORNOT_API_KEY" aiornot-local -- "$AIORNOT_MCP"
claude mcp list
```

In Claude Code, run:

```text
/mcp
```

Remove it later with:

```bash
claude mcp remove aiornot-local
```

## Add To Codex

After installing the local tool, run:

```bash
export AIORNOT_API_KEY="your_api_key"
export AIORNOT_MCP="$(uv tool dir)/aiornot/bin/aiornot-mcp"
codex mcp add aiornot-local --env AIORNOT_API_KEY="$AIORNOT_API_KEY" -- "$AIORNOT_MCP"
codex mcp list
```

Remove it later with:

```bash
codex mcp remove aiornot-local
```

Codex stores MCP servers in `~/.codex/config.toml`. The command above writes a
stdio server entry equivalent to:

```toml
[mcp_servers.aiornot-local]
command = "/absolute/path/to/aiornot-mcp"
enabled = true

[mcp_servers.aiornot-local.env]
AIORNOT_API_KEY = "your_api_key"
```

## Reinstall After Metadata Changes

Editable installs pick up source file changes, but reinstall after changing
console scripts, extras, or dependencies in `pyproject.toml`:

```bash
uv tool install --force --editable ".[mcp]" --python 3.12
```

## Remove The Local Tool

Uninstall the tool environment:

```bash
uv tool uninstall aiornot
```

Confirm it is gone:

```bash
uv tool list
command -v aiornot
command -v aiornot-mcp
```

## One-Off Runs Without Installing

For quick checks without changing the installed tool environment:

```bash
uv tool run --from "." aiornot --help
uv tool run --from ".[mcp]" --python 3.12 aiornot-mcp
```

The MCP command runs a stdio server and will wait for an MCP client to connect.
