# TODO — ShellMCPeek

### Completed setup

- [x] Create the project in `/home/fabio-spine/code_space/ShellMCPeek`.
- [x] Initialize Git on the `main` branch and add `.gitignore`.
- [x] Open a new VS Code window and save requirements and preferences.

### First iteration: installable prototype for manual evaluation

- [ ] Keep the extension fast, resource-efficient, minimal and maintainable; use Rust for the backend and only the TypeScript required by VS Code.

- [x] Check VS Code APIs for reading existing terminals, visible contents and scrollback; record stable API limitations and source links in README.md.
- [x] Agree on the terminal-reading approach: private VS Code internals for actual-buffer snapshots. The owner accepts compatibility maintenance after VS Code updates.
- [x] Save the verified PTY-mirror access technique, reproduction steps, inspector cleanup and evidence in [docs/terminal-access.md](docs/terminal-access.md), linked from README and AGENTS.
- [ ] Verify a bridge from the extension host to the renderer's internal buffer reader in a real VS Code window; document any required installation changes before applying them.
- [x] Run initial read-only live-access diagnostics: buffer reader present in installed code, but no accessible renderer debug endpoint found. No actual buffer read achieved; see README.md.
- [x] Read a real existing terminal through private VS Code internals and compare against the user's expected output. PTY mirror access succeeded; three independent marker matches and 30 repeated idle reads verified. Development probe saved in `scripts/`.
- [ ] Validate the PTY mirror against the renderer: scrollback retention, parser lag, UI/shell clears and alternate screen behavior. Use direct renderer access if parity is insufficient.
- [ ] Map PTY identifiers to the current window's terminal IDs, names and active terminal; the development probe currently lists PTYs across windows.
- [ ] Implement non-disruptive in-memory buffer snapshots. Clipboard/selection capture is rejected; reads must preserve focus, active terminal, selection, clipboard and ongoing user input. Never flush or clear the source buffer or create terminal dump files.
- [ ] Make Rust, Node.js/npm and Make available for building and packaging; these tools are currently absent from PATH.
- [ ] Check how to detect screen clearing and scrollback clearing (shell commands, control sequences and VS Code actions). Distinguish a cleared screen from a cleared buffer.
- [ ] Build the MCP backend in Rust with the smallest TypeScript adapter needed for VS Code.
- [ ] Implement `list_terminals`: stable identifier, name and essential information about terminals in the current window.
- [ ] Implement `read_terminal`: return the currently available contents without returning cleared output.
- [ ] Include `captured_at` in every successful read: ISO 8601 UTC with milliseconds, recorded at snapshot capture time.
- [ ] Handle terminals opened, closed or renamed during the session.
- [ ] Start the integration automatically with VS Code by default; provide only one VS Code setting to enable or disable automatic startup.
- [ ] Add `make start` and `make stop` to start and stop the MCP server. Track the managed instance and stop only that process; handle an already running server, stale process tracking and port conflicts clearly.
- [ ] Define a minimal set of server environment variables, including the listening port, with documented defaults so the server works without custom configuration. Bind to localhost by default.
- [ ] Make VS Code startup and Make targets use consistent server defaults and lifecycle behavior; define ownership and avoid duplicate server instances.
- [ ] Expose only read tools; never execute commands or send keystrokes or other terminal input.
- [ ] Keep the buffer in memory only, without history files or terminal content logs.
- [ ] Configure and test the MCP connection to Codex.
- [ ] Verify with real terminals: multiple shells, user-generated output, repeated reads, buffer clearing and terminal closure.
- [x] Perform the first coordinated manual activity check: read during a 30-second heartbeat process, verify it is still running and collect the owner's observation. Completed successfully; owner reported no visible interference.
- [ ] Manually verify that repeated reads of active and inactive terminals do not interrupt typing, running commands, continuous output or interactive applications, and leave focus, active terminal, selection and clipboard unchanged.
- [ ] Document installation, the automatic startup setting, Make commands, environment variables and verified limitations in the README. Keep the project and documentation simple.
- [ ] Prepare an installable VSIX package and verify installation.
- [ ] Deliver the prototype for the owner's manual evaluation before writing automated regression tests; collect feedback and fix confirmed issues.

### After manual evaluation: automated regression coverage

- [ ] Prioritize automated end-to-end tests over unit tests. Keep each test focused on one behavior while exercising as much of the real VS Code adapter, Rust backend and MCP connection as practical.
- [ ] Cover terminal listing and reading, multiple terminals, new output, screen and scrollback clearing, terminal closure and read-only behavior.
- [ ] Cover capture timestamps and non-interference during typing, running commands, continuous output and interactive applications, including reads of inactive terminals.
- [ ] Cover automatic startup enabled and disabled, Make start/stop, default and overridden ports, port conflicts and server cleanup.
- [ ] Keep tests isolated and repeatable, with automatic setup and cleanup; avoid timing-dependent sleeps and manual steps.
- [ ] Measure startup time and resource usage under representative terminal output; use findings to address regressions without introducing unnecessary complexity.

### Publication

- [x] Choose a license for the public project: MIT, included in `LICENSE`.
- [x] Create the GitHub repository `SpinFabio/ShellMCPeek`.
- [x] Check for secrets or terminal contents, create the first commit and push to GitHub.
- [ ] Publish a GitHub release with the installable VSIX package and installation instructions.
- [ ] Consider publishing to the VS Code Marketplace so the extension can be found and installed directly from VS Code.

Next step: validate the demonstrated PTY mirror path against rendered-buffer semantics and current-window terminal identity, then integrate with the Rust backend and minimal VS Code adapter. Only development probes exist so far; automated regression tests remain deferred until after the owner's manual evaluation.
