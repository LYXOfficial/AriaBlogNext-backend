---
title: 适配指北：我是怎么适配PJAX的
tags:
  - Hexo魔改
  - 避坑
categories:
  - Hexo魔改
cover: https://bu.dusays.com/2023/01/20/63c9e2851d1c6.webp
abbrlink: 30bce1d1
date: 2022-12-06 11:45:29
updated: 2022-12-06 11:45:29
swiper_index: 13
swiper_description: 适配pjax，暴增网站速度
---
前置教程：

{% link Hexo Butterfly博客魔改的一点点基础,Ariasakaの小窝,https://blog.yaria.top/posts/583ff077/ %}

昨天爆肝（主要是昨天下午没课）适配了pjax，当时把这个任务当成一个长期任务，没想到很快就搞定了，修改量也不是很大。

具体适配，其实并不多。

# DOM层面适配

有些DOM元素（自己魔改的）在不同页面的表现不一样，这时使用pjax切换页面后并不会进行更改，需要加上类名`.js-pjax`。

## 加上之后全页重载?

有的时候，加上了`.js-pjax`之后出现了全页重载的现象，这是因为前面的页面有这个元素，后面的没有，pjax出错导致全页重载的问题，这时应该把这个元素扩展到全站范围，并且在不需要的页面把元素置空。

说起来比较麻烦，其实大概就是这样。

典型例子，`commentBarrage`的pug本来是这么写的：
```py
if is_page()||is_post()
    .comment-barrage
```

显然，这时如果加上`.js-pjax`会使主页无法正常跳转，所以我们不妨把她扩展到主页范围：

```py
.comment-barrage.js-pjax
```
这样就不会重载了

（感谢糖果屋群友的帮助）

# JS适配

JS可是最恼火的了，首先，对于切换页面后出现bug的js，首先你应该尝试加上`data-pjax`类，因为它是在butterfly里面写好了的js重载筛选器：

![](https://bu.dusays.com/2023/01/20/63ca12362158c.webp)

这对于一些没有事件绑定的js是有效的，对于一些其它的则无效。

## 处理事件绑定问题

有时候，js里面会这么写:

```javascript
$(document).ready(()=>{
    //todo
})
//或者
window.onload=function(){
    //todo
}
//或者
window.addEventListener("DOMContentLoaded",()=>{
    //todo
})
```
这些写法在pjax下的表现就是首次加载执行，后面就不会执行了。

修改方法也不难，把所有要做的事情全部写在一个函数里面，绑定事件：

```javascript
window.addEventListener("pjax:complete",todo);//后面几次，pjax加载
window.addEventListener("DOMContentLoaded",todo);//第一次
function todo(){
    //代码
}
```

有时候一些本来不是函数的写了事件绑定，一定要注意全局和局部变量的问题。

# 解决鬼畜问题

对于一些定时器来说，每一次刷新都需要清除，否则就会鬼畜，比如弹幕的js，我们需要给定时器设置一个变量绑定，每一次刷新都进行`clearInternal(timer)`：

一个简化了的弹幕代码

```javascript
window.addEventListener("pjax:complete",clear);//后面几次，pjax加载
window.addEventListener("DOMContentLoaded",load);//第一次加载
function clear(){
    clearInternal(timer);
    document.querySelector(".comment-barrage").innerHtml="";
    load();
}
function load(){
    //init
    timer=setInteral(()=>{
        popCommentBarrage();
    },114514)
}
```

总的来说，就是这些了，对于一些没法适配pjax的第三方脚本（比如毒瘤的`bbtalk.min.js`，我们不妨加入`exclude`里面，然后对于APlayer依然可以用之前的[这个方案](/posts/614f1131)

{画个大饼，弹幕会改成Swiper。}