#!/usr/bin/env python3
"""Validate the generated Chaoshao board and its source snapshot."""

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data' / 'dashboard.json').read_text())
PAGE = (ROOT / 'index.html').read_text()


class FrameParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.frames = []

    def handle_starttag(self, tag, attrs):
        if tag == 'iframe':
            values = dict(attrs)
            self.frames.append((values.get('title', ''), values.get('srcdoc', '')))


def require(condition, message):
    if not condition:
        print(f'ERROR: {message}')
        sys.exit(1)


def main():
    dy, wx, summary = DATA['douyin'], DATA['wechat'], DATA['summary']
    require(dy['plays7d'] + wx['plays7d'] == summary['plays7d'], '双平台播放与总览不一致')
    require(dy['followers'] + wx['followers'] == summary['followers'], '双平台粉丝与总览不一致')
    require(dy['netFollowers7d'] + wx['netFollowers7d'] == summary['netFollowers7d'], '双平台净增与总览不一致')
    require(len(DATA['works']) == 8, '视频号 TOP 榜必须为 8 条')
    require(abs(wx['recommendPlays'] / wx['plays7d'] * 100 - wx['recommendShare']) < 0.1, '视频号推荐占比不一致')

    parser = FrameParser()
    parser.feed(PAGE)
    require(len(parser.frames) == 7, f'组件数量应为 7，实际 {len(parser.frames)}')
    docs = [html.unescape(srcdoc) for _, srcdoc in parser.frames]
    merged = '\n'.join(docs)

    required = [
        '双平台 · 数据对比', '粉丝画像 · 双平台', '运营健康罗盘',
        '流量来源 · 母题反差', '视频号 · 近10条 TOP8',
        '策略 · 风险 · 下一条', '第22轴', '功夫女足'
    ]
    require(not [item for item in required if item not in merged], '生成页面缺少潮少核心组件或内容')
    require('大陈日更' not in merged and '快手 · 粉丝' not in merged, '生成页面残留基准账号内容')
    require('grid-template-columns:repeat(12,1fr)' in PAGE, '桌面 12 列网格缺失')
    require('@media (max-width:1180px)' in PAGE, '1180px 手机断点缺失')
    require('html.host-mobile' in PAGE, 'iframe 手机自然高度机制缺失')
    require('min-height:44px' in PAGE, '手机触控区约束缺失')
    require(not re.findall(r'(?:src|href)=["\']https?://', PAGE, flags=re.I), '页面包含外部资源请求')

    scripts = []
    for doc in docs:
        scripts.extend(re.findall(r'<script>([\s\S]*?)</script>', doc))
    require(len(scripts) >= 7, '组件脚本未完整嵌入')

    print(
        'VALIDATION_OK: '
        f'components=7, plays={summary["plays7d"]}, followers={summary["followers"]}, '
        f'top8={sum(item["plays"] for item in DATA["works"])}, version={DATA["meta"]["version"]}'
    )


if __name__ == '__main__':
    main()
