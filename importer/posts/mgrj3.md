---
title: 博客魔改日记（3）
tags:
  - Hexo魔改
  - 魔改日记
categories:
  - Hexo魔改
cover: 'https://bu.dusays.com/2023/01/20/63c9e28e3847f.webp'
abbrlink: 670e47f
date: 2022-12-07 20:36:37
updated: 2022-12-07 20:36:37
---
前置教程：

{% link Hexo Butterfly博客魔改的一点点基础,Ariasakaの小窝,https://blog.yaria.top/posts/583ff077/ %}

最近在疯狂肝博客，主要方面在优化用户体验上，加功能加的比较少，

PS：很多js偷懒使用了jquery，请自行引入

# CommentBarrage V3.0

2023.1.22更新:

原有对于Cloudbase的方法不可用，请移步：

{% link 基于腾讯云Cloudbase云开发的Twikoo评论弹幕扩展,Ariasakaの小窝,https://blog.yaria.top/posts/8f578896/ V3.0 %}


![](https://bu.dusays.com/2023/01/20/63ca1319709c3.webp)

最近新写了`CommentBarrage`，原来的bug比较多，干脆直接改成swiper了，这样用户可以自由切换，灵感来源于[Eurkon](https://blog.eurkon.com)，不过并没有去那里扒。

参考了这个文档：

{% link 中文api,Swiper中文网,https://www.swiper.com.cn/api/index.html %}

PS:为了兼容`butterfly-swiper`，swiper使用的是`v5.4.5`，需要注意版本：

```yaml
swiper_css: https://cdnjs.cloudflare.com/ajax/libs/Swiper/5.4.5/css/swiper.min.css
swiper_js: https://cdnjs.cloudflare.com/ajax/libs/Swiper/5.4.5/js/swiper.min.js
```

弹幕的配置请参照旧版：

{% link Butterfly主题的留言弹幕界面增强版（支持Twikoo、Waline、Valine）,Ariasakaの小窝,/posts/69707535/ %}

`commentBarrage.js`参照以下进行修改:
```js
//commentBarrage v3.0 By Ariasaka
//for swiper and both(pjax or nopjax)
//ainb?!!!! qwq
/document.addEventListener('pjax:complete', startbarrage); //不用pjax请注释掉这一行
document.addEventListener('DOMContentLoaded', startbarrage);

function startbarrage(){
try{
clearInterval(timer);
document.querySelector('.comment-barrage').innerHTML="";
delete sw;
}catch(err){}
const commentBarrageConfig = {
	//浅色模式和深色模式颜色，务必保持一致长度，前面是背景颜色，后面是字体，随机选择，默认这个颜色还好
	lightColors:[
		['var(--lyx-white-acrylic2)','var(--lyx-black)'],
	],
	darkColors:[
		['var(--lyx-black-acrylic2)','var(--lyx-white)'],
	],
	//v3仅支持一个弹幕
	//弹幕显示间隔时间，单位ms
	barrageTime: 3000,
	//twikoo部署地址（Vercel、私有部署），腾讯云的为环境ID
	twikooUrl: "https://tkapi.yaria.top",
	//token获取见前文
	accessToken: "{YOUR_TOKEN}",
	pageUrl: window.location.pathname,
	barrageTimer: [],
	barrageList: [],
	barrageIndex: 0,
	// 没有设置过头像时返回的默认头像，见cravatar文档 https://cravatar.cn/developers/api，可以不改以免出错
	noAvatarType: "retro",
	dom: document.querySelector('.comment-barrage'),
	//是否默认显示留言弹幕
	displayBarrage: true,
	//头像cdn，默认cravatar
	avatarCDN: "cravatar.cn",
}
function checkURL(URL){
	var str=URL;
	//判断URL地址的正则表达式为:http(s)?://([\w-]+\.)+[\w-]+(/[\w- ./?%&=]*)?
	//下面的代码中应用了转义字符"\"输出一个字符"/"
	var Expression=/http(s)?:\/\/([\w-]+\.)+[\w-]+(\/[\w- .\/?%&=]*)?/;
	var objExp=new RegExp(Expression);
	if(objExp.test(str)==true){
	return true;
	}else{
	return false;
	}
	} 
function isInViewPortOfOne (el) {
    const viewPortHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight 
    const offsetTop = el.offsetTop
    const scrollTop = document.documentElement.scrollTop
    const top = offsetTop - scrollTop
    return top <= viewPortHeight
}
if(location.href.indexOf("posts")!=-1||location.href.indexOf("posts")!=-1)
document.onscroll = function() {
	if(commentBarrageConfig.displayBarrage){
		if(isInViewPortOfOne(document.getElementById("post-comment"))){
			$(".comment-barrage").hide();
		}
		else{
			$(".comment-barrage").show();
		}
	}
  }
function initCommentBarrage(){
	
	var data = JSON.stringify({
		"event": "COMMENT_GET",
		"commentBarrageConfig.accessToken": commentBarrageConfig.accessToken,
		"url": commentBarrageConfig.pageUrl
	});
	var xhr = new XMLHttpRequest();
	xhr.withCredentials = true;
	xhr.addEventListener("readystatechange", function() {
		if(this.readyState === 4) {
			commentBarrageConfig.barrageList = commentLinkFilter(JSON.parse(this.responseText).data);
			commentBarrageConfig.dom.innerHTML = '';
			for(commentBarrageConfig.barrageIndex=0;commentBarrageConfig.barrageIndex<commentBarrageConfig.barrageList.length;commentBarrageConfig.barrageIndex++){
				popCommentBarrage(commentBarrageConfig.barrageList[commentBarrageConfig.barrageIndex]);
			}
			kkksc03=new Swiper('.barrageswiper', {
				direction: "vertical",
				loop: true,
				mousewheel:true,
				autoplay: {
					delay: commentBarrageConfig.barrageTime,
					stopOnLastSlide: false,
					disableOnInteraction: false,
				}, 
			})
			kkksc03.el.onmouseover = function(){
				kkksc03.autoplay.stop();
			}
			kkksc03.el.onmouseout = function(){
				kkksc03.autoplay.start();
			}
		}
	});
	xhr.open("POST", commentBarrageConfig.twikooUrl);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(data);
}
function commentLinkFilter(data){
	data.sort((a,b)=>{
		return a.created - b.created;
	})
	let newData = [];
	data.forEach(item=>{
		newData.push(...getCommentReplies(item));
	});
	return newData;
}
function getCommentReplies(item){
	if(item.replies){
		let replies = [item];
		item.replies.forEach(item=>{
			replies.push(...getCommentReplies(item));
		})
		return replies;
	}else{
		return [];
	}
}
function popCommentBarrage(data){
	let barrage = document.createElement('div');
	let width = commentBarrageConfig.dom.clientWidth;
	let height = commentBarrageConfig.dom.clientHeight;
	barrage.className = 'comment-barrage-item'
	let ran = Math.floor(Math.random()*commentBarrageConfig.lightColors.length)
	document.getElementById("barragesColor").innerHTML=`[data-theme='light'] .comment-barrage-item { background-color:${commentBarrageConfig.lightColors[ran][0]};color:${commentBarrageConfig.lightColors[ran][1]}}[data-theme='dark'] .comment-barrage-item{ background-color:${commentBarrageConfig.darkColors[ran][0]};color:${commentBarrageConfig.darkColors[ran][1]}}`;
	if(data.avatar!=undefined){
		if(data.link!=undefined){
			if(!checkURL(data.link)){
				data.link="http://"+data.link;
			}
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="${data.avatar}"/>
				<a href="${data.link}" class="barrageNick" target="_blank">${data.nick}</a>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			`
		}
		else{
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="${data.avatar}"/>
				<div class="barrageNick">${data.nick}</div>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			`
		}
	}
	else{
		if(data.link!=undefined){
			if(!checkURL(data.link)){
				data.link="http://"+data.link;
			}
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="https://${commentBarrageConfig.avatarCDN}/avatar/${data.mailMd5}?d=${commentBarrageConfig.noAvatarType}"/>
				<a href="${data.link}" class="barrageNick" target="_blank">${data.nick}</a>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			`
		}
		else{
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="https://${commentBarrageConfig.avatarCDN}/avatar/${data.mailMd5}?d=${commentBarrageConfig.noAvatarType}"/>
				<div class="barrageNick">${data.nick}</div>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			`
		}
	}
	barrageContent=document.createElement('a');
	barrageContent.className="barrageContent";
	barrageContent.href="#"+data.id;
	barrageContent.innerHTML=data.comment;
	barrage.appendChild(barrageContent);
	aswiper = document.createElement('div');
	aswiper.className="swiper-slide";
	aswiper.setAttribute("style","height: 150px;");
	aswiper.append(barrage);
	commentBarrageConfig.dom.append(aswiper);
}
switchCommentBarrage = function () {
	localStorage.setItem("isBarrageToggle",Number(!Number(localStorage.getItem("isBarrageToggle"))))
	if(!isInViewPortOfOne(document.getElementById("post-comment"))){
	commentBarrageConfig.displayBarrage=!(commentBarrageConfig.displayBarrage);
    let commentBarrage = document.querySelector('.comment-barrage');
    if (commentBarrage) {
        $(commentBarrage).fadeToggle()
    }
}

}
if(localStorage.getItem("isBarrageToggle")==undefined){
	localStorage.setItem("isBarrageToggle","0");
}else if(localStorage.getItem("isBarrageToggle")=="1"){
	localStorage.setItem("isBarrageToggle","0");
	switchCommentBarrage()
}
initCommentBarrage()
}
```

`commentBarrage.css`:

```css
/* .comment-barrage {
	
	display: flex;
	flex-direction: column;
	justify-content: end;
	align-items: flex-end;
} */
.barrageswiper{
	position: fixed;
	margin: 0 0 30px 10px;
	z-index: 100;
	bottom: 10px;
	right: 55px;
}
@media screen and (max-width: 768px) {
	.comment-barrage {
		display: none;
	}
}
.comment-barrage .swiper-slide{
	position: relative;
	width: 250px;
}
.comment-barrage-item {
	position: absolute;
	bottom: 5px;
	width: 100%;
	min-height: 80px;
	max-height: 140px;
	height: min-content;
	margin: 4px 0;
	padding: 8px;
	background: rgba(0, 0, 0, 0.9);
	backdrop-filter: blur(20px) saturate(180%);
	border-radius: 8px;
	color: #fff;
	transition: 1s;
	display: flex;
	flex-direction: column;
	border: 1px solid rgba(255, 255, 255, 0.2);
	box-shadow: var(--heo-shadow-border);
}


.comment-barrage-item.out {
	opacity: 0;
}

/* @keyframes barrageIn {
	0% {
		transform: translateY(20%);
		-webkit-transform: translateY(20%);
		-moz-transform: translateY(20%);
		-ms-transform: translateY(20%);
		-o-transform: translateY(20%);
		opacity: 0;
}
	100% {
		transform: translateY(0%);
		-webkit-transform: translateY(0%);
		-moz-transform: translateY(0%);
		-ms-transform: translateY(0%);
		-o-transform: translateY(0%);
		opacity: 1;
	}
} */



.comment-barrage-item .barrageHead {
	height: 30px;
	padding: 0;
	line-height: 30px;
	font-size: 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.3);
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.comment-barrage-item .barrageAvatar {
	width: 16px;
	height: 16px;
	margin: 0;
	border-radius: 50%;
}

.comment-barrage-item .barrageContent {
	font-size: 14px;
	height: calc(100% - 30px);
	overflow: scroll;
}

.comment-barrage-item .barrageContent::-webkit-scrollbar {
	height: 0;
	width: 4px;
}

.comment-barrage-item .barrageContent::-webkit-scrollbar-button {
	display: none;
}
.barrageContent:not(.barrageContent:hover),.barrageNick:not(.barrageNick:hover){
	color:var(--global-font-color)!important;
}
.barrageswiper{
	height: 150px;
}
.comment-barrage-item p{
	line-height: 1.2;
	
}
```

# bbtalkLunboer

![](https://bu.dusays.com/2023/01/20/63ca131a84ea6.webp)

bbTalk已经停止维护且无官方的轮播插件，但是因为方便我还是在用，轮播我自己写了一个，之前的版本因为过于屎山与毒瘤并没有放出来，这次进行了pjax&swiper重构。

支持日期展示、自动链接替换(22.12.9 upd)，目前依然有部分bug：

![](https://bu.dusays.com/2023/01/20/63ca131b94254.webp)

![](https://bu.dusays.com/2023/01/20/63ca131ca18a2.webp)

ps：因为部分内容过于远古，甚至是刚搞博客就有的，所以可能会有诸多bug，窝不负责 awa

22.12.16 upd:修复部分bug，更改显隐逻辑

跟上面同理，基于swiper`5.4.5`。

请先自行引入`leancloud-av`:

```html
<script src="https://gcore.jsdelivr.net/npm/leancloud-storage@4.13.4/dist/av-min.js"></script>
```

`bbtalklunbo.js`:

```js
//bbtalkLunboer v2.0 By Ariasaka
AV.init({
    appId: "{YOUR_APPID}",
    appKey: "{YOUR_APPKEY}",
    serverURL: "{YOUR_URL}", //改成自己的，在设置->域名绑定
});
function lunbo(){
    var speaks=[];
const query = new AV.Query('content');
Date.prototype.Format = function (fmt) {
    var o = {
    "M+": this.getMonth() + 1, //月份
    "d+": this.getDate(), //日
    "H+": this.getHours(), //小时
    "m+": this.getMinutes(), //分
    "s+": this.getSeconds(), //秒
    "q+": Math.floor((this.getMonth() + 3) / 3), //季度
    "S": this.getMilliseconds() //毫秒
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
    if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
    }
query.find().then((talks) => {
    dat=new Date()
    for(i=talks.length;i>=talks.length-31;i--){
        var usedTime = Date.parse(dat) - Date.parse(talks[i]["createdAt"]);
        var days = Math.floor(usedTime / (24 * 3600 * 1000));
        var leave1 = usedTime % (24 * 3600 * 1000);  
        var hours = Math.floor(leave1 / (3600 * 1000));
        var leave2 = leave1 % (3600 * 1000);     
        var minutes = Math.floor(leave2 / (60 * 1000));
        var bbcontent=talks[i]["attributes"]["content"].replace(/<[^>]+>/g, "").replace(/<[^>]+>/g, "").replace(/(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\*\+,;=.]+\.(png|jpg|jpeg|webp)/g,"[图片]").replace(/(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\*\+,;=.]+/g,"[链接]");
        if(days>31){
            speaks.push(String(talks[i]["createdAt"].Format("yyyy-MM-dd"))+"："+bbcontent)
        }
        else if(days>0){
            speaks.push(String(days)+" 天前："+bbcontent);
        }
        else if(hours>0){
            speaks.push(String(hours)+" 小时前："+bbcontent);
        }
        else{
            speaks.push(String(minutes)+" 分钟前："+bbcontent);
        }
    }
    document.querySelector(".shuoshuo").innerHTML=""
    for(i=1;i<speaks.length;i++){
        var ch=document.createElement("div");
        ch.className="swiper-slide bbtalks";
        ch.innerHTML=speaks[i];
        document.querySelector(".shuoshuo").appendChild(ch)
    }
    var fxxkccf = new Swiper("#speaks-content", {
        loop: true,
        direction: "vertical",
        autoplay: {
            delay: 5000,
            disableOnInteraction: false, //暴戻语言 禁赛三年行为[doge]
        },
        mousewheel:true,
    })
    fxxkccf.el.onmouseover = function(){
        fxxkccf.autoplay.stop();
    }
    fxxkccf.el.onmouseout = function(){
        fxxkccf.autoplay.start();
    }
});
    
}
document.addEventListener('pjax:complete', (e) => {
lunbo();
})
document.addEventListener('DOMContentLoaded', (e) => {
    lunbo();
    })

```

pug更改：

在一个合适的地方（因为我自己的比较特殊，建议在`[blogRoot]\themes\acryple\layout\includes\mixins\post-ui.pug`的第二行插入这句（注意缩进），编写：

```py
include speaks.pug
```

同级目录新建speaks.pug：

```py
a(id="speaks" class="recent-post-item swiper-container" style="width:100%;height:auto;padding:10px;display:flex;" href="/speaks/")         
    i(class="fas fa-comment-alt" style="margin-top:10px")
    #speaks-content
        .shuoshuo.swiper-wrapper 博主说说
    i(class="fa fa-arrow-right" style="margin-top:10px")
```

然后添加css：

```css
[data-theme='light'] #speaks{
    color:var(--lyx-black);
    font-size:18px;
    border: 1px solid var(--lyx-border);
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);
    background-color: var(--lyx-white-acrylic1)!important;
    border-radius: 12px;
    margin-top:20px;
    margin-bottom: 10px;
}
[data-theme='dark'] #speaks{
    color:var(--lyx-white);
    font-size:18px;
    border: 1px solid var(--lyx-border);
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);
    border-radius: 12px;
    background-color: var(--lyx-black-acrylic2)!important;
    margin-top:20px;
    margin-bottom:10px;
}
#speaks:hover{
    border: 1px solid var(--lyx-theme);
    box-shadow:0 0 3px var(--lyx-theme)!important;
    
}
#speaks i{
    margin-right:10px;
    margin-left:10px;
}
#speaks{
    height: 56px!important;
}
.shuoshuo{
    flex:1;
    text-align: center;
}
.shuoshuo{
    transition-property: background-color,color,padding,font-size,border;
    transition-duration: 200ms;
}
.shuoshuo:hover{
    color:var(--lyx-theme); /*换成自己的颜色*/
}
.shuoshuo{
    white-space: nowrap;
} 
#speaks-content{
    max-width: 100%;
    overflow: hidden;
}
```

# 适配pjax

真的真的是大工程！！！

参考：

{% link 适配指北：我是怎么适配PJAX的,Ariasakaの小窝,https://blog.yaria.top/posts/30bce1d1/ %}

{% link pjax无法生效解决办法，butterfly主题维护你的pjax,Heo,https://blog.zhheo.com/p/3e567fa7.html %}

{% link Butterfly 安裝文檔(四) 主題配置-2,Butterfly,https://butterfly.js.org/posts/ceeb73f/#Pjax %}

# Ariasaka Console v0.1

![](https://bu.dusays.com/2023/01/20/63ca131dc145e.webp)
![](https://bu.dusays.com/2023/01/20/63ca131ecde9f.webp)

重构的博客设置，性能和ui美观度均有提高（目前仍有部分bug欢迎反馈）

注意与Leonus的切换背景有冲突。

新版博客设置进行了分区改造，把rightside全部转移到此，优化样式，性能优化，以及进行了前后端分离。

请先阅读这篇[之前的文章](https://blog.yaria.top/posts/ac792cf4/#%E5%8D%9A%E5%AE%A2%E8%AE%BE%E7%BD%AE)来参考修改

功能：
1. 自动主题切换
2. 左右栏切换
3. 把aside迁移了过来，请根据自己需求调整，并且隐藏默认aside
4. 切换背景，参考[Leonus](https://blog.leonus.cn/2022/bg2.html)
5. 切换字体，其实这个很费流量和速度
6. 切换主题，根据自己站的需求来加，可以删了
7. 其它的个性化设置（落樱特效参考下面）
8. 网站统计

(其中自动主题色和固定导航栏没写好)

新建`[blogRoot]/themes\acryple\layout\includes\setting.pug`：

```py
html
body
    #settingWindow.js-pjax
        span.setting-title 
            span#stt 控制面板
            a(id="close-console" onclick="toggleWinbox();") ×
        button#backer(onclick='$(\'.asetting\').hide();$(\'.settingx\').show();$(\'#backer\').hide()')
            i.fa.fa-chevron-left
            span 返回
        .settings
            #setting-buttons
                button.settingx(onclick='$(\'#theme-settings\').show();$(\'.settingx\').hide();$(\'#backer\').show();')
                    i.fas.fa-layer-group
                    span 外观
                button.settingx(onclick='$(\'#font-settings\').show();$(\'.settingx\').hide();$(\'#backer\').show();')
                    i.fa.fa-font
                    span 字体
                button.settingx(onclick='$(\'#background-settings\').show();$(\'.settingx\').hide();$(\'#backer\').show();')
                    i.far.fa-image
                    span 背景
                button.settingx(onclick='$(\'#con-echarts\').show();$(\'.settingx\').hide();$(\'#backer\').show();var evt = document.createEvent("HTMLEvents");evt.initEvent("resize", false, false);window.dispatchEvent(evt);')
                    i.fas.fa-chart-pie
                    span 统计
                button.settingx(onclick='$(\'#con-abouts\').show();$(\'.settingx\').hide();$(\'#backer\').show();')
                    i.fa.fa-cloud-download
                    span 关于
            #setting-hides
                #theme-settings.asetting
                    h2.content-head 性能设置
                    p
                        .content(style='display:flex')
                            input#blur(type='checkbox', onclick='setBlur()')
                            .content-text 禁用模糊效果
                        //- .content(style='display:flex')
                        //-     input#yjjs(type='checkbox', onclick='yjjs1()')
                        //-     .content-text 硬件加速
                        .content(style='display:flex')
                            input#fpson(type='checkbox', onclick='fpssw()' style="flex-shrink: 0")
                            .content-text
                                span 开启帧率检测（
                                a(href='javascript:window.location.reload()') 刷新
                                span 后生效）
                    p
                        h2.content-head 主题设置
                        //- .content(style='display:flex')
                        //-     input#hideAside(type='checkbox', onclick='toggleRightside()')
                        //-     .content-text 隐藏侧边栏
                        .content(style='display:flex')
                            input#hideAplayer(type='checkbox', onclick='toggleAplayer()')
                            .content-text 显示aplayer
                        .content(style='display:flex')
                            input#hideSakura(type='checkbox', onclick='toggleSakuras()')
                            .content-text 落樱特效
                        .content(style='display:flex')
                            input#autoTheme(type='checkbox', onclick='toggleAutoTheme()')
                            .content-text 明暗模式自动切换
                        .content(style='display:flex')
                            input#autoColor(type='checkbox', onclick='autoColor()')
                            .content-text 自动主题色（跟随文章封面）
                        | 未完工
                        .content(style='display:flex')
                            input#hideAplayer(type='checkbox', onclick='toggleNav()')
                            .content-text 固定导航栏
                        | ###
                        .content(style='display:flex')
                            button.content-button(onclick='switchTheme()') 切换主题
                          
                    p
                        h3.content-head 主题色
                        #themeColorSettings.content(style='display:flex')
                            input#red(type='radio', name='colors', onclick='setColor(\'red\')')
                            input#orange(type='radio', name='colors', onclick='setColor(\'orange\')')
                            input#yellow(type='radio', name='colors', onclick='setColor(\'yellow\')')
                            input#green(type='radio', name='colors', onclick='setColor(\'green\')')
                            input#blue(type='radio', name='colors', onclick='setColor(\'blue\')')
                            input#heoblue(type='radio', name='colors', onclick='setColor(\'heoblue\')')
                            input#darkblue(type='radio', name='colors', onclick='setColor(\'darkblue\')')
                            input#purple(type='radio', name='colors', onclick='setColor(\'purple\')')
                            input#pink(type='radio', name='colors', onclick='setColor(\'pink\')', checked)
                            input#black(type='radio', name='colors', onclick='setColor(\'black\')')
                            input#blackgray(type='radio', name='colors', onclick='setColor(\'blackgray\')')
                #font-settings.asetting
                    h2.content-head 字体设置
                    p#swfs
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'HYTMR\'!important;color:black', onclick='setFont(\'HYTMR\')') 汉仪唐美人
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'HYPailou\'!important;color:black', onclick='setFont(\'HYPailou\')') 汉仪新蒂牌楼
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'FZXJLJ\'!important;color:black', onclick='setFont(\'FZXJLJ\')') 方正金陵体
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'FZXS\'!important;color:black', onclick='setFont(\'FZXS\')') 方正像素体
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'ZhuZiAWan\'!important;color:black', onclick='setFont(\'ZhuZiAWan\')') 筑紫A丸ゴシック
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'FZODZK\'!important;color:black', onclick='setFont(\'FZODZK\')') 方正欧蝶正楷
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'Source Serif\'!important;color:black', onclick='setFont(\'Source Serif\')') 思源宋体
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:\'Source Sans\'!important;color:black', onclick='setFont(\'Source Sans\')') 思源黑体
                        br
                        a.swf(href='javascript:;', rel='noopener external nofollow', style='font-family:-apple-system, IBM Plex Mono ,monosapce,\'微软雅黑\', sans-serif;', onclick='setFont(\'main\')') 系统默认
                        br
                #background-settings.asetting
                    h2(style='margin-left:10px') 背景设置
                    div
                    span 注意:切换背景功能仅在Acrylic主题中生效，在Simple主题中无效
                    button.content-button(onclick='localStorage.removeItem(\'blogbg\');location.reload();')
                        i.fa-solid.fa-arrows-rotate
                        span  点我恢复默认背景
                    button.content-button(onclick='switchTheme()') 切换主题
                    h3 图片（手机）
                    .bgbox
                        a.pimgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6d4d539a5.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6d4d539a5.webp)\')')
                        a.pimgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6d4e15c9d.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6d4e15c9d.webp)\')')
                        a.pimgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6f22c03c6.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6f22c03c6.webp)\')')
                        a.pimgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6d56c83eb.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6d56c83eb.webp)\')')
                        a.pimgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6d50b439b.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6d50b439b.webp)\')')
                    h3 图片（电脑）
                    .bgbox
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6d5574d0e.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6d5574d0e.webp)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6d529adf9.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6d529adf9.webp)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d6d5159b31.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d6d5159b31.webp)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d718bbeef6.webp)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d718bbeef6.webp)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d72f237d19.jpg)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d72f237d19.jpg)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d72f2032c8.jpg)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d72f2032c8.jpg)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2021/12/01/7792ff0082ec4.jpg)', onclick='changeBg(\'url(https://bu.dusays.com/2021/12/01/7792ff0082ec4.jpg)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d72ee6d4f3.png)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d72ee6d4f3.png)\')')
                        a.imgbox(href='javascript:;', rel='noopener external nofollow', style='background-image:url(https://bu.dusays.com/2022/08/30/630d72ed76532.jpg)', onclick='changeBg(\'url(https://bu.dusays.com/2022/08/30/630d72ed76532.jpg)\')')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://bu.dusays.com/2022/09/17/6324aea549be6.webp)\')')
                            img(src='https://bu.dusays.com/2022/09/17/6324aea549be6.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://bu.dusays.com/2022/09/17/6324aec701a68.webp)\')')
                            img(src='https://bu.dusays.com/2022/09/17/6324aec701a68.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://bu.dusays.com/2022/09/17/6324aef4a5543.webp)\')')
                            img(src='https://bu.dusays.com/2022/09/17/6324aef4a5543.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://bu.dusays.com/2022/09/17/6324af3622884.webp)\')')
                            img(src='https://bu.dusays.com/2022/09/17/6324af3622884.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/5.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/5.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/6.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/6.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/7.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/7.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://bu.dusays.com/2022/12/08/6391b77ed767c.png)\')')
                            img(src='https://bu.dusays.com/2022/12/08/6391b77ed767c.png')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/9.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/9.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/10.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/10.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/11.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/11.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/12.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/12.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/13.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/13.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/14.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/14.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/15.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/15.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/16.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/16.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/17.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/17.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/18.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/18.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/19.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/19.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/20.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/20.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/21.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/21.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/22.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/22.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/23.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/23.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/24.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/24.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/25.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/25.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/26.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/26.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/27.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/27.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/28.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/28.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/29.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/29.webp')
                        a.imgbox(href='javascript:;', onclick='changeBg(\'url(https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/30.webp)\')')
                            img(src='https://cdn.afdelivr.top/npm/saiodgm-api@1.0.1/randomimg-my/30.webp')
                    h3 渐变色
                    .bgbox
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(to right, #eecda3, #ef629f)', onclick='changeBg(\'linear-gradient(to right, #eecda3, #ef629f)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(to right, #B7D31E, #42CE1E)', onclick='changeBg(\'linear-gradient(to right, #B7D31E, #42CE1E)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(to right, #06DE86, #06A5DE)', onclick='changeBg(\'linear-gradient(to right, #06DE86, #06A5DE)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(to right, #189BC4, #183DC4)', onclick='changeBg(\'linear-gradient(to right, #189BC4, #183DC4)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(to right, #C018C4, #C41818)', onclick='changeBg(\'linear-gradient(to right, #C018C4, #C41818)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(to right, #8B00BB, #030094)', onclick='changeBg(\'linear-gradient(to right, #8B00BB, #030094)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(to right, #eecda3, #ef629f)', onclick='changeBg(\'linear-gradient(to right, #eecda3, #ef629f)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(90deg, #ffd7e4 0%, #c8f1ff 100%)', onclick='changeBg(\'linear-gradient(90deg, #ffd7e4 0%, #c8f1ff 100%)\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: linear-gradient(45deg, #e5737b, #c6999e, #96b9c2, #00d6e8)', onclick='changeBg(\'linear-gradient(45deg, #e5737b, #c6999e, #96b9c2, #00d6e8)\')')
                    h3 纯色
                    .bgbox
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #7D9D9C', onclick='changeBg(\'#7D9D9C\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #fff', onclick='changeBg(\'#fff\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #49A6E9', onclick='changeBg(\'#49A6E9\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #F7CEFF', onclick='changeBg(\'#F7CEFF\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #FFFFCE', onclick='changeBg(\'#FFFFCE\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #CFFFCE', onclick='changeBg(\'#CFFFCE\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #17EFE9', onclick='changeBg(\'#17EFE9\')')
                        a.box(href='javascript:;', rel='noopener external nofollow', style='background: #9F17EF', onclick='changeBg(\'#9F17EF\')')
                #con-echarts.asetting
                    h1 文章统计
                    h2 监控
                    iframe(src="https://status.yaria.top" width="100%" height="500px" frameborder="no")
                    if !is_page()
                        h2 文章统计
                        script(src="https://npm.elemecdn.com/echarts@4.9.0/dist/echarts.min.js")
                        div(id="posts-chart" data-start="2021-01" style="border-radius: 8px; height: 300px; padding: 10px;")
                        div(id="tags-chart" data-length="10" style="border-radius: 8px; height: 300px; padding: 10px;")
                        div(id="categories-chart" data-parent="true" style="border-radius: 8px; height: 300px; padding: 10px;")
                    h2 访问统计
                        | 显示不出来请刷新页面
                        //-下面换成自己的51la统计
                
                #con-abouts.asetting
                    h1 关于
                    | Hexo-theme-Acryple v1.1.4
                    br
                    | Ariasaka Console v1.0
                    br
                    | 欢迎
                    a(href="/messageboard")
                        | 反馈！
        #setting-sidesl
            button(title="恢复默认设置" class="reSettings con-rightside")
                i.fa.fa-repeat
            #setting-sides
                button(title="繁简转换" class="con-rightside" id="con-translate"  onclick="javascript:rmf.translate();")
                    i.iconfont.icon-fanti
                button(title="昼夜切换" class="con-rightside" id="con-mode" onclick="switchDarkMode();")
                    i.fa.fa-adjust
                if is_post()||is_page()
                    button(title="阅读模式" class="con-rightside" id="con-reading" onclick="rmf.switchReadMode();")
                        i.fa.fa-book-open
                if !is_page()
                    button(title="单双栏切换" class="con-rightside" id="con-toggleaside" onclick="toggleAside();")
                        i.fas.fa-arrows-alt-h
                if !is_page()
                    button(title="左右栏切换" class="con-rightside" id="con-toggleleftaside" onclick="switchAside();")
                        i.fas.fa-binoculars
                if is_post()||is_page()
                    button(title="开关弹幕" class="con-rightside" id="con-barrage" onclick="switchCommentBarrage();")
                        i.iconfont.icon-danmu
                button(title="全屏" class="con-rightside" id="con-fullscreen" onclick="fullScreen();")
                    i.fas.fa-expand
            
```



js部分：

```javascript
document.addEventListener('pjax:complete', tosetting);
document.addEventListener('DOMContentLoaded', tosetting);
function tosetting(){
$("#settingWindow").hide();
if(localStorage.getItem("blur")=="false"){
    blur=0;
    }else{
        blur=1;
    
    }
    if(localStorage.getItem("yjjs")=="true"){
        yjjs=1;
    }else{
        yjjs=0;
        
    }
    if(localStorage.getItem("fpson")==undefined){
        localStorage.setItem("fpson","1");
    }
if(!blur){
    document.getElementById("settingStyle").innerText=`
    *,*:not(.card-info)::before,*::after{
        -webkit-backdrop-filter: none!important;
        backdrop-filter: none!important;
        -webkit-filter: none!important;
        filter: none!important;
    }`}
    else{
        document.getElementById("settingStyle").innerText=''
    }
setBlur=function(){
    blur=!blur;
    localStorage.setItem("blur",blur);
    if(!blur){
    document.getElementById("settingStyle").innerText=`
    *{
        -webkit-backdrop-filter: none!important;
        backdrop-filter: none!important;
        -webkit-filter: none!important;
        filter: none!important;
    }`}
    else{
        document.getElementById("settingStyle").innerText=''
    }
}
// if(yjjs){
//     document.getElementById("yjjs").innerText=`
//     *:not(#web_bg){
//         transform:translateZ(0);
//         backface-visibility: hidden
//     }`}
//     else{
//         document.getElementById("yjjs").innerText=``
//     }
yjjs1=function(){
    yjjs=!yjjs;
    localStorage.setItem("yjjs",yjjs)
    // if(yjjs){
    // document.getElementById("yjjs").innerText=`
    // *:not(#web_bg){
    //     transform:translateZ(0);
    //     backface-visibility: hidden
    // }`}
    // else{
    //     document.getElementById("yjjs").innerText=``
    // }
}
if(localStorage.getItem("blogTheme")=="acrylic"){
    document.getElementById("css").href="";
}
switchTheme=function(){
    if(document.getElementById("css").href==window.location.protocol+"//"+window.location.host+"/css/stylessimple.css"){
        document.getElementById("css").href=""
        localStorage.setItem("blogTheme","acrylic");
    }else{
        document.getElementById("css").href="/css/stylessimple.css"
        localStorage.setItem("blogTheme","simple");
    }
}
setColor=function(c){
    document.getElementById("themeColor").innerText=`:root{--lyx-theme:var(--lyx-${c})!important}`;
    localStorage.setItem("themeColor",c);

}
setFont=function(n){
    localStorage.setItem("font",n);
    if(n=="main"){
        var s=document.querySelectorAll("body,.aplayer")
        for(var i = 0; i <s.length; i++) {
            s[i].style.fontFamily="-apple-system, IBM Plex Mono ,monospace,'微软雅黑', sans-serif"
        }
    }
    else if(n=="HYPailou"){
        var s=document.querySelectorAll("body,.aplayer")
        for(var i = 0; i <s.length; i++) {
            s[i].style.fontFamily="Fredoka,HYPailou,KyoukashoProL,-apple-system, IBM Plex Mono ,monospace,'微软雅黑', sans-serif"
        }
    }
    else{
        var s=document.querySelectorAll("body,.aplayer")
        for(var i = 0; i <s.length; i++) {
            s[i].style.fontFamily="var(--global-font),KyoukashoProL,-apple-system, IBM Plex Mono ,monosapce,\"微软雅黑\", sans-serif"
        }
        document.body.style.fontFamily="var(--global-font),KyoukashoProL,-apple-system, IBM Plex Mono ,monosapce,'微软雅黑', sans-serif"
        document.documentElement.style.setProperty('--global-font', n)
    }
}
if(localStorage.getItem("themeColor")==undefined){
    localStorage.setItem("themeColor","pink");
}

setColor(localStorage.getItem("themeColor"));



if(localStorage.getItem("hideRightside")==undefined){
    localStorage.setItem("hideRightside","0");
}

if(localStorage.getItem("hideRightside")=="1"){
    $("#rightside").toggle()
}
toggleRightside=function(){
    $("#rightside").toggle();
    localStorage.setItem("hideRightside",Math.abs(Number(localStorage.getItem("hideRightside"))-1))
}
if(localStorage.getItem("font")==undefined){
    localStorage.setItem("font","HYTMR")
}
setFont(localStorage.getItem("font"))
// 存数据
// name：命名 data：数据
saveData=function(name, data) {
    localStorage.setItem(name, JSON.stringify({ 'time': Date.now(), 'data': data }))
}

// 取数据
// name：命名 time：过期时长,单位分钟,如传入30,即加载数据时如果超出30分钟返回0,否则返回数据
loadData=function(name, time) {
    let d = JSON.parse(localStorage.getItem(name));
    // 过期或有错误返回 0 否则返回数据
    if (d) {
        let t = Date.now() - d.time
        if (t < (time * 60 * 1000) && t > -1) return d.data;
    }
    return 0;
}
// 切换背景函数
// 此处的flag是为了每次读取时都重新存储一次,导致过期时间不稳定
// 如果flag为0则存储,即设置背景. 为1则不存储,即每次加载自动读取背景.
changeBg=function(s, flag) {
    let bg = document.getElementById('web_bg')
    if (s.charAt(0) == '#') {
        bg.style.backgroundColor = s
        bg.style.backgroundImage = 'none'
    } else bg.style.backgroundImage = s
    if (!flag) { saveData('blogbg', s) }
}
// 上面两个函数如果你有其他需要存取数据的功能，也可以直接使用

// 读取背景
try {
    let data = loadData('blogbg', 1440)
    if (data) changeBg(data, 1)
    else localStorage.removeItem('blogbg');
} catch (error) { localStorage.removeItem('blogbg'); }



fpssw=function(){
    if(localStorage.getItem("fpson")=="1"){
        localStorage.setItem("fpson","0");
    }else{
        localStorage.setItem("fpson","1");
    }
}
$(".asetting").hide();
$('#backer').hide();
$("#"+localStorage.getItem("themeColor")).attr("checked", true);
if(localStorage.getItem("blur")=="false"){
    document.getElementById("blur").checked=true;
}
if(localStorage.getItem("yjjs")=="true"){
    document.getElementById("yjjs").checked=true;
}
if(localStorage.getItem("fpson")=="1"){
    document.getElementById("fpson").checked=true;
}


if(localStorage.getItem("sakurahide")=="false"){
    document.getElementById("hideSakura").checked=true;
    isSakura=1;
}
else if(localStorage.getItem("sakurahide")==null){
    localStorage.setItem("sakurahide","false");
    document.getElementById("hideSakura").checked=true;
    isSakura=1;
}
else{
    setTimeout(
    stopp,1000);
    isSakura=0;
}
if(localStorage.getItem("aplayerhide")=="false"){
    document.getElementById("hideAplayer").checked=true;
}
else if(localStorage.getItem("aplayerhide")==null){
    localStorage.setItem("aplayerhide","false");
    document.getElementById("hideAplayer").checked=true;
}
else{
    doStuff=function() {
        flag=0;
        try{
            ap=aplayers[0];
            ap.list;
            flag=1;
        }catch{
            setTimeout(doStuff, 50);
            return;
        }
        if(flag){
            $(".aplayer-fixed").hide()
        }
    }
    doStuff();
    
}

document.getElementsByClassName("reSettings")[0].onclick=function(){
    localStorage.clear()
    window.location.reload()
}

toggleWinbox=function(){
    $("#settingWindow").fadeToggle();
    if(document.getElementById("settingWindow").style.display!="none"){
        document.getElementById("settingWindow").style.display="flex";
    }
}
fullScreen=function() {
    if (document.fullscreenElement) document.exitFullscreen()
    else document.documentElement.requestFullscreen();
}
toggleAside=function(){
    const $htmlDom = document.documentElement.classList
      $htmlDom.contains('hide-aside')
        ? saveToLocal.set('aside-status', 'show', 2)
        : saveToLocal.set('aside-status', 'hide', 2)
      $htmlDom.toggle('hide-aside')
}
toggleAplayer=function(){
    $(".aplayer-fixed").toggle()
    if(localStorage.getItem("aplayerhide")=="true"){
        localStorage.setItem("aplayerhide",false);
    }
    else{
        localStorage.setItem("aplayerhide",true);
    }
}
// position = $(window).scrollTop();
// $(window).scroll(function () {

//     scroll = $(window).scrollTop();
  
//     if (scroll > position) {
//       document.getElementsByTagName("header")[0].style.transform="translateY(58px)";
//     } else {
  
  
//         document.getElementsByTagName("header")[0].style.transform="";
  
//     }
  
//     position = scroll;
//   });
toggleSakuras=function(){
    isSakura=!isSakura;
    stopp(isSakura);
    if(localStorage.getItem("sakurahide")=="true"){
        localStorage.setItem("sakurahide",false);
    }
    else{
        localStorage.setItem("sakurahide",true);
    }
}
switchAside=function(){
    if(left){
        document.getElementById("aside-content").classList.add("right");
        document.querySelector(".layout > div:first-child").classList.add("left");
        localStorage.setItem("leftAside","false");
    }
    else{
        document.getElementById("aside-content").className="aside-content";
        document.querySelector(".layout > div:first-child").className="";
        try{
        document.querySelector("#recent-posts").className="recent-posts";
    }catch(err){}localStorage.setItem("leftAside","true");}
    left=!left;
}
left=1;
if(localStorage.getItem("leftAside")=="true"||localStorage.getItem("leftAside")==null){
    
}else{
    switchAside();
}
if(localStorage.getItem("autoTheme")=="true"){
    localStorage.setItem("autoTheme","false");
    document.getElementById("autoTheme").checked=true;
    var time=new Date();
    if(time.getHours()<=7||time.getHours()>=19){
        activateDarkMode()
        saveToLocal.set('theme', 'dark', 2)
        GLOBAL_CONFIG.Snackbar !== undefined && btf.snackbarShow(GLOBAL_CONFIG.Snackbar.day_to_night)
    }
    else{
        activateLightMode()
        saveToLocal.set('theme', 'light', 2)
        GLOBAL_CONFIG.Snackbar !== undefined && btf.snackbarShow(GLOBAL_CONFIG.Snackbar.night_to_day)
    }
}
if(location.href.indexOf('posts')!=-1){
    var xhr = new XMLHttpRequest();
    var url = document.querySelector('#page-header').style.backgroundImage.split('url("')[1].split('")')[0];
    xhr.open("GET","https://apis.yaria.top/api/imageColor?imgurl="+url, true);
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState===4) {
            if(xhr.status===200) {
                document.getElementById("themeColor").innerText=`:root{--lyx-theme:${xhr.responseText}!important}`;
            }
        }
    }
}
toggleAutoTheme=()=>{
    if(localStorage.getItem("autoTheme")=="true"){
        localStorage.setItem("autoTheme","false");
        $("#con-mode").show();
    }
    else{
        localStorage.setItem("autoTheme","true");
        var time=new Date();
        if(time.getHours()<=7||time.getHours()>=19){
            activateDarkMode()
            saveToLocal.set('theme', 'dark', 2)
            GLOBAL_CONFIG.Snackbar !== undefined && btf.snackbarShow(GLOBAL_CONFIG.Snackbar.day_to_night)
        }
        else{
            activateLightMode()
            saveToLocal.set('theme', 'light', 2)
            GLOBAL_CONFIG.Snackbar !== undefined && btf.snackbarShow(GLOBAL_CONFIG.Snackbar.night_to_day)
        }
        $("#con-mode").hide();
    }
}
}
switchDarkMode = function () {
    const nowMode = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
    if (nowMode === 'light') {
        activateDarkMode()
        saveToLocal.set('theme', 'dark', 2)
        GLOBAL_CONFIG.Snackbar !== undefined && btf.snackbarShow(GLOBAL_CONFIG.Snackbar.day_to_night)
    } else {
        activateLightMode()
        saveToLocal.set('theme', 'light', 2)
        GLOBAL_CONFIG.Snackbar !== undefined && btf.snackbarShow(GLOBAL_CONFIG.Snackbar.night_to_day)
    }
    // handle some cases
    typeof utterancesTheme === 'function' && utterancesTheme()
    typeof FB === 'object' && window.loadFBComment()
    window.DISQUS && document.getElementById('disqus_thread').children.length && setTimeout(() => window.disqusReset(), 200)
};
```

css:

```css
/*使用了Chrome105新特性has，兼容性不好qwq*/
.con-rightside{
    height:50px!important;
    width: 50px!important;
    border-radius: 30px;
    -webkit-border-radius: 30px;
    -moz-border-radius: 30px;
    -ms-border-radius: 30px;
    -o-border-radius: 30px;
    margin:10px;
    transition: all .3s;
    -webkit-transition: all .3s;
    -moz-transition: all .3s;
    -ms-transition: all .3s;
    -o-transition: all .3s;
}
.con-rightside:hover{
    background-color: rgba(129, 129, 129, 0.568);
}
.con-rightside i::before{
    font-size:30px;
}
[data-theme="dark"] .con-rightside i::before{
    color:white
}
.con-rightside:hover{
    background-color: rgba(129, 129, 129, 0.568);
}
@media screen and (max-width:600px){
    .con-rightside i::before{
        font-size: 16px;
    }
    .con-rightside{
        height:20px!important;
        width:20px!important;
    }
}
@media screen and (max-width:768px){
    #con-barrage{
        display: none!important;
    }   
}
#setting-buttons{
    display: flex;
    flex-wrap: wrap;
}
.setting-title{
    text-align: center;
    font-size: 30px;
    display: flex;
}
#setting-sides{
    margin-left: auto;
}
#setting-sides{
    white-space: nowrap;
}
#setting-sidesl{
    display: flex;
}
.settings .content{
    margin-left:20px;
}
.settings{
    margin:15px
}
/* 开关 */
.settings input[type="checkbox"] {
    width: 38px;
    height: 20px;
    position: relative;
    border: 1px solid #000000;
    background-color: #0000;
    border-radius: 12px;
    background-clip: content-box;
    display: inline-block;
    -webkit-appearance: none;
    user-select: none;
    outline: none;
transform: translateY(5px);}
[data-theme="dark"] .settings input[type="checkbox"] {
    border: 1px solid white;
}
.settings input[type="checkbox"]:before {
    content: '';
    width: 12px;
    height: 12px;
    position: absolute;
    top: 3px;
    left: 5px;
    border-radius: 10px;
    background-color: #000;}
[data-theme="dark"] .settings input[type="checkbox"]:before{
    background-color: white;
}
.settings input[type="checkbox"]:checked {
    background-color: var(--lyx-theme);border-color:var(--lyx-theme)}
.settings input[type="checkbox"]:checked:before {
    left: 19px;background-color: white!important;}

.settings input[type="checkbox"] {
    transition: border background-color box-shadow }
.settings input[type="checkbox"]:before {
    transition: left 0.2s;}
.settings input[type="checkbox"]:checked {
    background-color: var(--lyx-theme);
    /* transition: border ease 0.4s, background-color ease 1.2s; */
}.settings input[type="checkbox"]:checked:before {
    transition: left 0.2s;}
.settings input[type="checkbox"]:checked:hover{
    opacity: 0.8;
}
.settings input[type="checkbox"]:active{
    background-color: #666666!important;
    border-color:#666666!important;
}
.settings input[type="checkbox"]:active::before{
    background-color:white!important;
}
.settings{
    overflow: scroll;
    width: 100%;
}
#settingWindow{
    position: fixed;
    display: block;
    width: 80%;
    max-width: 800px;
    left: 50%;
    top: 50%;
    max-height: 80%;
    background-color: #ffffffdd;
    border-radius: 20px;
    -webkit-border-radius: 20px;
    -moz-border-radius: 20px;
    -ms-border-radius: 20px;
    -o-border-radius: 20px;
    border: 1px solid var(--lyx-border);
    padding:30px;
    backdrop-filter: blur(10px);
    -ms-transform-origin-y:translate(-50%,-50%);
    -webkit-transform:translate(-50%,-50%);
    -moz-transform:translate(-50%,-50%);
    -ms-transform:translate(-50%,-50%);
    -o-transform:translate(-50%,-50%);
    z-index: 514;
    display: none;
}
.settings{
    overflow: scroll;
    width: 100%;
}
#settingWindow{
    display: none;
    flex-direction: column;
}
.settingx{
    width: 46%;
    text-align: left;
    font-size: 28px;
    padding: 10px;
    margin: 10px;
    background-color: var(--lyx-light-grey);
    opacity: 0.8;
    border-radius: 10px;
}
.settingx:hover{
    background-color: var(--lyx-gray);
}
.settingx i{
    margin: 5px;
}
@media screen and (max-width:768px){
    .settingx{
        width:100%!important;
    }
}
.setting-title{
    text-align: center;
    font-size: 30px;
    display: flex;
}
#close-console{
    text-align: right;
}
#stt,#close-console{
    margin-left: auto;
}
#close-console:not(#close-console:hover){
    color: var(--global-font-color);
}
```

最后在`[blogRoot]/themes/butterfly/layout/includes/layout.pug`中添加：

```diff
...
include ./rightside.pug
!=partial('includes/third-party/search/index', {}, {cache: true})
+ !=partial('includes/setting',{}, {cache:false})
```

除此之外，还要引入一些外挂css标签，有些地方为了偷懒使用了jq，也需要加上:

```yaml
inject:
  head:
  - <style id="settingStyle"></style>
  - <style id="css"></style>
  - <style id="themeColor"></style>
  ...
  bottom:
  - <script type="text/javascript" src="https://gcore.jsdelivr.net/npm/jquery@latest/dist/jquery.min.js"></script>
  ...
```

# 全站存储桶静态化

来由是看到Mrzefr的服务推荐，看到了[缤纷云](https://bitiful.dogecast.com/)还不错，然后把字体扔上去。

{% link 推荐一些服务 (1),MrZefr,https://blog.mrzefr.cn/posts/recommend1/ %}

突然想到个点子，这个存储桶是国内浙江节点，且不用备案，收费不贵，免费够用，因为之前的NPM全站静态化因为目前能用的cdn太少（静态文件超100M，jsd系全挂）而放弃，故有此野路子手法。

这样做其实不如直接套CDN，唯一的优势是享受国内速度，但是不用备案

请先充分阅读并彻底理解本文章：

{% link SpeedUp!使用黑科技为你的网站提速,ChenYFan,https://blog.cyfan.top/p/d3c51290.html %}

## 上传网站

首先你需要想办法把网站传到存储桶上，你当然不会想着去手动更新，所以如果你使用Github actions上传的话，因为缤纷云这个存储桶兼容S3，直接使用AWS CLI即可。

不要看这么一点代码，可是翻遍全网资料才搞出来的，因为文档实在是太乱了。

在deploy的yml里面加入：
```yaml
    - name: Deploy static site to S3 bucket
      run: |
        export AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }}
        export AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }}
        export AWS_EC2_METADATA_DISABLED=true
        aws s3 sync --endpoint-url https://s3.ladydaily.com ./public s3://${{ secrets.AWS_BUCKET_NAME }}
