import smtplib

fromaddr = 'krangfromdimensionx@gmail.com'
toaddrs  = 'robert.weyant@gmail.com'

username = 'krangfromdimensionx@gmail.com'
password = 'Shredder'

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()

msg = "\r\n".join([
  "From: user_me@gmail.com",
  "To: user_you@gmail.com",
  "Subject: Just a message",
  "",
  "Why, oh why"
  ])
  
server.login(username,password)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()

