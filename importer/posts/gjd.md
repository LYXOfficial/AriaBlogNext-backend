---
title: 高精度算法学习笔记
abbrlink: 74e5e1ec
date: 2022-11-20 21:12:03
tags: 
- OI
- 高精度
- 学习笔记
categories:
- OI
cover: https://bu.dusays.com/2023/01/20/63c9e28073b4e.webp
description: 坑爹玩意，我用PY写不香吗？（咕咕咕）
updated: 2022-11-24 11:40:31
---
# 前言

作为一个曾经在BCM摆烂的蒟蒻，趁着网课期间，就恶补一顿吧。

# 为什么会有高精度

{% note info simple %}
22.11.29 发现部分特性，有空修修
{% endnote %}

众所周知，在刷题/比赛的路途中，我们总会遇到一些毒瘤题目，这种题呢它非常离谱，数据规模可以达到$0<=N<=10^{100}$之类的，就算是开挂的`unsigned __int128`也没救，所以就需要高精度qwq

一些常见类型的范围：


| 类型                                   | 长度           | 范围                                                                   |
|----------------------------------------|----------------|------------------------------------------------------------------------|
| `bool`                                   | 1B             | $0\sim 1$($true\parallel false$)                                                        |
| `short`                                  | 2B             | $-32768\sim 32767$                                                     |
| `unsigned short`                         | 2B             | $0\sim 65535$                                                          |
| `int`                                    | 4B(俗称的32位) | $-2147483648\sim 2147483647$($0x7fffffff$)($-2^{31}\sim 2^{31}-1$)       |
| `unsigned int`                           | 4B             | $0\sim 4294967295$($0\sim 2^{32}-1$)                                         |
| `long long`                              | 8B(俗称的64位) | $-2^{63}\sim 2^{63}-1$($–9223372036854775808\sim 9223372036854775807$) |
| `unsigned long long`(PS:CSP-J2022T2克星) | 8B             | $0\sim 2^{64}-1$ ($0\sim 18446744073709551615$)                        |
| `char`                                   | 1B             | $-128\sim 127$(PS:char为什么要有负数)                                  |
| `float`                                  | 4B             | $-3.4e-38\sim 3.4e+38$($6\sim 7$位有效数据)                            |
| `double`                                 | 8B             | $-1.7e-308\sim 1.7e+308$($15\sim 16$位有效数据)                        |
| `__int128`（正式比赛以及本地gcc不支持）                               | 16B(即128位)   |$-2^{127}\sim 2^{127}-1$($–1.70141183×10^{38}\sim 1.70141183×10^{38}-1$))|
| `unsigned __int128`                               | 16B   |$0\sim 2^{127}$($0\sim 3.40282367×10^{38}-1$)|

(实际上不建议使用unsigned类型，容易出现与signed冲突的问题。)

这么算下来，即便是`unsigned __int128`的数据范围也只在$0\le N\le 3.40282367×10^{38}-1$以内，这在某些题中依旧远远不够。

既然直接用内存存二进制数不行，那为什么不一位一位存呢？

所以就可以用一个字符数组`char num[1919]`来存高精度。

为什么要用字符数组呢？因为如果想做一些事的话字符数组会更加方便。

# 怎么算？

## 加法

既然是一位一位存的，自然能想到我们的竖式<del>（OI惊现小学二年级内容）</del>，竖式便是一位一位<del>いくいく（悲）</del>地加的：

$\quad 1145$  
$\;+1919$
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
$\quad 3064$

我们采用从末位到首位依次计算的方式：

`a=1 1 4 5`

`b=1 9 1 9`

首先计算$5+9=14$，这时我们发现有进位情况，用一个变量`jw`标记：

`jw=1`

`c=0 0 0 4`

然后计算$4+1+1=6$，(加上前面的进位)，此时这里是不进位的

`jw=0`

`c=0 0 6 4`

接着计算$1+9$,很显然这里有进位.

`jw=1`

`c=0 0 6 4`

再接着计算$1+1+1=3$(加上前面的进位),这时不进位

`jw=0`

`c=3 0 6 4`

