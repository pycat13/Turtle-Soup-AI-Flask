# Step 3：排行榜与提交得分

## 主要工作
- 实现真实排行榜数据接口 `/api/scores`，并提供手动提交入口 `/api/scores/submit`（登录态）。
- 封装 ScoreService：支持排行榜查询与手动提交；继续复用已有得分计算逻辑。
- 前端补齐排行榜页面与脚本，展示实时榜单。

## 后端改动
- `backend/services/score_service.py`
  - `calculate_score` 保留（限制在 0–100）。
  - 新增 `submit_score(user_id, puzzle_id, score_value)` 写入 `scores` 表。
  - 新增 `get_leaderboard(limit=20)`，按分数降序、时间降序，联查用户与谜题标题。
- `backend/api/scores.py`
  - `GET /api/scores?limit=20` 返回 `{"data": [...]}`，每项包含 `username/puzzle_title/puzzle_id/score/created_at`。
  - `POST /api/scores/submit`（`@login_required`）接收 `puzzle_id`、`score`，写入一条得分记录。

## 前端改动
- `frontend/scoreboard.html`：新增排行榜页面，使用主页样式，包含表格展示。
- `frontend/assets/js/scoreboard.js`：加载 `/api/scores` 渲染表格；处理空/失败/网络异常状态。

## 使用说明
- 正常游戏结束由 `/api/play/finish` 自动写分，不必手动提交；`/api/scores/submit` 主要用于调试或补录，需要登录。
- 访问 `scoreboard.html` 自动调用 `/api/scores` 获取排行榜并显示用户名、谜题标题、分数和时间。
