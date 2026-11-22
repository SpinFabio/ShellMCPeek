# Verified terminal access technique

Recorded on November 22, 2026. Tested on Linux with VS Code 1.147.0.

## What worked

Read the **existing in-memory xterm mirror in VS Code's PTY host**, through that process's Node inspector. This does not require clipboard capture, terminal selection, shell input, a renderer debug port, an installation patch or a VS Code restart.

The internal path is:

```javascript
ptyService._ptys.get(terminalId)._serializer._xterm.buffer.active
```

This is VS Code's existing mirror for reconnection/replay, not a second emulator created by ShellMCPeek. It is not yet proven identical to the renderer in all cases. The owner approved using private internals and accepts compatibility maintenance after VS Code updates. Do not reopen that decision merely because this interface is private.

## Reproduce the development probe

Run from the repository root with access to the user's host processes and loopback network. A sandbox may expose only its own process namespace; the successful experiment used host execution for process discovery, signaling and inspector access.

1. Find the current PTY host. Inspect `/proc/<pid>/exe` for the VS Code executable, then `/proc/<pid>/fd` symlink targets for an open file ending in `/ptyhost.log`. Do not read the log. Do not reuse a PID from a previous session, and do not signal the main process, renderer or extension host by mistake.
2. Verify process ownership and identity. Check the `SigCgt` mask in `/proc/<pid>/status`: the bit at `1 << (signal.SIGUSR1 - 1)` must be set. Confirm that `127.0.0.1:9229` is unused before enabling the default inspector. If occupied or ambiguous, stop and identify it rather than manipulating that listener.
3. Enable the verified PTY host's inspector using `os.kill(pty_pid, signal.SIGUSR1)`. This was tested without an initial debugger pause. Wait briefly for `http://127.0.0.1:9229/json/list`, then connect to the returned `webSocketDebuggerUrl`. Verify `process.pid` over CDP before further evaluation. The tested endpoint used loopback only.
4. Use the saved probe, passing the verified host PID. For example, after setting `PTY_HOST_PID` to that verified value:

   ```bash
   python3 scripts/probe_pty.py --pid "$PTY_HOST_PID"
   ```

   This lists internal PTY IDs, titles and shell PIDs. Choose a returned ID, set `PTY_ID`, then read metadata and optionally check an agreed non-sensitive marker:

   ```bash
   python3 scripts/probe_pty.py --pid "$PTY_HOST_PID" --terminal "$PTY_ID" --contains "agreed test marker"
   ```

   `--show` explicitly prints the buffer to stdout; otherwise contents remain in memory and only metadata/match results are printed. Never redirect contents to a file or include them in documentation.
5. Close any inspector opened for this experiment using the cleanup below. Confirm the listener closes and the PTY host remains running. Do this on errors as well as on success. The CLI probe releases its CDP references and disconnects, but **does not disable the inspector**; its lifecycle is the caller's responsibility.

Inspector access permits arbitrary code execution in that process. It is a development bootstrap, not the final read-only MCP interface. Never expose CDP evaluation or a general inspector proxy through MCP. The production design still needs bounded, read-only access and a reliable lifecycle.

## Finding the live service

`scripts/probe_pty.py:service` implements these steps:

1. Obtain the remote object ID of `Object.prototype` using `Runtime.evaluate`.
2. Call `Runtime.queryObjects` with that prototype to obtain reachable objects.
3. Find the prototype with its own function-valued `serializeTerminalState` descriptor. This method identifies the service; the probe **does not call it** or persist serialized state.
4. Query instances of that prototype and require exactly one instance containing a `_ptys` map.
5. Retain the service reference for repeated reads, then release the `shellmcpeek-probe` object group at teardown.

Discovery involves heap inspection and is additional overhead. Do not repeat discovery for every production read or count it as part of the measured warm read latency. Validate private object shapes and fail clearly when they change; never silently fall back to clipboard capture.

## Taking the snapshot

`scripts/probe_pty.py:snapshot` reads the selected mirror's active buffer synchronously:

- Set `captured_at = new Date().toISOString()` immediately before copying lines.
- Iterate `buffer.length` and read `buffer.getLine(i).translateToString(true)`.
- Join soft-wrapped physical lines using `line.isWrapped`; join logical lines with newlines.
- Return terminal identity, timestamp, dimensions, buffer type and text.

No input, acknowledgment, resize, flush or clear method is invoked. Do not introduce a flush to force freshness: measure parser lag and decide how to meet current-buffer semantics without modifying the user's terminal. Wrapped-line spacing and full renderer parity still need validation.

## Inspector cleanup

Using an already connected `CDP` client whose PID has been validated, the tested cleanup was:

```python
client.call("Runtime.releaseObjectGroup", objectGroup="shellmcpeek-probe")
client.evaluate('''(() => {
  setTimeout(() => process.getBuiltinModule("inspector").close(), 50);
  return true;
})()''')
client.close()
```

Scheduling inspector closure allows the evaluation response to arrive before disconnecting. Then poll the endpoint until it is unavailable and verify that the PTY process is still alive. Do not close an inspector that belongs to another debugging session.

## Evidence and limits

- Three live PTYs were enumerated, and three independent markers matched the user's target terminal. Actual terminal contents were read independently of the chat transcript; none were saved.
- Thirty consecutive idle reads returned the same buffer and timestamps. After discovery, median snapshot round-trip time was approximately 0.6 ms and maximum 0.9 ms in this experiment. This is not an end-to-end MCP performance measurement.
- During a coordinated 30-second activity run, a live read occurred at tick 27 while the process was still running. The owner reported no visible interference and normal completion. Maximum fixture scheduling delay across the run was 3.2 ms; the observed tick reported 0.1 ms. No causal conclusion follows from those timing values.
- The debugger was disabled afterward, with the PTY host still alive.

Remaining checks: mirror retention versus renderer scrollback, shell/UI clearing, parser lag, alternate screens, wrapped lines, typing, interactive applications, heavy output, and terminal lifecycle. Internal PTY IDs currently span windows; the VS Code adapter must map them to terminals in the current window and identify the active terminal. Cross-platform discovery and inspector setup are unverified.

The owner permits temporary interference while developing in this session. Final reads must preserve focus, active terminal, selection, clipboard and ongoing user operations. The heartbeat fixture in `scripts/terminal_activity.py` is for manual evaluation, not an automated regression suite. E2E coverage follows the owner's initial prototype evaluation.
