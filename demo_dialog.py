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
        ('^累加器$', 'accumulator'), # 格式为(<匹配模式>, <处理函数>), 匹配模式为正则表达式
        ('^github$', 'show_links'),
        ('^会话记录$', 'context_origin'), # 通过is_replay避免重复执行某段代码
        ('^会话菜单$', 'context_menu'), # 通过raise UnexpectAnswer将某个不合法输入当做下一个输入的入口
        ('.*', 'show_help'), # 默认的处理函数，请务必指定一个
    ],
    'event': [ # 事件消息，用事件类型进行匹配，事件类型包括关注(subscribe)和取关(unsubscribe)
        ('^subscribe$', 'show_welcome'),
        ('.*', 'show_help'), # 默认的处理函数，请务必指定一个
    ],
}

HELP = '''这个公众号是wechat-dialog项目的demo，可以用编写命令行程序的体验来编写公众号深度会话
源代码在GITHUB上,输入"github"（全小写）可以获得链接

共有三个DEMO：
- 回复"累加器"玩一玩累加，这是基本功能
- 回复"会话记录"看一下如何防止数据重复写入
- 回复"会话菜单"了解如何静默切换会话逻辑'''

# 下面这些是对话处理函数 - 一个python生成器(generator)
# 接收一个参数to_user: 这是用户的open_id
# 返回一个元祖：(<MsgType>, <内容>)
# 目前只测试过文本消息(TextMsg)和链接消息(NewsMsg)
# 相关例子可以看show_help和show_links
# accumulator是DEMO的核心 - 通过用户问答实现了一个累加器

def show_help(to_user):
    # 下面两行用于初始化，请保留
    yield None
    msg_content, is_replay = yield None # 获得用户的消息内容
    
    return ('TextMsg', HELP) # 如果没有后续会话就return，return格式(<MsgType>, <内容>)
    
def show_welcome(to_user):
    yield None
    msg_content, is_replay = yield None
    
    msg = '感谢关注！\n'+HELP
    return ('TextMsg', msg)

def show_links(to_user):
    yield None
    msg_content, is_replay = yield None
    
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
    msg_content, is_replay = yield None
    
    num_count, is_replay = yield ('TextMsg', '您需要累加几个数字？')
    try:
        num_count = int(num_count)
    except Exception:
        return ('TextMsg', '输入不合法！我们需要一个整数，请输入"开始"重新开启累加器')
    res = 0
    for i in range(num_count):
        num, is_replay = yield ('TextMsg', '请输入第%s个数字, 目前累加和:%s' % (i+1, res))
        try:
            num = int(num)
        except Exception:
            return ('TextMsg', '输入不合法！我们需要一个整数，请输入"开始"重新开启累加器')
        res += num
        
    # 注意：最后一个消息一定要用return不要用yield！return用于标记会话结束。
    return ('TextMsg', '累加结束，累加和: %s' % res)

context_start = None 
def context_origin(to_user):
    yield None
    msg_content, is_replay = yield None
    
    global context_start
    from datetime import datetime
    if not is_replay: # 加上这句可以让context_start只更新一次，避免replay过程中的重复操作
        context_start = datetime.now()
        context_start = datetime.strftime(context_start, '%Y-%m-%d %H:%M:%S')
    msg_content, is_replay = yield ('TextMsg', '您在%s开启了这段对话，随便聊聊吧，回复“结束”结束对话' % context_start)
    while True:
        if msg_content == '结束':
            return ('TextMsg', '会话结束，这段会话的开始时间是%s' % context_start)
        else:
            msgtime = datetime.now()
            msgtime = datetime.strftime(msgtime, '%Y-%m-%d %H:%M:%S')
            msg_content, is_replay = yield ('TextMsg', '%s：%s' % (msgtime, msg_content))

def context_menu(to_user):
    yield None
    msg_content, is_replay = yield None
    
    msg_content, is_replay = yield ('TextMsg', '菜单：\n1. 苹果\n2. 香蕉\n回复数字选择，如果回复的内容不合法会直接跳转，比如回复"累加器"会直接跳转到累加器对话。')
    if msg_content == '1':
        return ('TextMsg', '您选择的是：苹果')
    elif msg_content == '2':
        return ('TextMsg', '您选择的是：香蕉')
    else:
        # 不用输入特殊消息结束，直接进入下一段对话
        from wechat.bot import UnexpectAnswer
        raise UnexpectAnswer