```

### 创建key

你首先需要创建一个key，

在控制台的AccessKey里面创建一个用户，生成Key并保管好（只显示一次！！！）


![](https://bu.dusays.com/2023/01/20/63ca131fdce65.webp)

![](https://bu.dusays.com/2023/01/20/63ca1320f1ae7.webp)

![](https://bu.dusays.com/2023/01/20/63ca1322179ff.webp)

最后设置权限其实只用给写权限就行了。

### 设置secrets

给Actions加几个Secrets：

```conf
AWS_ACCESS_KEY_ID=你的Access Key
AWS_SECRET_ACCESS_KEY=你的Secret Key
AWS_BUCKET_NAME=你的Bucket名字
```

相信弄过Actions的各位童鞋们是一定有经验的，所以我就不加教程了。

## sw端

原理也是进行网站劫持，代码：

```javascript
const CACHE_NAME = 'ICDNCache';
let cachelist = [];
self.addEventListener('install', async function (installEvent) {
    self.skipWaiting();
    installEvent.waitUntil(
        caches.open(CACHE_NAME)
            .then(function (cache) {
                console.log('Opened cache');
                return cache.addAll(cachelist);
            })
    );
});
self.addEventListener('fetch', async event => {
    try {
        event.respondWith(handle(event.request))
    } catch (msg) {
        event.respondWith(handleerr(event.request, msg))
    }
});
const handleerr = async (req, msg) => {
    return new Response(`<h1>CDN分流器遇到了致命错误</h1>
    <b>${msg}</b>`, { headers: { "content-type": "text/html; charset=utf-8" } })
}
const lfetch = async (urls, url) => {
    let controller = new AbortController();
    const PauseProgress = async (res) => {
        return new Response(await (res).arrayBuffer(), { status: res.status, headers: res.headers });
    };
    if (!Promise.any) {
        Promise.any = function (promises) {
            return new Promise((resolve, reject) => {
                promises = Array.isArray(promises) ? promises : []
                let len = promises.length
                let errs = []
                if (len === 0) return reject(new AggregateError('All promises were rejected'))
                promises.forEach((promise) => {
                    promise.then(value => {
                        resolve(value)
                    }, err => {
                        len--
                        errs.push(err)
                        if (len === 0) {
                            reject(new AggregateError(errs))
                        }
                    })
                })
            })
        }
    }
    return Promise.any(urls.map(urls => {
        return new Promise((resolve, reject) => {
            fetch(urls, {
                signal: controller.signal
            })
                .then(PauseProgress)
                .then(res => {
                    if (res.status == 200) {
                        controller.abort();
                        resolve(res)
                    } else {
                        reject(res)
                    }
                })
        })
    }))
}
self.addEventListener('fetch', async event => {
    event.respondWith(handle(event.request))
});
const fullpath = (path) => {
    path = path.split('?')[0].split('#')[0]
    if (path.match(/\/$/)) {
        path += 'index'
    }
    if (!path.match(/\.[a-zA-Z]+$/)) {
        path += '.html'
    }
    return path
}

