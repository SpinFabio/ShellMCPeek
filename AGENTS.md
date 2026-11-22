# Working preferences

- Write commit messages in English using `AREA: brief description`, with the macro area in uppercase (for example, `SETUP: initialize project documentation`).
- Read README.md before starting. Keep this project minimal; prioritize read-only terminal access.
- Warn the user before recommending little-known or poorly adopted dependencies or projects; give verified adoption indicators when available.
- When the user requests a new project, ask only for its name if missing. Unless otherwise specified, create it under /home/fabio-spine/code_space, initialize Git and a suitable .gitignore, and open a new VS Code window. These setup actions are authorized by the new-project request.
- For other operations on the machine, propose one explained command at a time and wait for the user’s output unless explicitly asked to execute it.
- Do not record secrets, terminal history or terminal contents in repository documentation.
