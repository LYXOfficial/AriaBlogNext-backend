---
title: 表达式学习笔记
cover: 'https://bu.dusays.com/2023/01/20/63c9e10df1b7b.webp'
tags:
  - OI
  - 栈
  - 字符处理
  - 学习笔记
categories: OI
description: 括号，为什么这么坑呢？某Save Money机构究竟是出于什么目的，常考此题呢？为什么某蒟蒻依然调不来中缀转后缀？
abbrlink: 487b9d4c
date: 2022-12-19 19:12:28
updated: 2022-12-19 19:12:28
---

# 前言

众所周知，在€€￡的许多比赛中，出现得多的就是表达式题目了，比如：

{% link P8815 [CSP-J 2022] 逻辑表达式,洛谷,https://www.luogu.com.cn/problem/P8815 %}

{% link P7073 [CSP-J 2020] 表达式,洛谷,https://www.luogu.com.cn/problem/P7073 %}

{% link P1054 [NOIP2005 提高组] 等价表达式
,洛谷,https://www.luogu.com.cn/problem/P1054 %}

所以，这次，让我们来几个...~~只因~~基础的表达式吧。

# 前缀&&后缀

前缀和后缀表达式，其实都是一个东西，只不过顺序倒过来罢了。

那么后缀表达式，究竟是什么东西呢？

这是一个后缀表达式：

`514 810 + 24 114 * -`

很明显，后缀表达式把所有符号都后置了，这样做就不用考虑括号了。

那么，她的中缀形式（即正常人的写法）就是这样的：

$(24 \times 114)-(514+810)$

是不是，后缀表达式把符号都放在了两个数后面，不需要括号了，这样就可以直接从左往右而不用考虑顺序了。因为不加括号的 $24 \times 114-514+810$ 显然计算顺序都不一样，变成了先算 $24 \times 114$，再算 $(24 \times 114)-514$。

## 算法

那么怎么算呢？

我们不妨从左往右看，遇到符号的时候就把前面两个数按照这个符号来计算。

比如：$114 514 +$ ，这个式子，只需要按照加法的法则计算$114$和$514$ 两个数的和就可以了。

但是，如果我们要计算上面的式子：`514 810 + 24 114 * - `，该怎么算呢？

这时我们需要把还没算的数存起来了，而且肯定是不止一个两个的，于是你自然而然想到了栈的方法。

我们算的时候把每个数字依次进栈，遇到符号就把上面两个拉出来，算出结果再放回去，最后肯定栈里面就只剩一个元素了，直接输出即可{% span red,（注意实际上栈顶元素是运算的第一个数，下面一个才是第二个，不能搞反） %}。

如果我们要算上面的式子的话，栈的变化是这样的:

看到第一个元素$514$：

`stack: 514`

看到$810$：

`stack: 514 810`

看到加号：

`stack: 1324`

看到$24$：

`stack: 1324 24`

看到$114$:

`stack: 1324 24 114`

看到乘号：

`stack: 1324 2736`

最后看到减号：

`stack: 1412`

此时这个式子就算出来了，输出栈顶即可。

## 代码实现

然后这是一些例题的代码

### 洛谷P1449 后缀表达式

原题：

{% link P1449 后缀表达式,洛谷,https://www.luogu.com.cn/problem/P1449 %}

{% folding blue, 点击查看题面 %}
## 题目描述

所谓后缀表达式是指这样的一个表达式：式中不再引用括号，运算符号放在两个运算对象之后，所有计算按运算符号出现的顺序，严格地由左而右新进行（不用考虑运算符的优先级）。

如：$\texttt{3*(5-2)+7}$ 对应的后缀表达式为：$\texttt{3.5.2.-*7.+@}$。在该式中，`@` 为表达式的结束符号。`.` 为操作数的结束符号。

## 输入格式

输入一行一个字符串 $s$，表示后缀表达式。

## 输出格式

输出一个整数，表示表达式的值。

## 样例 #1

### 样例输入 #1

```
3.5.2.-*7.+@
```

### 样例输出 #1

```
16
```

## 提示

数据保证，$1 \leq |s| \leq 50$，答案和计算过程中的每一个值的绝对值不超过 $10^9$。
{% endfolding %}

这道题按照开始的方法算就行了，但是，但是它是用点来隔开的。所以呢只能手动拆数字了，建议用`stoi(string)`函数：

```cpp
#include <bits/stdc++.h>
using namespace std;
int main(){
	ios::sync_with_stdio(false);
	char c;
	char num[11]; //字符数组临时放数字
	int k=0;
	stack<int> eval;
	while(cin>>c){
		if(c=='@') break;
		if(isdigit(c)){
			num[k]=c; //是数字才加到字符数组里面
			k++;
		}
		else if(c=='.'){
			num[k]='\0';
			string nn=num;
			eval.push(stoi(nn)); //遇到点号分割，前面的转数字，并清空入栈
			k=0;
			memset(num,0,sizeof(num));
		}
        //以下为各种符号的处理
		else if(c=='+'){
			int a,b=eval.top();
			eval.pop();
            a=eval.top();
			eval.pop();
            eval.push(a+b);
			// cout<<a<<" "<<b<<endl;
		}
		else if(c=='-'){
			int a,b=eval.top();
			eval.pop();
            a=eval.top();
			eval.pop();
            eval.push(a-b); //注意实际上栈顶元素是运算的第一个数，下面一个才是第二个，不能搞反！！！不然会出错
			// cout<<a<<" "<<b<<endl;
		}
		else if(c=='*'){
			int a,b=eval.top();
			eval.pop();
            a=eval.top();
			eval.pop();
            eval.push(a*b);
			// cout<<a<<" "<<b<<endl;
		}
		else if(c=='/'){
			int a,b=eval.top();
			eval.pop();
            a=eval.top();
			eval.pop();
            eval.push(a/b);
			// cout<<a<<" "<<b<<endl;
		}
	}
	cout<<eval.top(); //最后输出栈顶即可
  	return 0;
}
```

### FZQOJ #139. 波兰表达式

*（PS：这是学校内部题）*

{% folding yellow open, 点击查看题面 %}
## 题目描述
波兰表达式是一种把运算符前置的算术表达式，例如普通的表达式 `2 + 3` 的逆波兰表示法为 `+ 2 3`。

波兰表达式的优点是运算符之间不必有优先级关系，也不必用括号改变运算次序，例如 `(2 + 3) * 4` 的逆波兰表示法为 `* + 2 3 4`。

本题求解波兰表达式的值，其中运算符包括 `+ - * /` 四个。

## 输入
输入为一行，其中运算符和运算数之间都用空格分隔，运算数是浮点数。

## 输出
输出为一行，表达式的值。 可直接用 `printf("%f ", v)` 输出表达式的值 。

## 样例输入
```
* + 11.0 12.0 + 24.0 35.0
```
## 样例输出
```
1357.000000
```
## 提示
可使用 `atof(str)` 把字符串转换为一个`double`类型的浮点数。`atof` 定义在 `cstdlib` 中。
{% endfolding %}

这即是前缀表达式了，方法都一样，但是得倒着来看，注意这道题是浮点数，还有输入有空格了，不用自己拆了，好耶！

```cpp
#include<bits/stdc++.h>
using namespace std; 
int main(){
	stack<double> eval;
	string evals[11451];
	int l=1;
	while(cin>>evals[l]){ 
		l++; //存表达式
	}
	for(int i=l-1;i>=1;i--){ //从后往前遍历表达式
		if(evals[i]=="+"){
			double a=eval.top();
			eval.pop();
			double b=eval.top(); //这里顺序不用反着来了
			eval.pop();
			eval.push(a+b); //一样的
		}
		else if(evals[i]=="-"){
			double a=eval.top();
			eval.pop();
			double b=eval.top();
			eval.pop();
			eval.push(a-b); 
		}
		else if(evals[i]=="*"){
			double a=eval.top();
			eval.pop();
			double b=eval.top();
			eval.pop();
			eval.push(a*b); 
		}
		else if(evals[i]=="/"){
			double a=eval.top();
			eval.pop();
			double b=eval.top();
			eval.pop();
			eval.push(a/b); 
		}
		else{
			eval.push(atof(evals[i].c_str())); //否则字符串转数字入栈
		}
	}
	printf("%.6lf",eval.top()); //输出栈顶即可，注意保留6位小数
	return 0;
}
```

# 万能的方法——中缀转后缀

## 基础转换

e.g. 洛谷P1981 [NOIP2013 普及组] 表达式求值

咕咕咕没关系,多画几个大饼 {% inlineImg https://npm.elemecdn.com/sticker-heo@2022.7.5/Sticker-100/%E7%8B%97%E5%A4%B4%E5%9B%B4%E8%84%96.png 50px %}

![](https://bu.dusays.com/2023/01/20/63ca10d120e5e.webp)

![](https://bu.dusays.com/2023/01/20/63ca10d1c7dd5.webp)

## 括号匹配