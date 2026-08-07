#!/usr/bin/env python3
"""Validate dashboard data reconciliation and generated-page safety."""

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "dashboard.json"
HTML_PATH = ROOT / "index.html"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.scripts = 0

    def handle_starttag(self, tag, attrs) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(str(values["id"]))
        if tag == "script":
            self.scripts += 1


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    dy = data["platforms"]["douyin"]
    wx = data["platforms"]["wechat"]
    summary = data["summary"]

    if dy["plays7d"] + wx["plays7d"] != summary["plays7d"]:
        fail("双平台播放与总览不一致")
    if dy["followers"] + wx["followers"] != summary["followers"]:
        fail("双平台粉丝与总览不一致")
    if dy["netFollowers7d"] + wx["netFollowers7d"] != summary["netFollowers7d"]:
        fail("双平台净增粉与总览不一致")
    if len(data["works"]["douyin"]) != 10 or len(data["works"]["wechat"]) != 10:
        fail("双平台作品榜必须各有 10 条")
    if data["experiments"][-1]["axis"] != summary["latestAxis"]:
        fail("最新实验轴与总览不一致")

    attributed = sum(item["value"] for item in wx["playSources"])
    if attributed > wx["plays7d"]:
        fail("视频号可归因来源超过总播放")
    coverage = attributed / wx["plays7d"]
    if coverage < 0.95:
        fail("视频号流量来源覆盖率低于 95%")

    ages = sum(item["value"] for item in wx["audience"]["ages"])
    if not 95 <= ages <= 101:
        fail("视频号年龄画像合计异常")

    if HTML_PATH.exists():
        html = HTML_PATH.read_text(encoding="utf-8")
        if "/*__DASHBOARD_DATA__*/" in html:
            fail("生成页面仍含数据占位符")
        external = re.findall(r'(?:src|href)=["\']https?://', html, flags=re.I)
        if external:
            fail("生成页面包含外部资源请求")
        required = ["运营健康罗盘", "近 10 条作品", "第 13 至 22 轴", "数据来源与指标口径"]
        missing = [label for label in required if label not in html]
        if missing:
            fail(f"生成页面缺少关键区块: {', '.join(missing)}")
        collector = IdCollector()
        collector.feed(html)
        duplicates = [key for key, count in Counter(collector.ids).items() if count > 1]
        if duplicates:
            fail(f"生成页面包含重复 ID: {', '.join(duplicates)}")
        if collector.scripts != 1:
            fail(f"生成页面脚本数量异常: {collector.scripts}")

    print(
        "VALIDATION_OK: "
        f"plays={summary['plays7d']}, followers={summary['followers']}, "
        f"wechat_source_coverage={coverage:.1%}, works=10+10, latest_axis={summary['latestAxis']}"
    )


if __name__ == "__main__":
    main()