const handle = async(req)=>{
    const urlStr = req.url
    const urlObj = new URL(urlStr);
    const urlPath = urlObj.pathname;
    const domain = urlObj.hostname;
    //从这里开始
    if(domain === ""){//这里写你需要拦截的域名
        return lfetch(["{改成你的存储桶url}"+fullpath(urlPath)])//屏蔽了自带的npm劫持，改为存储桶劫持
    }
    else{
        return fetch(req);
    }
}
```

目前暂未实现缓存功能qaq。

# 新版rightMenu，支持遮罩


参考此文章，这篇文章已经进行了修改：

{% link butterfly博客自定义右键菜单升级版,Ariasakaの小窝,/posts/11eb4aac/ %}

# pace加载条

{% link 为你的Butterfly添加顶部加载进度条,Xlenco,https://xlenco.eu.org/posts/769f.html%}

# 落樱特效（搭配博客设置食用）

添加js（参考自[ichika](https://ichika.cc)）：

```javascript
//樱花

var stop, staticx;
var img = new Image();
img.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUgAAAEwCAYAAADVZeifAAAACXBIWXMAAACYAAAAmAGiyIKYAAAHG2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXBSaWdodHM9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9yaWdodHMvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcGhvdG9zaG9wLzEuMC8iIHhtcFJpZ2h0czpNYXJrZWQ9IkZhbHNlIiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6NDFDMjQxQjYyNjIwNjgxMTgwODNEMjE2MDAzOTU1NDQiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDozNDVjOWViOC04NDc4LTFkNDctOGRjMi0yZDkyOGNhYTYxZWQiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6YjAzN2ZiMGItNTU5Mi0xYjRkLWJjZGQtOWU4NGExMDJiMGM2IiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIFBob3Rvc2hvcCBDQyAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDE4LTA1LTA5VDE0OjQ5OjM3KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAxOC0wNS0wOVQxNDo1MToyNSswODowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAxOC0wNS0wOVQxNDo1MToyNSswODowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjEyMjVlZWE3LTEyY2QtMTY0NC04ZDAzLWFjOTE2ZTAxZDQ1YyIgc3RSZWY6ZG9jdW1lbnRJRD0idXVpZDoxRDIwNUFGNjZCRDlFNTExOUM5REMwMzg2RjlEQjFGNyIvPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDphYmMzNjIzMy1hOWNkLWNiNDQtODViYi0zZTgyMjEwYmIxMjYiIHN0RXZ0OndoZW49IjIwMTgtMDUtMDlUMTQ6NTE6MjUrMDg6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE4IChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6YjAzN2ZiMGItNTU5Mi0xYjRkLWJjZGQtOWU4NGExMDJiMGM2IiBzdEV2dDp3aGVuPSIyMDE4LTA1LTA5VDE0OjUxOjI1KzA4OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2Vx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";

