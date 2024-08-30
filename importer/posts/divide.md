---
title: 【ABC254Ex】 Multiply or Divide by 2 题解
cover: 'https://bu.dusays.com/2023/07/29/64c48bea657a3.webp'
abbrlink: c1d78b77
tags:
  - OI
  - 贪心
  - 优先队列
categories: OI
date: 2023-07-22 08:17:53
updated: 2023-07-22 08:17:53
---

传送门：

{% link 【ABC254Ex】 Multiply or Divide by 2,洛谷,https://www.luogu.com.cn/problem/AT_abc254_h %}

### 题意

给你两个集合 $A$ 和 $B$ ，你可以把集合 $A$ 的任意一项变为原来的 $\left \lfloor\frac{1}{2}\right \rfloor $ 或 $2$ 倍，求至少需要操作几步才能使 $A=B$。如果无法将 $A$ 变为 $B$，输出 `-1`。

### 解析

考虑贪心，可以将“把 $A$ 的任意元素变为原来的两倍”转换为“把 $B$ 的任意元素变为原来的 $\frac{1}{2}$”，这两个方法是等效的。

我们维护两个优先队列 `a` 和 `b`代表集合 $A$ 和 $B$ ，每次取出两个集合的最大值进行转化，然后我们采用这样的贪心策略：

如果 `a.top()==b.top()` ，那么直接将这两个元素出队，这说明两个集合的这两个元素已经相等了。

如果 `b.top()>a.top()` ，那么将 `b.top()` 出队，除以2后再入队，这等价于将 集合 $A$ 的最大值乘上2。

大家应该意识到了一个问题，如果将 `b.top()` 除以2的话，实际上是和 `a.top()*2` 的效果并不完全一样，因为除以2时会向下取整，所以到后面会一直多一个 1 而无法将 $A$ 变为 $B$，这种情况就需要输出 `-1` 了。

接下来如果 `a.top()>b.top()` 的话，跟上面一样，将 `a.top()` 出队，除以2后再入队即可，不需要考虑其他条件，因为在题意中已经说到需要向下取整了。

### 代码

那么代码就很简单了，使用优先队列维护即可，单次修改（除 `a.top()==b.top()` 时）执行 `cnt++`，最后输出 `cnt` 作为答案即可。

#### 注释版

```c++
#include <bits/stdc++.h>
using namespace std;
int n,t,cnt; //cnt作为答案 
priority_queue<int> a,b; //优先队列 
int main(){
    ios::sync_with_stdio(0);
    cin>>n;
    for(int i=1;i<=n;i++)
        cin>>t,a.push(t); //直接在a和b中入队，不需要静态数组储存，后面用不到静态数组的 
    for(int i=1;i<=n;i++)
        cin>>t,b.push(t);
    while(!a.empty()){
        if(a.top()==b.top()) //贪心策略1，见TJ 
            a.pop(),b.pop();
        else if(a.top()>b.top()){ //贪心策略3，见TJ 
            t=a.top();
			a.pop(),a.push(t>>1),cnt++;
        }
        else if(b.top()>a.top()){ //贪心策略2，见TJ 
            if(b.top()&1) //b.top()是奇数则不满足*2的条件 
                cout<<"-1",exit(0); //退出程序，exit(0)等效于在main中return 0;，但是不用花括号 
            t=b.top(); //需要一个变量临时保存当前的堆顶 
			b.pop(),b.push(t>>1),cnt++; //位运算卡常 x>>1==x/2 
        }
    }
    cout<<cnt;
    return 0; //好习惯 
}
```

#### 无注释版

<span style="color:white">可以CTJ的版本</span>

```c++
#include <bits/stdc++.h>
using namespace std;
int n,t,cnt;
priority_queue<int> a,b;
int main(){
    ios::sync_with_stdio(0);
    cin>>n;
    for(int i=1;i<=n;i++)
        cin>>t,a.push(t);
    for(int i=1;i<=n;i++)
        cin>>t,b.push(t);
    while(!a.empty()){
        if(a.top()==b.top())
            a.pop(),b.pop();
        else if(a.top()>b.top()){
            t=a.top();
			a.pop(),a.push(t>>1),cnt++;
        }
        else if(b.top()>a.top()){
            if(b.top()&1)
                cout<<"-1",exit(0);
            t=b.top();
			b.pop(),b.push(t>>1),cnt++;
        }
    }
    cout<<cnt;
    return 0;
}
```

#### multiset做法

我这里提供一种 `multiset` 的做法，闲的没事写的（

```c++
#include <bits/stdc++.h>
using namespace std;
int n,t,cnt;
multiset<int> a,b;
int main(){
    ios::sync_with_stdio(0);
    cin>>n;
    for(int i=1;i<=n;i++)
        cin>>t,a.emplace(t); //emplace比insert稍微快一点
    for(int i=1;i<=n;i++)
        cin>>t,b.emplace(t);
    while(!a.empty()){
        if(*a.rbegin()==*b.rbegin())
            a.erase(--a.end()),b.erase(--b.end());
        else if(*a.rbegin()>*b.rbegin()){
            t=*a.rbegin();
            a.erase(--a.end()),a.emplace(t>>1),cnt++;
        }
        else if(*a.rbegin()<*b.rbegin()){
            if((*b.rbegin())&1)
                cout<<"-1",exit(0);
            t=*b.rbegin();
            b.erase(--b.end()),b.emplace(t>>1),cnt++;
        }
    }
    cout<<cnt;
    return 0;
}
```