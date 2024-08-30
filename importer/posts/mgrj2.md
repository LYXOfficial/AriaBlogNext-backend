---
title: 博客魔改日记（2）
abbrlink: becc831a
date: 2022-11-29 08:57:01
tags:
  - Hexo魔改
  - 魔改日记
categories:
  - Hexo魔改
cover: https://bu.dusays.com/2023/01/20/63c9e28c7b44a.webp

updated: 2022-11-29 12:01:24
---
前置教程：

{% link Hexo Butterfly博客魔改的一点点基础,Ariasakaの小窝,https://blog.yaria.top/posts/583ff077/ %}

好久没发魔改日记了，最近依然进行了很多博客更新，一样的发出来吧。

# 评论弹幕V2.0

突然感觉之前的评论弹幕不好看，于是就仿照洪哥的风格进行了一些样式功能，并且修复了QQ头像的bug，弹幕自带跳转评论功能，优化了动画，计划3.0加上swiper功能。

PS:V3.0:

{% link 博客魔改日记（3）,Ariasakaの小窝,https://blog.yaria.top/posts/670e47f/#CommentBarrage%20V3.0 %}

2023.1.22更新:

原有对于Cloudbase的方法不可用，请移步：

{% link 基于腾讯云Cloudbase云开发的Twikoo评论弹幕扩展,Ariasakaの小窝,https://blog.yaria.top/posts/8f578896/ V3.0 %}


2.0弹幕不再支持Waline/Valine评论（一样的，但是没人用，干脆摆烂了[doge]），支持了pjax

2.0弹幕的配置请参照旧版：

{% link Butterfly主题的留言弹幕界面增强版（支持Twikoo、Waline、Valine）,Ariasakaの小窝,/posts/69707535/ %}

不一样的是，`commentBarrage.css`请写成：

```css
.comment-barrage {
	position: fixed;
	bottom: 10px;
	right: 55px;
	padding: 0 0 30px 10px;
	z-index: 100;
	display: flex;
	flex-direction: column;
	justify-content: end;
	align-items: flex-end;
}

@media screen and (max-width: 768px) {
	.comment-barrage {
		display: none;
	}
}

.comment-barrage-item {
	min-width: 250px;
	max-width: 250px;
	width: fit-content;
	min-height: 80px;
	max-height: 144px;
	margin: 4px 0;
	padding: 8px;
	background: rgba(0, 0, 0, 0.9);
	backdrop-filter: blur(20px) saturate(180%);
	border-radius: 8px;
	color: #fff;
	animation: barrageIn 1.5s;
	transition: 1s;
	display: flex;
	flex-direction: column;
	border: 1px solid rgba(255, 255, 255, 0.2);
	box-shadow: var(--heo-shadow-border);
	-webkit-animation: barrageIn 1.5s;
}


.comment-barrage-item.out {
	opacity: 0;
}

@keyframes barrageIn {
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
}



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
```

而`commentBarrage.js`则参照以下进行修改:
{% tabs %}
<!-- tab forNormal -->
```javascript
//CommentBarrage 2.0 By Ariasaka
//因为C++的原因码风越来越奇怪了
const commentBarrageConfig = {
	//浅色模式和深色模式颜色，务必保持一致长度，前面是背景颜色，后面是字体，随机选择，默认这个颜色还好
	lightColors:[
		['var(--lyx-white-acrylic2)','var(--lyx-black)'],
	],
	darkColors:[
		['var(--lyx-black-acrylic2)','var(--lyx-white)'],
	],
	//同时最多显示弹幕数
	maxBarrage: 1,
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
	} //判断url合法性
function isInViewPortOfOne (el) {
    const viewPortHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight 
    const offsetTop = el.offsetTop
    const scrollTop = document.documentElement.scrollTop
    const top = offsetTop - scrollTop
    return top <= viewPortHeight
}
if(location.href.indexOf("posts")!=-1) //节流，优化非文章页面的弹幕显隐
document.onscroll = function() {
	if(commentBarrageConfig.displayBarrage){
	if(isInViewPortOfOne(document.getElementById("post-comment"))){
		document.getElementsByClassName("comment-barrage")[0].setAttribute("style",`display:none;`)
	}
	else{
		document.getElementsByClassName("comment-barrage")[0].setAttribute("style","")
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
		  }
		});
		xhr.open("POST", commentBarrageConfig.twikooUrl);
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send(data);
		timer=setInterval(()=>{
			console.log(commentBarrageConfig.barrageList);
			if(commentBarrageConfig.barrageList.length){
				popCommentBarrage(commentBarrageConfig.barrageList[commentBarrageConfig.barrageIndex]);
				commentBarrageConfig.barrageIndex += 1;
				commentBarrageConfig.barrageIndex %= commentBarrageConfig.barrageList.length;
			}
			if(commentBarrageConfig.barrageTimer.length > (commentBarrageConfig.barrageList.length > commentBarrageConfig.maxBarrage?commentBarrageConfig.maxBarrage:commentBarrageConfig.barrageList.length)){
				removeCommentBarrage(commentBarrageConfig.barrageTimer.shift())
			}
		},commentBarrageConfig.barrageTime)
//扒评论
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
			}//网址加协议头
            //增加评论和网址跳转
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="${data.avatar}"/>
				<a href="${data.link}" class="barrageNick" target="_blank">${data.nick}</a>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
			`
		}
		else{
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="${data.avatar}"/>
				<div class="barrageNick">${data.nick}</div>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
			`
		}
	}
	else{
		if(data.link!=undefined){ //QQ头像
			if(!checkURL(data.link)){
				data.link="http://"+data.link;
			}
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="https://${commentBarrageConfig.avatarCDN}/avatar/${data.mailMd5}?d=${commentBarrageConfig.noAvatarType}"/>
				<a href="${data.link}" class="barrageNick" target="_blank">${data.nick}</a>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
			`
		}
		else{
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="https://${commentBarrageConfig.avatarCDN}/avatar/${data.mailMd5}?d=${commentBarrageConfig.noAvatarType}"/>
				<div class="barrageNick">${data.nick}</div>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
			`
		}
	}
	commentBarrageConfig.barrageTimer.push(barrage);
	commentBarrageConfig.dom.append(barrage);
}
function removeCommentBarrage(barrage){
	barrage.className = 'comment-barrage-item out';
	
	if(commentBarrageConfig.maxBarrage!=1){
		setTimeout(()=>{
			commentBarrageConfig.dom.removeChild(barrage);
		},1000)
	}else{
		commentBarrageConfig.dom.removeChild(barrage);
	}
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
$(".comment-barrage").hover(function(){
	clearInterval(timer);
},function () {
	timer=setInterval(()=>{
		if(commentBarrageConfig.barrageList.length){
			popCommentBarrage(commentBarrageConfig.barrageList[commentBarrageConfig.barrageIndex]);
			commentBarrageConfig.barrageIndex += 1;
			commentBarrageConfig.barrageIndex %= commentBarrageConfig.barrageList.length;
		}
		if(commentBarrageConfig.barrageTimer.length > (commentBarrageConfig.barrageList.length > commentBarrageConfig.maxBarrage?commentBarrageConfig.maxBarrage:commentBarrageConfig.barrageList.length)){
			removeCommentBarrage(commentBarrageConfig.barrageTimer.shift())
		}
	},commentBarrageConfig.barrageTime)
})
if(localStorage.getItem("isBarrageToggle")==undefined){
	localStorage.setItem("isBarrageToggle","0");
}else if(localStorage.getItem("isBarrageToggle")=="1"){
	localStorage.setItem("isBarrageToggle","0");
	switchCommentBarrage()
}
initCommentBarrage()
```
<!-- endtab -->
<!-- tab forPjax -->
PJAX仍在不断debuging，特性包括但不限于：加载好几个元素，鬼畜动画，速度异常，不响应，不显示等

PS：要给`.comment-barrage`的pug加上`.js-pjax`，且去掉文章页特判，否则会全页重载以及出现更多特性
```js
//CommentBarrage 2.0 PJAXed By Ariasaka
//因为C++的原因码风越来越奇怪了

document.addEventListener('pjax:complete', startbarrage);
document.addEventListener('DOMContentLoaded', startbarrage);

function startbarrage(){
try{
clearInterval(timer);
document.querySelector('.comment-barrage').innerHTML="";
}catch(err){}
const commentBarrageConfig = {
	//浅色模式和深色模式颜色，务必保持一致长度，前面是背景颜色，后面是字体，随机选择，默认这个颜色还好
	lightColors:[
		['var(--lyx-white-acrylic2)','var(--lyx-black)'],
	],
	darkColors:[
		['var(--lyx-black-acrylic2)','var(--lyx-white)'],
	],
	//同时最多显示弹幕数
	maxBarrage: 1,
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
		document.getElementsByClassName("comment-barrage")[0].setAttribute("style",`display:none;`)
	}
	else{
		document.getElementsByClassName("comment-barrage")[0].setAttribute("style","")
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
		  }
		});
		xhr.open("POST", commentBarrageConfig.twikooUrl);
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send(data);
		timer=setInterval(()=>{
			if(commentBarrageConfig.barrageList.length){
				popCommentBarrage(commentBarrageConfig.barrageList[commentBarrageConfig.barrageIndex]);
				commentBarrageConfig.barrageIndex += 1;
				commentBarrageConfig.barrageIndex %= commentBarrageConfig.barrageList.length;
			}
			if(commentBarrageConfig.barrageTimer.length > (commentBarrageConfig.barrageList.length > commentBarrageConfig.maxBarrage?commentBarrageConfig.maxBarrage:commentBarrageConfig.barrageList.length)){
				removeCommentBarrage(commentBarrageConfig.barrageTimer.shift())
			}
		},commentBarrageConfig.barrageTime)

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
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
			`
		}
		else{
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="${data.avatar}"/>
				<div class="barrageNick">${data.nick}</div>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
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
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
			`
		}
		else{
			barrage.innerHTML = `
			<div class="barrageHead">
				<img class="barrageAvatar" src="https://${commentBarrageConfig.avatarCDN}/avatar/${data.mailMd5}?d=${commentBarrageConfig.noAvatarType}"/>
				<div class="barrageNick">${data.nick}</div>
				<a href="javascript:switchCommentBarrage()" style="font-size:20px">×</a>
			</div>
			<a class="barrageContent" href="#${data.id}">${data.comment}</a>
			`
		}
	}
	commentBarrageConfig.barrageTimer.push(barrage);
	commentBarrageConfig.dom.append(barrage);
}
function removeCommentBarrage(barrage){
	barrage.className = 'comment-barrage-item out';
	
	if(commentBarrageConfig.maxBarrage!=1){
		setTimeout(()=>{
			commentBarrageConfig.dom.removeChild(barrage);
		},1000)
	}else{
		commentBarrageConfig.dom.removeChild(barrage);
	}
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
$(".comment-barrage").hover(function(){
	clearInterval(timer);
},function () {
	timer=setInterval(()=>{
		if(commentBarrageConfig.barrageList.length){
			popCommentBarrage(commentBarrageConfig.barrageList[commentBarrageConfig.barrageIndex]);
			commentBarrageConfig.barrageIndex += 1;
			commentBarrageConfig.barrageIndex %= commentBarrageConfig.barrageList.length;
		}
		if(commentBarrageConfig.barrageTimer.length > (commentBarrageConfig.barrageList.length > commentBarrageConfig.maxBarrage?commentBarrageConfig.maxBarrage:commentBarrageConfig.barrageList.length)){
			removeCommentBarrage(commentBarrageConfig.barrageTimer.shift())
		}
	},commentBarrageConfig.barrageTime)
})
if(localStorage.getItem("isBarrageToggle")==undefined){
	localStorage.setItem("isBarrageToggle","0");
}else if(localStorage.getItem("isBarrageToggle")=="1"){
	localStorage.setItem("isBarrageToggle","0");
	switchCommentBarrage()
}
initCommentBarrage()
}
```
<!-- endtab -->
{% endtabs %}
# 关于页面魔改

{% link butterfly魔改关于页面,安知鱼,https://anzhiy.cn/posts/e62b.html %}

# 添加文章统计

{% link Hexo 博客文章统计图,Eurkon,https://blog.eurkon.com/post/1213ef82.html %}

# Page页面模糊背景

添加css:

```css
.page #page:not(.home #page){
    background: transparent!important;
    border: none!important;
    box-shadow: none!important;
    padding-top: 0;
    backdrop-filter: none!important;
}
#page::before{
    position: fixed;
    z-index:-114;
    bottom: 0;
    left:0;
    width: 100%;
    height: 100%;
    content:'';
    backdrop-filter: blur(10px);
    background:var(--lyx-white-acrylic2);
}
[data-theme="dark"] #page::before{
    background-color: var(--lyx-black-acrylic2)!important;
}
```

# 添加Katex

![](https://bu.dusays.com/2023/01/20/63ca1310b7ded.webp)

{% link Hexo + Butterfly 建站指南（八）使用 KaTeX 数学公式,Nick Xu,https://www.nickxu.top/2022/04/17/Hexo-Butterfly-%E5%BB%BA%E7%AB%99%E6%8C%87%E5%8D%97%EF%BC%88%E5%85%AB%EF%BC%89%E4%BD%BF%E7%94%A8-KaTeX-%E6%95%B0%E5%AD%A6%E5%85%AC%E5%BC%8F/ %}

# 杂七杂八的页面

参考自[Chuckle](https://chuckle.top)

## 小空调

先新建一个page：

```bash
hexo n page kongtiao
```

然后插入一个iframe在里面，并且在主题配置文件的导航栏中添加这个页面（略）

```markdown
<iframe src="}{一个页面链接}" width="100%" frameborder="0" scrolling="auto" height="800px"></iframe>
```

至于页面链接，你有几种选择：

{% tabs %}
<!-- tab 用Vercel自己部署一个 -->
这个方法我更推荐一点，万一哪天作者弃坑了呢？

Vercel的部署大家也很清楚，打开[vercel.com](https://vercel.com)，登录你的Vercel账号，然后[新建](https://vercel.com/new)一个项目，选择`Import Third-Party Git Repository`

![](https://bu.dusays.com/2023/01/20/63ca13118c0cc.webp)

复制代码仓库链接，即：[https://github.com/YunYouJun/air-conditioner](https://github.com/YunYouJun/air-conditioner)，点Continue，这时新建一个自己的仓库，等待部署即可。

![](https://bu.dusays.com/2023/01/20/63ca13126e6b4.webp)
![](https://bu.dusays.com/2023/01/20/63ca13138609e.webp)

部署好之后别忘了绑定域名，因为目前Vercel的自带域名是被魔法了的。

~~（盗用[第二篇文章原文](/posts/e433f3d)？）~~

返回项目主页，选择顶部的Setting-Domains
![1658104564627](https://bu.dusays.com/2023/01/20/63ca1314e69fd.webp)
![1658104824236](https://bu.dusays.com/2023/01/20/63ca131607c81.webp)

在顶部的文本框输入你的域名，比如ac.yaria.top，点击Add，这个选择框是让你选择www和根域名的关系（第一个就是输入根域名跳转到www，第二个就是输入www会跳转到根域名，根据你的喜好选择（如果不是www或者根域名就没有提示）），我选择第二个，然后点击Add就行了。

添加之后它会让你加入A记录或者CNAME记录，这时不管他说的是哪个记录，都在DNS那里加CNAME:`cname-china.vercel-dns.com`，这样可以防止被墙，Vercel会给你颁发证书，稍等一会即可正常访问了。
<!-- endtab -->
<!-- tab 用云游君的 -->
[https://ac.yunyoujun.cn](https://ac.yunyoujun.cn)
<!-- endtab -->
<!-- tab 用我的 -->
https://ac.yaria.top
<!-- endtab -->
{% endtabs %}

## 早报

*PS:自适应和样式没有完善，主要是跨域了不好搞*

跟上面一样，添加一个页面并嵌入iframe：

```markdown
<iframe src="{早报链接}" width="100%" frameborder="0" scrolling="auto" height="2500px"></iframe>
```

链接同样有多种选择：
{% tabs %}
<!-- tab 自己部署-->
部署参考：

{% link zkeq/news前后端均基于 vercel 的轻量级每日早报项目，支持一键部署，支持部署至服务器。后端由 FastAPI + BeautifulSoup 实现。,Github,https://github.com/zkeq/news %}

PS:绑定域名！！！（见上）
<!-- endtab -->
<!-- tab 作者的-->
https://news.icodeq.com
<!-- endtab -->
<!-- tab 我的-->
https://zb.yaria.top
<!-- endtab -->
{% endtabs %}

## 木鱼

{% link 写个网页版电子木鱼,轻笑Chuckle,https://chuckle.top/article/904a2780.html %}

# 浏览器过时提醒

参考：

{% link 老旧浏览器弹窗提醒,轻笑Chuckle,https://chuckle.top/article/e61f6567.html %}

# banIE

![](https://bu.dusays.com/2023/01/20/63ca1316d6af8.webp)

*Tip：因为IE不兼容上面的脚本，所以新开一个js文件*

新建`[blogRoot]/source/noie.html`

```html
<!-- 叔叔老家那里扒的qwq -->
<!DOCTYPE html>
<meta charset="utf-8">
<center style="padding-top:20px">很抱歉IE已经停止支持，因此本博客不再支持IE浏览器，如果想要正常浏览，请换用新版Edge或Chrome、Firefox、Opera等现代浏览器</center>

<html lang="en"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge"><meta name="spm_prefix" content="888.7521">
    <title>浏览器升级提示 | Ariasakaの小窝</title>
    <link href="https://at.alicdn.com/t/font_1454899_pqhvobved2o.css" rel="stylesheet" type="text/css">
    <style>
      * { padding: 0; margin: 0; box-sizing: border-box;}
      ul, li { list-style: none; }
      a:hover {text-decoration:none;}
      ins,a {text-decoration:none;}
      a:focus,*:focus {outline:none;}
  
      .b-content { width: 400px; margin: 60px auto; font-size: 14px; color: #999; }
      .pic-box { padding-bottom: 20px; border-bottom: 1px solid #eee; }
      .pic-box img { max-width:  100%; margin-bottom: 10px; }
      .pic-box p { line-height: 20px; font-size: 12px;}
      .text-box .title {text-align: center; margin: 30px 0;}
      .text-box .list {height: 90px;}
      .text-box .list li a { float: left; width: 100px; text-align: center; line-height: 24px; color: #666;}
      .text-box .list li .iconfont{ font-size: 30px; }
      .text-box .list li a span{ font-size: 12px; color: #999; }
      .copyright {margin-top: 20px; text-align: center;}
    </style>
  </head>
  <body>
    <div class="b-content">
      <div class="text-box">
        <div class="title">以下四款官方正版浏览器任君挑选</div>
        <div class="list">
          <ul>
            <li>
              <a href="https://www.google.cn/intl/zh-CN/chrome" target="_blank">
                <i class="iconfont icon-chrome"></i><br>
                Chrome<br>
                <span>谷歌</span>
              </a>
            </li>
            <li>
              <a href="https://www.mozilla.org/zh-CN/firefox/new" target="_blank">
                <i class="iconfont icon-firefox"></i><br>
                Firefox<br>
                <span>火狐</span>
              </a>
            </li>
            <li>
              <a href="https://www.microsoft.com/edge" target="_blank">
                <i class="iconfont icon-edge"></i><br>
                Edge（新版）<br>
                <span>微软</span>
              </a>
            </li>
            <li>
              <a href="https://www.opera.com/zh-cn" target="_blank">
                <i class="iconfont icon-opera"></i><br>
                Opera<br>
                <span>欧朋</span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  
  </body></html>
```

添加到hexo配置文件`_config.yml`中：
```yaml
skip_render: 
  - noie.html
```

新建`noie.js`并引用：

```javascript
if(!!window.ActiveXObject || "ActiveXObject" in window){
    window.location.href="./noie.html";
}
```

# 弹出欢迎&Cookie&F12提示的Snackbar

![](https://bu.dusays.com/2023/01/20/63ca13179f492.webp)

![](https://bu.dusays.com/2023/01/20/63ca131872c03.webp)

自带Referer提醒，新建`welcome.js`

注意要打开主题配置文件的Snackbar

```js
//首次访问弹窗
if (localStorage.getItem("popWelcomeWindow") != "0") {
    if(document.referrer==undefined||document.referrer.indexOf("yaria.top")!=-1||document.referrer.indexOf("ariasaka.top")!=-1){ //改成自己域名，注意是referrer!!! qwq
        Snackbar.show({
            pos: "top-right",
            showAction: false,
            text: '欢迎访问本站！'
        })
    }else{
        Snackbar.show({
                pos: "top-right",
                showAction: false,
                text: `欢迎来自${document.referrer.split("://")[1].split("/")[0]}的童鞋访问本站！`
            })
        localStorage.setItem("popWelcomeWindow", "0");
    }
}
if (sessionStorage.getItem("popCookieWindow") != "0") {
    setTimeout(function () {
        Snackbar.show({
            text: '本站使用Cookie和本地/会话存储保证浏览体验和网站统计',
            pos: 'bottom-right',
            actionText: "查看博客声明",
            onActionClick: function (element) {
                window.open("/license")
            },
        })
    }, 3000)
}
//不在弹出Cookie提醒
sessionStorage.setItem("popCookieWindow", "0");

//自带上文浏览器提示

function browserTC() {
    btf.snackbarShow("");
    Snackbar.show({
        text: '浏览器版本较低，网站样式可能错乱',
        actionText: '关闭',
        duration: '6000',
        pos: 'bottom-right'
    });
}
function browserVersion() {
    var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
    var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1; //判断是否IE<11浏览器
    var isIE11 = userAgent.indexOf('Trident') > -1 && userAgent.indexOf("rv:11.0") > -1;
    var isEdge = userAgent.indexOf("Edge") > -1 && !isIE; //Edge浏览器
    var isFirefox = userAgent.indexOf("Firefox") > -1; //Firefox浏览器
    var isOpera = userAgent.indexOf("Opera")>-1 || userAgent.indexOf("OPR")>-1 ; //Opera浏览器
    var isChrome = userAgent.indexOf("Chrome")>-1 && userAgent.indexOf("Safari")>-1 && userAgent.indexOf("Edge")==-1 && userAgent.indexOf("OPR")==-1; //Chrome浏览器
    var isSafari = userAgent.indexOf("Safari")>-1 && userAgent.indexOf("Chrome")==-1 && userAgent.indexOf("Edge")==-1 && userAgent.indexOf("OPR")==-1; //Safari浏览器
    if(isEdge) {
        if(userAgent.split('Edge/')[1].split('.')[0]<90){
            browserTC()
        }
    } else if(isFirefox) {
        if(userAgent.split('Firefox/')[1].split('.')[0]<90){
            browserTC()
        }
    } else if(isOpera) {
        if(userAgent.split('OPR/')[1].split('.')[0]<80){
            browserTC()
        }
    } else if(isChrome) {
        if(userAgent.split('Chrome/')[1].split('.')[0]<90){
            browserTC()
        }
    } else if(isSafari) {
        //不知道Safari哪个版本是该淘汰的老旧版本
    }
}
//2022-10-29修正了一个错误：过期时间应使用toGMTString()，而不是toUTCString()，否则实际过期时间在中国差了8小时
function setCookies(obj, limitTime) {
	let data = new Date(new Date().getTime() + limitTime * 24 * 60 * 60 * 1000).toGMTString()
	for (let i in obj) {
		document.cookie = i + '=' + obj[i] + ';expires=' + data
	}
}
function getCookie(name) {
	var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
	if (arr = document.cookie.match(reg))
		return unescape(arr[2]);
	else
		return null;
}
if(getCookie('browsertc')!=1){
    setCookies({
        browsertc: 1,
    }, 1);
    browserVersion();
}
```