# -*- coding: utf-8 -*-
"""在本机通过 Fusion MCP (HTTP) 直接运行 x4_case_fusion.py"""
import json, urllib.request, urllib.error, sys, os

URL = os.environ.get("FUSION_MCP_URL", "http://127.0.0.1:27182/mcp")

def post(payload, sid=None, tmo=1800):
    h = {"Content-Type": "application/json",
         "Accept": "application/json, text/event-stream"}
    if sid:
        h["MCP-Session-Id"] = sid
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=tmo)
        return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "x4_case_fusion.py"
    st, hd, raw = post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {},
        "clientInfo": {"name": "pi-x4", "version": "1.0"}}})
    sid = hd.get("MCP-Session-Id") or hd.get("mcp-session-id")
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)

    src = open(path, encoding="utf-8").read()
    st, hd, raw = post({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {
        "name": "fusion_mcp_execute",
        "arguments": {"featureType": "script",
                      "object": {"script": src, "readOnly": False}}}}, sid)
    d = json.loads(raw)
    res = d.get("result", {})
    txt = "\n".join(c.get("text", "") for c in res.get("content", []))
    # Fusion 侧日志是 UTF-8 被当 latin-1 解过一遍
    for enc in ("latin-1", "cp1252"):
        try:
            txt = txt.encode(enc).decode("utf-8")
            break
        except Exception:
            continue
    print(txt)
    if "error" in d:
        e = d["error"]
        print("=== ERROR ===")
        print(e if isinstance(e, str) else json.dumps(e, ensure_ascii=False))
    print("success:", res.get("success"))

main()
