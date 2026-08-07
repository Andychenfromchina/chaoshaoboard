# 潮少运营大数据看板

静态、无密钥的双平台运营快照看板，发布于 GitHub Pages：

- https://andychenfromchina.github.io/chaoshaoboard/

## 更新

1. 更新 `data/dashboard.json`。
2. 运行 `python3 scripts/validate_board.py`。
3. 运行 `python3 scripts/gen_chaoshaoboard.py`。
4. 在桌面端和手机端检查 `index.html` 后提交推送。

## 数据口径

- 账号层指标来自抖音创作者中心和视频号助手的静态快照。
- 作品层指标来自双平台作品管理页。
- `飞轮健康指数` 是内部运营优先级信号，不是平台官方评分。
- 页面与数据文件不包含账号凭证、Cookie、API Key 或发布令牌。
