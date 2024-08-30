---
title: 现阶段的OI板子垃圾桶（新版）
cover: 'https://npm.elemecdn.com/saiodgm-api@1.0.1/randomimg-my/16.webp'
abbrlink: '88504706'
swiper_description: awa
description: 一堆破板子，简直就是个乐色桶（
swiper_index: 15
date: 2023-03-12 08:00:13
updated: 2023-03-12 08:00:13
tags: 
- OI
- 数据结构
- 算法
categories:
- OI
---
考虑旧的板子文已经有了一些东西了，所以说开了个新的文章 QwQ

PS：时期不同 码风略有不同，但是大致一样

# CRT（中国剩余定理）

```cpp
#include<bits/stdc++.h>
#define ll long long
using namespace std;
ll n,x,y,ans;
ll a[24],m[24];
inline ll exgcd(ll a,ll b,ll &x,ll &y){
    if(b==0){
        x=1,y=0;
        return a;
    }
    ll ret=exgcd(b,a%b,x,y);
    ll t=x;x=y,y=t-(a/b)*y;
    return ret;
}

inline ll CRT(ll a[],ll m[],ll n){
    ll ans=0,M=1;
    for(ll i=1;i<=n;i++) M*=m[i];
    for(ll i=1;i<=n;i++){
        ll Mi=M/m[i];
        exgcd(Mi,m[i],x,y);
        ans=(ans+x*a[i]*Mi)%M;
    }
    if(ans<0) ans+=M;
    return ans;
} 

int main(){
	ios::sync_with_stdio(0);
	cin>>n;
    for(ll i=1;i<=n;i++) cin>>m[i]>>a[i];
    ans=CRT(a,m,n);
    cout<<ans;
    return 0;
}
```

# 差分

预处理复杂度 $O(n)$ 可以让元素修改复杂度降至 $O(1)$ 最后还原前缀和即可。

```cpp
#include <bits/stdc++.h>
#define int long long
using namespace std;
int n,m,a[114514],b[114514],c[114514];
signed main(){
	ios::sync_with_stdio(false);
	cin.tie(0);
	cout.tie(0);
	cin>>n>>m;
	for(int i=1;i<=n;i++){
		cin>>a[i];
		b[i]=a[i]-a[i-1];
	}
	for(int i=1;i<=m;i++){
		int t,x1,y1,z;
		cin>>t>>x1>>y1>>z;
		if(t==1){
			b[x1]+=z;
			b[y1+1]-=z;
		}
		else if(t==2){
			b[x1]-=z;
			b[y1+1]+=z;
		}
	}
	for(int i=1;i<=n;i++){
		a[i]=b[i]+a[i-1];
		c[i]=a[i]+c[i-1];
	}
	int x2,y2;
	cin>>x2>>y2;
	cout<<c[y2]-c[x2-1];
    return 0;
}
```

# 二分查找

$O(log\ n)$

```cpp
#include<bits/stdc++.h>
using namespace std;
int n,arr[1919810],x,ans;
int main(){
	ios::sync_with_stdio(0); 
	cin>>n;
	for(int i=1;i<=n;i++) cin>>arr[i];
	cin>>x;
	int l=1,r=n;
	while(l<=r){
		int mid=(l+r)>>1;
		if(arr[mid]==x) ans=mid,r=mid-1;
		else if(arr[mid]<x) l=mid+1;
		else r=mid-1;
	}
	if(!ans) cout<<-1;
	else cout<<ans;
	return 0;
}
```

这是QYC（我们教练）的循环版，我更倾向于使用分治来做:

```cpp
#include <bits/stdc++.h>
using namespace std;
int arr[1919810],n,x;
int binarySearch(int arr[],int p,int q,int t) {
    int mid=0;
    if(p>q) {
        return -1;
    }
    mid=p+(q-p)/2;
    if(t==arr[mid]) {
        return mid;
    }
    if(t<arr[mid]) {
        return binarySearch(arr,p,mid-1,t);
    }
    else{
        return binarySearch(arr,mid+1,q,t);
    }
}
int main(){
    ios::sync_with_stdio(0);
    cin>>n;
    for(int i=1;i<=n;i++) cin>>arr[i];
    cin>>x;
    cout<<binarySearch(arr,1,n,x)<<endl;
	return 0;
}
```

二分答案同理。

# 归并排序

$O(n\ log\ n) × O(n^2)$ 很难背的板子，但是效率比快排高且逆序对有要求