这时高精加法就实现了.

事实上,我们好像忽略了什么,对,数位对齐!

有一个不同位数的式子:

$\quad 1145$  
$+ \;\ \; 514$
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
$\quad 1659$

很显然,如果不对齐进行计算的话,因为数组下标是从1开始(虽然本身是0开始的)的,程序会处理成:

$\quad 1145$  
$\;+5140$
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
$\quad 6285$

这自然违背了数位要对齐的原则.

怎么解决呢?在上面说到了,数组的下标是从1开始的，那为什么不把她们倒着算呢？然后输出的时候只需要调回来就行了。

这时，式子就变成了：

$\quad 5411$  
$\;+451$
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-
$\quad 9651$

很显然，这时数位就对齐了，然后这时就能用程序从前往后算了，并且输出的时候给它倒序回来就行了。

所以这样就行了**吗？**并不是的。

按照上面的算法，程序重复执行计算每位的次数只是取ab两数中大的数的位数。
所以遇到例如`9999+1`这种进位之后的式子，如果程序只算4次的话，结果就是`0000`，很显然这是错误的。

遇到这种情况，不如多算一次。不过要注意不进位的情况，会出现前导零的问题，又得把记录位数的变量少-1才行。

好的，相信你已经学会了。

参考代码：

{% hideToggle 请确保你已经读懂算法，此代码仅作参考，请勿直接提交（尤其是洛谷） %}

```cpp
#include <bits/stdc++.h>
using namespace std;
struct longint{
	char num[114514]={'0'};
	int sign=0; //标记符号
	void read(){
		char c='0'; //快读
		int i=1;
		while((c<='9'&&c>='0')||c=='-'){
			c=getchar();
			if(c=='-') sign=1;
			else{
				num[i]=c;
				i++;
			}
		}
		num[i]='\0';
		return;
	}
	void print(){
		int n=strlen(num)-1; //快写
		if(n<1) putchar('0');
		if(sign) putchar('-');
		for(int i=1;i<=n;i++){
			putchar(num[i]);
		}
		return;
	}
	longint operator+(longint b2){
		int a[114514],b[114514],c[114514];
		longint c2;
        int la=strlen(num)-2;
        int lb=strlen(b2.num)-2; //算位数
        for(int i=1;i<=la;i++){
            a[la-i+1]=num[i]-'0';
        }
        for(int i=1;i<=lb;i++){
            b[lb-i+1]=b2.num[i]-'0'; //逆序存储
        }
        int lc=0,jw=0; 
        while(la>=lc||lb>=lc){ //取位数多的
            c[lc]=(a[lc]+b[lc])%10+jw; //算a+b，加上进位
            jw=(a[lc]+b[lc]+jw)/10; //jw变量（pinyin？）用于标记下一位
            lc++;
        }
        if(jw) c[lc++]=jw; //解决残余进位
        if(c[lc]==0) lc--;
        for(int i=lc;i>=1;i--){
            c2.num[lc-i+1]=c[i]%10+'0'; //给她逆序加回去
        }
        c2.num[lc+1]='\0'; //免得出bug
        return c2;
        //封装好结构体是个人所好，勿cue
    }
};
int main(){
	longint a,b;
	a.read();
	b.read();
	(a+b).print();
	return 0;
}
```

{% endhideToggle %}

## 减法

减法与加法差不多，但是可能会出现很多个0，而且如果a小于b（我们学校oj测试数据离谱qwq）的话得交换加负号

{% hideToggle 请确保你已经读懂算法，此代码仅作参考，请勿直接提交（尤其是洛谷） %}

