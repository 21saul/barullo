"""Minimal VectorCraft MCP client: python3 vc.py calls.json [--connect] -> runs tool calls in one session."""
import json, subprocess, sys, base64, os
CLI = "/mnt/c/Users/Veintiuno/tools/vc-bin/vectorcraft-0.10.0-windows-x64-portable/vectorcraft-cli.exe"

class VC:
    def __init__(self, connect=False):
        args = [CLI, "mcp"] + (["--connect", "127.0.0.1:7979"] if connect else ["--headless"])
        self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "barullo", "version": "1"}})
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"); self.p.stdin.flush()

    def rpc(self, method, params):
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}) + "\n"); self.p.stdin.flush()
        while True:
            d = json.loads(self.p.stdout.readline())
            if d.get("id") == self.n:
                if "error" in d: raise RuntimeError(d["error"])
                return d["result"]

    def call(self, name, **args):
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        out = []
        for c in r.get("content", []):
            if c["type"] == "text": out.append(c["text"])
            elif c["type"] == "image": out.append({"png": c["data"]})
        if r.get("isError"): raise RuntimeError(f"{name}: {out}")
        return out

    def png(self, name, path, **args):
        for o in self.call(name, **args):
            if isinstance(o, dict):
                open(path, "wb").write(base64.b64decode(o["png"])); return path

    def close(self): self.p.stdin.close(); self.p.wait(timeout=30)
