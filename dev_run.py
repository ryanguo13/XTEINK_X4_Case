# -*- coding: utf-8 -*-
"""把任意 py 脚本送到 Fusion MCP 执行: python3 dev_run.py /tmp/d5.py"""
import json, urllib.request, sys, os
URL = os.environ.get("FUSION_MCP_URL", "http://127.0.0.1:27182/mcp")

# 回环地址不走代理: 环境里的 NO_PROXY 写的是 127.* 通配, urllib 不认通配,
# 不显式给空 proxy handler 的话请求会被 http://127.0.0.1:7890 拦成 502。
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def post(p, sid=None, tmo=900):
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if sid: h["MCP-Session-Id"] = sid
    r = _opener.open(urllib.request.Request(URL, data=json.dumps(p).encode(), headers=h), timeout=tmo)
    return dict(r.headers), r.read().decode()
hd, raw = post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"dev","version":"1"}}})
sid = hd.get("MCP-Session-Id") or hd.get("mcp-session-id")
post({"jsonrpc":"2.0","method":"notifications/initialized"}, sid)
src = open(sys.argv[1], encoding="utf-8").read()
hd, raw = post({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"fusion_mcp_execute","arguments":{"featureType":"script","object":{"script":src,"readOnly":False}}}}, sid)
d = json.loads(raw); res = d.get("result", {})
txt = "\n".join(c.get("text","") for c in res.get("content", []))
for enc in ("latin-1","cp1252"):
    try: txt = txt.encode(enc).decode("utf-8"); break
    except Exception: pass
print(txt)
e = d.get("error")
if e: print("=== ERROR ===\n" + (e if isinstance(e,str) else json.dumps(e,ensure_ascii=False)))
