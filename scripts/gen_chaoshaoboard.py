#!/usr/bin/env python3
# gen_chaoshaoboard.py — 用大陈 V4 组件规范组装潮少双平台运营飞轮看板。
# 布局 V4(2026-08-07):真实三列 flex 布局,列内卡片按实测内容高度排布、每列最后一张卡拉伸补满。
# 窄屏态由外层页面显式传入 host-mobile,避免窄列 iframe 在桌面端误触发移动断点。
import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'templates' / 'dachen-dashboard-v3.json'
DATA_PATH = ROOT / 'data' / 'dashboard.json'
OUT = ROOT / 'index.html'
DATA = json.loads(DATA_PATH.read_text())
GAP = 10

# 实测内容高度(px)。nh=自然高;列内最后一张卡 flex 拉伸,其余固定 nh。
PLAN = {
    'title':  {'match': '标题栏',  'nh': 68},
    'left':   [{'match': '三平台',  'nh': 492}, {'match': '粉丝画像', 'nh': 476}],
    'center': [{'match': '健康罗盘', 'nh': 578}, {'match': '流量来源', 'nh': 290}],
    'right':  [{'match': '视频号',  'nh': 931}],
    'bottom': {'match': '策略',   'nh': 257},
}
# 桌面端让面板撑满列高；窄屏端由宿主加 html.host-mobile，恢复内容自然高度。
# 不能把宿主断点写在 iframe 内：桌面三列本身也很窄，会误判为移动端。
STRETCH_CSS = ('<style>html,body{height:100%!important;-webkit-text-size-adjust:100%;text-size-adjust:100%}'
               'body{display:flex!important;flex-direction:column!important}'
               'body>:first-child{flex:1 0 auto;display:flow-root}'
               'html.host-mobile,html.host-mobile body{height:auto!important;min-height:0!important;overflow-x:hidden!important}'
               'html.host-mobile body{display:block!important}'
               'html.host-mobile body>:first-child{height:auto!important;min-height:0!important;flex:none!important}'
               'html.host-mobile .panel{height:auto!important;min-height:0!important}'
               'html.host-mobile .tab,html.host-mobile button{min-height:44px}'
               'html.host-mobile .hd h1{white-space:normal!important;line-height:1.35}'
               'html.host-mobile .grp-t{flex-wrap:wrap}'
               'html.host-mobile .strategy{align-items:flex-start!important;flex-wrap:wrap!important}</style>')

# ---- 构建期内容补丁(源 JSON 保持原样) ----

# TOP 榜补丁(2026-07-23 复盘更新):源 JSON 已内嵌当期 8 条真实榜单,旧第 9/10 条(07-19/07-15)已过期,不再注入
TOP_EXTRA_ITEMS = '  </section>'

# 罗盘 KPI 卡片重设计:文字居中、顶部中央光条、径向光晕(覆盖原左侧竖条样式)
SCARD_CSS = ('<style>'
             '.scard{text-align:center;padding:8px 10px 7px;border:1px solid rgba(0,229,255,.3);'
             'border-radius:9px;overflow:hidden;'
             'background:radial-gradient(62% 100% at 50% 0%,rgba(0,229,255,.12),transparent 70%),'
             'linear-gradient(180deg,rgba(0,80,170,.26),rgba(0,40,100,.10));'
             'box-shadow:inset 0 0 14px rgba(0,90,220,.10)}'
             '.scard::before{content:"";position:absolute;top:0;left:50%;transform:translateX(-50%);'
             'width:56%;height:2px;border-radius:2px;'
             'background:linear-gradient(90deg,transparent,#00e5ff,transparent);'
             'box-shadow:0 0 8px rgba(0,229,255,.8)}'
             '.scard::after{content:none}'
             '.sl{display:block;margin:2px 0 1px;letter-spacing:.06em;color:rgba(168,208,240,.78)}'
             '.sv{font-size:16px}'
             '</style>')

# 隐藏各卡片标题栏右上角的 .mt 角标(时间/刻度标示):其定位依赖宿主变量,在本页面全部与标题重叠
HIDE_MT_CSS = '<style>.hd .mt,.mt{display:none!important}</style>'

# 流量来源卡片:面板改纵向 flex、图表区 flex:1 自动长高(柱子为百分比高度,随容器铺满底部空间)
TRAFFIC_CSS = ('<style>'
               '.panel{display:flex!important;flex-direction:column!important;height:100%}'
               '.cols{flex:1;align-items:stretch}'
               '.cols>section{display:flex;flex-direction:column;min-height:0}'
               '.vchart,.duo{flex:1;height:auto;min-height:128px}'
               '.foot{margin-top:auto;padding-top:8px;font-size:9px}'
               '.vval{font-size:9px}.vcats span,.dcats span{font-size:9px}'
               '</style>')

# TOP 榜桌面端随右列增高：把多余高度平均分配给 8 条榜单，不在底部留下空洞。
# 移动端恢复自然内容流，避免列表被强行拉长。
TOP_STRETCH_CSS = ('<style>'
                   '.panel{display:flex!important;flex-direction:column!important;height:100%}'
                   '.panel>section{display:flex;flex:1;flex-direction:column;min-height:0}'
                   '.item{flex:1;align-items:center}.item:last-child{margin-bottom:0}'
                   'html.host-mobile .panel>section{display:block;flex:none}'
                   'html.host-mobile .item{margin-bottom:7px;align-items:flex-start}'
                   '</style>')