```cpp
#include <bits/stdc++.h>
using namespace std;
struct longint{
	char num[114514]={'0'};
	int sign=0; //标记符号
	void read(){
		char c='0'; //快读
		int i=1;
		while((c<='9'&&c>='0')||c=='-'){
			c=getchar();
			if(c=='-') sign=1;
			else{
				num[i]=c;
				i++;
			}
		}
		num[i]='\0';
		return;
	}
	void print(){
		int n=strlen(num)-1; //快写
		if(n<1) putchar('0');
		if(sign) putchar('-');
		for(int i=1;i<=n;i++){
			putchar(num[i]);
		}
		return;
	}
	longint operator-(longint b2){
		int a[114514],b[114514],c[114514],la,lb;
		longint c2;
        if(strcmp(num,b2.num)>=0){
			la=strlen(num)-2;
			lb=strlen(b2.num)-2;
			for(int i=1;i<=la;i++){
				a[la-i+1]=num[i]-'0';
			}
			for(int i=1;i<=lb;i++){
				b[lb-i+1]=b2.num[i]-'0';
			}
		}
		else{
			//a比b小得交换改符号
			c2.sign=1;
			la=strlen(b2.num)-2;
			lb=strlen(num)-2;
			for(int i=1;i<=la;i++){
				a[la-i+1]=b2.num[i]-'0';
			}
			for(int i=1;i<=lb;i++){
				b[lb-i+1]=num[i]-'0';
			}
		}
        int lc=0,jw=0; 
        while(la>=lc||lb>=lc){ //取位数多的
            int n=a[lc]-b[lc]-jw; //算减法，得出负的就借位
            if(n<0){
                n+=10;
                jw=1;
            }
            else{
                jw=0;
            }
            c[lc]=n; 
            lc++;
        }
        while(c[lc]==0) lc--; //去0
        for(int i=lc;i>=1;i--){
            c2.num[lc-i+1]=c[i]%10+'0'; //给她逆序加回去
        }
        c2.num[lc+1]='\0'; //免得出bug
        return c2;
        //封装好结构体是个人所好，勿cue
    }
};
int main(){
	longint a,b;
	a.read();
	b.read();
	(a-b).print();
	return 0;
}
```
{% endhideToggle %}

# 一个高精结构体

我还写了个高精结构体，这个结构体做了一些符号、运算符重载的功能，起码更加方便了qwq（PS怎么重写scan/printf，cin/out呢？）