function Sakura(x, y, s, r, fn) {
    this.x = x;
    this.y = y;
    this.s = s;
    this.r = r;
    this.fn = fn;
}

Sakura.prototype.draw = function(cxt) {
    cxt.save();
    var xc = 40 * this.s / 4;
    cxt.translate(this.x, this.y);
    cxt.rotate(this.r);
    cxt.drawImage(img, 0, 0, 35 * this.s, 35 * this.s)
    //樱花大小
    cxt.restore();
}

Sakura.prototype.update = function() {
    this.x = this.fn.x(this.x, this.y);
    this.y = this.fn.y(this.y, this.y);
    this.r = this.fn.r(this.r);
    if (this.x > window.innerWidth || this.x < 0 || this.y > window.innerHeight || this.y < 0) {
        this.r = getRandom('fnr');
        if (Math.random() > 0.4) {
            this.x = getRandom('x');
            this.y = 0;
            this.s = getRandom('s');
            this.r = getRandom('r');
        } else {
            this.x = window.innerWidth;
            this.y = getRandom('y');
            this.s = getRandom('s');
            this.r = getRandom('r');
        }
    }
}

SakuraList = function() {
    this.list = [];
}
SakuraList.prototype.push = function(sakura) {
    this.list.push(sakura);
}
SakuraList.prototype.update = function() {
    for (var i = 0, len = this.list.length; i < len; i++) {
        this.list[i].update();
    }
}
SakuraList.prototype.draw = function(cxt) {
    for (var i = 0, len = this.list.length; i < len; i++) {
        this.list[i].draw(cxt);
    }
}
SakuraList.prototype.get = function(i) {
    return this.list[i];
}
SakuraList.prototype.size = function() {
    return this.list.length;
}