```cpp
#include <bits/stdc++.h>
#define int long long
using namespace std;
int n,a[114514],r[114514];
void Msort(int left,int right){
	int mid=(left+right)>>1;	
	if(left==right) return;
	Msort(left,mid);
	Msort(mid+1,right);
	int i=left,j=mid+1,k=left;
	while(i<=mid&&j<=right){
		if(a[i]<=a[j]){
			r[k]=a[i];
			k++,i++;
		}
		else{
			r[k]=a[j];
			k++,j++;
		}
	}
	while(i<=mid){
		r[k]=a[i];
		k++,i++;
	}
	while(j<=right){
		r[k]=a[j];
		k++,j++;
	}
	for(int i=left;i<=right;i++) a[i]=r[i];
}
signed main(){
	ios::sync_with_stdio(false);
	cin.tie(0);
	cout.tie(0);
	cin>>n;
	for(int i=1;i<=n;i++) cin>>a[i];
	Msort(1,n);
	for(int i=1;i<=n;i++) cout<<a[i];
	return 0;
} 
```

# 快速排序

$O(n\ log\ n) ~ O(n^2)$ 有时候会退化，建议直接用 `sort`或者`qsort`

```cpp
#include <bits/stdc++.h>
#define int long long
using namespace std;
int n,a[114514],r[114514];
void Msort(int left,int right){
	int mid=(left+right)>>1;	
	if(left==right) return;
	Msort(left,mid);
	Msort(mid+1,right);
	int i=left,j=mid+1,k=left;
	while(i<=mid&&j<=right){
		if(a[i]<=a[j]){
			r[k]=a[i];
			k++,i++;
		}
		else{
			r[k]=a[j];
			k++,j++;
		}
	}
	while(i<=mid){
		r[k]=a[i];
		k++,i++;
	}
	while(j<=right){
		r[k]=a[j];
		k++,j++;
	}
	for(int i=left;i<=right;i++) a[i]=r[i];
}
signed main(){
	ios::sync_with_stdio(false);
	cin.tie(0);
	cout.tie(0);
	cin>>n;
	for(int i=1;i<=n;i++){
		cin>>a[i];
	}
	Msort(1,n);
	for(int i=1;i<=n;i++) cout<<a[i];
	return 0;
} 
```

# 快速幂

```cpp
#include <bits/stdc++.h>
#define int long long 
using namespace std;
int qpow(int a,int b,int q){
	if(b==0) return 1%q;
	else if(b%2==1) return qpow(a,b-1,q)*a%q;
	else{
		int t=qpow(a,b/2,q);
		return t*t%q;
	}
}
signed main(){
	ios::sync_with_stdio(false);
	int a,b,c;
	cin>>a>>b>>c;
	cout<<qpow(a,b,c);
	return 0; 
}
```

# 前缀和

```cpp
#include <bits/stdc++.h>
#define int long long 
using namespace std;
signed main(){
	ios::sync_with_st dio(false);
	int n,m,a[114514],b[114514];
	cin>>n>>m;
	for(int i=1;i<=n;i++){
		cin>>a[i];
		b[i]=a[i]+b[i-1];
	}
	for(int i=1;i<=m;i++){
		int x,y;
		cin>>x>>y;
		cout<<b[y]-b[x-1]<<endl;
	}
    return 0;
}
```

# 最长不下降子序列 LIS

DP的经典问题.

状态转移方程：$F_i = max\left \{ F_i, max\left \{F_j\right \}  + 1\right \}  (j < i , a_j < a_i)$

```cpp
#include <bits/stdc++.h>
#define MAX 1145
#define inf 0x3f3f3f3f
using namespace std;
int n,dp[MAX],arr[MAX],ans=-inf;
int main(){
	ios::sync_with_stdio(false);
	cin>>n;
	for(int i=1;i<=n;i++) cin>>arr[i];
	dp[1]=1;
	for(int i=2;i<=n;i++){
		for(int j=1;j<i;j++)
			if(arr[j]<=arr[i]) dp[i]=max(dp[i],dp[j]);
		dp[i]++;
	}
	for(int i=1;i<=n;i++){
		ans=max(ans,dp[i]);
	}
	cout<<ans;
	return 0;
}
```

# 最长公共子序列 LCS

也是经典的DP：

状态转移方程 $f(i,j) = \left\{\begin{matrix} 0,\: & i = 0\:or\:j = 0 \\ 1 + f(i−1,j−1),\: & a_{i} = b_{j} \\ max(f(i,j−1),f(i−1,j)),\: & a_{i} \neq b_{j} \\  \end{matrix}\right.$

```cpp
#include<bits/stdc++.h>
using namespace std;
int dp[2005][2005],len1,len2;
char a[114514],b[114514];
int main(){
	ios::sync_with_stdio(false);
	cin>>a>>b;
	len1=strlen(a),len2=strlen(b);
	for(int i=1;i<=len1;i++)
		for(int j=1;j<=len2;j++)
			if(a[i-1]==b[j-1]) dp[i][j]=dp[i-1][j-1]+1;
			else dp[i][j]=max(dp[i-1][j],dp[i][j-1]);
	cout<<dp[len1][len2];
	return 0;
}
```