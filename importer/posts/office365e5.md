---
title: Microsoft365E5白嫖不完整指北（有好东西）
abbrlink: 29b0359b
date: 2022-08-09 15:05:07
tags:
  - 白嫖
  
  
categories:
  - 白嫖教程
cover: https://bu.dusays.com/2022/09/01/63103a5b3cd6b.webp
updated: 2022-10-04 08:50:19
---

{% note warning flat %}
警告：

坊间传闻，大概从2023年4月左右开始，因AI原因，微软开始了大面积的365E5强制过期/封号，尤其是使用了脚本（尤其是加入了黑名单的）的，过期后基本无解，除了转收费版，要不就在彻底删除前备份数据才有救了。(/▽＼)

本人已经中招，建议不要白嫖，还是花点小钱，或者推荐KMS激活并用OTP改Mondo2016

但是，白嫖依然万岁！！！AwA

~~小学机房毛的Office2019家庭版还在呢~~

{% endnote %}

# 之前的一些事

很早以前（大约2019年的时候）在拼夕夕上面买了个office365账号，存活了很久，但是显然问题不少。网盘没法用，还怕被控制，现在也是寿终正寝，登录不了了。还是想自己弄一个来，最开始选择的是教育版，找了很多教程，最后用的是一个临时邮箱注册的，可是却加入不了域，没多久就被管理员删号了。

于是我就自己弄了一个Microsoft365E5，E5是给开发者用的，用于开发，订阅能管90天，但你要定期使用用它们的API才能续期，后面我会放出自动续期的部署教程，使用我自己写的python代码，使用Vercel实现，方便部署。

# 申请沙盒

进入这个链接，点击立即加入，登录你的Microsoft个人账户，没有的话可以注册`<del class="noheimu">`（win10和11都普及了还有人居然没有ms账户？）。`</del>`