```cpp
struct longint{
	char num[114514]={'0'};
	int sign=0; //标记符号
	void read(){
		char c='0'; //快读
		int i=1;
		while((c<='9'&&c>='0')||c=='-'){
			c=getchar();
			if(c=='-') sign=1;
			else{
				num[i]=c;
				i++;
			}
		}
		num[i]='\0';
		return;
	}
	void print(){
		int n=strlen(num)-1; //快写
		if(n<1) putchar('0');
		if(sign) putchar('-');
		for(int i=1;i<=n;i++){
			putchar(num[i]);
		}
		return;
	}
	bool operator>(longint b){
		if(!sign&&!b.sign) return strcmp(num,b.num)>0;
		else if(!(sign)&&b.sign) return 1;
		else if(sign&&!b.sign) return 0;
		else return strcmp(num,b.num)<0;
	}
	bool operator<(longint b){
		if(!sign&&!b.sign) return strcmp(num,b.num)<0;
		else if(!(sign)&&b.sign) return 0;
		else if(sign&&!b.sign) return 1;
		else return strcmp(num,b.num)>0;
	}
	bool operator<=(longint b){
		if(strcmp(num,b.num)==0&&sign==b.sign) return 1;
		else if(!sign&&!b.sign) return strcmp(num,b.num)<0;
		else if(!(sign)&&b.sign) return 0;
		else if(sign&&!b.sign) return 1;
		else return strcmp(num,b.num)>0;
	}
	bool operator>=(longint b){
		if(strcmp(num,b.num)==0&&sign==b.sign) return 1;
		else if(!sign&&!b.sign) return strcmp(num,b.num)<0;
		else if(!(sign)&&b.sign) return 1;
		else if(sign&&!b.sign) return 0;
		else return strcmp(num,b.num)<0;
	}
	bool operator==(longint b){
		return strcmp(num,b.num)==0&&sign==b.sign;
	}
	longint operator+(longint b2){
		int a[114514],b[114514],c[114514];
		longint c2;
		if(sign==b2.sign){
			if(sign&&b2.sign) c2.sign=1; //同号相加
			int la=strlen(num)-2;
			int lb=strlen(b2.num)-2;
			for(int i=1;i<=la;i++){
				a[la-i+1]=num[i]-'0';
			}
			for(int i=1;i<=lb;i++){
				b[lb-i+1]=b2.num[i]-'0';
			}
			int lc=1,jw=0;
			while(la>=lc||lb>=lc){
				c[lc]=(a[lc]+b[lc])%10+jw;
				jw=(a[lc]+b[lc]+jw)/10;
				lc++;
			}
			if(jw) c[lc++]=jw;
			if(c[lc]==0) lc--;
			for(int i=lc;i>=1;i--){
				c2.num[lc-i+1]=c[i]%10+'0';
			}
			c2.num[lc+1]='\0';
		}
		else{
			//异号相加，尚未实现
			longint b3;
			memcpy(b3.num,num,sizeof(num));
			longint b4;
			memcpy(b4.num,b2.num,sizeof(b2.num));
			if(b3>b4){
				longint t=b3-b4;
				c2=t;
				c2.sign=b3.sign;
			}
			else{
				longint t=b4-b3;
				c2=t;
				c2.sign=b4.sign;
			}
		}
		return c2;
	}
	// void operator++(){
	// 	int jw=1,k=strlen(num)-1;
	// 	while(jw!=0){
	// 		jw=((int)num[k]-'0'+jw)/10;
	// 		num[k]=((int)num[k]-'0'+jw)%10+'0';
	// 		k--;
	// 	}
	// 	return;
	// } //++运算（莫名其妙不能用）
	longint operator-(longint b2){
		int a[114514],b[114514],c[114514],la,lb;
		longint c2;
		if(!b2.sign&&!sign){
			//正数相减
			if(strcmp(num,b2.num)>=0){
				la=strlen(num)-2;
				lb=strlen(b2.num)-2;
				for(int i=1;i<=la;i++){
					a[la-i+1]=num[i]-'0';
				}
				for(int i=1;i<=lb;i++){
					b[lb-i+1]=b2.num[i]-'0';
				}
			}
			else{
				c2.sign=1;
				la=strlen(b2.num)-2;
				lb=strlen(num)-2;
				for(int i=1;i<=la;i++){
					a[la-i+1]=b2.num[i]-'0';
				}
				for(int i=1;i<=lb;i++){
					b[lb-i+1]=num[i]-'0';
				}
			}
			int lc=1,jw=0;
			while(la>=lc||lb>=lc){
				int n=a[lc]-b[lc]-jw;
				if(n<0){
					n+=10;
					jw=1;
				}
				else{
					jw=0;
				}
				c[lc]=n;
				lc++;
			}
			if(jw) c[lc++]=jw;
			while(c[lc]==0) lc--;
			for(int i=lc;i>=1;i--){
				c2.num[lc-i+1]=c[i]%10+'0';
			}
			c2.num[lc+1]='\0';
		}
		else{
			//转加法（初一有理数的加减？！）
			longint b3;
			memcpy(b3.num,num,sizeof(num));
			b3.sign=sign;
			longint b4;
			memcpy(b4.num,b2.num,sizeof(b2.num));
			b4.sign=!sign;
			c2=b3+b4;
		}
		return c2;
	}
	longint operator*(longint b2){
		//高精乘法，咕咕咕
	}
};
```

不过还没有写完咕咕咕。。。

## TODO

没错，我要让她变得跟`int`/`long long`/`double`这些类型一样方便！

{% checkbox checked, 快读快写 %}
{% checkbox checked, 重载常见运算符 %}
{% checkbox checked, 高精加法 %}
{% checkbox checked, 高精减法 %}
{% checkbox 高精乘法 %}
{% checkbox 高精除法（高精/低精） %}
{% checkbox 高精除法（高精/高精） %}
{% checkbox 符号运算 %}
{% checkbox 兼容cin/cout、scanf/printf %}
{% checkbox 布尔运算 %}
{% checkbox 高速（快于）$O(n\ log(n) )$%}
{% checkbox 类型转换/兼容 %}
{% checkbox 简易赋值 %}
{% checkbox 支持小数 %}