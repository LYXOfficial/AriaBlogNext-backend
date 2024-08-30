---
title: '工欲善其事,必先利其器————论如何善用VSCode提高写OIの效率'
abbrlink: 5d71c71f
date: 2022-11-19 19:39:27
tags: 
- OI
categories:
- 经验教程
cover: https://bu.dusays.com/2023/01/20/63c9e287b0176.webp

updated: 2022-11-29 09:22:59
---

（内心OS：好久没写过这种教程了(。・ω・。)）

众所周知，作为一个权威的认证/比赛~~Save Money~~机构，€€￡的官方编辑器是我们熟知的DevC++。

这个编辑器非常的方便，她不用开项目，不用调配置，不用装编译器，以及她用50+M的安装包就能解决C++开发的优势使得€€￡选择了她。

实际上呢，`DevC++`这玩意却是又落后又难用又难看，没有代码补全，用的还是远古的`C++98`标准。这与CSP/NOIP/NOI中使用的C++14极其不符，并且调试功能没法用会闪退，极大地降低了OIer们的~~水题冲校榜~~刷题速度，成为了饱受各位OIer们诟病的一个编辑器。

~~（实际上你也可以用小熊猫，但是没VSCode好看）~~

于是想到了大名鼎鼎的万能编辑器-VSCode，她支持几乎所有的编程语言：Arduino、Python、Java、C#、.NET、VB、JS等等，以及各种标记语言：HTML、CSS、YAML、Markdown，这东西真的很nb欸qwq。

不过VSCode毕竟是编辑器，配置比较困难，当然只要你弄好了，会非常好用。

# 配置环境

## 装Code

首先安装VSCode，VSCode的安装比较简单，只需要点击[这个链接](http://vscode.cdn.azure.cn/stable/6261075646f055b99068d3688932416f2346dd3b/VSCodeUserSetup-x64-1.73.1.exe)（官网的很慢这个是官方CDN），然后一路安装即可（建议选为所有用户安装）

新版VSCode安装好之后会自动提示装中文语言包，点击即可（我早就装了就没法给图了）

你也可以在左下角的功能栏改些主题啊什么的，也可以把同步开着。

![](https://bu.dusays.com/2023/01/20/63ca1237f0016.webp)

![](https://bu.dusays.com/2023/01/20/63ca1238e20ef.webp)

## 配置代码环境

实际上devcpp里面是可以扒到一个gcc的，但是毕竟是很老的版本，所以建议换成新版。

点击[该链接](https://nchc.dl.sourceforge.net/project/mingw-w64/Toolchains%20targetting%20Win64/Personal%20Builds/mingw-builds/8.1.0/threads-posix/seh/x86_64-8.1.0-release-pos)下载Mingw8.1（新版10.0的安装方案很恶心且没必要用新版）

因为用的是NCHC台湾节点，所以速度稍慢，建议用IDM。

![](https://bu.dusays.com/2023/01/20/63ca1239de332.webp)

然后把压缩包解压，随便找个地方扔出去，然后复制这个链接+bin

e.g.`D:\mingw64\bin`

PS：用dev内置Mingw的路径是`{dev安装路径}\MinGW32(也可能是MinGW64看安装位数)\bin`

把她扔到环境变量（如下图里面）

![（地狱绘图qwq）](https://bu.dusays.com/2023/01/20/63ca123bcbf62.webp)

然后进入VSCode的插件区安装C/C++扩展

![](https://bu.dusays.com/2023/01/20/63ca123ceffb2.webp)

新建一个文件夹

![](https://bu.dusays.com/2023/01/20/63ca123e1211d.webp)

这时你就可以自由写代码了！

![](https://bu.dusays.com/2023/01/20/63ca123f409e7.webp)

然后为了运行代码，需要安装一个Code runner

![](https://bu.dusays.com/2023/01/20/63ca1240643d7.webp)

安装完之后用`Ctrl+Shift+P`进入面板，打开设置（json），添加：
```json
"code-runner.executorMap": {
    "c": "cd $dir && gcc $fileName -o $fileNameWithoutExt && $dir$fileNameWithoutExt",
    "cpp": "cd $dir && g++ -std=c++14 -o2 $fileName -o $fileNameWithoutExt && $dir$fileNameWithoutExt", //契合C€€￡官方环境并开启O2优化
},
"code-runner.runInTerminal": true,
"code-runner.ignoreSelection": true
```

![](https://bu.dusays.com/2023/01/20/63ca12418190a.webp)

（注意语法qwq）

然后单击右上角运行按钮快乐运行吧！

![](https://bu.dusays.com/2023/01/20/63ca1242b66c0.webp)

# 一些美化&骚操作

~~终于更新啦！~~

## 两下敲出一个板子

![](https://bu.dusays.com/2023/01/20/63ca1244057e1.webp)

在图中，只要输入一个关键字，就能快速打出快读快写、二分的代码，这无疑可以加快做题的速度，缺点也很明显，就是打久了会产生思维惰性，导致忘记模板。

这个东西其实是VSCode自带的自定义用户代码块。

### 配置

配置也不难，使用 `Ctrl+Shift+P` 打开快捷面板，输入 `User Snippets` ，就能看到一个配置项：“代码片段：配置用户代码片段”，回车，然后选择 `cpp.json` ~~(我不相信2202年了还有P党和C党)~~ 

![](https://bu.dusays.com/2023/01/20/63ca1244d6303.webp)

![](https://bu.dusays.com/2023/01/20/63ca1245c5284.webp)

然后打开json来配置，每一个键值对的格式如下：

```json
{
    "base": { /*这里填的东西与实际显示的无关，随便写*/
        "prefix": "base", //触发的关键字base
        "body": [//代码主片段
            "#include <bits/stdc++.h>",
            "using namespace std;",
            "", //每一行都要用引号括起来，加上逗号
            "int main(){",
            "	//代码",
            "    return 0;",
            "}", //实际上你也可以把代码写成一行，然后把换行ctrl+d改成"\n"
            //e.g: "inline void read(int &n){\n    int x=0,f=1;\n    char ch=getchar();\n    while(ch<'0'||ch>'9'){\n        if(ch=='-') f=-1;\n        ch=getchar();\n    }\n    while(ch>='0'&&ch<='9'){\n        x=(x<<1)+(x<<3)+(ch^48);\n        ch=getchar();\n    }\n    n=x*f;\n}"
        ],
        "description": "基本结构"//简单的描述
    },//这里需要加逗号
}
```

这样就配置好了。

## 换背景

相信大家都看到了，我的编辑器是有背景的。安装一个插件就可以了。

插件的原理很简单，因为 VSC 是基于 Electron 的，所以就可以通过修改 `css` 来更换。

咕咕咕...