function getRandom(option) {
    var ret, random;
    switch (option) {
    case 'x':
        ret = Math.random() * window.innerWidth;
        break;
    case 'y':
        ret = Math.random() * window.innerHeight;
        break;
    case 's':
        ret = Math.random();
        break;
    case 'r':
        ret = Math.random() * 6;
        break;
    case 'fnx':
        random = -0.5 + Math.random() * 1;
        ret = function(x, y) {
            return x + 0.5 * random - 0.6;
            //x轴速度
        }
        ;
        break;
    case 'fny':
        random = 0.8 + Math.random() * 0.7
        //y轴速度
        ret = function(x, y) {
            return y + random;
        }
        ;
        break;
    case 'fnr':
        random = Math.random() * 0.03;
        ret = function(r) {
            return r + random;
        }
        ;
        break;
    }
    return ret;
}

function startSakura() {

    requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.msRequestAnimationFrame || window.oRequestAnimationFrame;
    var canvas = document.createElement('canvas'), cxt;
    staticx = true;
    canvas.height = window.innerHeight;
    canvas.width = window.innerWidth;
    canvas.setAttribute('style', 'position: fixed;left: 0;top: 0;pointer-events: none;');
    canvas.setAttribute('id', 'canvas_sakura');
    document.getElementsByTagName('body')[0].appendChild(canvas);
    cxt = canvas.getContext('2d');
    var sakuraList = new SakuraList();
    for (var i = 0; i < 10; i++) {
        //樱花数量
        var sakura, randomX, randomY, randomS, randomR, randomFnx, randomFny;
        randomX = getRandom('x');
        randomY = getRandom('y');
        randomR = getRandom('r');
        randomS = getRandom('s');
        randomFnx = getRandom('fnx');
        randomFny = getRandom('fny');
        randomFnR = getRandom('fnr');
        sakura = new Sakura(randomX,randomY,randomS,randomR,{
            x: randomFnx,
            y: randomFny,
            r: randomFnR
        });
        sakura.draw(cxt);
        sakuraList.push(sakura);
    }
    stop = requestAnimationFrame(function() {
        cxt.clearRect(0, 0, canvas.width, canvas.height);
        sakuraList.update();
        sakuraList.draw(cxt);
        stop = requestAnimationFrame(arguments.callee);
    })
}

