# -*- coding: utf-8 -*-

import json
import re
import logging
from redis import StrictRedis

from . import reply, receive

logger = logging.getLogger('__main__')

dialog_module = None
hkey = None
redis_db = None

class UnexpectAnswer(Exception):
    ''' Raise it if user gives an unexpected answer
    Then this answer will be regarded as a start of new dialog
    '''
    pass

def _redis_replay(key, dialog):
    ''' Replay dialog based on redis history
    '''
    hist = redis_db.get(key)
    if not hist:
        raise Exception('Empty hist!')
    else:
        hist = json.loads(hist.decode('utf-8'))[1:]
    for step in hist:
        dialog.send((step, True))
    return dialog
        
def _redis_send(key, dialog, msg, expire=60):
    ''' Send msg to dialog and store history to redis
    '''
    hist = redis_db.get(key)
    if not hist:
        logger.debug(dialog.__name__)
        # 第一个元素用于存generator的名字，其余均为消息记录
        hist = [dialog.__name__]
    else:
        hist = json.loads(hist.decode('utf-8'))
    hist.append(msg)
    redis_db.setex(key, expire, json.dumps(hist))
    logger.debug(dialog)
    return dialog.send((msg, False))
    

def _new_dialog(msg_type, msg_content, to_user):
    redis_db.delete(hkey)
    # 根据router重新选择并构造回复器
    router = dialog_module.ROUTER[msg_type]
    for pattern, dialog_name in router:
        regex = re.compile(pattern)
        if regex.match(msg_content):
            dialog = getattr(dialog_module, dialog_name)(to_user)
            break
    else:
        raise Exception('Router not found')
    # 初始化操作
    dialog.send(None)
    _redis_send(hkey, dialog, msg_content)
    return dialog
    
def _replay_dialog(hist, to_user):
    # 从hist中获取这个消息的处理器
    dialog_name = json.loads(hist.decode('utf-8'))[0]
    dialog = getattr(dialog_module, dialog_name)(to_user)
    # 重现上下文
    dialog.send(None)
    _redis_replay(hkey, dialog)
    return dialog

def answer(data, module):
    # Extract msg
    msg = receive.parse_xml(data)
    msg_type = msg.MsgType
    to_user = msg.FromUserName
    from_user = msg.ToUserName
    if isinstance(msg, receive.TextMsg):
        msg_content = msg.Content.decode('utf-8')
    elif isinstance(msg, receive.EventMsg):
        msg_content = msg.Event.decode('utf-8')
    else:
        msg_content = 'default'
    
    # Initialize environment
    global dialog_module
    dialog_module = module
    global hkey
    hkey = dialog_module.REDIS_KEY % {'open_id': to_user}
    global redis_db
    redis_db = StrictRedis(
        host=dialog_module.REDIS_HOST, 
        port=dialog_module.REDIS_PORT, 
        password=dialog_module.REDIS_PASSWORD,
        db=0
    )
        
    hkey = dialog_module.REDIS_KEY % {'open_id': to_user}
    hist = redis_db.get(hkey)
    # 新会话或者会话超时，创建新会话
    if not hist:
        dialog = _new_dialog(msg_type, msg_content, to_user)
        logger.debug('new_dialog')
    # 存在会话记录，重现上下文
    else:
        logger.debug('replay_dialog')
        try:
            dialog = _replay_dialog(hist, to_user)
        except StopIteration:
            logger.error('会话记录错误..重新创建会话..')
            dialog = _new_dialog(msg_type, msg_content, to_user)
    # 发送消息
    while True:
        try:
            type, msg = _redis_send(hkey, dialog, msg_content)
            break
        except StopIteration as e:
            # 会话已结束，删去redis中的记录
            type, msg = e.value
            redis_db.delete(hkey)
            break
        except UnexpectAnswer:
            # 用户发送了一个不合法的回复时抛出这个异常
            # BOT会认为用户希望开启一段新的会话
            redis_db.delete(hkey)
            dialog = _new_dialog(msg_type, msg_content, to_user)
            continue
    
    wechat_reply = getattr(reply, type)
    print(wechat_reply(
        to_user, 
        from_user, 
        msg
    ).format())
    return wechat_reply(
        to_user, 
        from_user, 
        msg
    )
    