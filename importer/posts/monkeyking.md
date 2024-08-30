---
title: 猴王 题解 || 冷门的 pb_ds 库
tags:
- STL
- pbds
- OI
- C++
- 堆
- 数据结构
- 并查集
categories: OI
date: 2023-08-22 11:02:23
updated: 2023-08-22 11:02:23
abbrlink: houwang
cover: https://npm.elemecdn.com/saiodgm-api@1.0.1/randomimg-my/7.webp
---


# 前言

虽然很久以前（6月）在我们刚学并查集的时候 QYC 就给我们讲了左偏树可以拿来做这道题，但是左偏树作为拓展内容还是稍有难度，最近在 gcc 中看到 pb_ds 库，发现非常好用，于是就有了这种偷懒解法。

# pb_ds 库

pb_ds 库是内置于 GCC 中的一种拓展库，可以在 CCF 系列比赛中使用。

pb_ds 库中提供了许多好用的数据结构，比如远快于 `unordered_map` （umap 常数太大）的 `gp_hash_table` （查探法）和 `cc_hash_table`，还有我们接下来要用到的各种不同于 STL 的配对堆、二顶堆等其它在某些方面优于二叉堆的结构，以及在 C2025 现阶段尚未学习的各种平衡树。

下面重点讲一下 pb_ds ~~平板电视~~ 库中的 `__gnu_pbds::priority_queue`。

## 引入

可以使用：

```c++
#include <ext/pb_ds/priority_queue.hpp>
```

来引入 pb_ds 的 pq，但是你也可以通过以下方式图方便：

```c++
#include <bits/extc++.h>
using namespace std;
using namespace __gnu_cxx;
using namespace __gnu_pbds;
```

一次性导入包括 `std::` 在内的所有 GCC 内置库。

上面的 `bits/extc++.h` 在 TDM-GCC 下会报错，需要手动找到文件（编译器会提示）删除这一段：

```c++
#ifdef _GLIBCXX_HAVE_ICONV
 #include <ext/codecvt_specializations.h>
 #include <ext/enc_filebuf.h>
#endif
```

## 使用

使用以下方式来定义一个大根堆（比起STL少一个定义堆存储类型的参数，多一个类型声明）：

```cpp
__gnu_pbds::priority_queue<type,less<type>,pairing_heap_tag> //避免和stl混淆，pairing_heap_tag表示声明配对堆，可以合并
//有pairing_heap_tag binary_heap_tag binomial_heap_tag rc_binomial_heap_tag thin_heap_tag
//实测pairing_heap_tag在本题中表现最优秀，二叉堆会TLE，具体可以参考下文OIWiki
//实际上是可以缺省的
__gnu_pbds::priority_queue<type>
```

大体上和 STL 差不多，只不过支持了 `Remove()` 、`Modify()` 和 `Merge()` 操作：

Merge 复杂度 $O(1)$

```cpp
a.join(b); //将b并入a，b清空，两堆类型需要一致
```

Remove 和 Modify 需要迭代器支持：

```cpp
auto it=pq.push(114514); //push返回元素迭代器
pq.modify(it,1919810); //修改114514为1919810
pq.remove(it); //删除1919810
```

其它部分可以参见：https://oi-wiki.org/lang/pb-ds/pq/

# 解析

知道了可并堆的用法，我们就可以做这道题了。

我采用了这样的方案：维护一个数组 `pq a[]` 存储每一个猴子所在集合的朋友，再维护一个并查集来映射每一个猴子所在的集合，每次争斗后取出堆顶各自减半，再将两猴子的堆合并到第一个猴子那边，并合并并查集即可。

这样是不是比左偏树什么的简单多了qwq

# 代码

下面是这道题的代码，其实也就很简单了

## 注释版

```cpp
#include <bits/extc++.h>
using namespace std;
using namespace __gnu_pbds;
using namespace __gnu_cxx;
__gnu_pbds::priority_queue<int> pq[100005]; //这里要防止命名冲突，后面缺省即可
int n,m,fa[100005]; 
int find(int x){ //并查集板子
    return fa[x]==x?x:fa[x]=find(fa[x]);
}
inline void merge(int x,int y){
    int u=find(x),v=find(y);
    if(x!=y) fa[v]=u;
}
int main(){
    ios::sync_with_stdio(0);
    cin>>n,iota(fa,fa+1+n,0); //STL函数，连续给fa进行范围赋值
    for(int i=1,t;i<=n;i++)
        cin>>t,pq[i].push(t); //初始时各自为一个集合
    cin>>m;
    for(int i=1,x,y,t;i<=m;i++){
        cin>>x>>y;
        //两方各自取出堆顶并减半放回去（其实可以用modify但是稍微麻烦）
        t=pq[find(x)].top(),pq[find(x)].pop(),pq[find(x)].push(t/2);
        t=pq[find(y)].top(),pq[find(y)].pop(),pq[find(y)].push(t/2);
        //合并两个堆和并查集
        pq[find(x)].join(pq[find(y)]),merge(x,y);
        //输出最后的堆顶即可
        cout<<pq[find(x)].top()<<endl;
    }
    return 0;
}
//写完了awa
```

## 极速版

```cpp
#include <bits/extc++.h>
using namespace std;
using namespace __gnu_pbds;
using namespace __gnu_cxx;
__gnu_pbds::priority_queue<int> pq[100005];
int n,m,fa[100005];
int find(int x){
    return fa[x]==x?x:fa[x]=find(fa[x]);
}
inline void merge(int x,int y){
    int u=find(x),v=find(y);
    if(x!=y) fa[v]=u;
}
int main(){
    ios::sync_with_stdio(0);
    cin>>n,iota(fa,fa+1+n,0);
    for(int i=1,t;i<=n;i++)
        cin>>t,pq[i].push(t);
    cin>>m;
    for(int i=1,x,y,t;i<=m;i++){
        cin>>x>>y;
        t=pq[find(x)].top(),pq[find(x)].pop(),pq[find(x)].push(t/2);
        t=pq[find(y)].top(),pq[find(y)].pop(),pq[find(y)].push(t/2);
        pq[find(x)].join(pq[find(y)]),merge(x,y);
        cout<<pq[find(x)].top()<<endl;
    }
    return 0;
}
```