window.onresize = function() {
    var canvasSnow = document.getElementById('canvas_snow');
    canvasSnow.width = window.innerWidth;
    canvasSnow.height = window.innerHeight;
}

function stopp(e) {
    if (!e && document.getElementById("canvas_sakura")) {
        var child = document.getElementById("canvas_sakura");
        child.parentNode.removeChild(child);
        window.cancelAnimationFrame(stop);
    } else if (e && !document.getElementById("canvas_sakura")) {
        startSakura();
    }
}
window.addEventListener("DOMContentLoaded",
startSakura);
```

# fps显示
{% tabs %}
<!-- tab forNormal -->
```javascript
// if(window.localStorage.getItem("fpson")=="1"){
//如果要使博客设置上面的设置项能生效，就把上面一行取消注释
var rAF = function () {
    return (
        window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        function (callback) {
            window.setTimeout(callback, 1000 / 60);
        }
    );
}();
var frame = 0;
var allFrameCount = 0;
var lastTime = Date.now();
var lastFameTime = Date.now();
var loop = function () {
    var now = Date.now();
    var fs = (now - lastFameTime);
    var fps = Math.round(1000 / fs);
 
    lastFameTime = now;
    // 不置 0，在动画的开头及结尾记录此值的差值算出 FPS
    allFrameCount++;
    frame++;
 
    if (now > 1000 + lastTime) {
        var fps = Math.round((frame * 1000) / (now - lastTime));
        if(fps<=6){
            var kd=`<span style="color:#bd0000">卡成ppt</span>`
        }
        else if(fps<=10){
            var kd=`<span style="color:red">电竞级帧率</span>`
        }
        else if(fps<=14){
            var kd=`<span style="color:yellow">难受</span>`
        }
        else if(fps<24){
            var kd=`<span style="color:orange">卡</span>`
        }
        else if(fps<=40){
            var kd=`<span style="color:green">...</span>`
        }
        else{
            var kd=`<span style="color:#425aef">正常</span>`
        }
        document.getElementById("fps").innerHTML=`FPS:${fps} ${kd}`;
        frame = 0;
        lastTime = now;
    };
 
    rAF(loop);
}

