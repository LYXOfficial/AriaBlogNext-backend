---
title: Interval GCD 题解 || WHK废物快乐题
abbrlink: 9581764a
tags:
  - OI
  - 数论
  - 线段树
  - 树状数组
  - C++
categories: OI
date: 2023-07-16 00:18:06
updated: 2023-07-16 00:18:06
cover: https://bu.dusays.com/2023/07/16/64b2cd8354b26.webp
---

转自校内OJ博客，懒得改了（

这原本是lyd蓝书CH上的题欸……

### 题目

给定一个长度为$N$的数列$A$，以及$M$条指令 ($N≤5\times10^5$,$ M<=10^5$)，每条指令可能是以下两种之一：

`C l r d`，表示把 `A[l],A[l+1],…,A[r]` 都加上 `d`。

`Q l r`，表示询问 `A[l],A[l+1],…,A[r]` 的最大公约数(GCD)。

#### 输入
第一行两个整数$N,M$，第二行$N$个整数$A_i$，接下来M行每条指令的格式如题目描述所示。

#### 输出
对于每个询问，输出一个整数表示答案。

#### 样例
##### 样例输入1
```
5 5
1 3 5 7 9
Q 1 5
C 1 5 1
Q 1 5
C 3 3 6
Q 2 4
```
##### 样例输出1
```
1
2
4
```

#### 提示

$N,M≤2\times10^5$，$l<=r$，数据保证任何时刻序列中的数都是不超过2^62-1的正整数。

### 题意

给定一个序列，需要对其进行区间加和和查询 $\gcd$ 操作。

### 思路

首先看到了区间加和，自然想到是直接打懒标记，但是呢。。。 $\gcd$ 具有一些特殊性，我们并不能通过向下传递标记的方式维护 $\gcd$ 。

于是想到树状数组区间修改的差分数组方案。

我们创建一个数组 b 来维护这个数列的差分值即 $b_i=a_i-a_{i-1}$，每一次区间修改就对区间的头尾进行单点增加即可。

那么b有什么用呢？请看：

首先在我们刚学递归的时候，老师们就曾讲过《九章算术》中求 $\gcd$ 的更相减损术：

$\gcd(x,y)= \gcd(x,y-x)$

对于这个whk废物来说，证明它确实有点困难，不过通过BDFS的方式，得到了这样的答案：

设 $gcd(x,y)=k$ ，显然 $x=k\cdot p_1,y=k\cdot p_2$；

$\therefore \gcd(y,x-y)=\gcd(p_2\cdot k,k\cdot (p_1-p_2) )=k$

很好，我们证出来了这个之后可以容易地归纳出：

$\gcd(a_1,a_2,...a_{n-1},a_n)=\gcd(a_1,a_2-a_1,a_3-a_2,...a_{n-3}-a_{n-2},a_{n}-a{n-1})=\gcd(a_1,\gcd(a_2-a_1,a_3-a_2,...a_{n-3}-a_{n-2},a_{n}-a_{n-1}))$

*~~我不告诉你其实这个我没有证明出来是瞎猜的~~*

看到最后一个式子了么？$a_2-a_1,a_3-a_2,...a_{n-3}-a_{n-2},a_{n}-a_{n-1}$ 不就是我们刚刚维护的 $b$ 数组吗？那么问题就转化成了维护 $b$ 的 $\gcd$ 了。

最后还有一点，求 $\gcd$ 的时候第一个参数 $a_1$ 怎么求？非常简单，只需要维护一个树状数组来修改 $a$ ，传入 $a_l$ 就行了。

那么树状数组怎么区间增加呢？用树状数组维护一个差分数组，修改时更改左右端点，初始化为0表示原本 `a[i]` 的变化量，然后加上 `a[i]` 即可。

其实这也可以再打一个维护前缀和的线段树，但是有点麻烦了。

这时候 `Q l r` 就等价于：`gcd(a[l],ask(1,l+1,r))`

对于`gcd`函数来说，我直接采用了 gcc 内置的 `__gcd` 函数，反正CCF比赛都是能用的（喜）

### 代码

无坑。

#### 注释版

