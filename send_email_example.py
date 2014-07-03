import smtplib
from email.mime.text import MIMEText
#fromaddr = 'krangfromdimensionx@gmail.com'
#toaddrs  = 'robert.weyant@gmail.com;dougalehmann@yahoo.com'

#username = 'krangfromdimensionx@gmail.com'
#password = 'lcawhlwrmodhtmse'


email_credentials = 'email_credentials.txt'
def get_email_credentials(email_credentials = 'email_credentials.txt'):
    with open(email_credentials ,'r') as credentials_file:
        for line in credentials_file:
            (field,value) = line.split('=')
            if field == 'fromaddr': fromaddr=value.strip()
            if field == 'toaddrs': toaddrs=value.strip().split(',')
            if field == 'username': username=value.strip()
            if field == 'password': password=value.strip()
        try:        fromaddr
        except NameError: 
            print' fromaddr not valid.'
            exit()
            
        try:        toaddrs
        except NameError: 
            print' toaddrs not valid.'
            exit()
        
        try:        username
        except NameError: 
            print' username not valid.'
            exit()
    
        try:        password
        except NameError: 
            print' password not valid.'    
            exit()
    return (fromaddr,toaddrs,username,password)
 
(fromaddr,toaddrs,username,password)=get_email_credentials()
print fromaddr
print toaddrs

msg = MIMEText("""no escape from reality""")
sender =fromaddr
recipients = toaddrs
msg['Subject'] = "Caught in a landslide"
msg['From'] = sender
msg['To'] = ", ".join(recipients)

s = smtplib.SMTP('smtp.gmail.com:587')
s.ehlo()
s.starttls()
s.login(username,password)
s.sendmail(sender, recipients, msg.as_string())
s.quit()


'''
server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
print toaddrs

msg = "\r\n".join([
  "From: " + fromaddr,
  "To: " + toaddrs,
  "Subject: SECOND ONE",
  "",
  "SECOND TRY"
  ])

print msg  
server.login(username,password)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
'''