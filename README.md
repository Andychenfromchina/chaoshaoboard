# 潮少运营飞轮看板

页面设计与布局基于“大陈运营大数据看板”V4 组件规范，潮少仓库只维护独立的数据快照与内容映射。

## 更新方式

```bash
python3 scripts/gen_chaoshaoboard.py
```

生成后的 `index.html` 为自包含静态页面，无外部脚本、无账号凭证，可直接发布到 GitHub Pages。

## 文件

- `templates/dachen-dashboard-v3.json`：用户提供的 V4 基准组件模板。
- `data/dashboard.json`：潮少双平台数据快照。
- `scripts/gen_chaoshaoboard.py`：潮少内容映射、响应式组装与页面生成器。
