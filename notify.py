from twilio.rest import Client

def sendmsg():
    account_sid = 'YOUR ACCOUNT SID'
    auth_token = 'YOUR AUTH TOKEN'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_ = 'SENDER NUMBER',
        body = 'Unauthorized access in system',
        to = 'RECEIVER NUMBER'
    )

    print(message.sid)