# 兜底落位脚本(注入所有组件):渲染时间线被节流时,width/height 过渡可能永远到不了终点
# (2026-07-20 实翻:柱条集体停在 min-width 2px)。1.6s 后强制去过渡、直接定格最终尺寸;
# 流量柱在 flex 容器里百分比基准失效,按容器实高换算 px。
SETTLE_JS = ('<script>setTimeout(function(){'
             'document.querySelectorAll("[data-w]").forEach(function(el){'
             'el.style.transition="none";el.style.width=parseFloat(el.dataset.w)+"%";});'
             'document.querySelectorAll(".vchart,.duo").forEach(function(ch){var H=ch.clientHeight;'
             'ch.querySelectorAll("[data-h]").forEach(function(el){'
             'var lab=el.parentElement.querySelector(".vval");var max=H-(lab?lab.offsetHeight+8:8);'
             'el.style.transition="none";el.style.height=Math.max(2,max*parseFloat(el.dataset.h)/100)+"px";});});'
             '},1600);</script>')

# ---- 全局光线流动动效(2026-07-20,v2 性能重写) ----
# ⚠ 教训(2026-07-20 实翻):v1 用 background-position/box-shadow/filter/border-color 关键帧,
# 全是主线程重绘型动画,98 个叠加把渲染压垮——.bf 宽度过渡时间线冻结,柱条全部消失。
# v2 铁律:动画只准用 transform 和 opacity(合成器线程,零重绘);辉光一律做成静态阴影层+opacity 脉冲。
ANIM_CSS = ('<style>@media (prefers-reduced-motion:no-preference){'
            # 四角准星脉冲(opacity)
            '.cn{animation:cnP 3s ease-in-out infinite}'
            '@keyframes cnP{0%,100%{opacity:.6}50%{opacity:1}}'
            # 卡片标题栏横向扫光(transform)
            '.hd{overflow:hidden}'
            '.hd::after{content:"";position:absolute;top:0;bottom:0;left:0;width:30%;'
            'background:linear-gradient(105deg,transparent,rgba(140,225,255,.15),transparent);'
            'transform:translateX(-140%);animation:hdSweep 5.5s ease-in-out infinite;pointer-events:none}'
            '@keyframes hdSweep{0%{transform:translateX(-140%)}55%,100%{transform:translateX(440%)}}'
            # 横向进度条流光(transform;不动 .bf 的 position——absolute 定位改 relative 会让条塌陷)
            '.bf{overflow:hidden}'
            '.bf::after{content:"";position:absolute;top:0;bottom:0;left:0;width:55%;'
            'background:linear-gradient(100deg,transparent,rgba(255,255,255,.30),transparent);'
            'transform:translateX(-110%);animation:bfX 2.8s linear infinite;pointer-events:none}'
            '@keyframes bfX{0%{transform:translateX(-110%)}100%{transform:translateX(300%)}}'
            # 竖向柱体升腾流光(transform)
            '.vbar,.dbar{position:relative;overflow:hidden}'
            '.vbar::after,.dbar::after{content:"";position:absolute;left:0;right:0;bottom:0;height:45%;'
            'background:linear-gradient(0deg,transparent,rgba(255,255,255,.26),transparent);'
            'transform:translateY(120%);animation:vbY 3.2s linear infinite;pointer-events:none}'
            '@keyframes vbY{0%{transform:translateY(120%)}100%{transform:translateY(-330%)}}'
            # 玻璃 Tab / KPI 卡片斜向扫光(transform,错峰)
            '.tab,.scard{position:relative;overflow:hidden}'
            '.tab::after,.scard::after{content:"";position:absolute;top:-40%;bottom:-40%;left:0;width:24%;'
            'background:linear-gradient(90deg,transparent,rgba(180,235,255,.2),transparent);'
            'transform:translateX(-160%) skewX(-18deg);animation:sheenX 4.8s ease-in-out infinite;pointer-events:none}'
            '@keyframes sheenX{0%{transform:translateX(-160%) skewX(-18deg)}'
            '60%,100%{transform:translateX(560%) skewX(-18deg)}}'
            '.tab:nth-child(2)::after{animation-delay:.6s}.tab:nth-child(3)::after{animation-delay:1.2s}'
            '.tab:nth-child(4)::after{animation-delay:1.8s}'
            '.scard:nth-child(2)::after{animation-delay:.8s}.scard:nth-child(3)::after{animation-delay:1.6s}'
            # 翻牌数字盒霓虹呼吸:静态阴影层 + opacity 脉冲(逐位错峰)
            '.box{position:relative}'
            '.box::after{content:"";position:absolute;inset:-2px;border-radius:6px;pointer-events:none;'
            'box-shadow:0 0 12px rgba(0,229,255,.6);opacity:.15;animation:oP 2.6s ease-in-out infinite}'
            '.box:nth-child(2)::after{animation-delay:.2s}.box:nth-child(3)::after{animation-delay:.4s}'
            '.box:nth-child(4)::after{animation-delay:.6s}.box:nth-child(5)::after{animation-delay:.8s}'
            '.box:nth-child(6)::after{animation-delay:1s}'
            '@keyframes oP{0%,100%{opacity:.15}50%{opacity:1}}'
            # 罗盘表盘/健康分:静态辉光(不做 filter 动画)
            '.compass{filter:drop-shadow(0 0 8px rgba(34,211,238,.35))}'
            # 兴趣圆环:旋转高光弧(transform)
            '.donut{position:relative}'
            '.donut::after{content:"";position:absolute;inset:0;border-radius:50%;pointer-events:none;'
            'background:conic-gradient(from 0deg,transparent 0 72%,rgba(255,255,255,.28) 84%,transparent 96%);'
            '-webkit-mask:radial-gradient(circle,transparent 54%,#000 56% 90%,transparent 92%);'
            'mask:radial-gradient(circle,transparent 54%,#000 56% 90%,transparent 92%);'
            'animation:ringSpin 5.5s linear infinite}'
            '@keyframes ringSpin{to{transform:rotate(360deg)}}'
            '}</style>')

