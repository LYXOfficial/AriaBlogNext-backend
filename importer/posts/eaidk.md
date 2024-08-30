---
title: 如何在RK系开发板的linux冷门内核上编译CH340驱动
cover: 'https://bu.dusays.com/2024/03/15/65f44acbd6089.jpg'
abbrlink: dad8e69b
tags:
  - 硬件
  - 开发板
  - Linux
date: 2024-03-15 16:34:30
updated: 2024-03-15 16:34:30
categories:
- Linux
---
# 前言

大家多久没有看到本蒟蒻了呢qwq

前段时间在小黄鱼上面淘了一块 EAIDK310 开发板，只要 40 块钱，刚好我需要一个 OctoPrint 上位机，遂购之。

# 困境

这个板子的系统和安装 OctoPrint 我们下次再说，可是，当我尝试连接打印机的时候，却没有任何 USB 端口提示，自带的 `/dev/ttySx`当然也连接不了。怎么办呢？

然后我试了试 `lsusb`，并没有显示打印机的串口芯片 `CH340`（打印机用的是 `MKS_GEN_L v2.1` 板载 `CH340`）

肯定是缺少驱动啦，那么让我们来编译一下吧。

在wch官网上下载好驱动：

{% link CH341SER_LINUX.ZIP,wch.cn,https://www.wch.cn/downloads/CH341SER_LINUX_ZIP.html %}

然后解压，进入目录，执行 `sudo make&&sudo make install`。

然后便是报错，提示：`make[1]: *** /lib/modules/4.4.167/build: No such file or directory.  Stop.`

什么情况呢？

原来我们没有安装 `linux-headers`。

在 Ubuntu 下，往往只需要一句

```sh
sudo apt install linux-headers-$(uname -r)
```

可是这个玩意的官方系统的内核并未被Ubuntu官方所采用过，以至于apt并不能找到这个版本内核的头文件。

而且的而且是，它甚至不能升级内核，一升级就给 flash-kernel 报错

怎么办呢？

# 手动编译SDK大法

既然没提供linux-headers,那我们就直接用内核源码来编译呗（

这种情况下当然只能拿出linux内核手动编译了。当然，内核编译也是一件麻烦的事情（当然对于Linux用户来说为了一个小事情大动刀也很正常啦qwq），得做好心理准备。

## 准备

因开发板性能和空间问题，本文采用在x86实体机上交叉编译的方式来实现驱动编译

1. 任何较新的Linux发行版的实体机或虚拟机（建议Ubuntu/Debian/Arch）
2. 至少5G的剩余磁盘空间
3. gcc
4. aarch64-linux-gnu-gcc编译工具链
5. 瑞芯微芯片开发板
6. rk官方内核配置文件
7. 当前开发板的内核版本的linux-kernel源码
8. make（系统应该自带）
9. python3（系统应该自带）
10. 耐心
11. 良好的网络环境或工具来连接Github，如果没有，那就用上面的

## 安装交叉编译工具链

打开终端，执行以下命令：

```bash
cd /etc/
sudo mkdir toolchain
cd toolchain
sudo wget  https://mirrors.tuna.tsinghua.edu.cn/armbian-releases/_toolchain/gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu.tar.xz
sudo tar -xvf gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu.tar.xz
```

然后编辑环境变量：

```bash
sudo nano /etc/profile
```

在一堆append_path后面添加一行：

```bash
append_path '/etc/toolchain/gcc-linaro-7.4.1-2019.02-x86_64_aarch64-linux-gnu/bin'
```

然后保存退出，输入 `. /etc/profile` 或 `source /etc/profile` 应用 Path 的更改（如果未重启系统的话，每次打开新的终端会话都得执行一次）

## 下载内核源码

通过 `uname -r` 来获取你系统的内核版本，然后

在此链接下找到你系统内核对应的版本的tar.gz源码文件：

{% link Index of /kernel/,清华大学TUNA镜像站,https://mirrors.tuna.tsinghua.edu.cn/kernel/ %}

比如我的内核文件是 `https://mirrors.tuna.tsinghua.edu.cn/kernel/v4.x/linux-4.4.167.tar.gz`

然后再随便新建一个目录，用于存放源码并下载：

```bash
mkdir linux-headers-for-rk
cd linux-headers-for-rk
wget https://mirrors.tuna.tsinghua.edu.cn/kernel/v4.x/linux-4.4.167.tar.gz
tar -xzvf linux-4.4.167.tar.gz
cd linux-4.4.167
```

## 获取瑞芯微官方的内核配置文件

{% note warning %}
!!!本配置文件所在的项目非常老旧!!! 

官方已经不再在Github上面提供新版芯片的资料，因此如果是新版芯片，请自行找商家所要sdk,并解压kernel文件夹作为内核。
{% endnote %}

在编译之前，我们需要编辑一个配置文件，然而呢，这个配置文件实在是太麻烦了（几千项），好在瑞芯微官方有一个年久失修的官方内核，
里面有大量的配置文件，我们可以从中找到一个配置文件，然后修改一下，以适应我们的需求。

不过，其实我们只需要一个文件就够了，执行以下命令在当前内核应用该配置（如果是在sdk上面的话，找到/arch/arm64/configs/rockchip_linux_defconfig）

```bash
# $linux-headers-for-rk/linux-4.4.167>
wget https://raw.githubusercontent.com/rockchip-linux/kernel/develop-4.4/arch/arm64/configs/rockchip_linux_defconfig
sudo mv rockchip_linux_defconfig .config
```

## 修改Makefile以开启交叉编译

打开.config文件（建议使用gui软件方便编辑），然后找到 `ARCH` 和 `CROSS_COMPILE`这两行，然后修改为

```makefile
ARCH		?= arm64
CROSS_COMPILE ?= aarch64-linux-gnu-
```

## 配置开启CH340驱动

执行以下命令开启配置菜单

```bash
sudo make menuconfig
```

如果失败可以尝试 `sudo make nconfig`

然后：

{% note info %}
此步骤非常容易找不到，请一定细心。
{% endnote %}

+ 进入 `Device Drivers` -> `USB support` -> `USB Serial Converter support`
+ 按空格键选定 `USB Generic Serial Driver`，使其左侧方框带有星号，然后菜单会展开（如果已经展开可以忽略）
+ 按M键选择 `USB Winchipherd CH341 Single Port Serial Driver`，使其左侧尖括号框值为M,此时该驱动将被编译为模块。

如果想要编译其它驱动如CP2102之类，也可以选中CP2102的对应项。

如图：

![](https://bu.dusays.com/2024/03/15/65f43e57b25f0.png)

![](https://bu.dusays.com/2024/03/15/65f43e6eba49c.png)

![](https://bu.dusays.com/2024/03/15/65f43e75a7e02.png)

![](https://bu.dusays.com/2024/03/15/65f43f693851b.png)

最后选择下方save回车保存，返回菜单后一路exit即可退出。

除此之外，如果发现内核自带的ch341驱动太旧的话，也可以从官网下载驱动源码并解压 `ch341.c` 到 `driver/usb/serial` 下（未测试，可能不行，感兴趣的大家可以尝试）

## 正式编译（

本蒟蒻摸索了那么久配置，总算把这个东西整出来了，接下来呢？怎么样编译呢？

```bash
# $linux-headers-for-rk/linux-4.4.167>
sudo make -j8&&sudo make modules -j8
# PS：使用 -jX指定X线程编译，有显著加速效果
```

一般来说，执行这两个命令就好了。

### 解决GCC高版本报错

然而，如果你遇到了这个报错的话：

```log
/etc/toolchain/bin/aarch64-linux-gnu-ld: scripts/dtc/dtc-parser.tab.o:(.bss+0x50): multiple definition of `yylloc`; scripts/dtc/dtc-lexer.lex.o:(.bss+0x0): first defined here
```

怎么办呢？

在 `scripts/dtc/dtc-lexer.lex.c_shipped` 文件中找到YYLTYPE yyloc这一行，并在前面加上 `extern `，保存退出即可（大概六百多行） 

## 提取驱动

恭喜你经过了千辛万苦终于得到了 CH340 的驱动！！！

接下来让我们找到这个驱动的二进制文件，它在 `drivers/usb/serial/ch341.ko` 然后通过 `scp` 将这个文件拷贝到你的 OctoPrint 上位机上吧！

## 安装驱动

通过 `ssh` 登陆上位机，然后切换到拷贝的目录下，执行

```bash
sudo mv ./ch341.ko /lib/
sudo nano /lib/systemd/system/ch341.service
```

然后写入并保存：

```bash
[Unit]
Description=CH341AutoInst
[Service]
Type=simple
User=root
ExecStart=/sbin/insmod /lib/ch341.ko
[Install]
WantedBy=multi-user.target
```

然后执行：

```bash
sudo systemctl enable ch341.service
sudo systemctl start ch341.service
```

打开 OctoPrint,便可以发现可以正常连接上打印机了！！！

![](https://bu.dusays.com/2024/03/15/65f4472b2d5f7.png)

系统正常识别：

![](https://bu.dusays.com/2024/03/15/65f446c06c0d1.png)

![](https://bu.dusays.com/2024/03/15/65f446fb08329.png)

QwQ 便宜玩意的生态就真的是。。。

# 参考资料

{% link 交叉编译环境下对linux内核编译,CSDN,https://blog.csdn.net/ludaoyi88/article/details/115633849 %}

{% link RK3588 编译 CH341 驱动模块,CSDN,https://blog.csdn.net/qq_34117760/article/details/130910332 %}

{% link 编译Linux内核出现：usr/bin/ld: scripts/dtc/dtc-parser.tab.o:(.bss+0x50): multiple definition of `yylloc‘；,CSDN,https://blog.csdn.net/zhoukaiqili/article/details/126191871 %}