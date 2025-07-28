import streamlit as st
from single_agent import runnable
from st_copy_to_clipboard import st_copy_to_clipboard
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os

# --- Configuration ---
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

# Determine if running in Cloud Run or locally
IS_CLOUD_RUN = os.environ.get("K_SERVICE") is not None

if IS_CLOUD_RUN:
    # In Cloud Run, read client secrets from environment variable (Secret Manager)
    CLIENT_SECRETS_CONTENT = os.environ.get("CLIENT_SECRETS_JSON")
    if not CLIENT_SECRETS_CONTENT:
        st.error("CLIENT_SECRETS_JSON environment variable not found. Cannot authenticate.")
        st.stop()
    # Create a temporary file to load secrets from content
    with open("temp_client_secret.json", "w") as f:
        f.write(CLIENT_SECRETS_CONTENT)
    CLIENT_SECRETS_FILE = "temp_client_secret.json"
    # For Cloud Run, the redirect URI is the service URL
    REDIRECT_URI = f"https://{os.environ['K_SERVICE']}-{os.environ['K_REVISION'].split('--')[0]}-{os.environ['K_SERVICE'].split('-')[-1]}.run.app"
else:
    # Locally, read client secrets from file
    CLIENT_SECRETS_FILE = "client_secret.json"
    if not os.path.exists(CLIENT_SECRETS_FILE):
        st.error(f"Error: {CLIENT_SECRETS_FILE} not found. Please download it from Google Cloud Console.")
        st.stop()
    REDIRECT_URI = "http://localhost:8501"

# --- Helper Functions ---
def get_flow():
    """Creates and returns a Flow object for the OAuth 2.0 process."""
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def get_credentials():
    """
    Checks for credentials in the session state.
    Returns Credentials object or None.
    """
    if 'credentials' not in st.session_state:
        return None
    
    credentials_dict = st.session_state['credentials']
    return Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict.get('refresh_token'),
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        scopes=credentials_dict['scopes']
    )

# --- Main App Logic ---
st.set_page_config(layout="wide")

# Check for authentication code in URL query params
query_params = st.query_params
if 'code' in query_params and 'credentials' not in st.session_state:
    code = query_params['code']
    flow = get_flow()
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    st.session_state['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Clear the query params from the URL
    st.query_params.clear()
    st.rerun()

# Get credentials from session state
credentials = get_credentials()

if not credentials:
    # If not logged in, show the login button
    st.title("Welcome to the Amazon Reviewer App")
    st.write("Please log in to continue.")
    
    flow = get_flow()
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    st.link_button("Login with Google", authorization_url)

else:
    # If logged in, show the main app
    st.title("Amazon Product Reviewer")
    st.write("Welcome! You are logged in.")
    
    # You can now use the credentials to make authenticated API calls
    # For example, to get user info:
    from googleapiclient.discovery import build
    
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        # st.write("Your email address is:", user_info['email'])
        # st.write("Your name is:", user_info.get('name', 'N/A'))
        
        # if user_info.get('picture'):
        #     st.image(user_info['picture'], width=100)
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Your credentials may have expired.")
        if st.button("Logout"):
            del st.session_state['credentials']
            st.rerun()

    # Add a logout button
    if st.button("Logout"):
        del st.session_state['credentials']
        st.rerun()

    st.subheader("What would you like to review? Enter product name or URL")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_review" not in st.session_state:
        st.session_state.last_review = None
    if "finalized" not in st.session_state:
        st.session_state.finalized = False


    # Show all prior messages, with copy button for assistant responses
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                st_copy_to_clipboard(message["content"])



    if not st.session_state.finalized:
        # Only show the intro prompt if there are no user messages yet
        chat_prompt = "Your response"
        if prompt := st.chat_input(chat_prompt):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = runnable.invoke({"messages": st.session_state.messages})
                review = response["messages"][-1].content
                st.markdown(review)
            st.session_state.messages.append({"role": "assistant", "content": review})
            st.session_state.last_review = review


        # Show finalize button only after the agent signals readiness
        show_finalize = False
        if (
            st.session_session.last_review
            and len(st.session_state.messages) > 1
            and st.session_state.messages[-1]["role"] == "assistant"
            and st.session_state.messages[-2]["role"] == "user"
            and not st.session_state.finalized
        ):
            last_content = st.session_state.messages[-1]["content"]
            if last_content.strip().endswith("---REVIEW IS READY---"):
                show_finalize = True
        if show_finalize:
            if st.button("Finalize Review"):
                st.session_state.finalized = True

    # When finalized, ask for JSON output
    if st.session_state.finalized:
        structured_prompt = (
            "You are an API backend. Respond ONLY with plain JSON, not in a code block, and do not add any commentary.\n"
            "Please provide the finalized review in JSON with the following fields:\n"
            "{\n"
            '  "title": "<short review title>",\n'
            '  "review": "<the main review text>",\n'
            '  "followup": ["<first follow-up question>", "<second follow-up question>"]\n'
            "}\n"
            f"Base your response on this review:\n{st.session_state.last_review}"
        )
        response = runnable.invoke({"messages": st.session_state.messages + [{"role": "user", "content": structured_prompt}]})
        content = response["messages"][-1].content.strip()
        # Remove code block markers if present
        if content.startswith("```json"):
            content = content[len("```json"):]
        if content.startswith("```"):
            content = content[len("```"):]
        if content.endswith("```"):
            content = content[:-len("```")]
        try:
            data = json.loads(content)
            # Display each part as a separate chat message
            with st.chat_message("assistant"):
                st.markdown(f"**Title:** {data['title']}")
                st_copy_to_clipboard(data["title"])
            with st.chat_message("assistant"):
                st.markdown(f"**Review:**\n{data['review']}")
                st_copy_to_clipboard(data["review"])
        except Exception:
            st.markdown(response["messages"][-1].content)
        st.session_state.finalized = False
        st.session_state.last_review = None
