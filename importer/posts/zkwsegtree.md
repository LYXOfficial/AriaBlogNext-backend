---
title: 数据结构——浅谈 zkw 线段树
tags:
- OI
- C++
- 数据结构
- 线段树
- 位运算
categories: OI
date: 2023-08-22 15:29:08
updated: 2023-08-22 15:29:08
abbrlink: orzzkwdl
cover: https://cdn.fzoi.top/upload/user/st20250310/23082203323998.jpeg
---
# 前言

数论好难，所以回去看了看qwq

最近在复习前面的知识的时候突然发现 Tad 以前给我们发的 zkw 线段树讲稿，去研究了一番，发现这个玩意非常强大，然后就有感而发写了此文。。。

# 介绍

原讲稿可自行百度。

线段树确实是一个实用、高效还万能的数据结构，一切皆为 $O(\log n)$ ，问题在于它的常数极大，非常令人烦恼，经常被卡掉，即使是用二进制优化堆存储+快都快写依然力不从心。

实际上线段树是不需要递归的，有一些方式可以实现非递归线段树以减少递归开销。

ZKW 线段树就是一种不错的非递归解决方案。

它是由一位清华大佬张昆玮发明的一种非递归线段树，采用了二进制位运算的方式计算节点，所以具有相当优秀的常数，在一般 RMQ 问题中使用时间常数约为普通线段树的 $\begin{aligned}\frac{1}{2} \sim \frac{1}{4}\end{aligned}$ ，树状数组和 ST 表的 $\begin{aligned}\frac{4}{5}\sim \frac{5}{2}\end{aligned}$ 倍，算是相当优秀了。

zkw 线段树的整体代码给人了一种树状数组的简洁感，甚至他本人在演讲中告诉大家树状数组就是去掉一个 2 倍空间的线段树（

# 解析

本文参考了 https://www.cnblogs.com/frankchenfu/p/7132445.html ，故部分地方可能稍有雷同，请谅解。

下面将以求区间和为例进行讲解。

## 单点修改区间查询

### 建树

