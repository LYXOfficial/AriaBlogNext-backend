---
title: 「BZOJ2393」Cirno 的完美算数教室 题解
cover: 'https://npm.elemecdn.com/saiodgm-api@1.0.1/randomimg-my/15.webp'
abbrlink: 1d499ffd
tags:
  - OI
  - C++
  - 数论
  - 算法
  - AFO
categories: OI
date: 2023-08-29 09:12:48
updated: 2023-08-29 09:12:48
---
## 「BZOJ2393」Cirno 的完美算数教室

AFO 前的最后一篇题解，难蚌。

终于遇到了一个能写 TJ 的数论题了qwq，这个whk废物没救了。

### 题意

给定 $l$ 和 $r$，求 $l\sim r$ 之间能整除一个仅由 2 和 9 组成的数的个数。 $1 \le l < r \le 10^{10} $（原题范围貌似写的不对）

### 解析

容斥原理的一个练习题，可以先用 `dfs` $O(2^r)$ 求出所有 $\le r$ 的 $\texttt{baka}$ 数加入集合 $P$ ，然后 $O(n^2)$ 筛选掉每个对于 $x,y \in P (x < y)$ 时 $\operatorname{lcm}(x,y)=y$ 的 $y$，并将筛选完的 $x$ 加入 一个新集合 $U$。

*~~(PS：$\begin{aligned}\operatorname{lcm}(a,b)=\frac{ab}{\gcd(a,b)}\end{aligned}$)，筛选可以通过排序数组后把对应位置元素置 0 后续跳过的方案）~~*

如何处理 $\operatorname{lcm}$ 相同导致重复筛选的情况呢？可以通过 `dfs` 搜索并剪枝的方式枚举子集并去重。

~（最开始本蒟蒻用了 `map` 判重不幸 `TLE` 了，这个复杂度是 $O(n^3)$，$2^{10}$ 肯定过不了，警钟长鸣）~~

定义一个 `calc(t1,t2,lcm)` 函数，当达到边界条件$t1\ge |U|$ 时根据 $t2$ 的奇偶性来确定当前的 $ans$ 是需要增加还是排斥。否则继续搜索。在继续搜索之前，将当前的 $\operatorname{lcm}$ 乘以 $U_{t1}$ 并除以它们的最大公约数，这样可以计算出新的 $\operatorname{lcm}$。如果新的 $\operatorname{lcm}\le r$，则继续搜索，参数的 $t2$ 需要加 1，表示当前的数字可以被 $\texttt{baka}$ 数整除。

时间复杂度为 $O(2^n \log r)$。（$\log r$ 来源于 $\gcd$ 的计算）

### 代码

~~不行本蒟蒻懒得打注释了~~

```cpp
#include <bits/stdc++.h>
#define ll long long
using namespace std;
ll l,r,ans;
vector<ll> nums,u;
void dfs(ll num){
    if(num>r) return;
    if(num) nums.push_back(num);
    dfs(num*10+2),dfs(num*10+9);
}
void calc(ll t1,ll t2,ll lcm){
    if(t1>=u.size()){
        if(t2&1) ans+=r/lcm-(l-1)/lcm;
        else if(t2) ans-=r/lcm-(l-1)/lcm;
        return;
    }
    calc(t1+1,t2,lcm);
    lcm=lcm*u[t1]/__gcd(lcm,u[t1]);
    if(lcm<=r) calc(t1+1,t2+1,lcm);
}
int main(){
    cin>>l>>r;
    dfs(0),sort(nums.begin(),nums.end());
    for(int i=0;i<nums.size();i++){
        if(!nums[i]) continue;
        u.push_back(nums[i]);
        for(int j=i+1;j<nums.size();j++)
            if(nums[j]&&!(nums[j]%nums[i])) nums[j]=0;
    }
    calc(0,0,1),cout<<ans;
    return 0;
}
```