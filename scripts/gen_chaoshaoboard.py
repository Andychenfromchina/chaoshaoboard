#!/usr/bin/env python3
"""Generate the self-contained Chaoshao operations dashboard."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "dashboard.json"
OUTPUT_PATH = ROOT / "index.html"


TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0b0e12">
<title>潮少 · 运营大数据看板</title>
<style>
:root{
  --bg:#0b0e12;
  --surface:#11161c;
  --surface-2:#161d24;
  --line:#2b3540;
  --line-strong:#3a4754;
  --text:#eef3f6;
  --muted:#91a0ab;
  --cyan:#52d7e8;
  --green:#67d391;
  --amber:#f3b853;
  --magenta:#e36ea4;
  --red:#ff7a7a;
  --blue:#7aa2ff;
  --panel-radius:8px;
}
*{box-sizing:border-box}
html{background:var(--bg);color-scheme:dark;-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;min-width:320px;min-height:100vh;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;font-size:13px;line-height:1.55;overflow-x:hidden}
button{font:inherit;letter-spacing:0}
.skip-link{position:fixed;left:10px;top:10px;z-index:50;padding:8px 12px;background:var(--text);color:var(--bg);transform:translateY(-150%);border-radius:4px}
.skip-link:focus{transform:translateY(0)}
.shell{width:min(1460px,100%);margin:0 auto;padding:14px}
.topbar{min-height:74px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:center;padding:14px 18px;border:1px solid var(--line-strong);border-top:3px solid var(--cyan);border-radius:var(--panel-radius);background:var(--surface)}
.brand h1{margin:0;font-size:23px;line-height:1.2;font-weight:780;letter-spacing:0}
.brand p{margin:5px 0 0;color:var(--muted);font-size:12px}
.top-meta{display:grid;grid-template-columns:auto auto;gap:7px 16px;align-items:center;text-align:right;color:var(--muted);font-size:11px}
.top-meta strong{color:var(--text);font-size:12px}
.freshness{display:inline-flex;align-items:center;justify-content:flex-end;gap:7px}
.freshness::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 0 3px rgba(103,211,145,.13)}
.clock{font-variant-numeric:tabular-nums;color:var(--cyan)}
.layout{display:grid;grid-template-columns:minmax(260px,3fr) minmax(500px,6fr) minmax(270px,3fr);gap:10px;margin-top:10px;align-items:start}
.column{display:flex;min-width:0;flex-direction:column;gap:10px}
.panel{min-width:0;border:1px solid var(--line);border-radius:var(--panel-radius);background:var(--surface);overflow:hidden}
.panel-head{min-height:48px;display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line)}
.panel-head h2{margin:0;font-size:14px;line-height:1.35;font-weight:730;letter-spacing:0}
.panel-head p{margin:2px 0 0;color:var(--muted);font-size:10px;text-align:right;white-space:nowrap}
.panel-body{padding:14px}
.panel-foot{padding:10px 14px;border-top:1px solid var(--line);color:var(--muted);font-size:10px;line-height:1.6}
.panel-foot strong{color:var(--text)}
.section-label{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 8px;color:var(--muted);font-size:10px}
.section-label strong{color:var(--text);font-size:11px}
.compare-group+.compare-group{margin-top:17px}
.compare-row{display:grid;grid-template-columns:58px minmax(0,1fr) 66px;gap:8px;align-items:center;margin-top:7px}
.compare-name{color:var(--muted);font-size:10px}
.bar-track{position:relative;height:7px;border-radius:3px;background:#202832;overflow:hidden}
.bar-fill{position:absolute;inset:0 auto 0 0;width:0;border-radius:3px;background:var(--cyan);transition:width .7s ease}
.bar-fill.wechat{background:var(--magenta)}
.bar-fill.green{background:var(--green)}
.bar-fill.amber{background:var(--amber)}
.bar-fill.red{background:var(--red)}
.bar-value{text-align:right;font-variant-numeric:tabular-nums;font-size:11px;font-weight:700}
.target-marker{position:absolute;top:-2px;bottom:-2px;width:1px;background:rgba(255,255,255,.7)}
.comparison-callout{margin-top:16px;padding:10px 11px;border-left:3px solid var(--amber);background:rgba(243,184,83,.07);color:#d6dee4;font-size:11px}
.profile-rings{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}
.ring-wrap{text-align:center}
.ring{--p:50;--ring-color:var(--cyan);position:relative;width:94px;height:94px;margin:0 auto;border-radius:50%;background:conic-gradient(var(--ring-color) calc(var(--p)*1%),#26303a 0)}
.ring::after{content:"";position:absolute;inset:10px;border-radius:50%;background:var(--surface)}
.ring-value{position:absolute;inset:0;z-index:1;display:grid;place-items:center;font-size:17px;font-weight:800;font-variant-numeric:tabular-nums}
.ring-label{margin-top:6px;color:var(--muted);font-size:10px}
.dist-list{display:grid;gap:7px}
.dist-row{display:grid;grid-template-columns:68px minmax(0,1fr) 48px;gap:7px;align-items:center}
.dist-label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--muted);font-size:10px}
.dist-value{text-align:right;font-size:10px;font-variant-numeric:tabular-nums}
.stack{display:flex;width:100%;height:10px;margin:11px 0 7px;border-radius:3px;overflow:hidden;background:#202832}
.stack span{min-width:1px;height:100%}
.stack-legend{display:flex;flex-wrap:wrap;gap:5px 10px;color:var(--muted);font-size:9px}
.stack-legend i{display:inline-block;width:6px;height:6px;margin-right:4px;border-radius:1px}
.health-panel{min-height:500px}
.tabs{display:flex;gap:4px;padding:10px 14px 0;border-bottom:0}
.tab{min-height:36px;padding:7px 12px;border:1px solid transparent;border-radius:5px;background:transparent;color:var(--muted);cursor:pointer}
.tab:hover{color:var(--text);background:var(--surface-2)}
.tab[aria-selected="true"]{border-color:var(--line-strong);background:var(--surface-2);color:var(--text);box-shadow:inset 0 -2px 0 var(--cyan)}
.tab:focus-visible,summary:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}
.health-content{display:grid;grid-template-columns:230px minmax(0,1fr);gap:18px;padding:14px}
.gauge-box{display:flex;min-height:218px;flex-direction:column;align-items:center;justify-content:center;border-right:1px solid var(--line)}
.gauge{width:210px;height:125px;overflow:visible}
.gauge-base{fill:none;stroke:#26303a;stroke-width:12;stroke-linecap:round}
.gauge-arc{fill:none;stroke:var(--cyan);stroke-width:12;stroke-linecap:round;stroke-dasharray:0 251.2;transition:stroke-dasharray .7s ease,stroke .25s ease}
.gauge-needle{stroke:var(--text);stroke-width:2;stroke-linecap:round;transform-origin:100px 105px;transform:rotate(-90deg);transition:transform .7s ease}
.gauge-pin{fill:var(--text)}
.gauge-score{margin-top:-14px;font-size:34px;line-height:1;font-weight:850;font-variant-numeric:tabular-nums}
.gauge-label{margin-top:7px;text-align:center;color:var(--muted);font-size:10px}
.gauge-formula{margin-top:5px;max-width:210px;text-align:center;color:#6f7d87;font-size:9px}
.kpi-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.kpi{position:relative;min-height:93px;padding:12px;border:1px solid var(--line);border-radius:6px;background:var(--surface-2);overflow:hidden}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--cyan)}
.kpi[data-tone="green"]::before{background:var(--green)}
.kpi[data-tone="amber"]::before{background:var(--amber)}
.kpi[data-tone="magenta"]::before{background:var(--magenta)}
.kpi[data-tone="red"]::before{background:var(--red)}
.kpi-label{color:var(--muted);font-size:10px}
.kpi-value{margin-top:6px;font-size:21px;line-height:1;font-weight:800;font-variant-numeric:tabular-nums}
.kpi-detail{margin-top:8px;color:#aab5bd;font-size:9px;line-height:1.45}
.diagnosis{grid-column:1/-1;margin-top:3px;padding:10px 11px;border-left:3px solid var(--cyan);background:rgba(82,215,232,.07);font-size:11px;color:#d7e0e5}
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.chart-box{min-width:0;padding:10px;border:1px solid var(--line);border-radius:6px;background:var(--surface-2)}
.chart-title{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:6px;color:var(--muted);font-size:9px}
.chart-title strong{color:var(--text);font-size:11px}
.line-chart{width:100%;height:150px;display:block}
.chart-gridline{stroke:#2b3540;stroke-width:1}
.chart-line{fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.chart-area{opacity:.08}
.chart-dot{stroke:var(--surface-2);stroke-width:2}
.chart-axis-label{fill:#77858f;font-size:9px}
.retention-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.signal{padding:10px;border:1px solid var(--line);border-radius:6px;background:var(--surface-2)}
.signal-head{display:flex;justify-content:space-between;gap:8px;margin-bottom:8px;font-size:10px}
.signal-head span{color:var(--muted)}
.signal-head b{font-variant-numeric:tabular-nums}
.signal small{display:block;margin-top:6px;color:#77858f;font-size:9px}
.source-tabs{display:flex;gap:4px;margin-bottom:12px}
.source-tab{min-height:34px;flex:1;border:1px solid var(--line);border-radius:5px;background:transparent;color:var(--muted);cursor:pointer}
.source-tab[aria-pressed="true"]{background:var(--surface-2);color:var(--text);border-color:var(--magenta)}
.source-note{margin-top:12px;color:var(--muted);font-size:10px;line-height:1.6}
.works-panel{min-height:1010px}
.works-summary{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
.works-summary div{padding:9px;border:1px solid var(--line);border-radius:6px;background:var(--surface-2)}
.works-summary span{display:block;color:var(--muted);font-size:9px}
.works-summary strong{display:block;margin-top:3px;font-size:16px;font-variant-numeric:tabular-nums}
.works-list{display:grid;gap:8px}
.work-row{display:grid;grid-template-columns:23px minmax(0,1fr);gap:8px;align-items:start;padding-bottom:8px;border-bottom:1px solid rgba(43,53,64,.75)}
.work-row:last-child{border-bottom:0}
.rank{width:23px;height:23px;display:grid;place-items:center;border-radius:4px;background:#222b34;color:var(--muted);font-size:9px;font-weight:800}
.work-row:nth-child(1) .rank{background:rgba(243,184,83,.15);color:var(--amber)}
.work-title{display:flex;align-items:flex-start;justify-content:space-between;gap:6px;color:#dce4e9;font-size:10px;line-height:1.45}
.work-title span:first-child{min-width:0}
.status{flex:0 0 auto;padding:1px 5px;border:1px solid var(--line);border-radius:4px;color:var(--muted);font-size:8px}
.status.pending{border-color:rgba(243,184,83,.5);color:var(--amber)}
.work-bar{height:5px;margin-top:5px;border-radius:2px;background:#202832;overflow:hidden}
.work-bar span{display:block;width:0;height:100%;border-radius:2px;background:var(--magenta);transition:width .7s ease}
.work-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:5px;color:#78858e;font-size:8px}
.work-meta b{color:var(--text);font-size:10px;font-variant-numeric:tabular-nums}
.full-width{margin-top:10px}
.experiment-body{padding:14px}
.experiment-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.experiment-row{display:grid;grid-template-columns:92px minmax(0,1fr) 70px;gap:8px;align-items:center;padding:9px 10px;border:1px solid var(--line);border-radius:6px;background:var(--surface-2)}
.experiment-row.latest{border-color:rgba(243,184,83,.65);background:rgba(243,184,83,.06)}
.experiment-label strong{display:block;font-size:10px}
.experiment-label span{display:block;margin-top:2px;color:var(--muted);font-size:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dual-bars{display:grid;gap:5px}
.dual-bar{display:grid;grid-template-columns:14px minmax(0,1fr);gap:5px;align-items:center}
.dual-bar em{font-style:normal;color:var(--muted);font-size:8px}
.dual-bar div{height:5px;border-radius:2px;background:#202832;overflow:hidden}
.dual-bar span{display:block;width:0;height:100%;background:var(--cyan);transition:width .7s ease}
.dual-bar.wechat span{background:var(--magenta)}
.experiment-result{text-align:right;color:var(--muted);font-size:8px;line-height:1.45}
.experiment-result b{display:block;color:var(--text);font-size:9px;font-variant-numeric:tabular-nums}
.strategy-band{margin-top:10px;border-top:3px solid var(--amber)}
.strategy-line{padding:13px 15px;border-bottom:1px solid var(--line);font-size:12px;line-height:1.65}
.strategy-line strong{color:var(--amber)}
.strategy-grid{display:grid;grid-template-columns:repeat(3,1fr)}
.strategy-col{min-width:0;padding:14px 15px;border-right:1px solid var(--line)}
.strategy-col:last-child{border-right:0}
.strategy-col h3{margin:0 0 9px;font-size:11px}
.strategy-col ul{margin:0;padding-left:17px;color:#c6d0d6;font-size:10px;line-height:1.65}
.strategy-col li+li{margin-top:5px}
.strategy-col.wins h3{color:var(--green)}
.strategy-col.risks h3{color:var(--red)}
.strategy-col.actions h3{color:var(--cyan)}
.method{border-top:1px solid var(--line)}
.method summary{padding:11px 15px;cursor:pointer;color:var(--muted);font-size:10px}
.method-content{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:0 15px 14px;color:var(--muted);font-size:9px}
.method-content h4{margin:0 0 5px;color:var(--text);font-size:10px}
.method-content dl{margin:0}
.method-content dt{margin-top:6px;color:#c3cdd3}
.method-content dd{margin:1px 0 0}
.sources{display:grid;gap:5px}
.footer{padding:13px 4px 4px;text-align:center;color:#66747e;font-size:9px}
.noscript{margin:10px;padding:14px;border:1px solid var(--red);color:var(--text)}
@media (max-width:1180px){
  .layout{grid-template-columns:minmax(250px,4fr) minmax(430px,8fr)}
  .right-col{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;align-items:start}
  .works-panel{min-height:0}
}
@media (max-width:820px){
  .shell{padding:max(8px,env(safe-area-inset-top)) max(8px,env(safe-area-inset-right)) max(12px,env(safe-area-inset-bottom)) max(8px,env(safe-area-inset-left))}
  .topbar{grid-template-columns:1fr;padding:13px 14px}
  .top-meta{grid-template-columns:1fr auto;text-align:left}
  .freshness{justify-content:flex-start}
  .layout{display:flex;flex-direction:column}
  .center-col{order:1}.left-col{order:2}.right-col{order:3}
  .right-col{display:flex}
  .tab,.source-tab{min-height:44px}
  .health-content{grid-template-columns:1fr}
  .gauge-box{border-right:0;border-bottom:1px solid var(--line);padding-bottom:14px}
  .works-panel{min-height:0}
  .experiment-grid{grid-template-columns:1fr}
  .strategy-grid{grid-template-columns:1fr}
  .strategy-col{border-right:0;border-bottom:1px solid var(--line)}
  .strategy-col:last-child{border-bottom:0}
  .method-content{grid-template-columns:1fr}
}
@media (max-width:520px){
  .brand h1{font-size:19px}
  .panel-head{align-items:flex-start}
  .panel-head p{white-space:normal;max-width:120px}
  .tabs{display:grid;grid-template-columns:repeat(3,1fr)}
  .tab{padding:7px 4px}
  .kpi-grid,.chart-grid,.retention-grid,.profile-rings{grid-template-columns:1fr 1fr}
  .kpi{min-height:103px}
  .ring{width:86px;height:86px}
  .experiment-row{grid-template-columns:82px minmax(0,1fr) 60px}
  .works-summary{grid-template-columns:1fr 1fr}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}
}
</style>
</head>
<body>
<a class="skip-link" href="#dashboard">跳到数据总览</a>
<div class="shell">
  <header class="topbar">
    <div class="brand">
      <h1 id="brandTitle">百商AI新媒体运营飞轮</h1>
      <p id="brandSubtitle">广州潮少 · 抖音 / 视频号 · 运营大数据看板</p>
    </div>
    <div class="top-meta" aria-label="数据状态">
      <span>统计周期</span><strong id="period">--</strong>
      <span class="freshness">静态快照</span><strong id="freshness">--</strong>
      <span>版本</span><strong id="version">--</strong>
      <span>本地时间</span><strong class="clock" id="clock">--:--:--</strong>
    </div>
  </header>

  <main id="dashboard" class="layout">
    <div class="column left-col">
      <section class="panel" aria-labelledby="compareTitle">
        <div class="panel-head">
          <div><h2 id="compareTitle">双平台 · 数据对比</h2></div>
          <p>账号层 7 日快照</p>
        </div>
        <div class="panel-body" id="comparison"></div>
        <div class="panel-foot"><strong>读法：</strong>播放、粉丝、净增按组内最大值归一；互动率使用 0–2% 工作刻度，平台口径不同，不做简单合并。</div>
      </section>

      <section class="panel" aria-labelledby="audienceTitle">
        <div class="panel-head">
          <div><h2 id="audienceTitle">视频号 · 核心受众</h2></div>
          <p id="audienceSample">画像样本 --</p>
        </div>
        <div class="panel-body">
          <div class="profile-rings" id="profileRings"></div>
          <div class="section-label"><strong>年龄分布</strong><span>占画像样本</span></div>
          <div class="dist-list" id="ageDistribution"></div>
          <div class="section-label" style="margin-top:16px"><strong>关注来源</strong><span>共 1,223 人</span></div>
          <div class="stack" id="fanSourceStack" aria-label="视频号关注来源构成"></div>
          <div class="stack-legend" id="fanSourceLegend"></div>
        </div>
        <div class="panel-foot"><strong>受众判断：</strong>50 岁以上占 78.9%，男性占 56.7%。题材需要熟悉的体育事件、清楚的动作因果和直接选择题。</div>
      </section>
    </div>

    <div class="column center-col">
      <section class="panel health-panel" aria-labelledby="healthTitle">
        <div class="panel-head">
          <div><h2 id="healthTitle">运营健康罗盘 · 平台下钻</h2></div>
          <p>内部工作指数，非平台评分</p>
        </div>
        <div class="tabs" role="tablist" aria-label="平台切换">
          <button class="tab" id="tab-overview" role="tab" aria-selected="true" aria-controls="healthView" data-health="overview">总览</button>
          <button class="tab" id="tab-douyin" role="tab" aria-selected="false" aria-controls="healthView" data-health="douyin">抖音</button>
          <button class="tab" id="tab-wechat" role="tab" aria-selected="false" aria-controls="healthView" data-health="wechat">视频号</button>
        </div>
        <div class="health-content" id="healthView" role="tabpanel" aria-live="polite">
          <div class="gauge-box">
            <svg class="gauge" viewBox="0 0 200 120" role="img" aria-labelledby="gaugeSvgTitle gaugeSvgDesc">
              <title id="gaugeSvgTitle">飞轮健康指数</title>
              <desc id="gaugeSvgDesc">当前指数 53 分</desc>
              <path class="gauge-base" d="M20 105 A80 80 0 0 1 180 105"></path>
              <path class="gauge-arc" id="gaugeArc" d="M20 105 A80 80 0 0 1 180 105"></path>
              <line class="gauge-needle" id="gaugeNeedle" x1="100" y1="105" x2="100" y2="47"></line>
              <circle class="gauge-pin" cx="100" cy="105" r="5"></circle>
            </svg>
            <div class="gauge-score" id="gaugeScore">53</div>
            <div class="gauge-label" id="gaugeLabel">双平台飞轮健康指数</div>
            <div class="gauge-formula" id="gaugeFormula"></div>
          </div>
          <div class="kpi-grid" id="healthKpis"></div>
          <div class="diagnosis" id="healthDiagnosis"></div>
        </div>
      </section>

      <section class="panel" aria-labelledby="trendTitle">
        <div class="panel-head">
          <div><h2 id="trendTitle">抖音 · 触达与留存趋势</h2></div>
          <p>每日滚动 7 日口径</p>
        </div>
        <div class="panel-body">
          <div class="chart-grid">
            <div class="chart-box">
              <div class="chart-title"><strong>7 日播放</strong><span>41.3k → 39.3k</span></div>
              <svg class="line-chart" id="playsChart" role="img" aria-label="抖音七日播放趋势"></svg>
            </div>
            <div class="chart-box">
              <div class="chart-title"><strong>粉丝总量</strong><span>1,241 → 1,302</span></div>
              <svg class="line-chart" id="followersChart" role="img" aria-label="抖音粉丝趋势"></svg>
            </div>
          </div>
          <div class="retention-grid" id="retentionSignals"></div>
        </div>
        <div class="panel-foot"><strong>关键变化：</strong>08-06 起互动率升至 1.7% 以上，但完播率从 17.90% 降到 14.26%。增长与互动改善没有同步修复留存。</div>
      </section>

      <section class="panel" aria-labelledby="sourceTitle">
        <div class="panel-head">
          <div><h2 id="sourceTitle">分发来源 · 内容画像</h2></div>
          <p>平台差异诊断</p>
        </div>
        <div class="panel-body">
          <div class="source-tabs" aria-label="来源视图">
            <button class="source-tab" data-source-view="wechat" aria-pressed="true">视频号流量来源</button>
            <button class="source-tab" data-source-view="douyin" aria-pressed="false">抖音兴趣分布</button>
          </div>
          <div class="dist-list" id="sourceDistribution"></div>
          <p class="source-note" id="sourceNote"></p>
        </div>
      </section>
    </div>

    <div class="column right-col">
      <section class="panel works-panel" aria-labelledby="worksTitle">
        <div class="panel-head">
          <div><h2 id="worksTitle">近 10 条作品 · 平台榜</h2></div>
          <p>条宽使用平方根刻度</p>
        </div>
        <div class="tabs" role="tablist" aria-label="作品平台切换">
          <button class="tab works-tab" role="tab" aria-selected="true" data-works="wechat">视频号</button>
          <button class="tab works-tab" role="tab" aria-selected="false" data-works="douyin">抖音</button>
        </div>
        <div class="panel-body">
          <div class="works-summary" id="worksSummary"></div>
          <div class="works-list" id="worksList" aria-live="polite"></div>
        </div>
        <div class="panel-foot" id="worksNote"></div>
      </section>
    </div>
  </main>

  <section class="panel full-width" aria-labelledby="experimentTitle">
    <div class="panel-head">
      <div><h2 id="experimentTitle">运营飞轮 · 第 13 至 22 轴连续实验</h2></div>
      <p>双平台播放，平方根刻度</p>
    </div>
    <div class="experiment-body">
      <div class="experiment-grid" id="experimentGrid"></div>
    </div>
    <div class="panel-foot"><strong>当前判断：</strong>即时事件在抖音侧更容易获得点击，但无法保证视频号同步放量；小白动作是叙事条件，不是独立的分发充分条件。第 22 轴只记录上线，不提前写效果结论。</div>
  </section>

  <section class="panel strategy-band" aria-labelledby="strategyTitle">
    <div class="strategy-line"><strong id="strategyTitle">一句话策略：</strong><span id="strategyLine"></span></div>
    <div class="strategy-grid">
      <div class="strategy-col wins"><h3>本周期有效信号</h3><ul id="wins"></ul></div>
      <div class="strategy-col risks"><h3>当前风险</h3><ul id="risks"></ul></div>
      <div class="strategy-col actions"><h3>下一步行动</h3><ul id="actions"></ul></div>
    </div>
    <details class="method">
      <summary>数据来源与指标口径</summary>
      <div class="method-content">
        <div><h4>指标定义</h4><dl id="definitions"></dl></div>
        <div><h4>来源与新鲜度</h4><div class="sources" id="sources"></div></div>
      </div>
    </details>
  </section>

  <footer class="footer" id="footerText"></footer>
</div>
<noscript><p class="noscript">看板需要 JavaScript 渲染图表；账号快照：双平台 7 日播放 56,416，粉丝 2,525，近 7 日净增 62。</p></noscript>
<script>
"use strict";
const DATA = /*__DASHBOARD_DATA__*/;
const COLORS = ["#52d7e8","#e36ea4","#f3b853","#67d391","#7aa2ff","#ff7a7a"];
const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => Array.from(root.querySelectorAll(selector));
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const fmt = (value) => Number(value).toLocaleString("zh-CN");

function setMeta(){
  $("#brandTitle").textContent = DATA.meta.brand;
  $("#brandSubtitle").textContent = `${DATA.meta.account} · ${DATA.meta.subtitle}`;
  $("#period").textContent = DATA.meta.period;
  $("#freshness").textContent = DATA.meta.generatedAt.slice(5,16).replace("T"," ");
  $("#version").textContent = `v${DATA.meta.version}`;
  $("#footerText").textContent = `${DATA.meta.account} · ${DATA.meta.subtitle} · ${DATA.meta.period} · 静态快照，无账号凭证`;
  const tick = () => $("#clock").textContent = new Date().toLocaleTimeString("zh-CN",{hour12:false});
  tick(); setInterval(tick,1000);
}

function addBarRow(root, label, value, width, className="", marker=null){
  const row = el("div","compare-row");
  row.append(el("span","compare-name",label));
  const track = el("div","bar-track");
  const fill = el("span",`bar-fill ${className}`.trim());
  fill.dataset.width = Math.max(0,Math.min(100,width));
  track.append(fill);
  if(marker !== null){const m=el("i","target-marker");m.style.left=`${marker}%`;track.append(m)}
  row.append(track,el("span","bar-value",value));
  root.append(row);
}

function renderComparison(){
  const root = $("#comparison");
  const dy = DATA.platforms.douyin, wx = DATA.platforms.wechat;
  const groups = [
    {title:"7 日播放",note:`抖音为视频号 ${DATA.summary.douyinToWechatPlayRatio.toFixed(2)}×`,rows:[["抖音",fmt(dy.plays7d),100,""],["视频号",fmt(wx.plays7d),wx.plays7d/dy.plays7d*100,"wechat"]]},
    {title:"粉丝规模",note:`合计 ${fmt(DATA.summary.followers)}`,rows:[["抖音",fmt(dy.followers),100,""],["视频号",fmt(wx.followers),wx.followers/dy.followers*100,"wechat"]]},
    {title:"7 日净增粉",note:"增长集中在抖音",rows:[["抖音",`+${dy.netFollowers7d}`,100,"green"],["视频号",String(wx.netFollowers7d),0,"wechat"]]},
    {title:"互动率",note:"工作健康线 2%",marker:100,rows:[["抖音",`${dy.interactionRate}%`,dy.interactionRate/2*100,"amber"],["视频号",`${wx.interactionRate}%`,wx.interactionRate/2*100,"wechat"]]}
  ];
  groups.forEach(group=>{
    const section=el("div","compare-group");
    const head=el("div","section-label");head.append(el("strong","",group.title),el("span","",group.note));section.append(head);
    group.rows.forEach(row=>addBarRow(section,...row,group.marker ?? null));root.append(section);
  });
  const callout=el("div","comparison-callout",`双平台 7 日播放 ${fmt(DATA.summary.plays7d)}，抖音占 69.7%；净增粉合计 +${DATA.summary.netFollowers7d}。当前首要矛盾不是触达规模，而是留存与跨平台复制。`);
  root.append(callout);
}

function renderAudience(){
  const audience=DATA.platforms.wechat.audience;
  $("#audienceSample").textContent=`画像样本 ${fmt(audience.sample)}`;
  const rings=$("#profileRings");
  [["50 岁以上",audience.ages[0].value,"var(--magenta)"],["男性",audience.male,"var(--cyan)"]].forEach(item=>{
    const wrap=el("div","ring-wrap");
    const ring=el("div","ring");ring.style.setProperty("--p",item[1]);ring.style.setProperty("--ring-color",item[2]);
    ring.append(el("span","ring-value",`${item[1]}%`));wrap.append(ring,el("div","ring-label",item[0]));rings.append(wrap);
  });
  const ages=$("#ageDistribution"), max=audience.ages[0].value;
  audience.ages.forEach((item,index)=>{
    const row=el("div","dist-row");row.append(el("span","dist-label",item.label));
    const track=el("div","bar-track");const fill=el("span",`bar-fill ${index===0?"wechat":""}`);fill.dataset.width=item.value/max*100;track.append(fill);
    row.append(track,el("span","dist-value",`${item.value}%`));ages.append(row);
  });
  const source=DATA.platforms.wechat.fanSources,total=source.reduce((sum,item)=>sum+item.value,0);
  source.forEach((item,index)=>{
    const seg=el("span");seg.style.width=`${item.value/total*100}%`;seg.style.background=COLORS[index%COLORS.length];seg.title=`${item.label} ${fmt(item.value)}`;$("#fanSourceStack").append(seg);
    const lab=el("span");const dot=el("i");dot.style.background=COLORS[index%COLORS.length];lab.append(dot,document.createTextNode(`${item.label} ${Math.round(item.value/total*1000)/10}%`));$("#fanSourceLegend").append(lab);
  });
}

function renderHealth(key){
  const data=DATA.health[key],score=data.score;
  $$("[data-health]").forEach(tab=>tab.setAttribute("aria-selected",String(tab.dataset.health===key)));
  $("#healthView").setAttribute("aria-labelledby",`tab-${key}`);
  $("#gaugeScore").textContent=score;
  $("#gaugeLabel").textContent=data.label;
  $("#gaugeFormula").textContent=data.formula;
  $("#gaugeSvgDesc").textContent=`当前指数 ${score} 分`;
  $("#gaugeArc").style.strokeDasharray=`${score*2.512} 251.2`;
  $("#gaugeArc").style.stroke=score>=65?"var(--green)":score>=45?"var(--amber)":"var(--red)";
  $("#gaugeNeedle").style.transform=`rotate(${-90+score*1.8}deg)`;
  const root=$("#healthKpis");root.textContent="";
  data.kpis.forEach(item=>{const card=el("div","kpi");card.dataset.tone=item.tone;card.append(el("div","kpi-label",item.label),el("div","kpi-value",item.value),el("div","kpi-detail",item.detail));root.append(card)});
  $("#healthDiagnosis").textContent=data.diagnosis;
}

function enableArrowTabs(selector,attribute,callback){
  const tabs=$$(selector);
  tabs.forEach((tab,index)=>{
    tab.addEventListener("click",()=>callback(tab.dataset[attribute]));
    tab.addEventListener("keydown",event=>{
      if(!["ArrowLeft","ArrowRight"].includes(event.key))return;
      event.preventDefault();const next=(index+(event.key==="ArrowRight"?1:-1)+tabs.length)%tabs.length;tabs[next].focus();tabs[next].click();
    });
  });
}

function renderLineChart(id,values,labels,color,formatter){
  const svg=$(id),NS="http://www.w3.org/2000/svg",W=420,H=150,pad={l:12,r:12,t:12,b:24};
  svg.setAttribute("viewBox",`0 0 ${W} ${H}`);svg.textContent="";
  const min=Math.min(...values),max=Math.max(...values),range=Math.max(1,max-min);
  const x=i=>pad.l+i*(W-pad.l-pad.r)/(values.length-1),y=v=>pad.t+(max-v)/range*(H-pad.t-pad.b);
  [0,.5,1].forEach(f=>{const line=document.createElementNS(NS,"line");line.setAttribute("x1",pad.l);line.setAttribute("x2",W-pad.r);line.setAttribute("y1",pad.t+f*(H-pad.t-pad.b));line.setAttribute("y2",pad.t+f*(H-pad.t-pad.b));line.setAttribute("class","chart-gridline");svg.append(line)});
  const points=values.map((v,i)=>`${x(i)},${y(v)}`).join(" ");
  const area=document.createElementNS(NS,"polygon");area.setAttribute("points",`${pad.l},${H-pad.b} ${points} ${W-pad.r},${H-pad.b}`);area.setAttribute("fill",color);area.setAttribute("class","chart-area");svg.append(area);
  const line=document.createElementNS(NS,"polyline");line.setAttribute("points",points);line.setAttribute("stroke",color);line.setAttribute("class","chart-line");svg.append(line);
  values.forEach((value,index)=>{const circle=document.createElementNS(NS,"circle");circle.setAttribute("cx",x(index));circle.setAttribute("cy",y(value));circle.setAttribute("r",3.5);circle.setAttribute("fill",color);circle.setAttribute("class","chart-dot");const title=document.createElementNS(NS,"title");title.textContent=`${labels[index]} ${formatter(value)}`;circle.append(title);svg.append(circle)});
  [0,labels.length-1].forEach(index=>{const text=document.createElementNS(NS,"text");text.setAttribute("x",x(index));text.setAttribute("y",H-6);text.setAttribute("text-anchor",index===0?"start":"end");text.setAttribute("class","chart-axis-label");text.textContent=labels[index];svg.append(text)});
  const top=document.createElementNS(NS,"text");top.setAttribute("x",W-pad.r);top.setAttribute("y",10);top.setAttribute("text-anchor","end");top.setAttribute("class","chart-axis-label");top.textContent=formatter(max);svg.append(top);
}

function renderSignals(){
  const ct=DATA.platforms.douyin.content;
  const signals=[
    {label:"整体完播率",value:DATA.platforms.douyin.finishRate,target:25,unit:"%",tone:"red",note:"工作目标 25%"},
    {label:"5 秒完播率",value:ct.finish5s,target:55,unit:"%",tone:"amber",note:"工作目标 55%"},
    {label:"互动率",value:DATA.platforms.douyin.interactionRate,target:2,unit:"%",tone:"green",note:"距目标 0.24pp"},
    {label:"2 秒跳出率",value:ct.bounce2s,target:20,unit:"%",tone:"red",note:"低于 20% 为工作目标"}
  ];
  const root=$("#retentionSignals");
  signals.forEach(s=>{const box=el("div","signal");const head=el("div","signal-head");head.append(el("span","",s.label),el("b","",`${s.value}${s.unit}`));const track=el("div","bar-track");const fill=el("span",`bar-fill ${s.tone}`);fill.dataset.width=Math.min(100,s.value/s.target*100);track.append(fill);box.append(head,track,el("small","",s.note));root.append(box)});
}

function renderSourceView(key){
  $$("[data-source-view]").forEach(btn=>btn.setAttribute("aria-pressed",String(btn.dataset.sourceView===key)));
  const root=$("#sourceDistribution");root.textContent="";
  const isWechat=key==="wechat";
  const items=isWechat?DATA.platforms.wechat.playSources:DATA.platforms.douyin.interest;
  const max=Math.max(...items.map(i=>i.value));
  items.forEach((item,index)=>{const row=el("div","dist-row");row.append(el("span","dist-label",item.label));const track=el("div","bar-track");const fill=el("span",`bar-fill ${isWechat?"wechat":index===0?"amber":""}`.trim());fill.dataset.width=item.value/max*100;track.append(fill);row.append(track,el("span","dist-value",isWechat?fmt(item.value):`${item.value}%`));root.append(row)});
  $("#sourceNote").textContent=isWechat?"视频号可归因播放 17,102，占总播放 99.9%；推荐流 16,583，占总播放 96.9%。":"抖音兴趣前三为随拍、剧情、亲子，合计 72%；体育热点通过生活判断进入泛兴趣流量池。";
  requestAnimationFrame(animateBars);
}

function renderWorks(platform){
  $$("[data-works]").forEach(tab=>tab.setAttribute("aria-selected",String(tab.dataset.works===platform)));
  const works=DATA.works[platform],max=Math.max(...works.map(w=>w.plays),1),total=works.reduce((sum,w)=>sum+w.plays,0);
  const summary=$("#worksSummary");summary.textContent="";
  const platformData=DATA.platforms[platform];
  [["近 10 条播放",fmt(total)],["账号 7 日播放",fmt(platformData.plays7d)]].forEach(item=>{const box=el("div");box.append(el("span","",item[0]),el("strong","",item[1]));summary.append(box)});
  const root=$("#worksList");root.textContent="";
  works.forEach((work,index)=>{
    const row=el("div","work-row");row.append(el("span","rank",String(index+1)));
    const body=el("div");const title=el("div","work-title");title.append(el("span","",`第 ${work.axis} 轴 · ${work.title}`));
    const status=el("span",`status ${/中|审核/.test(work.status)?"pending":""}`.trim(),work.status);title.append(status);
    const bar=el("div","work-bar");const fill=el("span");fill.dataset.width=Math.sqrt(work.plays/max)*100;bar.append(fill);
    const meta=el("div","work-meta");const interactions=(work.likes||0)+(work.comments||0)+(work.shares||0)+(work.favorites||0);meta.append(el("span","",`${work.date} · 互动 ${fmt(interactions)}`),el("b","",`${fmt(work.plays)} 播放`));
    body.append(title,bar,meta);row.append(body);root.append(row);
  });
  const share=platformData.plays7d?total/platformData.plays7d*100:0;
  $("#worksNote").textContent=`近 10 条合计 ${fmt(total)} 播放，占账号 7 日播放 ${share.toFixed(1)}%。审核中或处理中作品按 0 记录，不参与效果判断。`;
  requestAnimationFrame(animateBars);
}

function renderExperiments(){
  const root=$("#experimentGrid"),max=Math.max(...DATA.experiments.flatMap(item=>[item.douyin,item.wechat]),1);
  DATA.experiments.forEach(item=>{
    const row=el("div",`experiment-row ${item.axis===DATA.summary.latestAxis?"latest":""}`.trim());
    const label=el("div","experiment-label");label.append(el("strong","",`第 ${item.axis} 轴 · ${item.name}`),el("span","",item.topic));
    const bars=el("div","dual-bars");
    [["抖",item.douyin,""],["号",item.wechat,"wechat"]].forEach(b=>{const line=el("div",`dual-bar ${b[2]}`.trim());line.append(el("em","",b[0]));const track=el("div");const fill=el("span");fill.dataset.width=Math.sqrt(b[1]/max)*100;track.append(fill);line.append(track);bars.append(line)});
    const result=el("div","experiment-result");result.append(el("b","",`${fmt(item.douyin)} / ${fmt(item.wechat)}`),document.createTextNode(item.result));
    row.append(label,bars,result);root.append(row);
  });
}

function renderStrategy(){
  $("#strategyLine").textContent=`${DATA.strategy.oneLine}（当前信心 ${DATA.strategy.confidence}）`;
  [["wins",DATA.strategy.wins],["risks",DATA.strategy.risks],["actions",DATA.strategy.actions]].forEach(([id,items])=>{const root=$(`#${id}`);items.forEach(item=>root.append(el("li","",item)))});
  const defs=$("#definitions");DATA.definitions.forEach(item=>{defs.append(el("dt","",item.metric),el("dd","",item.definition))});
  const sources=$("#sources");DATA.sources.forEach(item=>{const row=el("div");row.append(el("strong","",item.label),document.createTextNode(` · ${item.freshness} · ${item.coverage}`));sources.append(row)});
}

function animateBars(){
  $$('[data-width]').forEach(node=>{const target=node.dataset.width;node.style.width="0";requestAnimationFrame(()=>node.style.width=`${target}%`)});
}

function init(){
  setMeta();renderComparison();renderAudience();renderHealth("overview");
  renderLineChart("#playsChart",DATA.trends.douyinPlays7d,DATA.trends.labels,"#52d7e8",v=>`${(v/1000).toFixed(1)}k`);
  renderLineChart("#followersChart",DATA.trends.douyinFollowers,DATA.trends.labels,"#67d391",v=>fmt(v));
  renderSignals();renderSourceView("wechat");renderWorks("wechat");renderExperiments();renderStrategy();
  enableArrowTabs("[data-health]","health",renderHealth);
  enableArrowTabs("[data-works]","works",renderWorks);
  $$("[data-source-view]").forEach(btn=>btn.addEventListener("click",()=>renderSourceView(btn.dataset.sourceView)));
  requestAnimationFrame(animateBars);
}
init();
</script>
</body>
</html>
'''


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    output = TEMPLATE.replace("/*__DASHBOARD_DATA__*/", payload)
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"generated {OUTPUT_PATH} ({len(output):,} chars)")


if __name__ == "__main__":
    main()
