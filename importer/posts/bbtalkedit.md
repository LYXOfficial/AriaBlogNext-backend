---
title: BBTalk魔改：让bbtalk的样式变成瀑布流
abbrlink: '70734559'
date: 2022-08-15 14:55:03
tags:
  - Hexo魔改
description: 几个css？叫魔改？
  
categories:
  - Hexo魔改
cover: https://bu.dusays.com/2022/09/01/63103a7aee588.webp
updated: 2022-10-04 08:50:19
---
前置教程：

{% link Hexo Butterfly博客魔改的一点点基础,Ariasakaの小窝,https://blog.yaria.top/posts/583ff077/ %}

因为bbtalk默认的样式是时间轴（如图），但是我更喜欢瀑布流的样式（比如洪哥的），所以就写了一个简单的css用于修改样式。

![1660547037484](https://bu.dusays.com/2023/01/20/63ca10cca573d.webp)

![1660546977284](https://bu.dusays.com/2023/01/20/63ca10cdbca5f.webp)

css的效果（直接拿黑石的博客改的[doge]）：

![1660547017887](https://bu.dusays.com/2023/01/20/63ca10ceacbb9.webp)

![1660547415300](https://bu.dusays.com/2023/01/20/63ca10cfc5153.webp)

添加如下css即可应用

```css
#app .body{
    margin:0!important;
}
#app{
    display: flex;
    flex-wrap: wrap;
}
#app .tip{
    width:100%
}
.meta::before,.meta::after,.timenode::after,.timenode::before{
    display: none;
}
@media screen and (min-width: 1100px){
    .timenode{
    width:calc(100% / 3 - 40px)!important;
}
}
@media screen and (min-width: 768px) and (max-width: 1100px){
    .timenode{
        width:calc(100% / 2 - 40px)!important;
        }
    }
.timenode{
    min-width:300px;
    margin:15px;
    width:100%;
}
.timenode .body{
    width:100%;
    height:100%;
}
```

你可能会发现一个小bug~~（不，特性）~~，"再翻翻"按钮的位置有点奇怪，你可以自己研究一下把它弄好，也可以修改bbtalk的配置，让它同时渲染很多个（比如114514个这种达不到的），用下面的css隐藏掉按钮即可。

![1660548710001](https://bu.dusays.com/2023/01/20/63ca10d07d28c.webp)

```css
.load-ctn{
    display:none;
}
```
