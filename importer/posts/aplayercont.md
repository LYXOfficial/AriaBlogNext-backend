---
title: 不开pjax的APlayer不中断解决方案
abbrlink: 614f1131
date: 2022-11-23 10:53:11
tags: 
  - Hexo魔改
description: 这个方案好是好，最终还是选择了pjax，不过bb的bug使得她依然散发余辉。
  
categories:
  - Hexo魔改
cover: https://bu.dusays.com/2023/01/20/63c9e0f317e1f.webp

updated: 2022-12-02 14:45:00
---

前置教程：

{% link Hexo Butterfly博客魔改的一点点基础,Ariasakaの小窝,https://blog.yaria.top/posts/583ff077/ %}

最近心血来潮加了个aplayer，但是这个aplayer的体验特炸裂------每次刷新页面都得停止播放。对于我这种文章较短的站来说非常难受，于是我试了试pjax——————更炸裂了，说说、日历、轮播、弹幕等等一堆bug。

然后我采取了一种折中方案，使用js记录播放进度并且在每次刷新后都重新定位。（不过加载页面的过程是没歌的qwq）

<video src="https://gorilla.cdnja.co/v/o7/o7ZGX.mp4?token=3Qxa3K9gFncklbqj6z93vA&amp;expires=1669174164" muted autoplay loop controls></video>

js参考自：

{% link APlayer跳转页面保持音乐播放进度,l3yx's blog,https://l3yx.github.io/2020/04/29/APlayer-%E8%B7%B3%E8%BD%AC%E9%A1%B5%E9%9D%A2%E4%BF%9D%E6%8C%81%E9%9F%B3%E4%B9%90%E6%92%AD%E6%94%BE%E8%BF%9B%E5%BA%A6/ %}

因为原文章js的bug较多，且根据bf官方文档配置的Aplayer+Meetingjs的实现方式不太一样(因为1.2和2.0差别大)，所以进行了修改。

此js需要配合官方文档的Meetingjs食用

{% link Butterfly添加全局吸底Aplayer教程,Butterfly,https://butterfly.js.org/posts/507c070f/ %}

下面是代码，创建并在配置文件中引用即可完美食用

2022.12.2更新新版。

```javascript
function doStuff() {
    var flag=0;
    try{
        ap=aplayers[0]; //aplayer对象的存放位置挺离谱的
        ap.list;
        flag=1;
    }catch{
        setTimeout(doStuff, 50);//等待aplayer对象被创建（没找到初始化实例的地方只能这样了，这个判断代码是StackOverflow上面扒的（因为自己是个蒟蒻
        return;
    }
    if(flag){
        ap.lrc.hide();//自带播放暂停时显隐歌词，可以删
        document.getElementsByClassName("aplayer-icon-menu")[0].click()
        if(localStorage.getItem("musicIndex")!=null){
            musicIndex = localStorage.getItem("musicIndex");
            ap.list.switch(musicIndex);
            //歌曲可以本地储存下次访问体验更好
        }
        if(sessionStorage.getItem("musicTime") != null){
            window.musict = sessionStorage.getItem("musicTime");
            ap.setMode(sessionStorage.getItem("musicMode"));
            if(sessionStorage.getItem("musicPaused")!='1'){
                ap.play();
            }
            // setTimeout(function(){
            //     ap.seek(window.musict); //seek炸了我很久，最后决定加个延时（本来要用canplay但是莫名鬼畜了）
            // },500);
            var g=true; //加个变量以防鬼畜但是不知道怎么节流qwq
            ap.on("canplay",function(){
                if(g){
                    ap.seek(window.musict);
                    g=false;//如果不加oncanplay的话会seek失败就这原因炸很久
                }
            });
        }else{
            sessionStorage.setItem("musicPaused",1);
            ap.setMode("mini"); //新版添加了保存展开状态功能
        }
        if(sessionStorage.getItem("musicVolume") != null){
            ap.audio.volume=Number(sessionStorage.getItem("musicVolume"));
        }
        ap.on("pause",function(){sessionStorage.setItem("musicPaused",1);ap.lrc.hide()});//原基础上加了个检测暂停免得切换页面后爆零(bushi)（指社死）
        ap.on("play",function(){sessionStorage.setItem("musicPaused",0);ap.lrc.show()});//自带播放暂停时显隐歌词，后面那句可以删，上同
        ap.audio.onvolumechange=function(){sessionStorage.setItem("musicVolume",ap.audio.volume);};//新版增加保存音量免得切换页面爆零（doge
        setInterval(function(){
            musicIndex = ap.list.index;
            musicTime = ap.audio.currentTime;
            localStorage.setItem("musicIndex",musicIndex);
            //保存播放进度
            sessionStorage.setItem("musicTime",musicTime);
            sessionStorage.setItem("musicMode",ap.mode);
            //保存展开状态
        },200);//节流，200ms精度感知不大qwq
    }
}
doStuff();


```