# 标题栏专属(只用 opacity):翼展光线游走、信号点错峰闪烁;标题辉光改静态
TITLE_ANIM_CSS = ('<style>@media (prefers-reduced-motion:no-preference){'
                  '.wing i{animation:wingP 3.2s ease-in-out infinite}'
                  '.wing i:nth-child(2){animation-delay:.4s}.wing i:nth-child(3){animation-delay:.8s}'
                  '@keyframes wingP{0%,100%{opacity:.45}50%{opacity:1}}'
                  '.dots i{animation:dotP 2.2s ease-in-out infinite}'
                  '.dots i:nth-child(2){animation-delay:.4s}.dots i:nth-child(3){animation-delay:.8s}'
                  '@keyframes dotP{0%,100%{opacity:.4}50%{opacity:1}}'
                  '}</style>')

# 标题栏在窄屏改为两行：标题独占首行，更新时间与时钟分列第二行。
TITLE_MOBILE_CSS = ('<style>@media(max-width:760px){'
                    'body{padding:3px 0!important}'
                    '.band{height:auto!important;min-height:92px;grid-template-columns:1fr auto!important;'
                    'grid-template-areas:"title title" "left right";gap:8px 10px!important;padding:11px 13px!important}'
                    '.title{grid-area:title;padding:0 4px!important}.title h1{font-size:18px!important;line-height:1.25!important;white-space:normal!important}'
                    '.title .sub{font-size:9px!important;margin-top:3px!important}.side:first-child{grid-area:left}.side.r{grid-area:right}'
                    '.side{font-size:10px!important}.pill{padding:3px 8px!important}.side .pill.long,.live,.dots{display:none!important}'
                    '.clock{font-size:12px!important}.wing{display:none!important}'
                    '}</style>')

# 健康罗盘在移动端切为单列后，SVG 仍是 block 元素；显式自动外边距让表盘与分数共用中轴线。
HEALTH_MOBILE_CSS = ('<style>@media(max-width:520px){'
                     '.gauge{width:100%;justify-self:stretch}'
                     '.compass{margin-inline:auto}'
                     '}</style>')

# 移动端 iframe 不能沿用桌面设计稿高度。按每个 srcdoc 的首个可视组件实时量高，
# 同时给已发布的旧组件注入移动端自然高度兜底，修复巨幅空白与内容截断。
IFRAME_RESIZE_JS = r'''<script>
(function(){
  "use strict";
  var mq = window.matchMedia("(max-width:1180px)");
  var frames = Array.prototype.slice.call(document.querySelectorAll(".cell iframe"));
  var observers = new Map();
  var genericCss = "html{-webkit-text-size-adjust:100%;text-size-adjust:100%}html.host-mobile,html.host-mobile body{height:auto!important;min-height:0!important;overflow-x:hidden!important}html.host-mobile body{display:block!important}html.host-mobile body>:first-child{height:auto!important;min-height:0!important;flex:none!important}html.host-mobile .panel{height:auto!important;min-height:0!important}html.host-mobile .tab,html.host-mobile button{min-height:44px}html.host-mobile .hd h1{white-space:normal!important;line-height:1.35}html.host-mobile .grp-t{flex-wrap:wrap}html.host-mobile .strategy{align-items:flex-start!important;flex-wrap:wrap!important}";
  var titleCss = "@media(max-width:760px){body{padding:3px 0!important}.band{height:auto!important;min-height:92px;grid-template-columns:1fr auto!important;grid-template-areas:'title title' 'left right';gap:8px 10px!important;padding:11px 13px!important}.title{grid-area:title;padding:0 4px!important}.title h1{font-size:18px!important;line-height:1.25!important;white-space:normal!important}.title .sub{font-size:9px!important;margin-top:3px!important}.side:first-child{grid-area:left}.side.r{grid-area:right}.side{font-size:10px!important}.pill{padding:3px 8px!important}.side .pill.long,.live,.dots{display:none!important}.clock{font-size:12px!important}.wing{display:none!important}}";
  function docOf(frame){ try{return frame.contentDocument;}catch(_){return null;} }
  function inject(frame){
    var doc=docOf(frame); if(!doc||!doc.head) return null;
    doc.documentElement.classList.toggle("host-mobile",mq.matches);
    if(!doc.getElementById("mobile-intrinsic-fix")){
      var style=doc.createElement("style"); style.id="mobile-intrinsic-fix";
      style.textContent=genericCss+(frame.title.indexOf("标题栏")===0?titleCss:"");
      doc.head.appendChild(style);
    }
    return doc;
  }
  function measure(frame){
    var doc=inject(frame); if(!doc||!doc.body) return;
    if(!mq.matches){frame.style.removeProperty("height");frame.parentElement.style.removeProperty("height");return;}
    var first=doc.body.firstElementChild; if(!first) return;
    var cs=doc.defaultView.getComputedStyle(doc.body);
    var pad=(parseFloat(cs.paddingTop)||0)+(parseFloat(cs.paddingBottom)||0);
    var height=Math.ceil(Math.max(first.scrollHeight,first.getBoundingClientRect().height)+pad+1);
    if(height>0&&Math.abs(frame.clientHeight-height)>1){frame.style.height=height+"px";frame.parentElement.style.height=height+"px";}
  }
  function watch(frame){
    var doc=inject(frame); if(!doc||!doc.body) return;
    if(observers.has(frame)) observers.get(frame).disconnect();
    if("ResizeObserver" in window){
      var ro=new ResizeObserver(function(){measure(frame)}); ro.observe(doc.body.firstElementChild||doc.body); observers.set(frame,ro);
    }
    requestAnimationFrame(function(){measure(frame);requestAnimationFrame(function(){measure(frame)})});
    setTimeout(function(){measure(frame)},1700);
  }
  frames.forEach(function(frame){frame.addEventListener("load",function(){watch(frame)});watch(frame)});
  function refresh(){frames.forEach(measure)}
  if(mq.addEventListener) mq.addEventListener("change",refresh); else mq.addListener(refresh);
  window.addEventListener("resize",function(){clearTimeout(window.__boardResizeTimer);window.__boardResizeTimer=setTimeout(refresh,80)},{passive:true});
})();
</script>'''


