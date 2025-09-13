import os
import streamlit as st
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from Admin import show_dashboard

# Load environment variables
load_dotenv()

# Auth0 / OAuth2 config
client_id = os.getenv("OAUTH_CLIENT_ID")
client_secret = os.getenv("OAUTH_CLIENT_SECRET")
authorize_url = os.getenv("OAUTH_AUTHORIZE_URL")
token_url = os.getenv("OAUTH_TOKEN_URL")
redirect_uri = os.getenv("REDIRECT_URI")
scopes = os.getenv("OAUTH_SCOPES", "openid profile email").split()
auth0_domain = os.getenv("AUTH0_DOMAIN")  # e.g. dev-abc123.us.auth0.com

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "state" not in st.session_state:
    st.session_state.state = None

st.title("🔐 Streamlit OAuth2 Demo with Auth0")

# --- Handle token exchange if redirected back from Auth0 ---
if "code" in st.query_params and st.session_state.token is None:
    code = st.query_params["code"]
    try:
        # Create a fresh OAuth2 session with same state + scopes
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, state=st.session_state.state, scope=scopes)
        token = oauth.fetch_token(
            token_url,
            client_secret=client_secret,
            code=code,
            include_client_id=True
        )
        st.session_state.token = token
    except Exception as e:
        st.error(f"Token fetch failed: {e}")

# --- Show login if not logged in ---
if st.session_state.token is None:
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    login_url, state = oauth.authorization_url(authorize_url, prompt="login")  # Forces login screen
    st.session_state.state = state
    st.markdown(f"[🔑 Login here]({login_url})")

# --- Show dashboard if logged in ---
else:
    st.success("✅ You are logged in!")
    show_dashboard()

    # Logout button (Streamlit only)
    if st.button("Logout (Streamlit)"):
        st.session_state.token = None
        st.query_params.clear()

   
 

    
