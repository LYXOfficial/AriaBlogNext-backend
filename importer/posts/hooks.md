---
title: 运用 Windows 的 Hook 淦极域 && MinHook 入门教程 
cover: https://bu.dusays.com/2023/07/29/64c5221e7a165.jpg
abbrlink: 'mhaoxonk'
date: 2023-07-29 17:42:09
updated: 2023-07-29 22:29:09
tags:
- 编程
- Windows
- NoTopDomain
- C++
- Hook
categories: 编程
---
# 前言

因为 NTD 的某 UDP 重放攻击被机房的同学们大肆滥用（诸如乱关机），加上我们的 Tad 的一些坑人行为，于是就阅读并参考 JiyuTrainer 的源码，然后在 NoTopDomain 加上了拦截远程命令、杀进程和置顶功能。

阅读本文章前，请确保您拥有以下前置知识：

1. C/C++ 的语言基础
2. 能够简单使用 Windows API

如果您缺少一部分，建议先学习之后再过来。

# 了解 Hook技术

摘自：

{% link Hook（钩子技术）基本知识讲解，原理,CSDN,https://blog.csdn.net/qq_36381855/article/details/79962673 %}

## 一、什么是HOOK（钩子） 

对于Windows系统，它是建立在事件驱动机制上的，说白了就是整个系统都是通过消息传递实现的。hook（钩子）是一种特殊的消息处理机制，它可以监视系统或者进程中的各种事件消息，截获发往目标窗口的消息并进行处理。所以说，我们可以在系统中自定义钩子，用来监视系统中特定事件的发生，完成特定功能，如屏幕取词，监视日志，截获键盘、鼠标输入等等。

钩子的种类很多，每种钩子可以截获相应的消息，如键盘钩子可以截获键盘消息，外壳钩子可以截取、启动和关闭应用程序的消息等。钩子可以分为线程钩子和系统钩子，线程钩子可以监视指定线程的事件消息，系统钩子监视系统中的所有线程的事件消息。因为系统钩子会影响系统中所有的应用程序，所以钩子函数必须放在独立的动态链接库(DLL) 中。
       
所以说，hook（钩子）就是一个Windows消息的拦截机制，可以拦截单个进程的消息(线程钩子)，也可以拦截所有进程的消息(系统钩子)，也可以对拦截的消息进行自定义的处理。Windows消息带了一些程序有用的信息，比如Mouse类信息，就带有鼠标所在窗体句柄、鼠标位置等信息，拦截了这些消息，就可以做出例如金山词霸一类的屏幕取词功能。

## 二、Hook 分类

（1） 线程钩子监视指定线程的事件消息。

（2） 系统钩子监视系统中的所有线程的事件消息。因为系统钩子会影响系统中所有的应用程序，所以钩子函数必须放在独立的动态链接库(DLL)中。这是系统钩子和线程钩子很大的不同之处。

## 三、HOOK（钩子）的工作原理

在正确使用钩子函数前，我们先讲解钩子函数的工作原理。当您创建一个钩子时，WINDOWS会先在内存中创建一个数据结构，该数据结构包含了钩子的相关信息，然后把该结构体加到已经存在的钩子链表中去。新的钩子将加到老的前面。当一个事件发生时，如果您安装的是一个线程钩子，您进程中的钩子函数将被调用。如果是一个系统钩子，系统就必须把钩子函数插入到其它进程的地址空间，要做到这一点要求钩子函数必须在一个动态链接库中，所以如果您想要使用系统钩子，就必须把该钩子函数放到动态链接库中去。

当然有两个例外：工作日志钩子和工作日志回放钩子。这两个钩子的钩子函数必须在安装钩子的线程中。原因是：这两个钩子是用来监控比较底层的硬件事件的，既然是记录和回放，所有的事件就当然都是有先后次序的。所以如果把回调函数放在DLL中，输入的事件被放在几个线程中记录，所以我们无法保证得到正确的次序。故解决的办法是：把钩子函数放到单个的线程中，譬如安装钩子的线程。

### 几点需要说明的地方： 

（1） 如果对于同一事件（如鼠标消息）既安装了线程钩子又安装了系统钩子，那么系统会自动先调用线程钩子，然后调用系统钩子。

（2） 对同一事件消息可安装多个钩子处理过程，这些钩子处理过程形成了钩子链。当前钩子处理结束后应把钩子信息传递给下一个钩子函数。而且最近安装的钩子放在链的开始，而最早安装的钩子放在最后，也就是后加入的先获得控制权。

（3） 钩子特别是系统钩子会消耗消息处理时间，降低系统性能。只有在必要的时候才安装钩子，在使用完毕后要及时卸载。



**简单的说，就是在 Windows 进行消息处理时拦截该消息并进行额外的处理的一种系统机制，可以形象的当作一个钩子来比喻。**

# Windows Hook 的一个小实例

众所周知，极域会在广播和黑屏时加上一层键盘锁，使我们无法通过一些特殊的方式关掉它。实际上极域就是用了 Windows 的全局钩子拦截住了 WM_KEYBOARD 事件，然后返回一个错误值，使键盘无法正常使用。

那么我们就可以通过把钩子钩回去的方式来解除极域键盘锁了。

在 Windows API 文档中，提供了这样一种函数，可以设置一种全局钩子：

```cpp
HHOOK SetWindowsHookEx(
  int       idHook,
  HOOKPROC  lpfn,
  HINSTANCE hmod,
  DWORD     dwThreadId
);
```

其中，`idHook` 表示挂钩类型，`lpfn` 表示hook的回调函数（注意要强转以下），`hmod` 表示挂钩 DLL 句柄，如果想要设置为全局 Hook，参数需要写成 `GetModuleHandle(NULL)`，`dwThreadId` 表示挂钩线程，一般留为0即可。

那么我们解键盘锁的函数可以写成这样（具体讲解见注释）：

```cpp
HOOKPROC HookProc(int nCode,WPARAM wParam,LPARAM lParam){
    return 0; //这是Hook回调函数的参数，因为我们不需要执行任何内容，只是为了覆盖掉极域，所以直接返回0表示事件正常运行即可
}
void UnlockKeyboard(){
    HHOOK kbdHook=SetWindowsHookEx(WH_KEYBOARD_LL,(HOOKPROC)HookProc,GetModuleHandle(NULL),0); //设置Hook函数，注意要记录一个返回句柄
    Sleep(50); //等待一会
    UnhookWindowsHookEx(kbdHook); //根据前面返回的句柄卸载掉该Hook
}
```

不过实际上我们的 `UnlockKeyboard` 是需要循环执行的，所以我们一般会在程序里加一个线程，然后在里面这样写：

```cpp
bool canHook=1; //标记是否选中了需要解键盘锁选项的一个变量
while(1)
    if(canHook)
        UnlockKeyboard();
```

注意以上 API 在PyWin32 中不可用，建议用 C++ 编写后打包成 DLL 给 Python 调用（参考 `NTDTools.dll`）

# Hook一个 WinAPI 函数

~~PS：JiYuTrainer用的是 mhook 库，并不是我采用的 MinHook，后者稍微强大一些。~~

大家应该发现了，上面的 Hook 都是针对 Windows 的消息处理的，那我们能不能给一个函数挂钩呢？在极域内部实现中，它调用了 `CreateProcessW` `TerminateProcess` 等函数，我们是不是可以修改其内部实现后注入进极域实现拦截并与软件主进程通信呢？

微软并没有提供像样的解决方案。唯一勉强可以的是免费版的 Detour 库，可惜它只支持 32 位，且配置复杂，这显然不符合我们的要求。

不过微软没写，倒是有一个叫做 `MinHook` 的库实现了函数 Hook 的功能，使用了 inline hook 技术。

接下来介绍一下它的使用吧。

## MinHook 库的获取

因为许多 OIer 都使用的是 GCC 编译器，所以这里的配置教程都针对 GCC。

偶尔会遇到一些库函数版本不兼容，建议大家使用尽可能新的 GCC 版本。

首先在 Github 上获取 MinHook.h 和 MinHook.x(64/86).lib、MinHook.x(64/86).dll

{% link TsudaKageyu/minhook Release,Github,https://github.com/TsudaKageyu/minhook/release %}

然后下载 MinHook_133_bin.zip ，解压上面说到的三个文件，是 x86 还是 x64 根据自己编译软件情况决定，因为极域是 32 位的，直接下载 x86 即可，最后将这些文件拷贝到你的程序目录中。

## MinHook 的使用

首先我们需要引入以下头文件

```cpp
#include "MinHook.h"
#include <windows.h>
```

这样就可以开始调用 MinHook 的函数了。

为了初始化 MinHook，需要调用 `MH_Initialize()` 函数并检测是否初始化成功：

```cpp
if(MH_Initialize()!=MH_OK) return TRUE;
```

接下来需要创建一个钩子，在此之前，我们需要拿到 3 个东西：

1. 指向原版被勾函数的指针（real）
2. 自己定义的 Hook 函数（fake）
3. 原版被勾函数的参数类型定义（r）

这些函数的传参需要翻阅 Microsoft 文档后照抄下来，这里以 `MessageBoxA` 为例：

```cpp
int MessageBoxA(
  [in, optional] HWND   hWnd,
  [in, optional] LPCSTR lpText,
  [in, optional] LPCSTR lpCaption,
  [in]           UINT   uType
);
```

那么我们可以这样定义原函数的类型 `rMessageBoxA` ：

```cpp
typedef int (WINAPI *rMessageBoxA)(HWND hWnd,LPCSTR lpText,LPCSTR lpCaption,UINT uType);
```

然后创建指向原函数的指针：

```cpp
rMessageBoxA realMessageBoxA=(rMessageBoxA)&MessageBoxA;
```

最后我们来定义我们自己编写的 Hook 函数：

```cpp
int WINAPI fakeMessageBoxA(HWND hWnd,LPCSTR lpText,LPCSTR lpCaption,UINT uType){
    realMessageBoxA(hWnd,"Hooked!",lpCaption,uType); //改变消息框文本为Hooked!，忽略原本的参数
    return 1;
}
```

接下来就可以创建钩子了，同样注意判断是否创建成功：

```cpp
if(MH_CreateHook((PVOID*)&MessageBoxA,(PVOID*)&fakeMessageBoxA,reinterpret_cast<void**>(&realMessageBoxA))!=MH_OK)
    return TRUE;
```

最后启动钩子：

```cpp
if(MH_EnableHook((PVOID*)&MessageBoxA)!=MH_OK)
    return TRUE;
```

使用以下语句关闭钩子：

```cpp
if(MH_DisableHook((PVOID*)&MessageBoxA)!=MH_OK)
    return TRUE;
```

我们可以写一句调用试一试：

```cpp
MessageBoxA(0,"unHook","test",0);
```

那么整个程序就写成这样子：

```cpp
#include "MinHook.h"
#include <windows.h>
typedef int (WINAPI *rMessageBoxA)(HWND hWnd,LPCSTR lpText,LPCSTR lpCaption,UINT uType);
rMessageBoxA realMessageBoxA=(rMessageBoxA)&MessageBoxA;
int WINAPI fakeMessageBoxA(HWND hWnd,LPCSTR lpText,LPCSTR lpCaption,UINT uType){
    realMessageBoxA(hWnd,"Hooked!",lpCaption,uType); //改变消息框文本为Hooked!，忽略原本的参数
    return 1;
}
int main(){
    if(MH_Initialize()!=MH_OK) return TRUE;
    if(MH_CreateHook((PVOID*)&MessageBoxA,(PVOID*)&fakeMessageBoxA,reinterpret_cast<void**>(&realMessageBoxA))!=MH_OK)
        return TRUE;
    if(MH_EnableHook((PVOID*)&MessageBoxA)!=MH_OK)
        return TRUE;
    MessageBoxA(0,"unHook","test",0);
    // if(MH_DisableHook((PVOID*)&MessageBoxA)!=MH_OK)
        return TRUE;
    return 0;
}
```

## MinHook 的编译

如果我们直接运行程序，会得到以下结果：

```bash
c:/mingw/bin/../lib/gcc/mingw32/9.2.0/../../../../mingw32/bin/ld.exe: C:\Users\lyx-blbl\AppData\Local\Temp\cc0MgB7J.o:test.cpp:(.text+0x63): undefined reference to `MH_CreateHook@12'
c:/mingw/bin/../lib/gcc/mingw32/9.2.0/../../../../mingw32/bin/ld.exe: C:\Users\lyx-blbl\AppData\Local\Temp\cc0MgB7J.o:test.cpp:(.text+0x82): undefined reference to `MH_EnableHook@4'
c:/mingw/bin/../lib/gcc/mingw32/9.2.0/../../../../mingw32/bin/ld.exe: C:\Users\lyx-blbl\AppData\Local\Temp\cc0MgB7J.o:test.cpp:(.text+0xc8): undefined reference to `MH_DisableHook@4'
collect2.exe: error: ld returned 1 exit status
```

显然我们没有链接上 MinHook 的库函数，记得开始下载的 `MinHook.x86/64.lib` 吗？我们需要把它链接上，只需要在程序名后面加上这个lib文件即可。

```bash
g++ test.cpp MinHook.x86.lib -m32 -o test.exe
```

在运行时程序会寻找 MinHook.x86.dll，未找到时也会RE。

接下来运行程序，可以看到我们已经成功进行 Hook 了qwq！

![](https://bu.dusays.com/2023/07/30/64c5c99775d52.png)

# DLL 注入技术

大家应该发现了，这样子写 Hook 的话，只会对自己的程序起效，但是我们要是要淦极域或是其它软件怎么办呢？

这时候就需要请出我们的大杀器——DLL 注入了。

DLL，即动态链接库（Dynamic Link Library），用于在程序运行时动态加载方法函数并实时调用。

当然我们需要的并不是实时调用方法，那些软件也不会傻到自己调用我们写的函数，不过在 Windows API 的加载 DLL 所用的函数 `LoadLibrary` 中，每次用这个函数加载时都会运行 DLL 中导出的 `DllMain` 函数！

那么我们就可以想办法让一个进程用 `LoadLibrary` 加载自己写的 DLL 然后在 DLL 里面藏私活了。这样子就通过 DLL 注入技术实现了自己想要的功能。

## 编写 DLL

首先我们需要编写一份 DLL，来执行我们的东西。

在此之前，需要介绍以下 `DllMain` 的写法：

微软官方文档写成这样子：

```cpp
BOOL WINAPI DllMain(
    HINSTANCE hinstDLL,  // handle to DLL module
    DWORD fdwReason,     // reason for calling function
    LPVOID lpvReserved )  // reserved
{
    // Perform actions based on the reason for calling.
    switch( fdwReason ) 
    { 
        case DLL_PROCESS_ATTACH:
         // Initialize once for each new process.
         // Return FALSE to fail DLL load.
            break;

        case DLL_THREAD_ATTACH:
         // Do thread-specific initialization.
            break;

        case DLL_THREAD_DETACH:
         // Do thread-specific cleanup.
            break;

        case DLL_PROCESS_DETACH:
        
            if (lpvReserved != nullptr)
            {
                break; // do not do cleanup if process termination scenario
            }
            
         // Perform any necessary cleanup.
            break;
    }
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}
```

具体含义请自己机翻（，我们只需要在 switch 开关里面的 DLL_PROCESS_ATTACH 中塞东西就行了。

## 注入的方法

要想注入 DLL，我们一般采用以下方式：

- 申请一块长度为路径长度的内存地址，用于存储 `LoadLibrary` 的参数，即为 DLL 路径
- 把我们的路径参数甩到这块内存里面
- 在一个进程上创建远程线程并执行 `LoadLibrary` 函数，并把我们刚刚拿到的DLL路径内存地址给进去作为参数

写成 C++ 程序就是这样：

```c++
void InjectDLL(DWORD dwId,LPCSTR path){ //dwId为进程PID，path为DLL路径，采用窄字符方式
    HANDLE mProcess=OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwId); //打开进程
    LPTHREAD_START_ROUTINE fun =(LPTHREAD_START_ROUTINE)LoadLibraryA; //获取LoadLibrary地址
    SIZE_T pathSize=strlen(path)+1; //计算路径长度，注意要算对，加上 char*最后的 \0，如果不清楚建议重修C/C++语法基础
    LPVOID mBuffer=VirtualAllocEx(mProcess, NULL, pathSize, MEM_COMMIT, PAGE_READWRITE); //分配写入函数的地址
    WriteProcessMemory(mProcess, mBuffer, path, pathSize, NULL); //写入路径
    CreateRemoteThread(mProcess, NULL, 0, fun, mBuffer, 0, NULL); //创建远程线程并执行
    return;
}
```

至于怎么注入就看实际情况了，注意编译该注入器的位数必须与要注入的程序的位数一致（使用 `-m32` 和 `-m64`），如果不清楚的话可以使用 `IsWow64Process` 和 `GetSystemInfo` 来查看（具体使用见文档）

原因也很简单，32位软件运行在 WoW64环境中，内存分配的机制和64位软件不同，自然无法跨位数分配内存。

这是 NTD 注入进极域的效果：

![](https://bu.dusays.com/2023/08/08/64d23dc3ed12f.png)

![](https://bu.dusays.com/2023/08/08/64d23ddb589c9.png)

（Guy的顾辉和快端上来罢，赶紧似木琴，劳斯莱斯确实很好）

最后提示一下，请勿在任何游戏或测试中使用DLL注入！有封号风险！

（下为这个florr 90级的青红混合卡蒟蒻手贱下汉化插件被封号的悲剧qwq

![](https://bu.dusays.com/2023/08/08/64d2394aa1193.png)