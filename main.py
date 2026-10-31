# -*- coding: utf-8 -*-
"""AstrBot Star 插件：小亚信息流。

把 QQ 消息（群聊/私聊/机器人自身回复回显）实时投递给桌面宠物"小亚"：
- 钩全部消息事件，写入内存环形缓冲；
- 在服务器开一个带 token 的 HTTP 端口（默认 6186），桌宠轮询
  GET /events?key=<token>&since=<seq> 增量拉取；
- 结构化字段：seq/ts/kind/sender/text，桌宠侧负责展示与节流。

配置（WebUI 插件配置页）：
  token: 信息流鉴权 token（桌宠 companion.json 的 feed_key 需一致）
  port:  HTTP 监听端口（默认 6186）
"""
from __future__ import annotations

import json
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register("xiaoya_feed", "suiren0219", "小亚信息流：QQ 消息/机器人回复实时推给桌面宠物", "1.0.0")
class XiaoyaFeedPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.events: deque = deque(maxlen=300)
        self.seq = 0
        self.lock = threading.Lock()
        self.token = str(config.get("token", "xiaoya-feed-6K2M"))
        self.port = int(config.get("port", 6186))
        self._start_server()

    def _start_server(self) -> None:
        plugin = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                u = urlparse(self.path)
                q = parse_qs(u.query)
                if u.path != "/events" or q.get("key", [""])[0] != plugin.token:
                    self.send_response(403)
                    self.end_headers()
                    return
                try:
                    since = int(q.get("since", ["0"])[0])
                except ValueError:
                    since = 0
                with plugin.lock:
                    items = [e for e in plugin.events if e["seq"] > since]
                body = json.dumps({"events": items}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        try:
            srv = ThreadingHTTPServer(("0.0.0.0", self.port), Handler)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            logger.info(f"小亚信息流: HTTP :{self.port}/events 就绪")
        except OSError as e:
            logger.error(f"小亚信息流: 端口 {self.port} 监听失败 {e}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_any_message(self, event: AstrMessageEvent):
        text = (event.message_str or "").strip()
        if not text:
            return
        sender = event.get_sender_name() or str(event.get_sender_id() or "unknown")
        with self.lock:
            self.seq += 1
            self.events.append(
                {
                    "seq": self.seq,
                    "ts": time.time(),
                    "kind": "msg",
                    "sender": sender[:40],
                    "text": text[:200],
                }
            )
