# ShellMCPeek

A minimal VS Code extension that lets an AI agent peek into the terminals you already use, through MCP.

## First version

- List the terminals open in the current VS Code window.
- Read their current contents, matching what the user can inspect in the terminal.
- Include `captured_at` in every successful `read_terminal` response: an ISO 8601 UTC timestamp with milliseconds, recorded when the buffer snapshot is captured rather than when the response is sent.
- Read in the background without changing focus, the active terminal, selection or clipboard, sending input, or interrupting ongoing terminal operations.
- Reflect terminal buffer clearing: after the user clears the buffer, the next MCP read must not return the cleared contents. A prompt or subsequent output may remain visible.
- Start automatically with VS Code by default. The only VS Code setting enables or disables automatic startup.
- Read-only access only. Never execute commands or send terminal input.
- Keep terminal contents in memory only; do not persist terminal history or output.

## Implementation

Use Rust for the MCP backend. Use the smallest TypeScript adapter needed to integrate with the VS Code extension API, which does not load Rust extensions directly.

Before implementation, verify how VS Code exposes existing terminal contents, scrollback and clear events. Shell integration command capture alone may not reproduce the visible terminal buffer. Document any API limitations rather than claiming exact screen parity without verification.

MCP exposes only two tools: `list_terminals` and `read_terminal`.

Keep startup fast, resource usage low and the implementation minimal and maintainable. Provide Make targets to start and stop the MCP server, with environment variables and sensible defaults for essential server parameters such as the listening port. Stop only the server instance managed by the project.

Deliver an installable prototype for the owner's manual evaluation before writing automated regression tests. Then prioritize automated end-to-end tests, each focused on one behavior while exercising the real extension, Rust backend and MCP connection together.

## Status

Live terminal access has been demonstrated through VS Code's private PTY service. Development probes exist; the Rust backend, VS Code extension and MCP server have not been implemented yet. The PTY mirror still needs comparison with the rendered buffer before it can satisfy all requirements.

### Terminal API findings

Reviewed on November 22, 2026; installed VS Code version: 1.147.0.

- The [stable terminal API](https://code.visualstudio.com/api/references/vscode-api#Terminal) supports listing existing terminals, but does not expose a full-buffer snapshot or a buffer-cleared event.
- Shell integration can stream command output through `TerminalShellExecution.read()`. This is not a snapshot of the current terminal screen and does not recover output written before capture started. Retaining command output alone cannot guarantee that cleared contents are forgotten.
- The [raw output event](https://github.com/microsoft/vscode/blob/main/src/vscode-dts/vscode.proposed.terminalDataWriteEvent.d.ts) is still proposed. It exposes process output, not the existing rendered buffer or all UI clear actions. Microsoft explicitly notes performance concerns.
- Microsoft is still [exploring a terminal buffer API](https://github.com/microsoft/vscode/issues/207504). Proposed APIs add installation requirements and [cannot be used for normal Marketplace publication](https://code.visualstudio.com/api/advanced-topics/using-proposed-api).
- Selection/clipboard capture is rejected: reads must never change focus, the active terminal, selection or clipboard, or interrupt the user's work.

### Approved capture approach

Decision recorded on November 22, 2026: use private VS Code internals to obtain an in-memory snapshot of the actual terminal buffer. The owner accepts that VS Code updates may break the integration and require extension updates. Do not reopen the stable-versus-private API decision merely because those internals are unsupported.

The renderer's private buffer reader is not an ordinary extension API. A second access path has now been demonstrated: the PTY service's existing in-memory xterm mirror, used by VS Code for reconnection/replay. Preserve the current-buffer semantics rather than substituting captured command history. Keep terminal contents in memory only, with no permanent or temporary dumps, history files or content logs. Never flush or clear the source buffer.

Before claiming the prototype works, verify that repeated reads of active and inactive terminals leave user input, running processes, focus, active terminal, selection and clipboard unaffected. Include typing, long-running output and interactive terminal applications in the manual evaluation; automate these regressions after the owner's initial evaluation.

### Live access probe

The reproducible procedure, private object path, inspector lifecycle, saved scripts and verified results are documented in [docs/terminal-access.md](docs/terminal-access.md).

On November 22, 2026, initial renderer diagnostics found no accessible DevTools endpoint. A subsequent experiment successfully accessed the existing PTY host instead:

1. Identify the PTY utility process from its open `ptyhost.log` descriptor, without reading logs. Check that it has a SIGUSR1 handler before enabling its Node inspector.
2. Connect to that local inspector, verify the process ID, and locate the live PTY service with CDP `Runtime.queryObjects` and its `serializeTerminalState` prototype method.
3. Read `service._ptys.get(id)._serializer._xterm.buffer.active` directly. Only read buffer properties and lines; do not call input, flush, resize or clearing methods.
4. Release inspector object references, disconnect and disable the inspector opened for the experiment.

The probe listed three live PTYs and independently matched all three requested markers in the target terminal's existing contents. Thirty consecutive reads returned an unchanged buffer and capture timestamps. Median read latency after service discovery was approximately 0.6 ms (maximum 0.9 ms); discovery/connection is additional overhead. No terminal content was saved, and no clipboard operation, shell input, focus change, restart or installation patch was used. The inspector endpoint was closed afterward and the PTY service remained alive.

`scripts/probe_pty.py` and `scripts/cdp.py` are standard-library Python development tools, not the production architecture. The probe requires an already enabled local Node inspector and an explicit expected PTY PID. Without `--show`, it prints only metadata and optional `--contains` match results. Do not redirect terminal contents to files. Enabling the inspector is a development setup step; it grants much broader access than the two intended MCP tools and must not be exposed as an MCP capability.

Still unverified: full scrollback parity (the PTY mirror has its own configured retention), parser lag under heavy output, shell/UI clearing, alternate screens, per-window terminal identity and active state, typing and interactive application non-interference. The probe's successful idle reads do not establish these properties. Map PTY IDs to the current window through the VS Code adapter before exposing tools. Use a direct renderer path if the mirror cannot satisfy current-buffer semantics.

During development the owner permits experiments in the current session, including temporary interference. This permission does not relax the final product's non-interference requirement.

For the coordinated manual activity check, run `python3 scripts/terminal_activity.py` in the terminal being observed. It prints one heartbeat per second for 30 seconds and reports completion and maximum scheduling delay. Trigger the buffer probe while it is running and check for visual pauses or focus changes. A successful heartbeat run alone cannot prove that terminal rendering or input was unaffected. Do not treat the fixture as an automated regression test.

The first coordinated check passed on November 22, 2026: a live snapshot was captured during tick 27 while the activity process was still running. The owner reported no visible interference and confirmed completion in 30 seconds. The activity fixture's maximum scheduling delay was 3.2 ms across the run; the tick observed during capture reported 0.1 ms. These observations apply to this low-output workload only and do not establish causation for timing variation or cover typing, interactive applications or heavy output.

The implementation environment currently has VS Code but no `cargo`, `rustc`, `node`, `npm` or `make` on `PATH`. Build tooling must be made available before producing and checking an installable VSIX.

GitHub repository: [SpinFabio/ShellMCPeek](https://github.com/SpinFabio/ShellMCPeek).

## Next steps

See [TODO.md](TODO.md) for implementation, packaging and public GitHub publication tasks.

## License

[MIT](LICENSE)
