import io
import random
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendUserRoleEmail(email, Subject, params):
    txt = "<p>Dear customer,<p></br><p>Thank you for choosing our service and submitting your customization request. We are pleased to inform you that we have received your request and will generate your customized character within <b>1-7</b> working days.</p></br><p> We value every customer's needs and will process your customization request as soon as possible during this period. If you have any questions or need to know the progress of your order in a timely manner, please feel free to contact our customer service representatives.</p></br> <p>Thank you again for choosing us, and we look forward to providing you with better service.</p></br><p>Best regards,</p></br>  Never Alone Again"
    # 设置服务器所需信息
    # 163邮箱服务器地址
    mail_host = 'smtp.gmail.com'
    # 163用户名
    mail_user = 'develop@soulmate.health'
    # 密码(部分邮箱为授权码)
    mail_pass = 'lluuoodzsnjxlgwy'
    # 邮件发送方邮箱地址
    sender = 'develop@icyberelf.com'
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = [email]

    # 设置email信息
    # 邮件内容设置
    message = MIMEText(txt, 'html', 'utf-8')
    # 邮件主题
    message['Subject'] = Subject
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com')
        # 连接到服务器
        smtpObj.connect(mail_host, port=465)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        return 1
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误
        return 2


def sendRoleEmail(email, Subject, params={}):
    txt = f"<p>定制角色姓名 ={params.get('roleName')}<br/>" \
          f"定制角色性别={params.get('gender')}<br/>" \
          f"定制角色年纪={params.get('age')}<br/>" \
          f"" \
          f"定制角色爱好={params.get('roleCharacter')}<br/>" \
          f"" \
          f"定制角色介绍={params.get('roleIntroduction')}<br/>" \
          f"" \
          f"定制角色补充={params.get('replenish')}<br/>" \
          f"" \
          f"定制人用户Id={params.get('userId')}<br/>" \
          f"" \
          f"定制人邮箱 = {params.get('email')}</p>" \
          f"" \
          f"角色头像 = {params.get('url')}</p>"
    # 设置服务器所需信息
    mail_host = 'smtp.gmail.com'
    # 163用户名
    mail_user = 'develop@soulmate.health'
    # 密码(部分邮箱为授权码)
    mail_pass = 'lluuoodzsnjxlgwy'

    # 邮件发送方邮箱地址
    sender = 'develop@icyberelf.com'
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = [email]

    # 设置email信息
    # 邮件内容设置
    message = MIMEText(txt, 'html', 'utf-8')
    # 邮件主题
    message['Subject'] = Subject
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com')
        # 连接到服务器
        smtpObj.connect(mail_host, port=465)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        return 1
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误
        return 2


