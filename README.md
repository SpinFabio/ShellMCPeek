# ShellMCPeek

A minimal VS Code extension that lets an AI agent peek into the terminals you already use, through MCP.

## First version

- List the terminals open in the current VS Code window.
- Read their current contents, matching what the user can inspect in the terminal.
- Reflect terminal buffer clearing: after the user clears the buffer, the next MCP read must not return the cleared contents. A prompt or subsequent output may remain visible.
- Start automatically with VS Code by default. The only configuration setting enables or disables automatic startup.
- Read-only access only. Never execute commands or send terminal input.
- Keep terminal contents in memory only; do not persist terminal history or output.

## Implementation

Use Rust for the MCP backend. Use the smallest TypeScript adapter needed to integrate with the VS Code extension API, which does not load Rust extensions directly.

Before implementation, verify how VS Code exposes existing terminal contents, scrollback and clear events. Shell integration command capture alone may not reproduce the visible terminal buffer. Document any API limitations rather than claiming exact screen parity without verification.

MCP exposes only two tools: `list_terminals` and `read_terminal`.

## Status

Project scaffold only. No extension or MCP server has been implemented or tested yet.

GitHub repository: [SpinFabio/ShellMCPeek](https://github.com/SpinFabio/ShellMCPeek).

## Next steps

See [TODO.md](TODO.md) for implementation, packaging and public GitHub publication tasks.

## License

[MIT](LICENSE)
