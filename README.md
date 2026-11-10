# astrbot_plugin_xiaoya_feed

小亚信息流：把 QQ 消息（群聊/私聊/机器人回显）实时推给桌面宠物"小亚"的告示牌气泡。

## 工作方式
- 钩取全部平台消息 → 内存环形缓冲
- 服务器开放 HTTP 端口（默认 6186）：`GET /events?key=<token>&since=<seq>`
- 桌宠轮询增量拉取，格式：`{"events":[{"seq":1,"ts":...,"kind":"msg","sender":"...","text":"..."}]}`

## 安装
AstrBot WebUI → 插件 → 从 GitHub 安装 → 填本仓库地址。

## 配置
| 键 | 默认 | 说明 |
|---|---|---|
| token | xiaoya-feed-6K2M | 鉴权 token，桌宠侧 feed_key 需一致 |
| port | 6186 | HTTP 监听端口 |

## 安全提示
端口对外开放会暴露消息内容，token 请改成足够长的随机串（桌宠侧同步修改）。

## 许可证

本项目以 [GNU Affero General Public License v3.0](LICENSE)（AGPL-3.0）开源。

允许自由使用、学习、修改及商业分发；若分发修改版，或以网络服务形式向他人提供本项目或修改版，须同样以 AGPL-3.0 公开完整对应源代码。协议全文见 [LICENSE](LICENSE)。