loop();
// }
// else{$("#fps").hide()}

//如果要使博客设置上面的设置项能生效，就把上面两行取消注释

```
<!-- endtab -->
<!-- tab forPjax -->
```javascript
document.addEventListener('pjax:complete', fps);
document.addEventListener('DOMContentLoaded', fps);
function fps(){
// if(window.localStorage.getItem("fpson")=="1"){ 
//如果要使博客设置上面的设置项能生效，就把上面一行取消注释
var rAF = function () {
    return (
        window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        function (callback) {
            window.setTimeout(callback, 1000 / 60);
        }
    );
}();
var frame = 0;
var allFrameCount = 0;
var lastTime = Date.now();
var lastFameTime = Date.now();
var loop = function () {
    var now = Date.now();
    var fs = (now - lastFameTime);
    var fps = Math.round(1000 / fs);
 
    lastFameTime = now;
    // 不置 0，在动画的开头及结尾记录此值的差值算出 FPS
    allFrameCount++;
    frame++;
 
    if (now > 1000 + lastTime) {
        var fps = Math.round((frame * 1000) / (now - lastTime));
        if(fps<=6){
            var kd=`<span style="color:#bd0000">卡成ppt</span>`
        }
        else if(fps<=10){
            var kd=`<span style="color:red">电竞级帧率</span>`
        }
        else if(fps<=14){
            var kd=`<span style="color:yellow">难受</span>`
        }
        else if(fps<24){
            var kd=`<span style="color:orange">卡</span>`
        }
        else if(fps<=40){
            var kd=`<span style="color:green">...</span>`
        }
        else{
            var kd=`<span style="color:#425aef">正常</span>`
        }
        document.getElementById("fps").innerHTML=`FPS:${fps} ${kd}`;
        frame = 0;
        lastTime = now;
    };
 
    rAF(loop);
}

loop();
// }
// else{$("#fps").hide()}

//如果要使博客设置上面的设置项能生效，就把上面两行取消注释
}
```
<!-- endtab -->
{% endtabs %}

css:
```css
#fps{
    position: fixed;
    right:10px;
    bottom:4px;
    z-index: 1919810;
}

[data-theme="light"] #fps{
    background-color: var(--lyx-white-acrylic1);
    padding: 4px;
    border-radius: 4px;
    backdrop-filter: blur(10px);
}
[data-theme="dark"] #fps{
    background-color: var(--lyx-black-acrylic1);
    padding: 4px;
    border-radius: 4px;
    backdrop-filter: blur(10px);
}
```

然后在主题配置文件中插入：
```yaml
inject:
    head:
    ...
    bottom:
    - <div id="fps"></div>

注意该功能

