# wechat-dialogs
一个微信公众号处理复杂会话的轮子，使用python generator和redis管理对话上下文

# 部署demo

代码中附带了一个Flask写的小demo，可以直接部署测试。另外代码是在python3下写的。

安装步骤如下：
1. 根据requirement.txt安装依赖包（其实就redis和flask..）
2. 安装一个Redis，知道它的IP地址，端口号，密码等信息
3. 在demo_dialog.py的开头更改相应的REDIS配置信息
4. 启动demo_server.py: python ./demo_server.py
5. 去微信公众平台绑定公众号服务器

# 应用到其他项目

1. 编写自己的对话逻辑，类似demo_dialog.py
2. 在服务器代码中用wechat.bot.answer(post_data, dialog_module)获取相应的回复

相关文章：http://www.jianshu.com/p/974cf38291ec