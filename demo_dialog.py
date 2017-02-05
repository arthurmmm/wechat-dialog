# -*- coding: utf-8 -*-

# REDIS 配置，请自行替换
REDIS_HOST = 'your_redis_ip'
REDIS_PORT = 6379
REDIS_PASSWORD = 'your_redis_password'
REDIS_DB = 0
# REDIS KEY的格式，会接收用户的open_id作为变量
REDIS_KEY='wechat-dialog:demo:%(open_id)s'

# 初始配置，根据用户信息分配对应的会话处理器
ROUTER = {
    'text': [ # 文本消息，用文本内容进行匹配
        ('^开始$', 'accumulator'), # 格式为(<匹配模式>, <处理函数>), 匹配模式为正则表达式
        ('^github$', 'show_links'),
        ('.*', 'show_help'), # 默认的处理函数，请务必指定一个
    ],
    'event': [ # 事件消息，用事件类型进行匹配，事件类型包括关注(subscribe)和取关(unsubscribe)
        ('^subscribe$', 'show_welcome'),
        ('.*', 'show_help'), # 默认的处理函数，请务必指定一个
    ],
}

HELP = '''这个公众号是wechat-dialog项目的demo，通过公众号消息回复实现了一个简单的数字累加器和字符串拼接器
源代码在GITHUB上,输入"github"（全小写）可以获得链接

请在聊天窗口中输入"开始"，注意请在一分钟内给出回答哦。'''

# 下面这些是对话处理函数 - 一个python生成器(generator)
# 接收一个参数to_user: 这是用户的open_id
# 返回一个元祖：(<MsgType>, <内容>)
# 目前只测试过文本消息(TextMsg)和链接消息(NewsMsg)
# 相关例子可以看show_help和show_links
# accumulator是DEMO的核心 - 通过用户问答实现了一个累加器

def show_help(to_user):
    # 下面两行用于初始化，请保留
    yield None
    msg_content = yield None # 获得用户的消息内容
    
    return ('TextMsg', HELP) # 如果没有后续会话就return，return格式(<MsgType>, <内容>)
    
def show_welcome(to_user):
    yield None
    msg_content = yield None
    
    msg = '感谢关注！\n'+HELP
    return ('TextMsg', msg)

def show_links(to_user):
    yield None
    msg_content = yield None
    
    return ('NewsMsg', [
        {
            'title': '项目源码', 
            'description': 'github上的项目源码，喜欢的话顺手点个STAR吧(๑•ᴗ•๑)', 
            'url': 'https://github.com/arthurmmm/wechat-dialog',
            # 可以选择不设置pic_url,使用默认缩略图。在reply.py中可以设置默认缩略图。
            'pic_url': 'https://help.github.com/assets/images/site/be-social.gif',
        },
        # 最多支持8个链接
    ])
        
def accumulator(to_user):
    yield None
    msg_content = yield None
    
    num_count = yield ('TextMsg', '您需要累加几个数字？')
    try:
        num_count = int(num_count)
    except Exception:
        return ('TextMsg', '输入不合法！我们需要一个整数，请输入"开始"重新开启累加器')
    res = 0
    for i in range(num_count):
        num = yield ('TextMsg', '请输入第%s个数字, 目前累加和:%s' % (i+1, res))
        try:
            num = int(num)
        except Exception:
            return ('TextMsg', '输入不合法！我们需要一个整数，请输入"开始"重新开启累加器')
        res += num
        
    # 注意：最后一个消息一定要用return不要用yield！return用于标记会话结束。
    return ('TextMsg', '累加结束，累加和: %s' % res)