```cpp
#include <bits/stdc++.h>
#define gcd __gcd //节约码长... 
#define int long long //坏习惯，但是我用了 
using namespace std;
struct node{
    int l,r,data; //维护的线段树，我采用结构体维护单个节点 
}t[2000005];
int m,n,arr[500005],l,r,a,b[500005],c[500005];
char ch;
// 线段树板子 
void build(int p,int l,int r){
    t[p].l=l,t[p].r=r;
    if(l==r) t[p].data=b[l];
    else{
        int mid=(l+r)>>1;
        build(p*2,l,mid);
        build(p*2+1,mid+1,r);
        t[p].data=gcd(t[p*2].data,t[p*2+1].data); //这里把板子上面的min改为gcd就行了 
    }
}
void change(int p,int x,int v){
    if(t[p].l==t[p].r) t[p].data+=v;
    else{
        int mid=(t[p].l+t[p].r)>>1;
        if(x<=mid) change(p*2,x,v);
        else change(p*2+1,x,v);
        t[p].data=gcd(t[p*2].data,t[p*2+1].data); //l18，s++
    }
}
int ask(int p,int l,int r){
    if(l<=t[p].l&&r>=t[p].r) return abs(t[p].data);
    int mid=(t[p].l+t[p].r)>>1,val=0; //这里val必须初始化为0不然会爆0 
    if(l<=mid) val=gcd(val,ask(p*2,l,r));
    if(r>mid) val=gcd(val,ask(p*2+1,l,r));
    return val;
}
// 树状数组板子，实际上维护的是差分，前缀和即为a[i]的变化量 
inline int lowbit(int x) {return x&-x;}
inline int gs(int x){
	int ans=0;
	for(;x;x-=lowbit(x)) ans+=c[x];
	return ans;
}
inline void add(int x,int y){
	for(;x<=n;x+=lowbit(x)) c[x]+=y;
}
signed main(){ /*因为用了 #define int long long导致函数返回值变成long long而编译器又不允许，
signed又等价于int，所以只能这样子写（其实在编译器宽松的情况下可以不加返回类型和return 0来压行，但是CCF比赛必爆0）*/
    ios::sync_with_stdio(0); //读入优化 
    cin>>n>>m; 
    for(int i=1;i<=n;i++)
        cin>>arr[i],b[i]=arr[i]-arr[i-1]; //维护差分数组 
    build(1,1,n); // 不build_tree见祖宗 
    while(m--){ //循环m次的简便写法，m减到0变成false即停止 
        cin>>ch;
        switch(ch){ //switch开关，稍微比if简单，注意除最后一部分外每个部分结束要加break不然爆0 
            case 'C':
                cin>>l>>r>>a;
                //维护线段树和树状数组的差分
                add(l,a),change(1,l,a);
                change(1,r+1,-a),add(r+1,-a);
                break;
            case 'Q':
                cin>>l>>r;
                // 见上文 
                cout<<gcd(ask(1,l+1,r),arr[l]+gs(l))<<endl;
                break;
        }
    }
    return 0;
}
```

#### 极速版

~~*无注释版*~~ <span style="color:white">可以CTJ的代码</span>

```cpp
#include <bits/stdc++.h>
#define gcd __gcd
#define int long long
using namespace std;
struct node{
    int l,r,data;
}t[2000005];
int m,n,arr[500005],l,r,a,b[500005],c[500005];
char ch;
void build(int p,int l,int r){
    t[p].l=l,t[p].r=r;
    if(l==r) t[p].data=b[l];
    else{
        int mid=(l+r)>>1;
        build(p*2,l,mid);
        build(p*2+1,mid+1,r);
        t[p].data=gcd(t[p*2].data,t[p*2+1].data);
    }
}
void change(int p,int x,int v){
    if(t[p].l==t[p].r) t[p].data+=v;
    else{
        int mid=(t[p].l+t[p].r)>>1;
        if(x<=mid) change(p*2,x,v);
        else change(p*2+1,x,v);
        t[p].data=gcd(t[p*2].data,t[p*2+1].data);
    }
}
int ask(int p,int l,int r){
    if(l<=t[p].l&&r>=t[p].r) return abs(t[p].data);
    int mid=(t[p].l+t[p].r)>>1,val=0;
    if(l<=mid) val=gcd(val,ask(p*2,l,r));
    if(r>mid) val=gcd(val,ask(p*2+1,l,r));
    return abs(val);
}
inline int lowbit(int x) {return x&-x;}
inline int gs(int x){
	int ans=0;
	for(;x;x-=lowbit(x)) ans+=c[x];
	return ans;
}
inline void add(int x,int y){
	for(;x<=n;x+=lowbit(x)) c[x]+=y;
}
signed main(){
    ios::sync_with_stdio(0);
    cin>>n>>m;
    for(int i=1;i<=n;i++)
        cin>>arr[i],b[i]=arr[i]-arr[i-1];
    build(1,1,n);
    while(m--){
        cin>>ch;
        switch(ch){
            case 'C':
                cin>>l>>r>>a;
                add(l,a),change(1,l,a);
                if(r<n) change(1,r+1,-a),add(r+1,-a);
                break;
            case 'Q':
                cin>>l>>r;
                cout<<gcd(ask(1,l+1,r),arr[l]+gs(l))<<endl;
                break;
        }
    }
    return 0;
}
```