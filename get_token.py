from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'production/gmail_credentials.json',
    scopes=[
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
)

creds = flow.run_local_server(port=0)
print("\nNEW REFRESH TOKEN:", creds.refresh_token)