def n(value):
    return f'{value:,}'


def replace_body(doc, markup):
    head, rest = doc.split('<body>', 1)
    if '<script>' in rest:
        tail = rest[rest.index('<script>'):]
    else:
        tail = rest[rest.index('</body>'):]
    return f'{head}<body>\n{markup.strip()}\n{tail}'


def compare_markup():
    dy, wx, total = DATA['douyin'], DATA['wechat'], DATA['summary']
    return f'''
<div class="panel">
  <i class="cn tl"></i><i class="cn tr"></i><i class="cn bl"></i><i class="cn br"></i>
  <header class="hd"><h1>双平台 · 数据对比</h1><span class="mt">{DATA['meta']['period']}</span></header>
  <section class="grp" aria-label="7日播放对比">
    <div class="grp-t"><span>7日播放 · 双平台占比</span><span>抖音是视频号 2.30×</span></div>
    <div class="brow"><span class="bn"><i class="dot dy"></i>抖音</span><div class="bt"><div class="bf dy" data-w="69.7"></div></div><span class="bv">{n(dy['plays7d'])}</span></div>
    <div class="brow"><span class="bn"><i class="dot sp"></i>视频号</span><div class="bt"><div class="bf sp" data-w="30.3"></div></div><span class="bv">{n(wx['plays7d'])}</span></div>
    <div class="brow"><span class="bn"><i class="dot ks"></i>合计</span><div class="bt"><div class="bf ks" data-w="100"></div></div><span class="bv">{n(total['plays7d'])}</span></div>
  </section>
  <section class="grp" aria-label="粉丝总量对比">
    <div class="grp-t"><span>粉丝总量 · 双平台占比</span></div>
    <div class="brow"><span class="bn"><i class="dot dy"></i>抖音</span><div class="bt"><div class="bf dy" data-w="51.6"></div></div><span class="bv">{n(dy['followers'])}</span></div>
    <div class="brow"><span class="bn"><i class="dot sp"></i>视频号</span><div class="bt"><div class="bf sp" data-w="48.4"></div></div><span class="bv">{n(wx['followers'])}</span></div>
    <div class="brow"><span class="bn"><i class="dot ks"></i>合计</span><div class="bt"><div class="bf ks" data-w="100"></div></div><span class="bv">{n(total['followers'])}</span></div>
  </section>
  <section class="grp" aria-label="7日净增粉对比">
    <div class="grp-t"><span>7日净增粉</span><em>增长集中在抖音</em></div>
    <div class="brow"><span class="bn"><i class="dot dy"></i>抖音</span><div class="bt"><div class="bf dy" data-w="100"></div></div><span class="bv">+{dy['netFollowers7d']}</span></div>
    <div class="brow"><span class="bn"><i class="dot sp"></i>视频号</span><div class="bt"><div class="bf sp" data-w="1"></div></div><span class="bv">{wx['netFollowers7d']}</span></div>
    <div class="brow"><span class="bn"><i class="dot ks"></i>合计</span><div class="bt"><div class="bf ks" data-w="100"></div></div><span class="bv">+{total['netFollowers7d']}</span></div>
  </section>
  <section class="grp" aria-label="互动率对比">
    <div class="grp-t"><span>互动率 · 绝对刻度 0~2%</span><em>健康线 2%</em></div>
    <div class="brow"><span class="bn"><i class="dot dy"></i>抖音</span><div class="bt"><div class="bf dy" data-w="88"></div><span class="baseline" style="left:100%"><em>2%</em></span></div><span class="bv">{dy['interactionRate']:.2f}%</span></div>
    <div class="brow"><span class="bn"><i class="dot sp"></i>视频号</span><div class="bt"><div class="bf sp" data-w="2"></div></div><span class="bv">{wx['interactionRate']:.2f}%*</span></div>
    <div class="brow"><span class="bn"><i class="dot ks"></i>目标</span><div class="bt"><div class="bf ks" data-w="100"></div></div><span class="bv">2.00%</span></div>
  </section>
  <p class="note"><b>读法</b>：前三组按双平台占比展示；互动率按 0~2% 绝对刻度。视频号互动率以 5 赞 + 1 评除以 17,116 播放估算。<b>最大事件：抖音互动升至 1.76%，但完播降至 14.26%。</b></p>
</div>'''