{% link Microsoft开发人员计划申请,Microsoft,https://developer.microsoft.com/zh-cn/microsoft-365/dev-program %}

![1660033409614](https://bu.dusays.com/2023/01/20/63ca132eee8ff.webp)

然后按照下图输入信息，一路下一步。

![1660033559082](https://bu.dusays.com/2023/01/20/63ca133033216.webp)

![1660033616635](https://bu.dusays.com/2023/01/20/63ca1331356a8.webp)

![1660033668080](https://bu.dusays.com/2023/01/20/63ca13322f7aa.webp)

首次注册会进入一个配置沙盒的页面，

![1660037786677](https://bu.dusays.com/2023/01/20/63ca133345811.webp)

这个沙盒其实就是你的订阅，然后初始化管理员和账户，如下图：

![1660037853830](https://bu.dusays.com/2023/01/20/63ca1334545e5.webp)

然后等一会~~好东西就要来了，这可能需要亿分钟，请滚回功率，坐和放宽~~，沙盒就成功创建了。

# 一些其它的设置

按理来说，现在你就可以在Microsoft365中登录账号并且启用许可证了，当然有一些东西你要自己改改最好。

## 自定义域名

如果你想要更容易记住的账户，可以看看这个教程。

进入这个链接：

{% link 更改Microsoft 365 E5内部账号域名,Microsoft,https://admin.microsoft.com/Adminportal/Home?#/Domains %}

### 自定义onmicrosoft域名

进入上面的链接，选择你的初始onmicrosoft域名，进去之后会显示一个添加onmicrosoft域（预览），点击按指引操作即可。

### 自定义成自己的域名

进入上面的链接，点击添加域，进入添加界面。

![1660087163722](https://bu.dusays.com/2023/01/20/63ca13356b980.webp)

输入你的域名（最好是二级域名，以免冲突），点击使用此域

![1660087159540](https://bu.dusays.com/2023/01/20/63ca1336a5647.webp)

验证界面默认会让你使用cloudflare验证，如果不是，选择另一个域主机，看样子支持国内大部分的解析服务商。如果没有就选择其它按照指引操作吧。

![1660087369518](https://bu.dusays.com/2023/01/20/63ca1337b94a5.webp)

点击验证，然后进入授权页面授权就好了。

然后一路下一步，添加dns记录的时候再授权一遍即可。

### 改邮箱

要使用自定义域名，你还需要设置账户的邮箱。

进入

{% link 账户管理,Microsoft,https://admin.microsoft.com/Adminportal/Home?#/users %}

按照下图操作：

![1660088810761](https://bu.dusays.com/2023/01/20/63ca1338de9e5.webp)

![1660088878242](https://bu.dusays.com/2023/01/20/63ca1339ed8a6.webp)

添加之后最好设为主邮箱，然后保存更改。

添加好之后，你就可以用你的名字@你的域名来登录了

进入Office，登录账户，反复重启激活，成功！

![1660089240424](https://bu.dusays.com/2023/01/20/63ca133b15363.webp)

# 修改Onedrive大小

E5有整整5T的空间欸！不利用好可惜了，不过e5默认是1t大小，要改成5t。

进入 {你的默认分配组织名字(就是默认邮件地址的onmicrosoft前面的那个)}.+ <a href="https://admin.sharepoint.com/_layouts/15/online/AdminHome.aspx#/settings/OneDriveStorageQuota">admin.sharepoint.com/_layouts/15/online/AdminHome.aspx#/settings/OneDriveStorageQuota</a>这个链接，在右侧栏中输入5120，保存即可。

![1660089618540](https://bu.dusays.com/2023/01/20/63ca133c1b8eb.webp)

# 续期

注：目前的续期方式都不是永久的，因为现在的Azure Client Secret已经变成有效期最多两年了，到期之后需要去官网换一个密钥重新部署。

~~告诉你们一件事，之前KBY的E5到期之后居然自动续期了，而且调用过任何API，非常玄幻。~~

## Vercel部署方式（推荐）

博主一直在研究Microsoft 365 API，现在程序还没写出来，所以暂时推荐用下面的方法。

（PS：Vercel-Alist）

## 在线续期网站

这个网站可以实现自动续期功能，不一定有安全性和稳定性。

（23.5.21 upd：）目前作者因考虑到形势原因已经关停网站。

进入这个网站登录:

{% link E5在线续期-登录,e5.qyi.io,https://e5.qyi.io %}

点击这个小猫猫头像登录，会自动跳转到Gtihub授权。

![1660101977763](https://bu.dusays.com/2023/01/20/63ca133cdefe1.webp)

登录成功后，返回个人中心，点击新建，输入一个名字。

![1660102119447](https://bu.dusays.com/2023/01/20/63ca133de1805.webp)

然后你需要一个CLIENT_ID和CLIENT_SECRET，以下是申请方式。

## 获取CLIENT_ID

进入Azure门户（官方这么翻译的）

{% link Microsoft Azure,Microsoft,https://portal.azure.com %}

按照这样操作：

![1660107884593](https://bu.dusays.com/2023/01/20/63ca133f18df5.webp)

![1660107914595](https://bu.dusays.com/2023/01/20/63ca13403864a.webp)

重定向URI必须写成`<a href="https://e5.qyi.io/outlook/auth2/receive">`https://e5.qyi.io/outlook/auth2/receive`</a>`否则登录会报错

![1660108030329](https://bu.dusays.com/2023/01/20/63ca134163472.webp)

注册之后返回刚刚的应用注册界面，复制应用程序（客户端）ID。

![1660108177756](https://bu.dusays.com/2023/01/20/63ca134251c46.webp)

我们还需要一个密钥，点进你的应用，选择证书和密码，点击新客户端密码，

![1660108273717](https://bu.dusays.com/2023/01/20/63ca13436559e.webp)

然后在右侧添加，时间选24个月，所以两年之后你要来换一个。

![1660108341695](https://bu.dusays.com/2023/01/20/63ca1344747b2.webp)

然后复制值

![1660108399118](https://bu.dusays.com/2023/01/20/63ca134555141.webp)

确保两个数据都在剪贴板里面，回到续期配置个人中心，点击应用右边的配置，输入你刚刚复制的ID和Secret，调用时间默认，最后授权即可。

![1660108495470](https://bu.dusays.com/2023/01/20/63ca1347117d3.webp)

享受5T超大Onedrive和Office完整版的快乐吧！
