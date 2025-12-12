# Step 4：前端登录注册 + JWT 驱动的用户身份

## 主要工作
- 将游戏流程从硬编码 `user_id=1` 改为 JWT 登录态：
  - `/api/play/start`、`/api/play/chat`、`/api/play/finish` 全部要求登录（`@login_required`），使用 `g.current_user.id`。
  - 会话归属校验：chat/finish 需 session.user_id == 当前用户，否则 403。
- 完成登录/注册页面与前端逻辑，统一用 JWT Header 调后端。

## 后端改动
- `backend/api/play.py`：为 start/chat/finish 增加 `@login_required`，用 `g.current_user.id`；校验会话归属；返回 403 forbidden。

## 前端改动
- 新页面：
  - `frontend/login.html`：登录表单，成功后按 `redirect` 参数或首页跳转。
  - `frontend/register.html`：注册后自动登录跳转首页。
- 脚本和页面引用：
  - `frontend/play_mode.html` 引入 `api.js`。
  - `frontend/assets/js/play_mode.js` 改用 `apiFetch` 调 `/api/play/start`，401 时跳转登录。
  - `frontend/assets/js/play.js` 对 chat/finish 的 401 进行登录重定向提示。
  - `frontend/index.html` 登录按钮根据是否有 token 切换为 Logout（清除 token 后刷新）。
- 其他：
  - 登录/注册逻辑使用已有 `assets/js/api.js`（自动附带 Authorization）与 `assets/js/auth.js`（login/register/logout 封装）。

## 使用说明
1. 先访问 `register.html` 创建账号，或 `login.html` 登录（支持 `?redirect=...` 回跳）。
2. 登录后首页右上角按钮会变为 Logout，可清除 token。
3. 选择谜题进入 `play_mode`，调用 `/api/play/start` 自动绑定当前用户；聊天/结束接口也要求登录且会校验 session 归属。
