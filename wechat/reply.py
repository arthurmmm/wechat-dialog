# -*- coding: utf-8 -*-
# filename: reply.py
import time
import json

class Msg(object):
    def __init__(self):
        pass
    def __repr__(self):
        value_dict = {k: str(v) for k, v in self.__dict__.items()}
        return json.dumps(value_dict, indent=4)
    def format(self):
        return "success"

class TextMsg(Msg):
    def __init__(self, toUserName, fromUserName, content):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def format(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict)

class NewsMsg(Msg):
    ''' article = {
        'title': xxx,
        'description': xxx,
        'pic_url': xxx, # Use avator pic as default
        'url': xxx,
    }
    '''
    def __init__(self, toUserName, fromUserName, articles):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['ArticleCount'] = len(articles)
        self.__dict['Articles'] = ''
        self.articles = articles
        
    def format(self):
        XmlArticle = """
        <item>
        <Title><![CDATA[%(title)s]]></Title> 
        <Description><![CDATA[%(description)s]]></Description>
        <PicUrl><![CDATA[%(pic_url)s]]></PicUrl>
        <Url><![CDATA[%(url)s]]></Url>
        </item>
        """
        for article in self.articles:
            if 'pic_url' not in article:
                article['pic_url'] = 'http://okmokavp8.bkt.clouddn.com/images/Untitled%20picture.png'
            xml = XmlArticle % article
            self.__dict['Articles'] += xml
            
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime><![CDATA[{CreateTime}]]></CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>{ArticleCount}</ArticleCount>
        <Articles>{Articles}</Articles>
        </xml>
        """
        return XmlForm.format(**self.__dict)
        
class ImageMsg(Msg):
    def __init__(self, toUserName, fromUserName, mediaId):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = mediaId
    def format(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
        </xml>
        """
        return XmlForm.format(**self.__dict)