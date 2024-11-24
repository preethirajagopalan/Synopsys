import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(to, subject, text, html=False, pdfs=[], fro='network-core@synopsys.com', server="mailhost.synopsys.com"):
    """
    Sends an email with the given arguments.

    :type to: List(string)
    :type subject: string
    :type text: string
    :type html: bool
    :type pdfs: List(string)
    :type fro: string
    :type server: string
    :rtype: void

    EXAMPLE USAGE:
    send_mail(['winston@synopsys.com'], 'Test Email', 'This is a test!')
    """
    assert type(to)==list

    # sets the metadata of the email
    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    formatted_text = MIMEText(text, 'html') if html else MIMEText(text)
    msg.attach(formatted_text)

    # open and read pdfs for attachment
    for pdf in pdfs:
        # read contents
        filename = pdf['filename']

        with open(filename, "r") as f:
            pdf_contents = f.read()

        pdf_attachment = MIMEApplication(pdf_contents, _subtype = "pdf")
        pdf_attachment.add_header('content-disposition', 'attachment', filename=pdf['display_name'])
        msg.attach(pdf_attachment)

    # send the email
    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string())
    smtp.quit()
