python 自动发帖
=================

代码仅供学习使用，请勿乱搞。。
----

###配置
    首先去官网注册账号  [注册地址](http://i.gamersky.com)
    配置文件中填写注册的账号密码；
    本地要安装redis服务
```ini
[user]
userName =
password =

[url]
loginUrl = http://i.gamersky.com/user/login
userHome = http://i.gamersky.com/home/
userInfo = http://i.gamersky.com/api/logincheck
addComment = http://cm.gamersky.com/api/addcommnet
getNewsList = http://db2.gamersky.com/LabelJsonpAjax.aspx

[redis]
host = 127.0.0.1
port = 6399
password=
db = 3

[send]
# 本次要发送成功的条数
newsNum = 1
# 是否跳过曾经发送过评论的帖子
isDistinct = 1
# 记录发送url缓存key名称
successKey = success_key
# 要发送的内容
content = 右边的小手很好玩，点一下变色，再点一下又变色；特别有意思。。
# 延迟发送时间
sleepSend = 20
```

###三方包列表
        redis,requests
###运行
```Bash
python3 app.py
```