```

# 公告栏欢迎

自行新建并修改以下js,cv自[ichika](https://ichika.cc)[doge保命

```js
document.addEventListener('pjax:complete', todis);
document.addEventListener('DOMContentLoaded', todis);
function todis(){
$.ajax({
    type: 'get',
    url: 'https://apis.map.qq.com/ws/location/v1/ip',
    data: {
        key: 'T3EBZ-TJ7LI-YRBG2-5ZLUR-KD3OS-U6BJO',
        output: 'jsonp',
    },
    dataType: 'jsonp',
    success: function (res) {
        ipLoacation = res;
        function getDistance(e1, n1, e2, n2) {
            const R = 6371
            const { sin, cos, asin, PI, hypot } = Math
        
            let getPoint = (e, n) => {
                e *= PI / 180
                n *= PI / 180
                return { x: cos(n) * cos(e), y: cos(n) * sin(e), z: sin(n) }
            }
        
            let a = getPoint(e1, n1)
            let b = getPoint(e2, n2)
            let c = hypot(a.x - b.x, a.y - b.y, a.z - b.z)
            let r = asin(c / 2) * 2 * R
            return Math.round(r);
        }
        
        function showWelcome() {
        
            let dist = getDistance(107.38779, 29.70239, ipLoacation.result.location.lng, ipLoacation.result.location.lat);
        
            let pos = ipLoacation.result.ad_info.nation;
            let posdesc;
            switch (ipLoacation.result.ad_info.nation) {
                case "日本":
                    posdesc = "よろしく，一起去看樱花吗";
                    break;
                case "美国":
                    posdesc = "Make America Great Again!";
                    break;
                case "英国":
                    posdesc = "想同你一起夜乘伦敦眼";
                    break;
                case "俄罗斯":
                    posdesc = "干了这瓶伏特加！";
                    break;
                case "法国":
                    posdesc = "C'est La Vie";
                    break;
                case "德国":
                    posdesc = "Die Zeit verging im Fluge.";
                    break;
                case "澳大利亚":
                    posdesc = "一起去大堡礁吧！";
                    break;
                case "加拿大":
                    posdesc = "拾起一片枫叶赠予你";
                    break;
                case "中国":
                    pos = ipLoacation.result.ad_info.province + " " + ipLoacation.result.ad_info.city;
                    switch (ipLoacation.result.ad_info.province) {
                        case "北京市":
                            posdesc = "北——京——欢迎你~~~";
                            break;
                        case "天津市":
                            posdesc = "讲段相声吧。";
                            break;
                        case "重庆市":
                            posdesc = "老乡！！！"
                            break;
                        case "河北省":
                            posdesc = "山势巍巍成壁垒，天下雄关。铁马金戈由此向，无限江山。";
                            break;
                        case "山西省":
                            posdesc = "展开坐具长三尺，已占山河五百余。";
                            break;
                        case "内蒙古自治区":
                            posdesc = "天苍苍，野茫茫，风吹草低见牛羊。";
                            break;
                        case "辽宁省":
                            posdesc = "我想吃烤鸡架！";
                            break;
                        case "吉林省":
                            posdesc = "状元阁就是东北烧烤之王。";
                            break;
                        case "黑龙江省":
                            posdesc = "很喜欢哈尔滨大剧院。";
                            break;
                        case "上海市":
                            posdesc = "众所周知，中国只有两个城市。";
                            break;
                        case "江苏省":
                            switch (ipLoacation.result.ad_info.city) {
                                case "南京市":
                                    posdesc = "欢迎来自安徽省南京市的小伙伴。";
                                    break;
                                case "苏州市":
                                    posdesc = "上有天堂，下有苏杭。";
                                    break;
                                default:
                                    posdesc = "散装是必须要散装的。";
                                    break;
                            }
                            break;
                        case "浙江省":
                            posdesc = "东风渐绿西湖柳，雁已还人未南归。";
                            break;
                        case "安徽省":
                            posdesc = "蚌埠住了，芜湖起飞。";
                            break;
                        case "福建省":
                            posdesc = "井邑白云间，岩城远带山。";
                            break;
                        case "江西省":
                            posdesc = "落霞与孤鹜齐飞，秋水共长天一色。";
                            break;
                        case "山东省":
                            posdesc = "遥望齐州九点烟，一泓海水杯中泻。";
                            break;
                        case "湖北省":
                            posdesc = "来碗热干面！";
                            break;
                        case "湖南省":
                            posdesc = "74751，长沙斯塔克。";
                            break;
                        case "广东省":
                            posdesc = "老板来两斤福建人。";
                            break;
                        case "广西壮族自治区":
                            posdesc = "桂林山水甲天下。";
                            break;
                        case "海南省":
                            posdesc = "朝观日出逐白浪，夕看云起收霞光。";
                            break;
                        case "四川省":
                            posdesc = "康康川妹子。";
                            break;
                        case "贵州省":
                            posdesc = "茅台，学生，再塞200。";
                            break;
                        case "云南省":
                            posdesc = "玉龙飞舞云缠绕，万仞冰川直耸天。";
                            break;
                        case "西藏自治区":
                            posdesc = "躺在茫茫草原上，仰望蓝天。";
                            break;
                        case "陕西省":
                            posdesc = "来份臊子面加馍。";
                            break;
                        case "甘肃省":
                            posdesc = "羌笛何须怨杨柳，春风不度玉门关。";
                            break;
                        case "青海省":
                            posdesc = "牛肉干和老酸奶都好好吃。";
                            break;
                        case "宁夏回族自治区":
                            posdesc = "大漠孤烟直，长河落日圆。";
                            break;
                        case "新疆维吾尔自治区":
                            posdesc = "驼铃古道丝绸路，胡马犹闻唐汉风。";
                            break;
                        case "台湾省":
                            posdesc = "我在这头，大陆在那头。";
                            break;
                        case "香港特别行政区":
                            posdesc = "永定贼有残留地鬼嚎，迎击光非岁玉。";
                            break;
                        case "澳门特别行政区":
                            posdesc = "性感荷官，在线发牌。";
                            break;
                        default:
                            posdesc = "社会主义大法好。";
                            break;
                    }
                    break;
                default:
                    posdesc = "带我去你的国家逛逛吧。";
                    break;
            }
        
            //判断时间
            let timeChange;
            let date = new Date();
            if (date.getHours()>= 5 && date.getHours() < 11) timeChange = "<span>上午好</span>，一日之计在于晨";
            else if (date.getHours()>= 1 && date.getHours() < 13) timeChange = "<span>中午好</span>，该摸鱼吃午饭了";
            else if (date.getHours() >= 13 && date.getHours() < 15) timeChange = "<span>下午好</span>，懒懒地睡个午觉吧！";
            else if (date.getHours() >= 15 && date.getHours() < 16) timeChange = "<span>三点几啦</span>，饮茶先啦！";
            else if (date.getHours() >= 16 && date.getHours() < 19) timeChange = "<span>夕阳无限好！</span>";
            else if (date.getHours() >= 19 && date.getHours() < 24) timeChange = "<span>晚上好</span>，夜生活嗨起来！";
            else timeChange = "夜深了，早点休息，少熬夜";
        
            document.getElementsByClassName("announcement_content")[0].innerHTML =
                `欢迎来自<span>${pos}</span>的小伙伴，${timeChange}<br>
        你距离Ariasaka约有<span>${dist}</span>公里，${posdesc}
        <br>
        <br>
        本网站的Twikoo评论系统使用<a href="https://cravatar.cn">Cravatar</a>头像系统，请自行绑定邮箱配置
        `;
        }
        showWelcome()
    }
})
    function switchPostChart () {
    let color = document.documentElement.getAttribute('data-theme') === 'light' ? '#4C4948' : 'rgba(255,255,255,0.7)'
    if (document.getElementById('posts-chart') && postsOption) {
      try {
        let postsOptionNew = postsOption
        postsOptionNew.title.textStyle.color = color
        postsOptionNew.xAxis.nameTextStyle.color = color
        postsOptionNew.yAxis.nameTextStyle.color = color
        postsOptionNew.xAxis.axisLabel.color = color
        postsOptionNew.yAxis.axisLabel.color = color
        postsOptionNew.xAxis.axisLine.lineStyle.color = color
        postsOptionNew.yAxis.axisLine.lineStyle.color = color
        postsOptionNew.series[0].markLine.data[0].label.color = color
        postsChart.setOption(postsOptionNew)
      } catch (error) {
        console.log(error)
      }
    }
    if (document.getElementById('tags-chart') && tagsOption) {
      try {
        let tagsOptionNew = tagsOption
        tagsOptionNew.title.textStyle.color = color
        tagsOptionNew.xAxis.nameTextStyle.color = color
        tagsOptionNew.yAxis.nameTextStyle.color = color
        tagsOptionNew.xAxis.axisLabel.color = color
        tagsOptionNew.yAxis.axisLabel.color = color
        tagsOptionNew.xAxis.axisLine.lineStyle.color = color
        tagsOptionNew.yAxis.axisLine.lineStyle.color = color
        tagsOptionNew.series[0].markLine.data[0].label.color = color
        tagsChart.setOption(tagsOptionNew)
      } catch (error) {
        console.log(error)
      }
    }
    if (document.getElementById('categories-chart') && categoriesOption) {
      try {
        let categoriesOptionNew = categoriesOption
        categoriesOptionNew.title.textStyle.color = color
        categoriesOptionNew.legend.textStyle.color = color
        if (!categoryParentFlag) { categoriesOptionNew.series[0].label.color = color }
        categoriesChart.setOption(categoriesOptionNew)
      } catch (error) {
        console.log(error)
      }
    }
    }
    document.querySelector(".rightMenu-item:has(.fa-moon)").addEventListener("click", function () { setTimeout(switchPostChart, 100) })
    document.getElementById("con-mode").addEventListener("click", function () { setTimeout(switchPostChart, 100) })}
    //
```

# 更好的首页轮播

基于Akilar的npm版进行修改，部分代码~~（扒~~来自[Leonus](https://blog.leonus.cn)，部分功能进行了精简：

{% link Swiper bar,Akilar,https://akilar.top/posts/8e1264d1/ %}

![](https://bu.dusays.com/2023/01/20/63ca132333058.webp)

先进行安装

```bash
npm i -s hexo-butterfly-swiper-lyx
```

注意，如果安装过`hexo-butterfly-swiper`请先卸载：

```bash
npm un -s hexo-butterfly-swiper
```

然后在主题`_config.yml`里编写：

```yaml
# hexo-butterfly-swiper-lyx
# see https://blog.yaria.top/posts/670e47f/#%E6%9B%B4%E5%A5%BD%E7%9A%84%E9%A6%96%E9%A1%B5%E8%BD%AE%E6%92%AD
swiper:
  enable: true # 开关
  priority: 5 # 过滤器优先权
  enable_page: all # 应用页面
  layout: # 挂载容器类型
    type: class
    name: swiper-div
    index: 0
  default_descr: 
  swiper_css: https://cdnjs.cloudflare.com/ajax/libs/Swiper/5.4.5/css/swiper.min.css
  swiper_js: https://cdnjs.cloudflare.com/ajax/libs/Swiper/5.4.5/js/swiper.min.js
  custom_css: https://npm.elemecdn.com/hexo-butterfly-swiper-lyx/lib/swiperstyle.css
  custom_js: https://npm.elemecdn.com/hexo-butterfly-swiper-lyx/lib/swiper_init.js
```

注意，因为切换键采用了自己的配色方案，建议添加css覆盖掉：

```css
.swiper-button-next:after, .swiper-button-prev:after{
    color:#66ccff!important; /*自己改*/
}
```

除此之外，在1.0.2版本中，为了和原版描述区分开来，所以swiper的描述项改为了`swiper_description`，当然你也可以装回`1.0.1`：

```bash
npm install -s hexo-butterfly-swiper-lyx@1.0.1
```

# Twikoo Magic

扩展更多表情包，参考：

![](https://bu.dusays.com/2023/01/20/63ca132432405.webp)

{% link 2X-ercha/Twikoo-Magic：Twikoo自定义表情列表 | HexoPlusPlus自定义表情列表（其实基于OwO的项目都可以用的啦）,Github,https://github.com/2X-ercha/Twikoo-Magic %}