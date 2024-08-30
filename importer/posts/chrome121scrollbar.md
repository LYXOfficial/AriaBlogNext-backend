---
title: ！！！如何解决Chrome121更新后导致的滚动条样式失效！！！
cover: ''
abbrlink: dea522be
date: 2024-03-09 11:05:28
updated: 2024-03-09 11:05:28
tags: 
  - Hexo魔改
categories:
  - Hexo魔改
---
好久没有管博客了，今天回去看看发现滚动条炸掉了（

于是搜了一下，果然又是谷歌大刀部乱砍 CSS 特性导致的，只要更新到基于Chrome121版本以上的浏览器（我现在用的是Edge 122）就会有这个问题。

具体地说，就是 `::-webkit-scrollbar` 这个伪类被砍掉了，导致目前有些滚动条样式有些受限，不过谷歌给了两个新属性，可以作为临时替代：

```css
body{
    scrollbar-width: {none,thin,auto};
    scrollbar-color:{};
}
```

不过 `overflow:overlay` 已经没了 :(

所以说，只需要加上一句 `scrollbar-width: none;` 就可以隐藏滚动条了。