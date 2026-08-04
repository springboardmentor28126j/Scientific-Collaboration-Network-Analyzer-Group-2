import smtplib

HOST = "smtp-relay.brevo.com"
PORT = 587

USERNAME = "b3501c001@smtp-brevo.com"
PASSWORD = "xsmtpsib-21cd26d28ce4d069e0c62518d8a648f3d4a39eacad165c699d799df8d0d2cfaa-8bu6wXUmQAKApTca"

server = smtplib.SMTP(HOST, PORT)
server.starttls()

print("Logging in...")

server.login(USERNAME, PASSWORD)

print("Success!")

server.quit()