def audience_markup():
    dy, wx = DATA['douyin'], DATA['wechat']
    colors = ['#22d3ee', '#3b82f6', '#a855f7', '#ec4899', '#fbbf24', '#34d399', '#64748b']
    circumference, offset, circles, legend = 276.5, 0.0, [], []
    for (label, value), color in zip(dy['interests'], colors):
        dash = circumference * value / 100
        circles.append(f'<circle cx="60" cy="60" r="44" fill="none" stroke="{color}" stroke-width="15" stroke-dasharray="{dash:.1f} {circumference}" stroke-dashoffset="{-offset:.1f}" transform="rotate(-90 60 60)"/>')
        legend.append(f'<div><i style="background:{color}"></i>{label}<b>{value}%</b></div>')
        offset += dash
    max_age = wx['ages'][0][1]
    age_rows = []
    for index, (label, value) in enumerate(wx['ages']):
        cls = 'gd' if index == 0 else 'sp'
        age_rows.append(f'<div class="brow{" lead" if index == 0 else ""}"><span class="bn">{label}</span><div class="bt"><div class="bf {cls}" data-w="{value/max_age*100:.1f}"></div></div><span class="bv">{value:.1f}%</span></div>')
    top_three = sum(value for _, value in dy['interests'][:3])
    return f'''
<div class="panel">
  <i class="cn tl"></i><i class="cn tr"></i><i class="cn bl"></i><i class="cn br"></i>
  <header class="hd"><h1>粉丝画像 · 双平台</h1><span class="mt">{DATA['meta']['period']}</span></header>
  <div class="sec-t"><b>抖音 · 兴趣分布</b><span>合计 100% · 粉丝 {n(dy['followers'])}</span></div>
  <section class="donut-row" aria-label="抖音兴趣分布">
    <div class="donut"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="44" fill="none" stroke="rgba(20,44,96,.9)" stroke-width="15"/>{''.join(circles)}</svg><div class="dc"><b>{top_three}%</b><span>兴趣前三</span></div></div>
    <div class="leg">{''.join(legend)}</div>
  </section>
  <div class="sec-t"><b>视频号 · 年龄分布</b><span>画像样本 {n(wx['audienceSample'])}</span></div>
  <section aria-label="视频号年龄分布">{''.join(age_rows)}</section>
  <div class="sec-t"><b>视频号 · 性别</b></div>
  <section aria-label="视频号性别：男{wx['male']}，女{wx['female']}"><div class="gbar"><div class="m" style="width:{wx['male']}%"></div><div class="f" style="width:{wx['female']}%"></div></div><div class="glab"><span>男 {wx['male']}%</span><span>女 {wx['female']}%</span></div></section>
  <p class="warnbox"><b>受众结论：</b>视频号 50 岁+占 {wx['ages'][0][1]}%，男性占 {wx['male']}%；抖音兴趣前三为随拍、剧情、亲子。选题继续使用熟悉体育事件、清楚动作因果和直接选择题。</p>
</div>'''


def traffic_markup():
    wx, ex = DATA['wechat'], DATA['experiments']
    source = [
        ('推荐', wx['recommendPlays']), ('分享', wx['sharePlays']), ('订阅号', wx['subscriptionPlays']),
        ('朋友♡', wx['friendPlays']), ('其他', wx['otherPlays']), ('主页', wx['homePlays'])
    ]
    max_source = source[0][1]
    cols = ''.join(f'<div class="vcol{" hot" if i == 0 else ""}"><span class="vval">{n(value)}</span><div class="vbar" data-h="{math.sqrt(value/max_source)*100:.1f}"></div></div>' for i, (_, value) in enumerate(source))
    cats = ''.join(f'<span>{label}</span>' for label, _ in source)
    life_height = math.sqrt(ex['lifeAverage'] / ex['eventAverage']) * 100
    return f'''
<div class="panel">
  <i class="cn tl"></i><i class="cn tr"></i><i class="cn bl"></i><i class="cn br"></i>
  <header class="hd"><h1>流量来源 · 母题反差</h1><span class="mt">{DATA['meta']['period']}</span></header>
  <div class="cols">
    <section aria-label="视频号7日流量来源柱状图">
      <div class="sec-t"><b>视频号 · 7日流量来源</b><span>推荐占 {wx['recommendShare']}% · √刻度</span></div>
      <div class="vchart">{cols}</div><div class="vcats">{cats}</div>
      <p class="foot">推荐播放 {n(wx['recommendPlays'])}，占总播放 <b>{wx['recommendShare']}%</b>；推荐池仍是绝对主场，也是当前最大单点依赖。</p>
    </section>
    <section aria-label="母题支柱均播放对比柱状图">
      <div class="sec-t"><b>抖音母题 · 均播放</b><span>反差 {ex['ratio']:.2f}×</span></div>
      <div class="duo"><div class="dcol"><span class="vval" style="color:#22d3ee">{n(ex['eventAverage'])}</span><div class="dbar a" data-h="100"></div></div><div class="dcol"><span class="vval" style="color:#f87171">{n(ex['lifeAverage'])}</span><div class="dbar b" data-h="{life_height:.1f}"></div></div></div>
      <div class="dcats"><span>即时体育 · 5条</span><span>奇观/生活 · 4条</span></div>
      <p class="foot">第 13、14、16、18、21 轴即时体育均播 {n(ex['eventAverage'])}，其余奇观/生活决策轴均播 {n(ex['lifeAverage'])}。<b>即时事件提供点击理由</b>，小白动作负责把事件变成生活决策。</p>
    </section>
  </div>
</div>'''


