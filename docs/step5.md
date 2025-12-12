# Step 5：管理后台（管理员接口 + UI）

## 主要工作
- 提供带 `admin_required` 的管理接口：用户列表、谜题 CRUD。
- 管理后台前端页面，支持创建/编辑/删除谜题、查看用户。
- 创建开发用管理员账号种子，便于直接登录。

## 后端改动
- `backend/api/admin.py`：新增 admin Blueprint，全部 `@admin_required`。
  - `GET /api/admin/users`：用户列表。
  - `GET /api/admin/puzzles`：谜题列表（含标准答案）。
  - `POST /api/admin/puzzles`：创建谜题。
  - `PUT /api/admin/puzzles/<id>`：更新谜题。
  - `DELETE /api/admin/puzzles/<id>`：删除谜题。
- `backend/services/auth_service.py`：新增 `list_users()`。
- `backend/app.py`：
  - 注册 `admin_bp`。
  - 种子管理员账号 admin/admin123（仅开发用）。

## 前端改动
- `frontend/admin.html`：管理后台页面，包含谜题创建表单、谜题列表（带编辑/删除）、用户列表。
- `frontend/assets/js/admin.js`：管理逻辑。
  - 需登录且管理员，否则跳转登录。
  - 调用 `/api/admin/puzzles` 做列表/创建/更新/删除。
  - 调用 `/api/admin/users` 查看用户。
- 其他：`admin.html` 引入 `api.js` 以携带 JWT。

## 使用说明
1. 用种子管理员 `admin/admin123` 登录。
2. 打开 `admin.html` 进行谜题管理和用户查看；非管理员访问会被拒绝并跳登录。
3. 普通用户仍通过前面的 `/api/puzzles` 和游戏接口进行游玩，管理接口仅限管理员。
