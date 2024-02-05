import requests
import webbrowser
from urllib.parse import urlparse, parse_qs

def get_user_input(prompt):
    return input(prompt)

def authenticate_trakt():
    print("Welcome to Trakt OAuth Authentication.")

    # Prompt user for client ID and secret
    client_id = get_user_input("Enter your Trakt client ID: ")
    client_secret = get_user_input("Enter your Trakt client secret: ")

    # Step 1: Get Authorization Code
    auth_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
    print(f"Visit the following URL to authorize your application:\n{auth_url}")
    webbrowser.open(auth_url)

    authorization_code = get_user_input("Enter the authorization code from the URL: ")

    # Step 2: Exchange Authorization Code for Access Token
    token_url = "https://trakt.tv/oauth/token"
    payload = {
        "code": authorization_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        print(f"\nAuthentication successful!\nYour Trakt access token is:\n{access_token}")
    else:
        print(f"\nAuthentication failed. Please check your credentials and try again.")

if __name__ == "__main__":
    authenticate_trakt()