def works_markup():
    works, wx, dy = DATA['works'], DATA['wechat'], DATA['douyin']
    peak = max(item['plays'] for item in works)
    rows = []
    for index, item in enumerate(works):
        rank_class = f' r{index + 1}' if index < 3 else ''
        rows.append(f'''<div class="item{" hot" if index == 0 else ""}"><span class="rank{rank_class}">{index + 1}</span><div class="ib">
      <p class="t" title="第{item['axis']}轴 · {item['title']}">第{item['axis']}轴 · {item['title']}</p>
      <div class="bt"><div class="bf" data-w="{math.sqrt(item['plays']/peak)*100:.1f}"></div></div>
      <div class="stats"><span class="play">{n(item['plays'])}</span><span>赞 {item['likes']}</span><span>评 {item['comments']}</span><span>藏 {item['favorites']}</span><span class="dt">{item['date']}</span></div></div></div>''')
    total = sum(item['plays'] for item in works)
    return f'''
<div class="panel">
  <i class="cn tl"></i><i class="cn tr"></i><i class="cn bl"></i><i class="cn br"></i>
  <header class="hd"><h1>视频号 · 近10条 TOP8</h1><span class="mt">√ 刻度</span></header>
  <div class="trend"><div class="tcard"><span class="tl2">视频号 · 7日播放</span><span class="tv2">{n(wx['plays7d'])} <small>净增 {wx['netFollowers7d']}</small></span></div><div class="tcard"><span class="tl2">抖音 · 7日播放</span><span class="tv2">{n(dy['plays7d'])} <small>▲ +{dy['netFollowers7d']} 粉丝</small></span></div></div>
  <section aria-label="视频号近10条作品播放榜">{''.join(rows)}</section>
  <p class="foot"><b>√ 压缩刻度</b>：条宽 = √(播放/榜首播放)。TOP8 合计 <b>{n(total)}</b>，占视频号 7 日播放 <b>{total/wx['plays7d']*100:.1f}%</b>；第22轴“功夫女足”刚发布为 0，待冷启动回收后进入榜单。</p>
</div>'''


def strategy_markup():
    strategy = DATA['strategy']
    return f'''
<div class="panel">
  <i class="cn tl"></i><i class="cn tr"></i><i class="cn bl"></i><i class="cn br"></i>
  <header class="hd"><h1>策略 · 风险 · 下一条</h1><span class="mt">飞轮复盘 · {DATA['meta']['updated']}</span></header>
  <section class="strategy" aria-label="一句话策略"><span class="st">策略</span><p>{strategy['oneLine']}</p><span class="conf">信心 {strategy['confidence']}</span></section>
  <section class="cards" aria-label="核心风险与行动">
    <article class="card"><div class="ck"><span class="ico">!</span><div><div class="ct">抖音留存继续下滑</div><div class="cv">最高优先级</div></div></div><p>{strategy['riskOne']} <b>下一轮先修前 2 秒与信息密度。</b></p></article>
    <article class="card"><div class="ck"><span class="ico">×</span><div><div class="ct">视频号推荐依赖</div><div class="cv">结构风险</div></div></div><p>{strategy['riskTwo']} <b>抖音强样本不能直接迁移为视频号结论。</b></p></article>
    <article class="card"><div class="ck"><span class="ico">✓</span><div><div class="ct">即时体育公式有效</div><div class="cv">阶段信号</div></div></div><p>{strategy['win']} 小白连续动作是叙事条件，<b>不是独立的分发充分条件。</b></p></article>
    <article class="card next"><div class="ck"><span class="ico">→</span><div><div class="ct">下一步 · 回收第22轴</div><div class="cv">功夫女足轴</div></div></div><p>{strategy['next']}</p><div class="tagrow"><span class="tag">KPI：完播 / 平均观看 / 2秒跳出</span><span class="tag">节点：2h / 24h / 48h</span></div></article>
  </section>
</div>'''


