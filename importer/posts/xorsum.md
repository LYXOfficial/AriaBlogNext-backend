---
title: 【ABC098D】 XOR Sum 2 题解
cover: 'https://bu.dusays.com/2023/05/28/6472bf2b1e976.jpg'
abbrlink: c8da5f65
tags:
  - OI
  - C++
  - 双指针
  - 位运算
categories: OI
description: 一鸽又咕的文章...
date: 2023-06-30 17:37:37
updated: 2023-06-30 17:37:37
---

题目链接：

{% link 【ABC098D】 Xor Sum 2,洛谷,https://www.luogu.com.cn/problem/AT_arc098_b %}

### 题解

#### 题目大意

给出一个序列 $A$ ，求 $A_l \oplus A_{l+1} \oplus \dots \oplus A_r = A_l + A_{l + 1} +\dots+ A_r$ （ $\oplus$ 即为 $xor$ 异或 ）

#### 解析

众所周知，异或是位运算中的一种不进位加法，即为如果两个 $bit$ 相等返回 $0$ ，反之返回 $1$。

为什么说是不进位加法呢？比如 $1_2+1_2=10_2$，但是 $1_2 \oplus 1_2=0_2$，前面一位的 $1$ 没了。

因为 $xor$ 的这种特性，易得 $a \oplus b\le a+b$。

比如 $(1000001)_2+(10001)_2=(1000010)_2$，而$(1000001)_2 \oplus (10001)_2=(1001000)_2$。

题目要求求 $A_l \oplus A_{l+1} \oplus \dots \oplus A_r = A_l + A_{l + 1} +\dots+ A_r$，所以这个区间要是能满足要求的话就需要满足所有 $bit$ 上最多只有一个 $1$ 才能让 $a+b= a \oplus b$。

所以这些数据肯定是有单调性的，然后用双指针扫一遍，用了实时处理前缀 $xor$、和的方式，稍微省了一些空间。

### 代码

~~Like QYC, it had some bug and I digged many pits. So if you Ctrl+ACV in one go, you'll see quite lots of frogs are shouting.~~ 坑删了

请自己理解思路之后打代码。

```cpp
#include <bits/stdc++.h>
#define ll long long
using namespace std;
int n,a[1919810];
ll l=1,sxor,sum,ans;
int main() {
	ios::sync_with_stdio(0); //加速读入
    cin>>n;
    for(int i=1;i<=n;i++) cin>>a[i];
    for(int r=1;r<=n;r++){
        sum+=a[r],sxor^=a[r]; //处理当前前缀sum和xor
        while(sxor!=sum&&(l<r)) //向左边扩展范围
            sum-=a[l],sxor^=a[l++]; //算xor和sum
        ans+=r-l+1;
    }
    cout<<ans;
}
```