![](https://cdn.fzoi.top/upload/user/st20250310/23082106539311.png)

这是一个长度为4的线段对应的二叉树，树上的每个节点对应的权值就是每个节点编号的二进制表示。可见第三层的节点右移一位之后，就变成了他们的父节点。同理，第二层中的结点也可以通过相同的方式变成根节点。

看起来和普通的线段树一样，都是堆存储，不过...

这棵树其实是可以使用普通的循环方式存下来的。

我们先获取一个全局变量bit表示这棵线段树非叶子节点的总数，可以通过循环移位的方式拿到：

```cpp
for(bit=1;bit<=n+1;bit<<=1);
```

然而人家这个bit以后都是要用到的呢:(

然后给所有叶子节点赋值：

```cpp
for(int i=bit+1;i<=bit+n;i++)
	t[i]=arr[i-bit];
```

接下来呢？当然是向上传递了，实际上只需要倒序遍历非叶子节点（保证层数从下向上传递），然后加和即可。

```cpp
for(int i=bit-1;i;i--)
   t[i]=t[i<<1]+t[i<<1|1]; //位运算优化堆存储
```

那么整个build就长这样了：

```cpp
inline void build(){
    for(bit=1;bit<=n+1;bit<<=1);
    for(int i=bit+1;i<=bit+n;i++)
        t[i]=arr[i-bit];
    for(int i=bit-1;i;i--)
        t[i]=t[i<<1]+t[i<<1|1];
}
```

当然是非常的简洁啦~ 比起原版递归线段树真的好了很多，虽然时间复杂度都是 $O(n)$ ，但是没有递归开销

```c++
//原版
void build(int p,int l,int r){
	t[p].l=l,t[p].r=r;
	if(l==r){
		t[p].sum=a[l];
		return;
	}
	int mid=(l+r)>>1;
	build(p*2,l,mid);
	build(p*2+1,mid+1,r);
	t[p].sum=t[p*2].sum+t[p*2+1].sum;
}
```

### 单点修改

修改敲简单的！先找到它对应在树上的叶子节点，然后一直找父亲传递就好了欸！

```cpp
inline void change(int x,int v){
    for(t[x+=bit]=v,x>>=1;x;x>>=1)
        t[x]=t[x<<1]+t[x<<1|1];
}
```

比起原版是不是简单多了？

```cpp
void change(int p,int x,int v){
    if(t[p].l==t[p].r) t[p].data=v;
    else{
        int mid=(t[p].l+t[p].r)>>1;
        if(x<=mid) change(p*2,x,v);
        else change(p*2+1,x,v);
        t[p].data=t[p*2].data+t[p*2+1].data;
    }
}
```

### 区间查询

区间查询稍微麻烦一小点了，首先要把区间化为开区间（为了防止越界到其他位置，大家可以结合上面的那个图看一下），然后从下往上找父亲传递就好了。

```cpp
inline int ask(int l,int r){
    int ans=0;
    for(l+=bit-1,r+=bit+1;l^r^1;l>>=1,r>>=1){
        if(~l&1) ans+=t[l^1];
        if(r&1) ans+=t[r^1];
    }
    return ans;
}
```

类似普通线段树，需要判断左右孩子。

`~l&1` ,意思是是否为左儿子，对于兄弟节点来说，最低位为 0 或 1,0 为左儿子，1 为右儿子，对于左端点 `l` 来说，我们只需向右合并更新 `ans`（加上兄弟节点，也就是右节点，`l^1`），而不管其左边。当然 `r&1`，同理意思是是否为右儿子。

每次循环后移向其父节点继续操作，退出条件为 `l^r^1` ,为什么呢？若 `l` 和 `r` 不为同一点或兄弟节点，`l^r^1` 一定为 `true`，否则在为同一点或兄弟节点时跳出循环。

### 代码

最后贴出一道[树状数组1](https://loj.ac/p/130)のzkw线段树版本：

PS：板子不好找，将就用树状数组的。

对比时间复杂度：

树状数组：https://loj.ac/s/1819032
zkw: https://loj.ac/s/1869150
普通线段树：https://loj.ac/s/1869161

（快读zkw甚至比树状数组快

```cpp
#include <bits/stdc++.h>
using namespace std;
int m,n,bit,t[4000005],arr[4000005],l,r,a,b;
char ch;
inline void build(){
    for(bit=1;bit<=n+1;bit<<=1);
    for(int i=bit+1;i<=bit+n;i++)
        t[i]=arr[i-bit];
    for(int i=bit-1;i;i--)
        t[i]=t[i<<1]+t[i<<1|1];
}
inline void change(int x,int v){
    for(t[x+=bit]=v,x>>=1;x;x>>=1)
        t[x]=t[x<<1]+t[x<<1|1];
}
inline int ask(int l,int r){
    int ans=0;
    for(l+=bit-1,r+=bit+1;l^r^1;l>>=1,r>>=1){
        if(~l&1) ans+=t[l^1];
        if(r&1) ans+=t[r^1];
    }
    return ans;
}
int main(){
    ios::sync_with_stdio(0);
    cin>>n>>m;
    for(int i=1;i<=n;i++) cin>>arr[i];
    build();
    for(int i=1;i<=m;i++){
        cin>>ch;
        switch(ch){
            case '1':
                cin>>a>>b;
                change(a,ask(a,a)+b);
                break;
            case '0':
                cin>>l>>r;
                cout<<ask(l,r)<<endl;
                break;
        }
    }
    return 0;
}
```

## 区间修改区间查询

与平常所用的线段树不同，因为实现原理的差别（一个是递归传递一个是迭代递推），所以说我们像普通线段树一样来进行懒标记是超级麻烦的qwq。

那么我们该怎么办呢？还记得在树状数组中学到的差分吗？我们这里也需要用到类似的思想，不过按照zkw的说法，这叫做标记永久化。

考虑维护一个结构体堆 $t$ 作为线段树，定义 $sum$ 为线段树本来维护的和，而 $add$ 为该节点和它父亲的差，即为差分数组。

那么我们就相当于在维护一个永久化标记（树上差分？）了。

原文：

其实堆式存储也可以自顶向下访问

就是上下各走一次而已

但是我们有更好的办法

这里我们采用标记永久化的思想（就是不下推lazy tag让他彻底lazy下去）

```c
int add[MAXN<<2];
```

![](https://cdn.fzoi.top/upload/user/st20250310/23082109003769.png)

因为要维护两个数值了，所以我采用了结构体 `pair` 的方式建树。

```cpp
#define add first
#define sum second //方便理解
pair<int,int> t[4000005];
//如果用的是结构体别忘了初始化
```

### 区间建树

只需要维护 $sum$ 就好了awa

```c++
inline void build(){
    for(bit=1;bit<=n+1;bit<<=1);
    for(int i=bit+1;i<=bit+n;i++)
        t[i].sum=arr[i-bit];
    for(int i=bit-1;i;i--)
        t[i].sum=t[i<<1].sum+t[i<<1|1].sum;
}
```

### 区间修改

这是一棵zkw线段树（图源某lg日报）:

![](https://cdn.fzoi.top/upload/user/st20250310/23082210188759.jpeg)

如果我们需要修改区间 `[2,10]` 整体加 $k$ 的话，会涉及到这些部分：

![](https://cdn.fzoi.top/upload/user/st20250310/23082210533353.jpeg)

当然，为了确保永久化正确性，我们需要上推到根节点（这样可能会出现常数在数据水的时候比逼近于普通线段树了）

有了这样的差分维护思想（说实话也感觉跟平常的lazy大差不差），我们就可以写出区间修改代码了：

```cpp
inline void change(int l,int r,int v){
    int lc=0,rc=0,len=1; 
    for(l+=bit-1,r+=bit+1;l^r^1;l>>=1,r>>=1,len<<=1){
        if(~l&1) t[l^1].add+=v,lc+=len;
        if(r&1)  t[r^1].add+=v,rc+=len;
        t[l>>1].sum+=v*lc,t[r>>1].sum+=v*rc;
    }
    for(lc+=rc;l>1;l>>=1)
        t[l>>1].sum+=v*lc;
}
```

### 区间查询

过程类似，基本上查询加上即可，不过注意加上原数组的 $sum$。

```cpp
#include <bits/stdc++.h>
#define int long long
#define sum first
#define add second
using namespace std;
int m,n,bit,arr[1000005],l,r,a,b,x;
pair<int,int> t[4000005];
char ch;
template<typename T>
inline void read(T* n){
    T x=0;bool f=1;
    char c=getchar();
    while(c<48||c>57)
        f=c!=45,c=getchar();
    while(c>47&&c<58)
        x=(x<<3)+(x<<1)+(c^48),
        c=getchar();
    *n=f?x:-x;
}
template<typename T>
inline void read(initializer_list<T*> il){
    for(auto &it:il) read<T>(it);
}
template<typename T>
void read(T* beg,T* ed){
    for(;beg!=ed;++beg)
        read<T>(beg);
}
template<typename T>
void write(T x){
    if(x<0) putchar(45),x=-x;
    if(x>9) write(x/10);
    putchar(x%10+48);
}
inline void build(){
    for(bit=1;bit<=n+1;bit<<=1);
    for(int i=bit+1;i<=bit+n;i++)
        t[i].sum=arr[i-bit];
    for(int i=bit-1;i;i--)
        t[i].sum=t[i<<1].sum+t[i<<1|1].sum;
}
inline void change(int l,int r,int v){
    int lc=0,rc=0,len=1; 
    for(l+=bit-1,r+=bit+1;l^r^1;l>>=1,r>>=1,len<<=1){
        if(~l&1) t[l^1].add+=v,lc+=len;
        if(r&1)  t[r^1].add+=v,rc+=len;
        t[l>>1].sum+=v*lc,t[r>>1].sum+=v*rc;
    }
    for(lc+=rc;l>1;l>>=1)
        t[l>>1].sum+=v*lc;
}
inline int ask(int l,int r){
    int lc=0,rc=0,len=1,ans=0;
    for(l+=bit-1,r+=bit+1;l^r^1;l>>=1,r>>=1,len<<=1){
        if(~l&1) ans+=t[l^1].sum+len*t[l^1].add,lc+=len;
        if(r&1) ans+=t[r^1].sum+len*t[r^1].add,rc+=len;
        if(t[l>>1].add) ans+=t[l>>1].add*lc;
        if(t[r>>1].add) ans+=t[r>>1].add*rc; 
    }
    for(lc+=rc,l>>=1;l;l>>=1)
        if(t[l].add) ans+=t[l].add*lc;
    return ans;
}
signed main(){
    read({&n,&m}),read(arr+1,arr+1+n),build();
    for(int i=1;i<=m;i++){
        ch=getchar();
        switch(ch){
            case '1': read({&a,&b,&x}),change(a,b,x);break;
            case '2': read({&l,&r}),write(ask(l,r)),puts("");
        }
    }
    return 0;
}
```

### 代码

贴出一份[树状数组3](https://loj.ac/p/132)或[P3372（线段树1）](https://www.luogu.com.cn/problem/P3372)的zkw版完整版代码（不开ll真见祖宗qwq）

复杂度对比：

普通线段树：https://loj.ac/s/1819042
zkw： https://loj.ac/s/1869146

```cpp
#include <bits/stdc++.h>
#define int long long
#define sum first
#define add second
using namespace std;
int m,n,bit,arr[1000005],l,r,a,b,x,op;
pair<int,int> t[4000005];
template<typename T>
inline void read(T* n){
    T x=0;bool f=1;
    char c=getchar();
    while(c<48||c>57)
        f=c!=45,c=getchar();
    while(c>47&&c<58)
        x=(x<<3)+(x<<1)+(c^48),
        c=getchar();
    *n=f?x:-x;
}
template<typename T>
inline void read(initializer_list<T*> il){
    for(auto &it:il) read<T>(it);
}
template<typename T>
void read(T* beg,T* ed){
    for(;beg!=ed;++beg)
        read<T>(beg);
}
template<typename T>
void write(T x){
    if(x<0) putchar(45),x=-x;
    if(x>9) write(x/10);
    putchar(x%10+48);
}
inline void build(){
    for(bit=1;bit<=n+1;bit<<=1);
    for(int i=bit+1;i<=bit+n;i++)
        t[i].sum=arr[i-bit];
    for(int i=bit-1;i;i--)
        t[i].sum=t[i<<1].sum+t[i<<1|1].sum;
}
inline void change(int l,int r,int v){
    int lc=0,rc=0,len=1; 
    for(l+=bit-1,r+=bit+1;l^r^1;l>>=1,r>>=1,len<<=1){
        if(~l&1) t[l^1].add+=v,lc+=len;
        if(r&1)  t[r^1].add+=v,rc+=len;
        t[l>>1].sum+=v*lc,t[r>>1].sum+=v*rc;
    }
    for(lc+=rc;l>1;l>>=1)
        t[l>>1].sum+=v*lc;
}
inline int ask(int l,int r){
    int lc=0,rc=0,len=1,ans=0;
    for(l+=bit-1,r+=bit+1;l^r^1;l>>=1,r>>=1,len<<=1){
        if(~l&1) ans+=t[l^1].sum+len*t[l^1].add,lc+=len;
        if(r&1) ans+=t[r^1].sum+len*t[r^1].add,rc+=len;
        if(t[l>>1].add) ans+=t[l>>1].add*lc;
        if(t[r>>1].add) ans+=t[r>>1].add*rc; 
    }
    for(lc+=rc,l>>=1;l;l>>=1)
        if(t[l].add) ans+=t[l].add*lc;
    return ans;
}
signed main(){
    read({&n,&m}),read(arr+1,arr+1+n),build();
    for(int i=1;i<=m;i++){
        read(&op);
        switch(op){
            case 1: read({&a,&b,&x}),change(a,b,x);break;
            case 2: read({&l,&r}),write(ask(l,r)),puts("");
        }
    }
    return 0;
}
```