def health_patch(doc):
    summary, dy, wx, ex = DATA['summary'], DATA['douyin'], DATA['wechat'], DATA['experiments']
    health = {
        'overview': {'health': summary['flywheelHealth'], 'glab': '综合健康分 · 双平台均值', 'formula': f"（{summary['douyinHealth']}+{summary['wechatHealth']}）/ 2 ≈ {summary['flywheelHealth']}",
            'left': [['抖音 · 粉丝', n(dy['followers'])], ['视频号 · 关注', n(wx['followers'])], ['当前实验轴', '第22轴']],
            'right': [['抖音互动率', f"{dy['interactionRate']:.2f}%", 'gd'], ['视频号推荐占比', f"{wx['recommendShare']}%", 'warn'], ['抖音完播率', f"{dy['finishRate']}%", 'bad']],
            'dlab': '7日总播放 · 双平台', 'digits': str(summary['plays7d']), 'dsub': f"合计粉丝 {n(summary['followers'])} · <b>净增 +{summary['netFollowers7d']}</b> · 第22轴监测中",
            'diag': [['策略 · 事件带点击', '即时体育事件负责点击，小白连续实体动作负责叙事，大陈画内真实对白完成判断；烧录字幕成为发布硬门。', 'g'], ['当前 · 功夫女足轴', '30秒双平台已发布，先回收2h/24h/48h留存，不提前写效果结论。', 'g']]},
        'douyin': {'health': summary['douyinHealth'], 'glab': '平台健康分 · 抖音', 'formula': f"粉丝 {n(dy['followers'])} · 7日 +{dy['netFollowers7d']}",
            'left': [['粉丝', n(dy['followers'])], ['7日播放', n(dy['plays7d'])], ['播放中位', n(dy['playsMedian'])]],
            'right': [['5s完播率', f"{dy['finish5s']}%"], ['2s跳出率', f"{dy['bounce2s']}%", 'warn'], ['整体完播率', f"{dy['finishRate']}%", 'bad']],
            'dlab': '7日播放 · 抖音', 'digits': str(dy['plays7d']), 'dsub': f"互动率 <b>{dy['interactionRate']:.2f}%</b> · 平均观看 {dy['averageWatch']}",
            'diag': [['现象', '互动率与涨粉改善，但完播连续下滑；增长信号和留存风险同时存在，不能只读总播放。', ''], ['杠杆', '保留即时体育事件与小白动作，下一条只改前2秒和信息密度，避免同时叠加多个新变量。', 'g']]},
        'shipinhao': {'health': summary['wechatHealth'], 'glab': '平台健康分 · 视频号', 'formula': f"关注 {n(wx['followers'])} · 净增 {wx['netFollowers7d']}",
            'left': [['关注者', n(wx['followers'])], ['7日播放', n(wx['plays7d'])], ['7日赞/评', f"{wx['likes7d']}/{wx['comments7d']}"]],
            'right': [['推荐占比', f"{wx['recommendShare']}%", 'warn'], ['新增/流失', f"{wx['fansAdded7d']}/{wx['fansLost7d']}", 'warn'], ['互动率估算', f"{wx['interactionRate']:.2f}%", 'bad']],
            'dlab': '7日播放 · 视频号', 'digits': str(wx['plays7d']), 'dsub': f"推荐 {n(wx['recommendPlays'])} · 分享 {n(wx['sharePlays'])}",
            'diag': [['根因', '推荐池仍贡献96.9%播放，但近期作品没有复现第14轴；新增与流失相抵，社交扩散尚未启动。', ''], ['杠杆', '按50岁以上男性受众重写开头，把事件、动作和选择题在前3秒说清，独立判断视频号冷启动。', 'g']]},
        'flywheel': {'health': 50, 'glab': '实验健康分 · 第22轴', 'formula': '已发布 · 等待2h/24h/48h回收',
            'left': [['强样本', '第18轴'], ['上条播放 · 抖', '3,444'], ['当前实验', '第22轴']],
            'right': [['烧录字幕', '已通过', 'gd'], ['成片时长', '30.19s', 'warn'], ['双平台', '已发布', 'gd']],
            'dlab': '当前运营实验轴', 'digits': '00022', 'dsub': '功夫女足 · <b>冷启动监测中</b>',
            'diag': [['已验证', ex['strongResult'] + '，即时事件是当前最强点击理由。', 'g'], ['待验证', '30秒时长与烧录字幕能否提升理解而不牺牲完播；本轴只记录上线，不提前写效果结论。', '']]}
    }
    doc = doc.replace('kuaishou', 'flywheel').replace('>快手</button>', '>飞轮</button>')
    doc = doc.replace('统计周期 2026-07-20 ~ 07-26', f"统计周期 {DATA['meta']['period']}")
    payload = json.dumps(health, ensure_ascii=False, separators=(',', ':'))
    doc, count = re.subn(r'var DATA = \{.*?\n  \};\n\n  var needle', f'var DATA = {payload};\n\n  var needle', doc, flags=re.S)
    if count != 1:
        raise RuntimeError(f'健康罗盘 DATA 替换失败: {count}')
    return doc


def content_patch(title, doc):
    if title.startswith('标题栏'):
        doc = doc.replace('统计周期 2026-07-20 ~ 07-26', f"统计周期 {DATA['meta']['period']}")
        doc = doc.replace('更新 07-27 11:14', f"更新 {DATA['meta']['updated']}")
        doc = doc.replace('大陈日更 · 抖音 / 视频号 / 快手', DATA['meta']['subtitle'])
        return doc
    if title.startswith('三平台'):
        return replace_body(doc, compare_markup())
    if title.startswith('粉丝画像'):
        return replace_body(doc, audience_markup())
    if title.startswith('健康罗盘'):
        return health_patch(doc)
    if title.startswith('视频号'):
        return replace_body(doc, works_markup())
    if title.startswith('流量来源'):
        return replace_body(doc, traffic_markup())
    if title.startswith('策略'):
        return replace_body(doc, strategy_markup())
    return doc