def sendEmail(email, Subject):
    li_code = []
    for k in range(48, 58):  # 数字0-9
        li_code.append(chr(k))
    code = random.sample(li_code, 6)
    ran_code1 = "".join(code)
    # 设置服务器所需信息
    # 163用户名
    mail_user = 'develop@soulmate.health'
    # 密码(部分邮箱为授权码)
    mail_pass = 'lluuoodzsnjxlgwy'
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = [email]

    # 设置email信息
    # 邮件内容设置
    message = MIMEMultipart()
    ran_code = "<span style='color:red;'>" + ran_code1 + "</span>"
    if Subject == 1:
        # 登录
        mess = f"Thank you for choosing Never Alone Again. This is an email regarding your verification code. Please enter the following code on the login or verification page to complete your account login:<br><br>" \
               f"Verification Code: {ran_code}<br><br>" \
               f"This code will be valid for the next 30 minutes, so please complete the process as soon as possible. If you did not initiate this login request, please disregard this email.<br><br>" \
               f"If you need any assistance or have any questions, please feel free to contact our customer support team. We are here to assist you.<br><br>" \
               f"Enjoy using Never Alone Again!<br><br>" \
               f"Never Alone Again Team<br>" \
               f"Contact us: sunsun@soulmate.health"

        message = MIMEText(mess, 'html', 'utf-8')

    if Subject == 2:
        mess = f"Thank you for choosing Never Alone Again. This is an email regarding your verification code. Please enter the following code on the login or verification page to complete your account registration:<br><br>" \
               f"Verification Code: {ran_code}<br><br>" \
               f"This code will be valid for the next 30 minutes, so please complete the process as soon as possible. If you did not initiate this registration request, please disregard this email.<br><br>" \
               f"If you need any assistance or have any questions, please feel free to contact our customer support team. We are here to assist you.<br><br>" \
               f"Enjoy using Never Alone Again!<br><br>" \
               f"Never Alone Again Team<br>" \
               f"Contact us: sunsun@soulmate.health"

        message = MIMEText(mess, 'html', 'utf-8')
        # 注册

    if Subject == 3:
        # 找回密码
        mess = f"Thank you for choosing Never Alone Again. This is an email regarding your verification code. Please enter the following code on the login or verification page to complete your account Forgot password:<br><br>" \
               f"Verification Code: {ran_code}<br><br>" \
               f"This code will be valid for the next 30 minutes, so please complete the process as soon as possible. If you did not initiate this Forgot password request, please disregard this email.<br><br>" \
               f"If you need any assistance or have any questions, please feel free to contact our customer support team. We are here to assist you.<br><br>" \
               f"Enjoy using Never Alone Again!<br><br>" \
               f"Never Alone Again Team<br>" \
               f"Contact us: sunsun@soulmate.health"

        message = MIMEText(mess, 'html', 'utf-8')

    if Subject == 4:
        # 注销主题
        mess = f"Thank you for choosing Never Alone Again. This is an email regarding your verification code. Please enter the following code on the login or verification page to complete your account Cancel account:<br><br>" \
               f"Verification Code: {ran_code}<br><br>" \
               f"This code will be valid for the next 30 minutes, so please complete the process as soon as possible. If you did not initiate this Cancel account request, please disregard this email.<br><br>" \
               f"If you need any assistance or have any questions, please feel free to contact our customer support team. We are here to assist you.<br><br>" \
               f"Enjoy using Never Alone Again!<br><br>" \
               f"Never Alone Again Team<br>" \
               f"Contact us: sunsun@soulmate.health"

        message = MIMEText(mess, 'html', 'utf-8')

    message['Subject'] = "Your Never Alone Again Verification Code"
    # 发送方信息
    message['From'] = mail_user
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com')

        # 连接到服务器
        smtpObj.connect('smtp.gmail.com', port=465)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            mail_user, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        return ran_code1
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误


def sendUserDataEmail(email, Subject, workbook):
    # 设置服务器所需信息
    mail_user = 'develop@soulmate.health'
    # 密码(部分邮箱为授权码)
    mail_pass = 'lluuoodzsnjxlgwy'
    # 邮件接收方邮箱地址
    receivers = [email]

    # 将 Workbook 内容保存在内存中
    buffer = io.BytesIO()
    workbook.save(buffer)

    # 设置email信息
    # 邮件内容设置
    message = MIMEMultipart()
    mess = "Dear Never Alone Again User,<br><br>" \
           "Thank you for choosing Never Alone Again. We are pleased to inform you that your account data is now ready for download, and you can retrieve and save this data at your convenience.<br><br>" \
           "Please click the above link, and you will be redirected to a secure page to download your data file. The data is provided in CSV format, which you can open and analyze using compatible applications.<br><br>" \
           "To ensure the security of your data, please do not share the download link with any unverified sources. If you encounter any issues or require further assistance, please feel free to contact our customer support team.<br><br>" \
           "Thank you for choosing Never Alone Again, and enjoy using our app!<br><br>" \
           "Best regards,<br><br>" \
           "Never Alone Again Data Team<br><br>" \
           "Contact us: <a href='mailto:sunsun@soulmate.health'>sunsun@soulmate.health</a>"
    message.attach(MIMEText(mess, 'html', 'utf-8'))
    # 邮件主题
    message['Subject'] = Subject
    # 发送方信息
    message['From'] = mail_user
    # 接收方信息
    message['To'] = receivers[0]

    # 添加附件
    attachment = MIMEApplication(buffer.getvalue(), Name="userData.xlsx")
    attachment['Content-Disposition'] = "attachment; filename=userData.xlsx"
    message.attach(attachment)

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com')

        # 连接到服务器
        smtpObj.connect('smtp.gmail.com', port=465)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(mail_user, receivers, message.as_string())
        # 退出
        smtpObj.quit()
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误


if __name__ == '__main__':
    sendEmail('keykong167@163.com', '验证码’')
