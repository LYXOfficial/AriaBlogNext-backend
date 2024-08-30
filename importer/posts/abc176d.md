---
title: "[ABC176D] Wizard in Maze 题解"
tags:
- OI
- 搜索
- 算法
- BFS
- C++
categories: OI
date: 2023-08-22 08:44:46
updated: 2023-08-22 08:44:46
abbrlink: abc176d
cover: https://npm.elemecdn.com/saiodgm-api@1.0.1/randomimg-my/18.webp
---
### 题意

黄水题（

传送门：

{% link [ABC176D] Wizard in Maze,洛谷,https://www.luogu.com.cn/problem/AT_abc176_d %}

给出一个包含 `#` 和 `.` 的地图，有两种移动方式：一种是在 `.` 间移动，一种是在移动到以当前点为中心的 `5x5` 的矩阵内的任意 `.`。问至少需要进行多少次第二种移动才能从给定的 $(sx,sy)$ 走到 $(dx,dy)$。如果无解输出 `-1`。（这一点题目中并没有说，是在WA了两个点之后发现的）

### 解析

#### 初版

考虑使用 `BFS` 来搜索路径。我们将 `.` 第一种移动花费的代价设为 `0` ，第二种花费代价则为 `1` 。问题就转换为了求矩阵最短路问题，最后得到的最小代价即为第二种移动的最少次数，然后输出后 `break` 即可。

可以将当前的花费代价、$x$ 和 $y$ 存在一个 `pair<int,pair<int,int>>` 中，然后放在队列里面进行搜索。

不同于图上最短路，这类矩阵最短路的代价是在队列存储的 `pair` 中传递的，显然这会导致可能出现最先搜到的并不是最优解，那么我们需要记录 `ans=min(cnt,ans)` 最后输出，如果 `ans==INF` 就输出 `-1` 否则输出 `ans`。

##### 6分代码

然后很容易得到一段朴素的 BFS 代码。

```c++
#include <bits/stdc++.h>
using namespace std;
int n,m,sx,sy,dx,dy,cnt,ans=1e9;
const int fx[]={1,0,-1,0},fy[]={0,1,0,-1};
char c[1005][1005];
int vis[1005][1005];
queue<pair<int,pair<int,int>>> q;
int main(){
    ios::sync_with_stdio(0);
    cin>>n>>m>>sx>>sy>>dx>>dy;
    for(int i=1;i<=n;i++)
        for(int j=1;j<=m;j++)
            cin>>c[i][j];
    q.push(make_pair(0,make_pair(sx,sy))); //初始化，pair内容可以当作dfs的参数来理解
    while(!q.empty()){
        auto p=q.front();
        q.pop();
        if(p.second.first==dx&&p.second.second==dy) //边界条件，走到底了已经
            ans=min(ans,p.first);
        vis[p.second.first][p.second.second]=1; //标记走过
        for(int t=0;t<4;t++){
            int nx=p.second.first+fx[t],ny=p.second.second+fy[t]; //在方案1中扩展状态并入队
            if(c[nx][ny]=='#') continue;
            if(nx<1||ny<1||nx>n||ny>m) continue;
            if(vis[nx][ny]) continue;
            q.push(make_pair(p.first,make_pair(nx,ny)));
        }
        for(int i=p.second.first-2;i<=p.second.first+2;i++) //以x,y为中心的5*5矩阵等价于((x+2,x-2),(y+2,y-2))
            for(int j=p.second.second-2;j<=p.second.second+2;j++){
                if(i<1||j<1||i>n||i>m) continue; //在方案2中扩展状态并入队
                if(c[i][j]=='#') continue;
                if(vis[i][j]) continue;
                q.push(make_pair(p.first+1,make_pair(i,j))); 
            }
    }
    cout<<(ans==1e9?-1:ans); //判断是否有解并输出
    return 0;
}
```

恭喜你喜提6分 TLE：

![](https://cdn.fzoi.top/upload/user/st20250310/23072007384883.png)

#### 优化1

显然这需要优化。

考虑贪心，每一次尽量找代价最小的进行转移。

如果使用数组暴力肯定会炸，可以使用优先队列和双端队列。

因为代价只有 `0` 和 `1`，显然当代价为 `0` 时放到双端队列队头，为 `1` 是放在队尾，就可以保证它内部是有序的，每次取出队头扩展时也一定是最近的，就不需要记录 `ans` 了，找到直接输出即可。

当然也可以使用优先队列，但是这里双端队列的复杂度仅为 $O(1)$，而优先队列为 $O(\log n)$，稍比 `deque` 高，所以优先考虑 `deque`。

很容易改写出双端队列版。

##### 42分代码

```c++
#include <bits/stdc++.h>
using namespace std;
int n,m,sx,sy,dx,dy,cnt;
const int fx[]={1,0,-1,0},fy[]={0,1,0,-1};
char c[1005][1005];
int vis[1005][1005];
deque<pair<int,pair<int,int>>> q;
int main(){
    ios::sync_with_stdio(0);
    cin>>n>>m>>sx>>sy>>dx>>dy;
    for(int i=1;i<=n;i++)
        for(int j=1;j<=m;j++)
            cin>>c[i][j];
    q.push_back(make_pair(0,make_pair(sx,sy)));
    while(!q.empty()){
        auto p=q.front();
        // cerr<<p.second.first<<" "<<p.second.second<<endl; //PS：cerr是好东西（自己搜）
        q.pop_front();
        if(p.second.first==dx&&p.second.second==dy)
            cout<<p.first,exit(0); //边界条件，直接输出后退出
        vis[p.second.first][p.second.second]=1;
        for(int t=0;t<4;t++){
            int nx=p.second.first+fx[t],ny=p.second.second+fy[t];//方案1，入队头
            if(c[nx][ny]=='#') continue;
            if(nx<1||ny<1||nx>n||ny>m) continue;
            if(vis[nx][ny]) continue;
            q.push_front(make_pair(p.first,make_pair(nx,ny)));
        }
        for(int i=p.second.first-2;i<=p.second.first+2;i++)
            for(int j=p.second.second-2;j<=p.second.second+2;j++){
                if(i<1||j<1||i>n||i>m) continue; //方案2，入队尾
                if(c[i][j]=='#') continue;
                if(vis[i][j]) continue;
                q.push_back(make_pair(p.first+1,make_pair(i,j)));
            }
    }
    cout<<-1; //无解
    return 0;
}
```

这份代码只有42分。会爆彩虹（AC+TLE+MLE）。

#### 卡常+玄学部分の优化3

上一份代码只有42分，但是我们已经优化过了，原因会让人感到非常玄学。

经过了一番BFS和DFS的结合体之后，我想到一种优化方案：

问题出在这一句上，方案2的转移如果每次都循环 `25` 次未免浪费时间了，遇到超出坐标范围时应该直接在循环边界里面限制下，就可以卡掉一个 `25` 的时间和空间常数（估计是这么多实际上可能只有 `5~10` 的）：

```c++
if(i<1||j<1||i>n||i>m) continue;
```

我们删掉这一句，把循环的边界改为：

```cpp
for(int i=max(p.second.first-2,1);i<=min(p.second.first+2,n);i++)
            for(int j=max(p.second.second-2,1);j<=min(m,p.second.second+2);j++){
```

这道题就通过了。

卡常万岁！！！

### 代码

#### 注释版

```c++
#include <bits/stdc++.h>
using namespace std;
int n,m,sx,sy,dx,dy;
const int fx[]={1,0,-1,0},fy[]={0,1,0,-1}; //扩展的4个方向
char c[1005][1005]; //地图
int vis[1005][1005];
deque<pair<int,pair<int,int>>> q; //双端队列，pair的三个元素分别存储当前转移代价和xy坐标
int main(){
    ios::sync_with_stdio(0); //读入优化
    cin>>n>>m>>sx>>sy>>dx>>dy;
    for(int i=1;i<=n;i++)
        for(int j=1;j<=m;j++)
            cin>>c[i][j];
    q.push_back(make_pair(0,make_pair(sx,sy)));
    while(!q.empty()){
        auto p=q.front(); //弹出队头，用auto自动推导偷懒
        q.pop_front();
        if(p.second.first==dx&&p.second.second==dy)
            cout<<p.first,exit(0); //边界条件，第一个就是最优解，输出后直接退出
        vis[p.second.first][p.second.second]=1; //标记走过
        for(int t=0;t<4;t++){ //4个方向扩展
            int nx=p.second.first+fx[t],ny=p.second.second+fy[t];
            if(c[nx][ny]=='#') continue; //不是路不走
            if(nx<1||ny<1||nx>n||ny>m) continue; //边界
            if(vis[nx][ny]) continue; //走过
            q.push_front(make_pair(p.first,make_pair(nx,ny))); //方案1，压入队头，当前代价不变
        }
        for(int i=max(p.second.first-2,1);i<=min(p.second.first+2,n);i++) //限制循环边界，卡常
            for(int j=max(p.second.second-2,1);j<=min(m,p.second.second+2);j++){
                if(c[i][j]=='#') continue; //不是路不走
                if(vis[i][j]) continue; //走过
                q.push_back(make_pair(p.first+1,make_pair(i,j))); //方案2，压入队尾，当前代价+1
            }
    }
    cout<<-1; //无解
    return 0;
}
```

#### 无注释版

<span style="color:white">可以CTJ的版本</span>

```cpp
#include <bits/stdc++.h>
using namespace std;
int n,m,sx,sy,dx,dy,cnt;
const int fx[]={1,0,-1,0},fy[]={0,1,0,-1};
char c[1005][1005];
int vis[1005][1005];
deque<pair<int,pair<int,int>>> q;
int main(){
    ios::sync_with_stdio(0);
    cin>>n>>m>>sx>>sy>>dx>>dy;
    for(int i=1;i<=n;i++)
        for(int j=1;j<=m;j++)
            cin>>c[i][j];
    q.push_back(make_pair(0,make_pair(sx,sy)));
    while(!q.empty()){
        auto p=q.front();
        q.pop_front();
        if(p.second.first==dx&&p.second.second==dy)
            cout<<p.first,exit(0);
        vis[p.second.first][p.second.second]=1;
        for(int t=0;t<4;t++){
            int nx=p.second.first+fx[t],ny=p.second.second+fy[t];
            if(c[nx][ny]=='#') continue;
            if(nx<1||ny<1||nx>n||ny>m) continue;
            if(vis[nx][ny]) continue;
            q.push_front(make_pair(p.first,make_pair(nx,ny)));
        }
        for(int i=max(p.second.first-2,1);i<=min(p.second.first+2,n);i++)
            for(int j=max(p.second.second-2,1);j<=min(m,p.second.second+2);j++){
                if(c[i][j]=='#') continue;
                if(vis[i][j]) continue;
                q.push_back(make_pair(p.first+1,make_pair(i,j)));
            }
    }
    cout<<-1;
    return 0;
}
```

#### 优先队列版

~~没事干写的~~

实测复杂度带的 $\log$ 会被卡掉：

```cpp
#include <bits/stdc++.h>
using namespace std;
int n,m,sx,sy,dx,dy;
const int fx[]={1,0,-1,0},fy[]={0,1,0,-1};
char c[1005][1005];
int vis[1005][1005];
priority_queue<pair<int,pair<int,int>>,vector<pair<int,pair<int,int>>>,greater<pair<int,pair<int,int>>>> q;
int main(){
    ios::sync_with_stdio(0);
    cin>>n>>m>>sx>>sy>>dx>>dy;
    for(int i=1;i<=n;i++)
        for(int j=1;j<=m;j++)
            cin>>c[i][j];
    q.push(make_pair(0,make_pair(sx,sy)));
    while(!q.empty()){
        auto p=q.top();
        q.pop();
        if(p.second.first==dx&&p.second.second==dy)
            cout<<p.first,exit(0);
        vis[p.second.first][p.second.second]=1;
        for(int t=0;t<4;t++){
            int nx=p.second.first+fx[t],ny=p.second.second+fy[t];
            if(c[nx][ny]=='#') continue;
            if(nx<1||ny<1||nx>n||ny>m) continue;
            if(vis[nx][ny]) continue;
            q.push(make_pair(p.first,make_pair(nx,ny)));
        }
        for(int i=max(p.second.first-2,1);i<=min(p.second.first+2,n);i++)
            for(int j=max(p.second.second-2,1);j<=min(m,p.second.second+2);j++){
                if(c[i][j]=='#') continue;
                if(vis[i][j]) continue;
                q.push(make_pair(p.first+1,make_pair(i,j)));
            }
    }
    cout<<-1;
    return 0;
}
```

各位大佬们点个赞嘛qwq~
