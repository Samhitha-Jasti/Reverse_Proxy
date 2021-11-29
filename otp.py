import smtplib
import random
import string

senderacc="adityamitra5102devacc@gmail.com"
senderpass="DevPassword1"

def genOtp():
	characters = string.digits
	password = ''.join(random.choice(characters) for i in range(4))
	return password

def sendEmail(id,otp):
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(senderacc, senderpass)
	message = "Subject:Authorization OTP\n\nThe OTP for Authorization is "+otp
	s.sendmail(senderacc, id, message)
	s.quit()