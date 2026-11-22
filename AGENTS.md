# Working preferences

- Write commit messages in English using `AREA: brief description`, with the macro area in uppercase (for example, `SETUP: initialize project documentation`).
- Read README.md before starting. Keep this project minimal; prioritize read-only terminal access.
- Warn the user before recommending little-known or poorly adopted dependencies or projects; give verified adoption indicators when available.
- When the user requests a new project, ask only for its name if missing. Unless otherwise specified, create it under /home/fabio-spine/code_space, initialize Git and a suitable .gitignore, and open a new VS Code window. These setup actions are authorized by the new-project request.
- For other operations on the machine, propose one explained command at a time and wait for the user’s output unless explicitly asked to execute it.
- Do not record secrets, terminal history or terminal contents in repository documentation.

# Project decisions

- Before continuing terminal-access implementation, read [docs/terminal-access.md](docs/terminal-access.md). It records the successful PTY-mirror technique, reproduction steps, inspector cleanup and remaining limitations; reuse the saved probes rather than restarting feasibility research.
- Keep all repository documentation and commit messages in English.
- Implement the backend in Rust, with only the TypeScript adapter required by VS Code. Optimize for fast startup, low resource use, minimal dependencies and maintainability.
- MCP must expose only `list_terminals` and `read_terminal`. Never add command execution, keystrokes or write mode, including as a future option.
- The only VS Code setting is automatic startup, enabled by default. Essential server environment variables may override documented defaults, including the port; bind to localhost by default.
- Provide `make start` and `make stop`. Stop only the managed server instance and coordinate lifecycle ownership with the extension; never kill arbitrary processes by port or name.
- Deliver an installable prototype for the owner's manual evaluation before writing automated regression tests. After feedback, prioritize isolated, automatic E2E tests that exercise real components and focus each test on one behavior. Do not add unit tests by default.
- Read the terminal API findings in README.md before choosing a capture implementation. Stable APIs do not currently provide a full-buffer snapshot. Shell execution output is not the current rendered buffer; raw output events are proposed and do not solve pre-existing contents or UI clearing.
- The owner explicitly approved private VS Code internals for actual-buffer snapshots and accepts maintenance when VS Code changes. Do not ask again merely because the API is private or unstable. Verify the extension-host/renderer bridge; authorization to use internals does not mean that bridge already exists. Explain any required installation modifications before applying them. Do not replace current-buffer reads with command-output capture.
- Clipboard/selection capture has been explicitly rejected. Reads must not change focus, active terminal, selection or clipboard, interrupt input or flush/clear the terminal. Research non-disruptive snapshots; do not ask the owner to reconsider clipboard capture.
- Include `captured_at` on every successful `read_terminal` result, using ISO 8601 UTC with milliseconds at snapshot capture time. Keep snapshots in memory only; never create temporary or permanent terminal dumps.
- Verify non-interference with active and inactive terminals, ongoing typing, running commands, continuous output and interactive applications. Manual evaluation comes first; automated E2E regression coverage follows the owner's feedback.
- Live access succeeded via the PTY host's existing xterm mirror: `service._ptys.get(id)._serializer._xterm.buffer.active`. `scripts/probe_pty.py` and `scripts/cdp.py` preserve the development probe; no new Python dependency is required. This is experimental tooling, not a replacement for the Rust implementation.
- The probe found the user's target from independent marker matches and performed 30 stable idle reads. Renderer parity, retention limits, heavy-output lag, clears, interactive non-interference and mapping PTYs to the current VS Code window/active terminal are still unverified. Do not claim complete buffer parity or full non-interference from this result.
- The owner permits temporary interference in the current development session. Final product reads must remain non-disruptive. Node inspector access is a development mechanism with broad privileges: validate target PID, keep it local, and close any inspector opened for experiments afterward. Never expose arbitrary inspector evaluation through MCP.
- The first coordinated 30-second activity check passed: a real read occurred during tick 27 and the owner reported no visible interference and normal completion. This covers only a low-output heartbeat process; typing, interactive apps, heavy output and clearing still require verification. Keep only aggregate findings in documentation, not pasted terminal transcripts.
