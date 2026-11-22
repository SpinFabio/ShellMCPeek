"""Read VS Code's existing PTY mirror through an already enabled Node inspector.

Development experiment, not the MCP server. No terminal input or file dumps.
Only summaries are printed unless --show is explicitly supplied.
"""

import argparse
import json
import time
import urllib.request

from cdp import CDP


def service(client):
    prototype = client.call(
        "Runtime.evaluate", expression="Object.prototype", objectGroup="shellmcpeek-probe"
    )["result"]["objectId"]
    objects = client.call("Runtime.queryObjects", prototypeObjectId=prototype,
                          objectGroup="shellmcpeek-probe")["objects"]["objectId"]
    prototypes = client.call(
        "Runtime.callFunctionOn", objectId=objects, objectGroup="shellmcpeek-probe",
        functionDeclaration='''function () {
          return this.filter(o => typeof Object.getOwnPropertyDescriptor(
            o, "serializeTerminalState")?.value === "function");
        }'''
    )["result"]["objectId"]
    count = client.call("Runtime.callFunctionOn", objectId=prototypes,
                        functionDeclaration="function(){return this.length}",
                        returnByValue=True)["result"]["value"]
    if count != 1:
        raise RuntimeError(f"Expected one PTY service prototype, found {count}")
    prototype = client.call("Runtime.callFunctionOn", objectId=prototypes,
                            functionDeclaration="function(){return this[0]}",
                            objectGroup="shellmcpeek-probe")["result"]["objectId"]
    return client.call("Runtime.queryObjects", prototypeObjectId=prototype,
                       objectGroup="shellmcpeek-probe")["objects"]["objectId"]


def snapshot(client, services, terminal_id=None):
    result = client.call(
        "Runtime.callFunctionOn", objectId=services,
        arguments=[{"value": terminal_id}], returnByValue=True,
        functionDeclaration='''function (id) {
          if (this.length !== 1 || !(this[0]._ptys instanceof Map)) {
            throw new Error("Unexpected PTY service layout");
          }
          const service = this[0];
          if (id === null) {
            return {captured_at: new Date().toISOString(), terminals:
              Array.from(service._ptys, ([id, p]) => ({id, name:p.title, pid:p.pid}))};
          }
          const p = service._ptys.get(id);
          if (!p) throw new Error("Unknown terminal ID");
          const xterm = p._serializer?._xterm;
          if (!xterm?.buffer?.active) throw new Error("PTY mirror unavailable");
          const captured_at = new Date().toISOString();
          const buffer = xterm.buffer.active;
          const lines = [];
          for (let i = 0; i < buffer.length; i++) {
            const line = buffer.getLine(i);
            if (!line) throw new Error("Buffer changed during read");
            const text = line.translateToString(true);
            if (line.isWrapped && lines.length) lines[lines.length - 1] += text;
            else lines.push(text);
          }
          return {id, name:p.title, captured_at, source:"vscode-pty-mirror",
            buffer_type:buffer.type, rows:xterm.rows, columns:xterm.cols,
            line_count:buffer.length, text:lines.join("\\n")};
        }'''
    )
    return result["result"]["value"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=9229)
    parser.add_argument("--pid", type=int, required=True, help="Expected PTY host PID")
    parser.add_argument("--terminal", type=int, help="Read this internal PTY ID")
    parser.add_argument("--contains", action="append", default=[], help="Report a match without printing contents")
    parser.add_argument("--show", action="store_true", help="Print contents to stdout; never redirect to a file")
    args = parser.parse_args()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(f"http://127.0.0.1:{args.port}/json/list", timeout=3) as response:
        targets = json.load(response)
    if len(targets) != 1 or targets[0].get("type") != "node":
        raise RuntimeError("Expected one local Node inspector target")
    client = CDP(targets[0]["webSocketDebuggerUrl"])
    started = time.monotonic()
    try:
        pid = client.evaluate("process.pid")["value"]
        if pid != args.pid:
            raise RuntimeError("Inspector PID does not match the expected PTY host")
        services = service(client)
        result = snapshot(client, services, args.terminal)
        if "text" in result:
            text = result.pop("text")
            result["characters"] = len(text)
            result["matches"] = {marker: marker in text for marker in args.contains}
            if args.show:
                result["text"] = text
        result["probe_ms"] = round((time.monotonic() - started) * 1000, 2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        try:
            client.call("Runtime.releaseObjectGroup", objectGroup="shellmcpeek-probe")
        finally:
            client.close()


if __name__ == "__main__":
    main()