def apply_patches(title, doc):
    doc = content_patch(title, doc)
    if title.startswith('标题栏'):
        doc = doc.replace('新媒体运营数据驾驶舱', '百商AI新媒体运营飞轮', 1)
        doc = doc.replace('</head>', TITLE_MOBILE_CSS + TITLE_ANIM_CSS + '</head>', 1)
    else:
        doc = doc.replace('</head>', HIDE_MT_CSS + ANIM_CSS + '</head>', 1)
        doc = doc.replace('</body>', SETTLE_JS + '</body>', 1)
    if title.startswith('视频号'):
        doc = doc.replace('</head>', TOP_STRETCH_CSS + '</head>', 1)
        doc = doc.replace('  </section>', TOP_EXTRA_ITEMS, 1)
    if title.startswith('健康罗盘'):
        doc = doc.replace('</head>', HEALTH_MOBILE_CSS + SCARD_CSS + '</head>', 1)
    if title.startswith('流量来源'):
        doc = doc.replace('</head>', TRAFFIC_CSS + '</head>', 1)
    return doc

d = json.loads(SRC.read_text())
period = DATA['meta']['period']
by_prefix = {w['title'][:3]: w for w in d['widgets']}

def widget(match, stretch=True):
    w = next(w for w in d['widgets'] if w['title'].startswith(match))
    doc = apply_patches(w['title'], w['files']['index.html'])
    if stretch:
        doc = doc.replace('</head>', STRETCH_CSS + '</head>', 1)
    display_title = {
        '三平台': '双平台 · 数据对比',
        '健康罗盘': '运营健康罗盘 · 平台下钻',
        '视频号': '视频号 · 近10条 TOP8',
    }.get(next((key for key in ('三平台', '健康罗盘', '视频号') if w['title'].startswith(key)), ''), w['title'])
    return display_title, html.escape(doc, quote=True)

def cell(match, nh, last=False, stretch=True):
    t, doc = widget(match, stretch)
    style = f'flex:1 1 {nh}px;min-height:{nh}px' if last else f'flex:0 0 {nh}px;height:{nh}px'
    return (f'<div class="cell" style="{style};--nh:{nh}px">'
            f'<iframe title="{html.escape(t)}" srcdoc="{doc}" scrolling="no"></iframe></div>')

def column(key, span):
    items = PLAN[key]
    inner = '\n'.join(cell(it['match'], it['nh'], last=(i == len(items) - 1)) for i, it in enumerate(items))
    return f'<div class="col" style="grid-column:span {span}">\n{inner}\n</div>'

tt, tdoc = widget(PLAN['title']['match'], stretch=False)
bt = PLAN['bottom']
btitle, bdoc = widget(bt['match'], stretch=True)
title_cell = (f'<div class="cell trow" style="--nh:{PLAN["title"]["nh"]}px">'
              f'<iframe title="{html.escape(tt)}" srcdoc="{tdoc}" scrolling="no"></iframe></div>')
bottom_cell = (f'<div class="cell brow" style="--nh:{bt["nh"]}px">'
               f'<iframe title="{html.escape(btitle)}" srcdoc="{bdoc}" scrolling="no"></iframe></div>')

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>广州潮少 · 运营大数据看板</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  html{{background:#04081a;color-scheme:dark;-webkit-text-size-adjust:100%;text-size-adjust:100%}}
  body{{background:radial-gradient(1200px 700px at 50% -10%, #0d1f4c 0%, #060d24 55%, #04081a 100%);min-height:100vh;min-height:100svh;padding:14px;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;overflow-x:hidden}}
  .wrap{{max-width:1440px;margin:0 auto;display:flex;flex-direction:column;gap:{GAP}px}}
  .grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:{GAP}px;align-items:stretch}}
  .col{{display:flex;flex-direction:column;gap:{GAP}px;min-width:0}}
  .cell{{position:relative;min-width:0}}
  .cell iframe{{width:100%;height:100%;border:0;display:block;background:transparent}}
  .trow{{height:{PLAN['title']['nh']}px}}
  .brow{{height:{bt['nh'] + 8}px}}
  .foot{{text-align:center;font-size:10px;color:rgba(150,190,230,.45)}}
  @media (max-width:1180px){{
    body{{padding:max(8px,env(safe-area-inset-top)) max(8px,env(safe-area-inset-right)) max(12px,env(safe-area-inset-bottom)) max(8px,env(safe-area-inset-left))}}
    .wrap{{gap:8px}}
    .grid{{display:flex;flex-direction:column}}
    .col{{gap:8px}}
    .cell{{height:auto!important;min-height:0!important;flex:none!important}}
    .cell iframe{{height:150px;overflow:hidden}}
    .trow,.brow{{height:auto}}
    .foot{{font-size:9px;line-height:1.6;padding:2px 4px}}
  }}
</style>
</head>
<body>
<div class="wrap">
{title_cell}
<main class="grid">
{column('left', 3)}
{column('center', 6)}
{column('right', 3)}
</main>
{bottom_cell}
<p class="foot">广州潮少 · 双平台运营飞轮看板 · 统计周期 {html.escape(period)} · 静态快照,无密钥无接口 · {DATA['meta']['version']}</p>
</div>
{IFRAME_RESIZE_JS}
</body>
</html>
'''
OUT.write_text(page)
print(f'wrote {OUT} ({len(page)} bytes)')
