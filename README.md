# wechat-dialogs
一个微信公众号处理复杂会话的轮子，使用python generator和redis管理对话上下文

比如你只需要写下面这种代码：

```python
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
```

就能实现截图这种功能：

![Paste_Image.png](http://upload-images.jianshu.io/upload_images/4610828-e4d47cdc45d03c89.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

# 部署demo

代码中附带了一个Flask写的小demo，可以直接部署测试。另外代码是在python3下写的。

安装步骤如下：
1.  根据requirement.txt安装依赖包（其实就redis和flask..）
2.  安装一个Redis，知道它的IP地址，端口号，密码等信息
3.  在demo_dialog.py的开头更改相应的REDIS配置信息
4.  启动demo_server.py: python ./demo_server.py
5.  去微信公众平台绑定公众号服务器

# 应用到其他项目

1. 编写自己的对话逻辑，类似demo_dialog.py
2. 在服务器代码中用wechat.bot.answer(post_data, dialog_module)获取相应的回复

相关博客：
*  http://www.jianshu.com/p/974cf38291ec
*  http://blog.arthurmao.me/2017/02/python-redis-wechat-dialog