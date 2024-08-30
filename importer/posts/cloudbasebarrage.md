---
title: 基于腾讯云Cloudbase云开发的Twikoo评论弹幕扩展
cover: 'https://bu.dusays.com/2023/01/22/63cca204a67d2.webp'
abbrlink: 8f578896
date: 2023-01-22 00:42:00
updated: 2023-01-22 00:42:00
tags: 
- Hexo魔改
- 避坑
categories: Hexo魔改
---
# 前言

最近发现腾讯云的云开发是可以嫖六个月的（别问我，学生优惠），而且刚好twikoo的vercel api很慢，就换上了，刚好发现两者的api不一样，原来的js需要修改（post参数不一样，原本返回的json现在嵌套了一层，遂给出教程。该js基于CommentBarrage3.0（其实是全版本通用修改？），参考：

{% link 博客魔改日记（3）,Ariasakaの小窝,https://blog.yaria.top/posts/670e47f/#CommentBarrage V3.0 %}

# apiUrl的获取

在原有的js配置项中有apiUrl，可以这么获取：

![](https://bu.dusays.com/2023/01/22/63cca0c5593a3.png)

23.1.22更新：原有版本因为accesstoken问题改为了自动获取，您无需手动获取token。

# js的修改

js则需要这么修改，修改了一些api解析部分：

```javascript
...
function initCommentBarrage(){
	try{
		var data = JSON.stringify({
			//带有{envid}的需要自己改成你的envid
			"access_token": JSON.parse(localStorage.getItem("access_token_{envid}")).content,
			"dataVersion": "2020-01-10",
			"env": "{envid}",
			"function_name": "twikoo",
			"request_data": `{"event":"COMMENT_GET","url":"${commentBarrageConfig.pageUrl}"}`,
			"seqId": "3e580ab19eb64", //这里随便，但是必须有
			"action": "functions.invokeFunction"
		});
		var xhr = new XMLHttpRequest();
		xhr.withCredentials = true;
		xhr.addEventListener("readystatechange", function() {
			if(this.readyState === 4) {
				commentBarrageConfig.barrageList = commentLinkFilter(JSON.parse(JSON.parse(this.responseText).data.response_data).data);
				... //视版本而异
		});
		xhr.open("POST", commentBarrageConfig.twikooUrl);
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.send(data);
	}catch(e){setTimeout(()=>{initCommentBarrage()},100)} //如果原有token过期等待原有评论系统自己刷新，我甩锅了（bushi）
}
...
```
水文成功，经验+3，告辞（雾）