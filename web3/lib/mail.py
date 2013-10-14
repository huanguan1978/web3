#!/bin/env python
'''sendmail use smtp
'''

import smtplib
import mimetypes

import email
import email.header
import email.utils
import email.mime.base
import email.mime.text
import email.mime.audio
import email.mime.image
import email.mime.multipart

class Smtp:
    
    def __init__(self, username:str, password:str, server:str='localhost', port:int=25):
        self._username = username
        self._password = password
        self._server = server
        self._port = port

        self._smtp = None
        self._esmtp = True

    def __del__(self):
        if self._smtp:
            self._smtp.quit()
        self._smtp = None

    def message(self, from_:str, to:str, reply_to:str=None,cc:tuple=None, bcc:tuple=None, subject:str=None, text_message:str=None, html_message:str=None, attachments:tuple=None):
        '''MIME mssage '''
        msg = email.mime.multipart.MIMEMultipart('alternative')
        msg['To'] = to
        msg['From'] = from_
        msg['Date'] = email.utils.formatdate(localtime=1)
        msg['Message-ID'] = email.utils.make_msgid()
        
        if subject:
            msg['Subject'] = email.header.Header(subject, 'utf-8')
        if reply_to:
            msg['Reply-To'] = email.header.Header(reply_to)
        if cc:
            msg['Cc'] = ','.join(cc)
        if bcc:
            msg['Bcc'] = ','.join(bcc)

        if text_message:
            msg.attach(email.mime.text.MIMEText(text_message, 'plain', 'utf-8'))

        if html_message:
            msg.attach(email.mime.text.MIMEText(html_message, 'html', 'utf-8'))
        
        if attachments:
            for attachment in attachments:

                ctype, encoding = mimetypes.guess_type(attachment)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)

                fd = None
                try:
                    fd = open(attachment, 'rb')
                except:
                    raise
                else:
                    if 'text' == maintype:
                        chunk = email.mime.text.MIMEText(fd.read(), subtype, 'utf-8')
                    elif 'image' == maintype:
                        chunk = email.mime.image.MIMEImage(fd.read(), subtype)
                    elif 'audio' == maintype:
                        chunk = email.mime.audio.MIMEAudio(fd.read(), subtype)
                    else:
                        chunk = email.mime.base.MIMEBase(maintype, subtype)
                        chunk.set_payload(fd.read(), 'base64')

                    chunk.add_header('Content-Disposition', 'attachment', filename = attachment)
                    msg.attach(chunk)
                    
                finally:
                    if fd:
                        fd.close()

        return msg


    def sendmessage(self, msg,  mail_options=[], rcpt_options={}):
        '''sendmail '''
        if self._smtp:
            if self._esmtp and self._smtp.has_extn('size'):
                if len(msg.as_string()) > int(self._smtp.esmtp_features['size']):
                    print("msg size > esmpt size {}".format(self._smpt.esmtp_features['size']))
                    raise

                
            return self._smtp.send_message(msg, mail_options=mail_options, rcpt_options=rcpt_options)
            
    def smtp(self, debuglevel:int=0):
        '''smpt instance'''
        try:
           self._smtp = smtplib.SMTP(self._server, self._port)
        except:
            raise
        else:
            if debuglevel:
                self._smtp.set_debuglevel(debuglevel)
            try:
                ehlo = self._smtp.ehlo()
            except:
                self._esmtp = False
            else:
                if not (200 <= ehlo[0] <=299):
                    raise stmplib.SMTPHeloError(ehlo[0], self._smtp.ehlo_resp)

            try:
                helo = self._smtp.helo()
            except:
                raise
            else:
                if self._esmtp and self._smtp.has_extn('starttls'):
                    try:
                        self._smtp.starttls()
                    except:
                        raise
                    else:
                        try:
                            ehlo = self._smtp.ehlo()
                        except:
                            raise
                        else:
                            if not (200 <= ehlo[0] <= 299):
                                raise stmplib.SMTPHeloError(ehlo[0], self._smtp.ehlo_resp)

                            if self._smtp.has_extn('auth'):
                                try:
                                    self._smtp.login(self._username, self._password)
                                except:
                                    raise
