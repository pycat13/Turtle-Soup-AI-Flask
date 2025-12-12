# Step 6：模式差异前端完善 + 聊天界面优化

## 主要工作
- 为不同模式加入前端提示与限制展示：
  - **限时模式**：倒计时显示，依据 `limit_seconds` 和 `start_time` 计算剩余时间。
  - **限题模式**：展示已问/总数与剩余次数。
- 聊天界面优化：
  - 消息气泡分左右：系统/AI 在左，玩家在右。
  - 聊天区域增加底部内边距，避免发送按钮被挡；对话不再占满全屏。
  - 增加顶部状态条（时间、提问数）。

## 前端改动
- `frontend/play_mode.html` + `assets/js/play_mode.js`
  - Start 游戏后将 `limit_seconds/limit_questions/start_time` 透传到 `play.html` 查询参数。
  - 调用依然走 `/api/play/start`（401 会跳登录）。
- `frontend/play.html`
  - 新增状态栏容器，显示倒计时与提问数。
- `frontend/assets/js/play.js`
  - 读取 URL 中的 `limit_seconds/limit_questions/start_time`，启动倒计时，统计提问次数（成功问答时递增）。
  - 消息气泡区分角色；401 自动跳登录。
- `frontend/assets/css/play.css`
  - 聊天区域改为 `flex` 垂直布局并增加底部 padding，预留发送/完成按钮区域。
  - 气泡左右区分：用户右侧粉色，系统/AI 左侧白色。
  - 调整聊天区高度、状态条样式，发送按钮不会被遮挡。

## 使用说明
- 进入限时模式时会看到实时倒计时；限题模式会显示“已问/总数”和剩余次数。
- 聊天时，玩家问题显示在右侧，系统/AI 回答在左侧，发送按钮完全可见。
