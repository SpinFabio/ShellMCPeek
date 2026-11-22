# TODO — ShellMCPeek

### Completed setup

- [x] Create the project in `/home/fabio-spine/code_space/ShellMCPeek`.
- [x] Initialize Git on the `main` branch and add `.gitignore`.
- [x] Open a new VS Code window and save requirements and preferences.

### First version: minimal, read-only access

- [ ] Check VS Code APIs for reading existing terminals, visible contents and scrollback; verify stable API limitations before choosing the architecture.
- [ ] Check how to detect screen clearing and scrollback clearing (shell commands, control sequences and VS Code actions). Distinguish a cleared screen from a cleared buffer.
- [ ] Build the MCP backend in Rust with the smallest TypeScript adapter needed for VS Code.
- [ ] Implement `list_terminals`: stable identifier, name and essential information about terminals in the current window.
- [ ] Implement `read_terminal`: return the currently available contents without returning cleared output.
- [ ] Handle terminals opened, closed or renamed during the session.
- [ ] Start the integration automatically with VS Code by default; provide only one configuration setting to enable or disable automatic startup.
- [ ] Expose only read tools; never execute commands or send keystrokes or other terminal input.
- [ ] Keep the buffer in memory only, without history files or terminal content logs.
- [ ] Configure and test the MCP connection to Codex.
- [ ] Verify with real terminals: multiple shells, user-generated output, repeated reads, buffer clearing and terminal closure.
- [ ] Document installation, the automatic startup setting and verified limitations in the README. Keep the project and documentation simple.
- [ ] Prepare an installable VSIX package and verify installation.

### Publication

- [x] Choose a license for the public project: MIT, included in `LICENSE`.
- [x] Create the GitHub repository `SpinFabio/ShellMCPeek`.
- [ ] Check for secrets or terminal contents, create the first commit and push to GitHub.
- [ ] Publish a GitHub release with the installable VSIX package and installation instructions.
- [ ] Consider publishing to the VS Code Marketplace so the extension can be found and installed directly from VS Code.

Next step: verify whether VS Code APIs support reading the actual terminal buffer and detecting its clearing. Implementation has not started.
