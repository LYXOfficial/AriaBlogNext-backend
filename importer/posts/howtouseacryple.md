---
title: 如何更加方便地修改Acryple作为自己的主题
cover: 'https://bu.dusays.com/2023/01/20/63c9e28661570.webp'
abbrlink: f34c4b49
date: 2022-12-16 15:54:24
updated: 2022-12-30 15:54:24
tags:
  - Hexo魔改
  - 避坑
categories:
  - Hexo魔改
---

前置教程：

{% link Hexo Butterfly博客魔改的一点点基础,Ariasakaの小窝,https://blog.yaria.top/posts/583ff077/ %}

主题仓库：

{% link Hexo-theme-Acryple,Github,https://github.com/lyxofficial/hexo-theme-acryple %}

前几个月开源了Acryple主题，可惜的是，我为了图方便，直接把本站放在了主题仓库里面。为了方便大家食用，我制作了这篇教程，以及一个更方便的优化仓库及教程，之后会放在之前的`Hexo-theme-Acryple`这个仓库，自己的博客则作为私有仓库。

{% tip bell %}
12.29 修复了之前的友链页导致无法渲染的bug，最近一直没时间改，致歉。
{% endtip %}

# 初步准备工作

找一个文件夹，打开终端，先把现成的Acryple克隆下来：

```bash
git clone https://github.com/LYXOfficial/Hexo-theme-Acryple.git
```

然后安装依赖：

```bash
npm install
```

此时你的站点应该已经准备就绪了。

# 基础修改

首先，对于一些作者、评论什么的配置，你应该参考butterfly官方文档进行修改，请注意该主题是Butterfly 4.2.2。

{% link Butterfly官方文档,Butterfly,https://butterfly.js.org %}

# 修改BBTalk

对于bbtalk的修改，首先你应该读懂官方文档：

{% link BBTalk官方文档,BBTalk,https://bb.js.org %}

需要注意的是，现在BBTalk的微信公众号已经跑路，我的建议是直接在Leancloud的地方修改数据库，也非常方便，甚至对于在学校这种微信困难时期很管用。

然后修改`themes\acryple\source\js\bbtalklunbo.js`和`source\speaks\index.md`里面的key。

除此之外，首页BB轮播有上限100个的bug，注意及时删除。

# 修改关于页面

关于页面的修改参考：

{% link butterfly魔改关于页面,安知鱼,https://anzhiy.cn/posts/e62b.html %}

这里的方案与安知鱼的基本一样，众多的css都在`ariasakablog.css`中，建议配合{% kbd Ctrl %}+{% kbd F %}查找相应图片链接。

# 修改APlayer播放列表

## 白嫖NPM（推荐）

首先，为了了解NPM的使用，你需要先看此文章：

{% link NPM图床的使用,Akilar,http://akilar.top/posts/3e956346/#npm%E5%9B%BE%E5%BA%8A%E7%9A%84%E4%BD%BF%E7%94%A8 %}

相信你已经学会了NPM，假设你有Python的话，你就可以使用我的这个简单脚本快速下载歌单到你的文件夹，并且还加了多线程:

注意安装requests：

```bash
pip install requests
```

```python
import requests,json
from threading import Thread
url="https://api.i-meto.com/meting/api?server=netease&type=playlist&id={换成你的歌单id}" #具体参数见Metingjs文档，server如果不是网易云可以替换
t=[]
req=json.loads(requests.get(url).text)
def doget(key):
    a=key["title"].replace("/","").replace("\\","")
    b=key["url"]
    req=requests.get(b).content
    f=open("music/%s.mp3"%a,"wb+")
    f.write(req)
    f.close()
    b=key["pic"]
    req=requests.get(b).content
    f=open("pic/%s.jpg"%a,"wb+")
    f.write(req)
    f.close()
    b=key["lrc"]
    req=requests.get(b).content
    f=open("lyric/%s.lrc"%a,"wb+")
    f.write(req)
    f.close()
    print(a,"OK")
for key in range(len(req)-1,0,-1):
    t.append(Thread(target=doget,args=(req[key],)))
    t[len(t)-1].start()
```

这时，你就可以初始化并发布了：

```bash
npm init
npm publish
```

如果要更新的话：

```bash
npm version patch
npm publish
```

为了方便写js，可以用以下脚本来生成列表，此处白嫖eleme（一般来说使用jsd系的cdn会超100M的限制）:

```python
import requests,json,urllib
url="https://api.i-meto.com/meting/api?server=netease&type=playlist&id={你的歌单ID}" #具体参数见Metingjs文档，server如果不是网易云可以替换
cdnurl="https://npm.elemecdn.com/{你的仓库名字}/"
t=[]
req=json.loads(requests.get(url).text)
print("ap.list.add([")
for key in range(len(req)-1,0,-1):
    key=req[key]
    a=urllib.request.quote(key["title"].replace("/","").replace("\\",""))
    print("""    {
    name: "%s",
    artist: "%s",
    url: "%smusic/%s.mp3",
    cover: "%spic/%s.jpg,
    lrc: %slyric/%s.lrc",
    },"""%(key["title"],key["author"],cdnurl,a,cdnurl,a,cdnurl,a))
print("])")
```

这串代码就拿来替换下面删除部分。

最后，为了让你的歌曲快点拉到回源，建议多点几下，或者是用这个脚本：

```python
import requests,json,urllib
from threading import Thread
url="https://api.i-meto.com/meting/api?server=netease&type=playlist&id={歌单名}"
cdnurl="https://npm.elemecdn.com/{仓库名}"
req=json.loads(requests.get(url).text)
t=[]
def doget(key):
    global out,req
    f=0
    key=req[key]
    b=urllib.request.quote(key["title"].replace("/","").replace("\\",""))
    try:
        req=requests.get('%s/music/%s.mp3'%(cdnurl,b),timeout=20)
        if req.status_code!=200:
            raise Exception
        req=requests.get('%s/pic/%s.jpg'%(cdnurl,b),timeout=10)
        if req.status_code!=200:
            raise Exception
        req=requests.get('%s/lyric/%s.lrc'%(cdnurl,b),timeout=10)
        if req.status_code!=200:
            raise Exception
    except:
        f=1
    print(key["title"]+" OK "+("but timeout or error" if f==1 else ""))
for key in range(len(req)-1,0,-1):
    t.append(Thread(target=doget,args=(key,)))
    t[len(t)-1].start()
```

一直运行这个脚本，直到输出没有`but timeout or error`就好了

这样虽然麻烦，但是不会出现播放时error的问题。

## 白嫖meting

删除`themes\acryple\source\js\aplayersave.js`里的部分内容：

```diff
function doStuff() {
    ...
    if(flag){
-        ap.list.add([{
-            name: 'Grow Slowly',
-            artist: '井口裕香',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Grow%20Slowly.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Grow%20Slowly.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Grow%20Slowly.lrc',
-        },
-        {
-            name: '霜雪千年（Cover 洛天依 / 乐正绫）',
-            artist: '双笙（陈元汐） / 封茗囧菌',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E9%9C%9C%E9%9B%AA%E5%8D%83%E5%B9%B4%EF%BC%88Cover%20%E6%B4%9B%E5%A4%A9%E4%BE%9D%20%20%E4%B9%90%E6%AD%A3%E7%BB%AB%EF%BC%89.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E9%9C%9C%E9%9B%AA%E5%8D%83%E5%B9%B4%EF%BC%88Cover%20%E6%B4%9B%E5%A4%A9%E4%BE%9D%20%20%E4%B9%90%E6%AD%A3%E7%BB%AB%EF%BC%89.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E9%9C%9C%E9%9B%AA%E5%8D%83%E5%B9%B4%EF%BC%88Cover%20%E6%B4%9B%E5%A4%A9%E4%BE%9D%20%20%E4%B9%90%E6%AD%A3%E7%BB%AB%EF%BC%89.lrc',
-        },
-        {
-            name: '灯火里的中国 (舒楠监制 官方正式版)',
-            artist: '张也 / 周深',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E7%81%AF%E7%81%AB%E9%87%8C%E7%9A%84%E4%B8%AD%E5%9B%BD%20%28%E8%88%92%E6%A5%A0%E7%9B%91%E5%88%B6%20%E5%AE%98%E6%96%B9%E6%AD%A3%E5%BC%8F%E7%89%88%29.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E7%81%AF%E7%81%AB%E9%87%8C%E7%9A%84%E4%B8%AD%E5%9B%BD%20%28%E8%88%92%E6%A5%A0%E7%9B%91%E5%88%B6%20%E5%AE%98%E6%96%B9%E6%AD%A3%E5%BC%8F%E7%89%88%29.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E7%81%AF%E7%81%AB%E9%87%8C%E7%9A%84%E4%B8%AD%E5%9B%BD%20%28%E8%88%92%E6%A5%A0%E7%9B%91%E5%88%B6%20%E5%AE%98%E6%96%B9%E6%AD%A3%E5%BC%8F%E7%89%88%29.lrc',
-        },
-        {
-            name: 'Windows Welcome Music (Remix) (Remix)',
-            artist: 'Sugar95',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Windows%20Welcome%20Music%20%28Remix%29%20%28Remix%29.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Windows%20Welcome%20Music%20%28Remix%29%20%28Remix%29.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Windows%20Welcome%20Music%20%28Remix%29%20%28Remix%29.lrc',
-        },
-        {
-            name: 'Falling Again',
-            artist: 'Nurko / Roniit',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Falling%20Again.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Falling%20Again.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Falling%20Again.lrc',
-        },
-        {
-            name: '云女孩',
-            artist: '符白牙 / lunari.io',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E4%BA%91%E5%A5%B3%E5%AD%A9.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E4%BA%91%E5%A5%B3%E5%AD%A9.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E4%BA%91%E5%A5%B3%E5%AD%A9.lrc',
-        },
-        {
-            name: 'See You Again',
-            artist: 'See You Again',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/See%20You%20Again.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/See%20You%20Again.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/See%20You%20Again.lrc',
-        },
-        {
-            name: 'sister\'s noise',
-            artist: 'fripSide',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/sister%27s%20noise.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/sister%27s%20noise.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/sister%27s%20noise.lrc',
-        },
-        {
-            name: '心做し',
-            artist: '一之瀬ユウ / GUMI',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E5%BF%83%E5%81%9A%E3%81%97.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E5%BF%83%E5%81%9A%E3%81%97.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E5%BF%83%E5%81%9A%E3%81%97.lrc',
-        },
-        {
-            name: '君に嘘',
-            artist: '湊貴大 / 初音ミク',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E5%90%9B%E3%81%AB%E5%98%98.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E5%90%9B%E3%81%AB%E5%98%98.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E5%90%9B%E3%81%AB%E5%98%98.lrc',
-        },
-        {
-            name: '溯 (Reverse)',
-            artist: 'CORSAK胡梦周 / 马吟吟',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E6%BA%AF%20%28Reverse%29.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E6%BA%AF%20%28Reverse%29.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E6%BA%AF%20%28Reverse%29.lrc',
-        },
-        {
-            name: 'ふわふわ♪',
-            artist: '牧野由依',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E3%81%B5%E3%82%8F%E3%81%B5%E3%82%8F%E2%99%AA.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E3%81%B5%E3%82%8F%E3%81%B5%E3%82%8F%E2%99%AA.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E3%81%B5%E3%82%8F%E3%81%B5%E3%82%8F%E2%99%AA.lrc',
-        },
-        {
-            name: 'LEVEL5 -judgelight-',
-            artist: 'fripSide',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/LEVEL5%20-judgelight-.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/LEVEL5%20-judgelight-.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/LEVEL5%20-judgelight-.lrc',
-        },
-        {
-            name: '打上花火',
-            artist: 'Daoko / 米津玄師',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E6%89%93%E4%B8%8A%E8%8A%B1%E7%81%AB.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E6%89%93%E4%B8%8A%E8%8A%B1%E7%81%AB.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E6%89%93%E4%B8%8A%E8%8A%B1%E7%81%AB.lrc',
-        },
-        {
-            name: '勾指起誓',
-            artist: '洛天依 / ilem',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E5%8B%BE%E6%8C%87%E8%B5%B7%E8%AA%93.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E5%8B%BE%E6%8C%87%E8%B5%B7%E8%AA%93.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E5%8B%BE%E6%8C%87%E8%B5%B7%E8%AA%93.lrc',
-        },
-        {
-            name: '红莲华（《鬼灭之刃》动画OP）',
-            artist: '池绛不吃姜',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E7%BA%A2%E8%8E%B2%E5%8D%8E%EF%BC%88%E3%80%8A%E9%AC%BC%E7%81%AD%E4%B9%8B%E5%88%83%E3%80%8B%E5%8A%A8%E7%94%BBOP%EF%BC%89.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E7%BA%A2%E8%8E%B2%E5%8D%8E%EF%BC%88%E3%80%8A%E9%AC%BC%E7%81%AD%E4%B9%8B%E5%88%83%E3%80%8B%E5%8A%A8%E7%94%BBOP%EF%BC%89.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E7%BA%A2%E8%8E%B2%E5%8D%8E%EF%BC%88%E3%80%8A%E9%AC%BC%E7%81%AD%E4%B9%8B%E5%88%83%E3%80%8B%E5%8A%A8%E7%94%BBOP%EF%BC%89.lrc',
-        },
-        {
-            name: 'Lemon',
-            artist: '是Wei呀',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Lemon.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Lemon.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Lemon.lrc',
-        },
-        {
-            name: 'Alive',
-            artist: 'ReoNa',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Alive.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Alive.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Alive.lrc',
-        },
-        {
-            name: 'All in good time',
-            artist: '川田まみ',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/All%20in%20good%20time.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/All%20in%20good%20time.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/All%20in%20good%20time.lrc',
-        },
-        {
-            name: 'aLIEz (澤野弘之 LIVE[nZk]004 (2016/11/03@TOKYO DOME CITY HALL))',
-            artist: '瑞葵(mizuki)',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/aLIEz%20%28%E6%BE%A4%E9%87%8E%E5%BC%98%E4%B9%8B%20LIVE%5BnZk%5D004%20%2820161103%40TOKYO%20DOME%20CITY%20HALL%29%29.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/aLIEz%20%28%E6%BE%A4%E9%87%8E%E5%BC%98%E4%B9%8B%20LIVE%5BnZk%5D004%20%2820161103%40TOKYO%20DOME%20CITY%20HALL%29%29.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/aLIEz%20%28%E6%BE%A4%E9%87%8E%E5%BC%98%E4%B9%8B%20LIVE%5BnZk%5D004%20%2820161103%40TOKYO%20DOME%20CITY%20HALL%29%29.lrc',
-        },
-        {
-            name: 'only my railgun',
-            artist: 'fripSide',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/only%20my%20railgun.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/only%20my%20railgun.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/only%20my%20railgun.lrc',
-        },
-        {
-            name: '恋愛サーキュレーション',
-            artist: '花澤香菜',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E6%81%8B%E6%84%9B%E3%82%B5%E3%83%BC%E3%82%AD%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E6%81%8B%E6%84%9B%E3%82%B5%E3%83%BC%E3%82%AD%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E6%81%8B%E6%84%9B%E3%82%B5%E3%83%BC%E3%82%AD%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3.lrc',
-        },
-        {
-            name: '千本桜',
-            artist: '黒うさP / 初音ミク',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E5%8D%83%E6%9C%AC%E6%A1%9C.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E5%8D%83%E6%9C%AC%E6%A1%9C.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E5%8D%83%E6%9C%AC%E6%A1%9C.lrc',
-        },
-        {
-            name: '起风了',
-            artist: '买辣椒也用券',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/%E8%B5%B7%E9%A3%8E%E4%BA%86.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/%E8%B5%B7%E9%A3%8E%E4%BA%86.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/%E8%B5%B7%E9%A3%8E%E4%BA%86.lrc',
-        },
-        {
-            name: 'Heaven is a Place On Earth',
-            artist: 'fripSide',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Heaven%20is%20a%20Place%20On%20Earth.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Heaven%20is%20a%20Place%20On%20Earth.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Heaven%20is%20a%20Place%20On%20Earth.lrc',
-        },
-        {
-            name: 'とある日の午後',
-            artist: 'Laqshe',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/とある 日の午後.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/とある 日の午後.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/とある 日の午後.lrc',
-        },
-        {
-            name: '群青',
-            artist: 'YOASOBI',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/群青.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/群青.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/群青.lrc',
-        },
-        {
-            name: 'WATER',
-            artist: 'A-39 / 沙包P / 初音ミク',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/WATER.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/WATER.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/WATER.lrc',
-        },
-        {
-            name: 'Minecraft',
-            artist: 'C418',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Minecraft.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Minecraft.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Minecraft.lrc',
-        },
-        {
-            name: 'Haggstrom',
-            artist: 'C418',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/Haggstrom.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/Haggstrom.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/Haggstrom.lrc',
-        },
-        {
-            name: '横竖撇点折',
-            artist: '米白',
-            url: 'https://npm.elemecdn.com/musiccdn-ariasaka/music/横竖撇点折.mp3',
-            cover: 'https://npm.elemecdn.com/musiccdn-ariasaka/pic/横竖撇点折.jpg',
-            lrc: 'https://npm.elemecdn.com/musiccdn-ariasaka/lyric/横竖撇点折.lrc',
-        }
-    ]);
    }
}
document.addEventListener('DOMContentLoaded', (e) => {
    doStuff();
})
```

然后修改`_config.acryple.yml`:

```yaml
inject:
...
    bottom:
    ...
    - <div class="aplayer no-destroy" data-id="{你的歌单名}" data-server="netease" data-type="playlist" data-listFolded="false" data-preload="metadata" data-theme="var(--lyx-theme)" data-fixed="true" data-autoplay="false" data-volume=0.1 style="z-index:514"> </div>
    ...
```

# 修改页脚运行时间

修改`[blogRoot]\themes\acryple\source\js\sitetime.js`：

```javascript
function siteTime(){
    ...
    var todaySecond = today.getSeconds();
    var t1 = Date.UTC(2022,6,4,12,00,00); //修改为自己的网站起始日期
    var t2 = Date.UTC(todayYear,todayMonth,todayDate,todayHour,todayMinute,todaySecond);
    var diff = t2-t1;
    ...
}
siteTime();
```

# 修改Github日历

使用店长魔改版：

{% link Gitcalendar,Akilarの糖果屋,https://akilar.top/posts/1f9c68c9/ %}

~~注意：一般来说我不会跑路，所以`apiurl`不用改[doge]~~

# 修改sw

参考：



# PWA修改

主要是图标，修改`[blogRoot]\source\img`里面的各种pwa图标。

然后修改`[blogRoot]\source\manifest.json`，参考：

{% link Butterfly主题的PWA实现方案,Akilarの糖果屋,http://akilar.top/posts/8f31c3d0/ %}

# 修改评论弹幕

你需要修改评论弹幕的参数，参考：

{% link 博客魔改日记（3）,Ariasaka,/posts/670e47f/#CommentBarrage V3.0 %}

{% link Butterfly主题的留言弹幕界面增强版（支持Twikoo、Waline、Valine）,Ariasakaの小窝,/posts/69707535/ %}

# 修改个人信息

最好把`Ariasaka`全局替换成你的网名，然后站名也是。

# 修改朋友圈

友链朋友圈前端方案采用林木木的，目前使用`v5.0.6`，部署参考:

然后修改`[blogRoot]\source\fcircle\index.md`和`[blogRoot]\themes\acryple\source\js\randomFriend.js`里面的`apiUrl`项

# 需要注意的点

## Twikoo

发现Twikoo没有控制面板入口了吗？其实昵称栏输入我网名就行啦！

## 友链

**`theme_color`必须加引号！！！**

**`theme_color`必须加引号！！！**

## CDN

我使用了Tianli的JSD CDN，请先充分阅读使用条款并申请使用方可使用。

{% link 免费JSD镜像使用手册,Tianli's blog,https://tianli-blog.club/jsd/ %}

也可以全局替换为其它CDN，比如`eleme,zhimg,afdelivr`等，当然最香的是CW/SW劫持并发请求。

## 头像

{% span red, 头像必须是60x60!!! %}{% span red, 卡片上的头像必须是60x60!!! %}

因为某些莫名奇妙的bug，卡片上的头像必须是60x60，否则会溢出或者变小、拉伸。头像在：`source/img/a.webp`。

~~PS：这个特性从我最开始研究魔改，7月的时候就存在了，一直没有修~~

## 文章

### abbrlink

我采用了`abbrlink`永久链接，请注意。

### 外挂标签

内置店长的外挂标签，不过注意`link`标签采用的是洪哥的方案，会稍有不同：

```markdown
{% link [name],[author],[link] %}
<!-- 自动提取图标，可以显示作者 -->
```

而原版为：

```markdown
{% link [title], [link], [icon] %}
<!-- 手动设置图标，不能可以显示作者 -->
```

{% link Tag Plugins Plus,Akilarの糖果屋,https://akilar.top/posts/615e2dec/ %}

{% link Hexo的Butterfly魔改：网址卡片外挂标签,张洪Heo,https://blog.zhheo.com/p/ccaf9148.html %}

## 评论

主题内置了Twikoo Magic+Heo表情包，如果用Twikoo的话，请在Twikoo评论控制面板中修改owo的路径为`owo.json`

## NODEMODULES

{% span red, 复制文件夹的时候千万别拷node_modules文件夹！！！ %}

**不然你会感到4KIO的无力！！！** 

因为`node_modules`里面的文件又小又散，正确打开方式是留下`package.json`，删掉`package-lock.json`，然后在新文件夹里运行`npm install`

# 可有可无的其它修改指南

## 修改banner

全部都在`source\people.html`里面，自己修改内容即可（注意这是一个完整的html）

## NPM的合理白嫖

~~白嫖鸽子UP？！咕咕咕。。。~~

## 个性化博客设置

## 善用GithubAction

## 套CDN

相信你看完了之后，已经不认识修改两个字了。不过这样基本上就可以把博客变成自己的了。