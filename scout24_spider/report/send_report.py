import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


class SendReport:

    def __init__(self, server_addr='', username='', password='', from_addr='',
                 to_addr='', subject='', msg='', path=''):
        self.server = smtplib.SMTP(server_addr)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(username, password)
        self.from_addr = from_addr
        self.subject = subject

        if isinstance(to_addr, list):
            self.to_addr = to_addr
        else:
            self.to_addr = [to_addr]

        self.message_body = msg
        self.path_to_attachment = path

        self.message = None

    def send_text_mail(self):
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (self.from_addr, ", ".join(self.to_addr), self.subject, self.message_body)

        self.server.sendmail(self.from_addr, self.to_addr, message)
        self.server.close()

    def send_multipart_mail(self):
        self.message = MIMEMultipart()
        self.message['From'] = self.from_addr
        self.message['To'] = COMMASPACE.join(self.to_addr)
        self.message['Date'] = formatdate(localtime=True)
        self.message['Subject'] = self.subject

        self.message.attach(MIMEText(self.message_body))

        with open(self.path_to_attachment, 'rb') as f:
            part = MIMEApplication(
                f.read(),
                Name=basename(self.path_to_attachment)
            )

        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(self.path_to_attachment)
        self.message.attach(part)
        self.server.sendmail(self.from_addr, self.to_addr, self.message.as_string())
        self.server.close()


