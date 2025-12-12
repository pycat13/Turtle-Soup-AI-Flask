# Step 9：管理入口与计时修复

## 变更概览
- 首页新增 Admin 入口（指向 `/admin.html`）。
- 管理后台前端校验改为：必须登录且为管理员才能进入，否则直接跳登录（避免先露出页面再跳转）。
- 计时模式倒计时回退为 5 分钟，避免出现 0s 立即结束。
- 题库种子已扩充为 6 道谜题（若数据库为空会自动插入）。

## 修改文件
- `frontend/index.html`：顶部按钮增加 Admin 链接。
- `frontend/assets/js/admin.js`：`ensureAdmin` 调用 `/api/auth/me` 校验 `is_admin`，未通过立即跳登录。
- `frontend/assets/js/play.js`：在计时模式缺省时回退 `limitSeconds=300`，`startTime` 为空时使用当前时间，防止倒计时为 0。
- `backend/app.py`：种子题维持 6 道（已含在文件中，启动空库自动写入）。

## 使用说明
- 仅管理员账号（默认种子 `admin/admin123`）可访问 `/admin.html`；非管理员会直接跳转到登录页。
- 计时模式默认倒计时 5 分钟，不会出现立即结束的情况。
