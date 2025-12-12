# Step 1：打通最小闭环（模式统一 + 前后端路由对齐 + 静态托管/CORS）

## 主要工作
- 后端增加静态文件托管与全局 CORS，便于直接打开 `frontend/` 下的 HTML 和跨域调用。
- 统一模式命名为 `free / timed / limited_questions`，前端选择页改为调用 `/api/play/start` 获取 `session_id` 后跳转。
- 对话页改为纯静态 HTML + JS，使用查询参数携带 `session_id/puzzle_id/mode`，通过 `/api/play/chat` 提问、`/api/play/finish` 结束。
- 新增简单的前端 API 帮助函数，支持自动附带 `Authorization`（为后续 JWT 做准备）。
- 修复首页静态资源路径、按钮入口（排行榜/Login），并临时保留静态谜题卡片（后续步骤会改为动态拉取）。

## 修改/新增文件
- `backend/app.py`：添加静态文件托管（前端资源）、全局 CORS 头。
- `backend/models/__init__.py`：修正导入（修复原来 `__inti__` 命名问题）。
- `frontend/index.html`：修复样式路径；按钮链接到 `scoreboard.html` / `login.html`；卡片跳转到 `play_mode.html?puzzle_id=...`。
- `frontend/play_mode.html`：样式/脚本路径改为 `/assets/...`；模式值统一；Start 按钮调用后端 `/api/play/start`。
- `frontend/assets/js/play_mode.js`：重写为调用 `/api/play/start`，获取 `session_id` 后携带参数跳转 `play.html`。
- `frontend/play.html`：重写为静态页面；增加结束按钮；引用 `/assets/js/api.js` 与新逻辑。
- `frontend/assets/js/play.js`：重写问答逻辑，读取 URL 参数，调用 `/api/play/chat`、`/api/play/finish`，加载谜题信息（预期从 `/api/puzzles/{id}` 获取）。
- `frontend/assets/css/play.css`：调整聊天区高度，新增结束按钮样式与状态文本。
- `frontend/assets/js/api.js`：新增 API 助手（附带 JWT Header）。
- `frontend/assets/js/auth.js`：登录/注册/退出的前端封装（占位，供后续页面使用）。

## 说明
- 谜题详情目前通过调用 `/api/puzzles/{id}` 加载，后端 API 尚未实现，将在 Step 2 完成。
- 登录注册页面/排行榜/管理后台等仍是占位，将在后续步骤补齐。
