# LongXL6 — GitHub 个人首页仓库

## 用途
GitHub profile README 仓库（与用户名同名的特殊仓库）。`README.md` 直接展示在 https://github.com/LongXL6 首页顶部。

## 结构
- `README.md` — 首页内容：定制 SVG 头图 + GitHub 统计卡 + 自动更新区块
- `assets/banner.svg` — 手工定制的动画头图（自包含 SVG，无外部资源，动画用 SMIL/CSS，兼容 GitHub camo 代理的 `<img>` 嵌入）
- `.github/workflows/snake.yml` — 每日生成贪吃蛇吃贡献格动画，输出到 `output` 分支
- `.github/workflows/activity.yml` — 每 6 小时更新 README 里的"最近动态"区块

## 部署方式
推送到 GitHub 仓库 `LongXL6/LongXL6`（public）即生效，无其他部署步骤。
注意：仓库必须是 public 且与用户名同名，README 才会显示在首页。
首次推送后需在仓库 Settings → Actions 确认 workflow 有写权限（`GITHUB_TOKEN` 默认权限设为 read/write）。

## 凭证
无。两个 workflow 都只用 GitHub 自带的 `GITHUB_TOKEN`，不需要额外 secret。
