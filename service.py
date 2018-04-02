import requests, os, json, re, time

import helper, cache


# 基类
class App(object):
    def __init__(self):
        # utl客户端
        self.__session = requests.Session()
        # 用户信息
        self.__user = None
        # 初始化登录
        self.__login()

        # 当前第几页
        self.page = 0
        # 已成功发送多少条
        self.success_num = 0
        # 本次要发送成功的条数
        self.newsNum = int(helper.common.getConfig('send', 'newsNum'))
        # 是否跳过曾经发送过评论的帖子
        self.isDistinct = helper.common.getConfig('send', 'isDistinct')
        # 记录发送url缓存key名称
        self.successKey = helper.common.getConfig('send', 'successKey')
        # 要发送的内容
        self.content = helper.common.getConfig('send', 'content')
        # 延迟发送时间
        self.sleepSend = int(helper.common.getConfig('send', 'sleepSend'))
    # 登录  is_reload 强制重新登录
    def __login(self):
        # 已登录
        if not self.__user is None:
            return self.__user
        # 有session记录  直接自动登录
        if not self.__session.cookies:
            # 打开session文件
            with open('session', 'rt') as file:
                cookie = file.read()
                if cookie:
                    dic = json.loads(cookie)
                    for item in dic:
                        self.__session.cookies.set(item, dic[item])
                    self.__get_user()
                    # 获取用户信息成功
                    if not self.__user is None:
                        return
        # 重新登录
        # 请求体数据
        posts = {
            'userName': helper.common.getConfig('user', 'userName'),
            'loginPassword': helper.common.getConfig('user', 'password'),
            'persistent': 'true',
            'showCode': 'false',
        }
        self.__session = requests.Session()
        # 登录成功后  cookie自动记录
        res = self.__session.post(helper.common.getConfig('url', 'loginUrl'), posts)
        if res.json()['Message'] != 'ok':
            print("登录失败")
            print(res.json())
            os._exit(0)
        # 登录成功 记录session  防止重复登录
        cookie = self.__session.cookies.get_dict()
        with open('session', 'wt') as file:
            file.write(json.dumps(cookie))
        # 获取用户信息
        self.__get_user()
        # 获取用户信息成功
        if not self.__user is None:
            return
        else:
            print("登录失败！")
            os._exit(0)

    def __get_user(self):
        res = self.__session.get(helper.common.getConfig('url', 'userInfo'))
        json_str = res.content.decode('utf-8')[1:-2]
        if json_str == '""':
            self.__user = None
            return
        self.__user = json.loads(json_str)

    def get_user_info(self):
        return self.__user

    def get_client(self):
        return self.__session

    def run(self):
        '''
        主运行进程方法
        :return:
        '''
        self._run(1)

    def _run(self, page=1):
        lists = self.__get_news_list(page)
        for item in lists:
            self.send_comment(item)
            if self.success_num >= self.newsNum:
                # 数量已够 结束
                print('已成功发送 %s 条评论！' % (self.success_num))
                return
            # 延迟10秒后再发送 防止太快封号
            time.sleep(self.sleepSend)
        if self.success_num < self.newsNum:
            self._run(page + 1)

    def __get_news_list(self, page=-1):
        '''
        每次取一页
        :param page:
        :return:
        '''
        if page == -1:
            page = self.page + 1
        url = helper.common.getConfig('url', 'getNewsList')
        response = self.__session.get(url, data={"page": page,
                                                 "jsondata": '{"type":"updatenodelabel","isCache":true,"cacheTime":60,"nodeId":"11007","isNodeId":"true"}'}).content.decode(
            'utf-8')
        if not response:
            print('获取新闻列表失败！')
            return []
        # 正则匹配链接
        pa = re.compile(r'http:\/\/[a-z\.]{10,30}\/[a-z]{3,15}\/\d{6}\/\d{7}\.shtml')
        # 用set存储 取出重复
        lists = set(pa.findall(response))
        if not lists:
            print('获取新闻第 %s 页列表失败' % (page))
        return lists

    def send_comment(self, url):
        '''
        发表评论
        :return:
        '''

        # 截取url中帖子id
        news_id = re.search('(\d{7}).shtml', url).group(1)
        if not news_id:
            print('获取新闻id失败！')
            return
        # 判断跳过重复
        if self.isDistinct == '1' and self.check_is_send(news_id):
            print("重复的文章：", url)
            return
        posts = {
            'jsondata': '{"sid":' + news_id + ',"content":"' + self.content + '"}'
        }
        href = helper.common.getConfig('url', 'addComment')
        res = self.__session.post(href, posts)
        json_str = res.json()
        if json_str["status"] == 'ok':
            self.add_news_log(news_id, url)
            self.success_num = self.success_num + 1
            print('第 %s 条评论发送成功：%s' % (self.success_num, url))
        else:
            print(json_str)

    def check_is_send(self, news_id):
        '''
        判断帖子id是否曾经发送过评论
        :return:
        '''
        res = cache.cache.hget(self.successKey, news_id)
        if res:
            return True
        else:
            return False

    def add_news_log(self, news_id, url):
        '''
        记录帖子已经发送 防止重复发送
        :return:
        '''
        cache.cache.hset(self.successKey, news_id, url)

app = App()
