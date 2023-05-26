import smtplib
from email.mime.text import MIMEText


class EmailSender:
    __from_addr: str = None
    __pwd: str = None
    __emailer: smtplib.SMTP_SSL = None

    def __init__(self, from_addr, pwd, host: str) -> None:
        self.__from_addr = from_addr
        self.__pwd = pwd
        self.__host = host
        self.__emailer = smtplib.SMTP_SSL(self.__host, 465, timeout=10)
        self.__emailer.login(self.__from_addr, self.__pwd)

    def send(self, to_addr: str, content: str, subject: str) -> bool:
        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = self.__from_addr
        msg["To"] = to_addr
        self.__emailer = smtplib.SMTP_SSL(self.__host, 465, timeout=10)
        # self.__emailer.login(self.__from_addr, self.__pwd)
        try:
            self.__emailer.login(self.__from_addr, self.__pwd)
            self.__emailer.send_message(
                msg=msg, from_addr=self.__from_addr, to_addrs=to_addr
            )
            return True
        except smtplib.SMTPException as e:
            raise e
