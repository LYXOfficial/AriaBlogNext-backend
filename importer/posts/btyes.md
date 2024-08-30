---
title: 宝塔有什么不能用的！破解HydroOJ安装脚本限制
cover: 'https://bu.dusays.com/2023/01/30/63d70d660f7ba.png'
abbrlink: 976a035b
tags:
  - 服务器
  - 避坑
categories:
  - 避坑教程
date: 2023-01-30 08:15:29
updated: 2023-01-30 08:15:29
---
突然想折腾个OJ出来，看着[hydrooj](https://hydro.js.org/)挺好，遂尝试安装。

可是由于作者对宝塔的极其抵触，导致安装程序一旦检测到宝塔就自动退出，我就不信邪了，为什么不能修改源码呢。

![](https://bu.dusays.com/2023/01/30/63d70d660f7ba.png)

下载脚本里面的`setup.sh`，很明显的，从23行开始到下面的`EOF123`有一串base64代码，于是我转换了一下，得到了一串min.js。

![](https://bu.dusays.com/2023/01/30/63d70ddb75f75.png)

![](https://bu.dusays.com/2023/01/30/63d70f4dc31df.png)

格式化后搜索`bt`不难发现这个部分：

这就是自动退出的部分了。

![](https://bu.dusays.com/2023/01/30/63d71038aeb42.png)

只需要把它注释掉，再编码放回去即可。

```js
      if (process.env.IGNORE_BT) return;
      n("bt default").code || (s.warn("warn.bt"), process.exit(1))
```

![](https://bu.dusays.com/2023/01/30/63d71093b5e33.png)

![](https://bu.dusays.com/2023/01/30/63d710c0cec7c.png)

![](https://bu.dusays.com/2023/01/30/63d7113048690.png)