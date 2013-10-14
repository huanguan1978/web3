import os
import sys
import unittest

sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../')))


from web3.lib.mail import Smtp

username = 'huanguan1978@163.com'
password = ''
server = 'smtp.163.com'
port = 25

from_ = 'huanguan1978@163.com'
to = 'crown.hg@gmail.com'
reply_to = '147146017@qq.com'
cc = ('147146017@qq.com', 'huanguan1978@hotmail.com')
subject = '测试邮件'
attachments = ('/home/crown/t.txt', '/home/crown/d_nb_0001.jpg')
html = \
'''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title data-lang="title">email confirm</title>
  </head>
  <body>
    <h2 data-lang="title">email confirm</h2>
    <p data-lang="notify">
      你可通过复制下列网址到浏览器地栏或单击下列网址进行邮箱验证:
    </p>
    <p>
      <a href="h">h</a>
    </p>
  </body>
</html>
'''

smtp = Smtp(username, password, server, port)
smtp.smtp()
#msg = smtp.message(from_, to, reply_to, cc, subject = subject, attachments=attachments)
msg = smtp.message(from_, to, html_message=html)
#print(repr(msg.as_string()))
smtp.sendmessage(msg)

del smtp
