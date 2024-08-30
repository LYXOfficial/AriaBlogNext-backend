---
title: 【公测中/NoTopDomain】还在忍受极域的烦恼吗？
cover: 'https://bu.dusays.com/2023/05/20/6467b45f37cfe.webp'
abbrlink: 55af90aa
date: 2023-05-19 23:36:09
updated: 2023-05-19 23:36:09
tags: 
- OI
- 编程
- PyQt5
- NoTopDomain
- Python
- C++
categories: 编程
---
{% link LYXOfficial/NoTopDomain,Github,https://github.com/lyxofficial/notopdomain %}

因为信息老师的奇怪行为（上课禁了U盘网站）导致本蒟蒻水题困难，于是在五一开始编写此程序。

{% note info %}
《宇宙安全声明》

如果被OI教练/信息老师骂诸如说是：

“如果你还是以这个态度来面对竞赛的话，那我觉得你的竞赛生涯已经结束了。”

这种的话，本蒟蒻并不会背锅。
{% endnote %}

# 软件截图

![](https://bu.dusays.com/2023/05/20/6467a21bb795a.png)

![](https://bu.dusays.com/2023/05/20/6467a21fa5d84.png)

# 软件介绍

因为并不擅长MFC/Qt C++ GUI开发，选择了自己有经验的PyQt5（本来打算用PySide6的但是对Win7等老机房兼容不好），借助PyWin32API和psutil加以实现，打包用的是nuitka，本机使用Py38-32环境，不过因为有时候会在学校打（是Py311-64），所以有时候大小会从16M变成21M左右。

我也知道Python效率略低且打包文件稍大，不过还是控制在了可接受范围吧（qwq

既然名字都叫 NoTopDomain 了，主要功能与极域有关，至于学生机房管理助手，因为我们学校并没有安装\~\~ ~~（曾经装过却因为一堆bug断送了几个OIer的竞赛生涯）~~，这时建议用：

{% link BengbuGuards/mythwaretoolkit,Github,https://github.com/BengbuGuards/mythwaretoolkit %}

软件可能会报毒（尤其是b1.4+更容易爆，但是似乎只有Win10会报，Win11扫描一下也没有爆），需要手动给杀毒软件加白名单

主要功能相信大家也大概清楚了：

1. 杀掉/启动极域
2. 挂起/恢复极域
3. 多线程定时循环+DLL保持自身最前（因为没做令牌窃取超级置顶，所以广播时会闪烁）
4. 多线程定时循环+DLL解除黑屏等键盘限制（鼠标限制因用户体验已放弃）
5. 解除广播全屏化（也可以解除共享屏幕，注意只是解了按钮）
6. 智慧的解法：把鼠标拖到解禁了的按钮按一下再拖回来 awa（在设置第二项）
7. 一部分QSS
8. 解除U盘/软件限制（暂不可恢复）
9. 解除网站访问限制（暂不可恢复）
10. 唤起任务管理器并勾选置顶
11. 杀掉选定/输入进程
12. 修改选定窗口置顶状态（采用的是SWP_TOPMOST而不是SWP_TOP）
13. 热键唤起：默认Alt+M唤起主窗口，Alt+T唤起任务管理器，Alt+Y切换当前窗口置顶，Alt+K杀死当前进程
14. 脱离极域远程关机
15. 脱离教师远程控制（尚未实现）
16. 屏蔽教师远程命令（尚未实现）
17. 获取极域密码（尚未实现）（PS：mythware_super_password）
18. 强制卸载极域（尚未实现）
19. 解除工具栏提交（尚未实现）
20. 接收因杀掉极域等时教师发送的文件的遗漏部分（已抛弃）
21. 解除工具限制（如TSK CMD等）
22. 解除映像劫持（主要防学机管）
23. 重启资源管理器
24. 检测极域/广播/黑屏状态
25. 一部分配置、设置快捷键

目前软件因为部分功能未完成，依然停留在beta阶段，尽量一周一更，欢迎使用（

以上部分功能体验并不好，欢迎大家反馈（暂时只支持Github提交issue/pr，以前uClock Dxdownload的那种邮箱反馈个人感觉不太合适。）

# 下载链接

除上文Github外，还可以在蓝奏云下载，包含了所有历史Release及源码：

{% link NoTopDomain,蓝奏云,https://xydc.lanzouo.com/b018x6qza %}

密码:2al0