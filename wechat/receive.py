# -*- coding: utf-8 -*-
# filename: receive.py
import xml.etree.ElementTree as ET
import json

def parse_xml(web_data):
    if len(web_data) == 0:
        return None
    xmlData = ET.fromstring(web_data)
    msg_type = xmlData.find('MsgType').text
    if msg_type == 'text':
        return TextMsg(xmlData)
    elif msg_type == 'image':
        return ImageMsg(xmlData)
    elif msg_type == 'link':
        return LinkMsg(xmlData)
    elif msg_type == 'event':
        return EventMsg(xmlData)
    else:
        return Msg(xmlData)

class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        
    def __repr__(self):
        value_dict = {k: str(v) for k, v in self.__dict__.items()}
        return json.dumps(value_dict, indent=4)

class EventMsg(object):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Event = xmlData.find('Event').text.encode("utf-8")
        
class TextMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Content = xmlData.find('Content').text.encode("utf-8")

class ImageMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text
        
class LinkMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Title = xmlData.find('Title').text
        self.Description = xmlData.find('Description').text
        self.Url = xmlData.find('Url').text