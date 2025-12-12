# Step 2：题库真实化（puzzles 表/CRUD，前端拉列表进入游戏）

## 主要工作
- 建立真实的谜题模型与 CRUD API，替换之前的 mock。
- 游戏流程改为使用数据库中的谜题；后端 start/chat/finish 均基于真实 puzzle。
- 首页改为从 API 动态拉取谜题列表，跳转到模式选择页。
- 对话页加载谜题描述（不暴露标准答案给普通用户）。

## 后端改动
- `backend/models/puzzle.py`：新增 SQLAlchemy 模型（id/title/description/standard_answer/created_by/created_at），`to_dict` 支持控制是否返回标准答案。
- `backend/services/puzzle_service.py`：实现 list/get/create/update/delete。
- `backend/api/puzzles.py`：新增 Blueprint，提供：
  - `GET /api/puzzles` 列表（无标准答案）
  - `GET /api/puzzles/<id>` 详情（管理员可看到标准答案）
  - `POST/PUT/DELETE /api/puzzles`（`@admin_required`）
- `backend/api/play.py`：改为使用真实 `Puzzle` 查询，去掉 mock。
- `backend/services/game_service.py`：重写文件，start 时校验 puzzle 存在，chat/finish 用真实 puzzle。
- `backend/app.py`：注册 `puzzles_bp`；启动时种子两条示例谜题（仅开发演示，异常不阻塞）。

## 前端改动
- `frontend/index.html`：卡片容器改为动态生成；引入 `/assets/js/puzzles.js`（会调用 `/api/puzzles`）。
- `frontend/assets/js/puzzles.js`：拉取谜题列表并生成卡片，点击进入 `play_mode.html?puzzle_id=...`。
- `frontend/assets/js/play.js`：保持加载 `/api/puzzles/{id}` 作为谜题描述来源（不含标准答案）。

## 使用说明
- 首页加载后会自动请求 `/api/puzzles` 填充卡片。
- 进入 `play_mode.html` 选择模式后调用 `/api/play/start`，跳转到 `play.html` 携带 `session_id/puzzle_id/mode`。
- `play.html` 在加载时请求 `/api/puzzles/{id}` 用于显示标题/情境，提问/结束分别调用 `/api/play/chat` 和 `/api/play/finish`。

## 后续衔接
- Step 3 将补齐排行榜数据展示。
- Step 4 会让 start 接口读取 JWT 登录态，替换硬编码的 `user_id=1`，并完善登录/注册页面。
