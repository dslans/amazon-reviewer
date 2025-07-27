
import streamlit as st
from single_agent import runnable
from st_copy_to_clipboard import st_copy_to_clipboard
import json

# # --- Google OAuth2 Auth Setup ---
# from streamlit_oauth import OAuth2Component


# # Load Google OAuth2 credentials from .env using load_dotenv
# from dotenv import load_dotenv
# import os
# load_dotenv()
# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
# GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
# GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
# GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


# # Load allowed emails from YAML config
# import yaml
# AUTH_USERS_PATH = os.path.join(os.path.dirname(__file__), '../terraform/auth_users.yaml')
# def load_allowed_emails():
#     try:
#         with open(AUTH_USERS_PATH, 'r') as f:
#             data = yaml.safe_load(f)
#         # Extract just the email part (after 'user:')
#         return set(u.split(':',1)[1] for u in data.get('invoker_users', []) if u.startswith('user:'))
#     except Exception as e:
#         st.error(f"Failed to load allowed users: {e}")
#         return set()
# ALLOWED_EMAILS = load_allowed_emails()

# oauth2 = OAuth2Component(
#     GOOGLE_CLIENT_ID,
#     GOOGLE_CLIENT_SECRET,
#     GOOGLE_AUTH_URL,
#     GOOGLE_TOKEN_URL
# )

# def get_user_email(token):
#     import requests
#     if not token or "access_token" not in token:
#         return None
#     resp = requests.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"})
#     if resp.status_code == 200:
#         return resp.json().get("email")
#     return None

# # --- Auth Flow ---
# if "token" not in st.session_state:
#     st.session_state.token = None
# if "user_email" not in st.session_state:
#     st.session_state.user_email = None

# if not st.session_state.token:
#     token = oauth2.authorize_button(
#         "Login with Google",
#         "openid email profile",
#         GOOGLE_USERINFO_URL,
#         key="google_oauth"
#     )
#     if token:
#         st.session_state.token = token
#         st.session_state.user_email = get_user_email(token)
#         st.experimental_rerun()
#     st.stop()
# elif not st.session_state.user_email:
#     st.session_state.user_email = get_user_email(st.session_state.token)
#     if not st.session_state.user_email:
#         st.warning("Could not fetch your email. Please try logging in again.")
#         st.session_state.token = None
#         st.stop()

# if st.session_state.user_email not in ALLOWED_EMAILS:
#     st.error(f"Access denied. Your email ({st.session_state.user_email}) is not authorized.")
#     if st.button("Logout"):
#         st.session_state.token = None
#         st.session_state.user_email = None
#         st.experimental_rerun()
#     st.stop()

# if st.button("Logout"):
#     st.session_state.token = None
#     st.session_state.user_email = None
#     st.experimental_rerun()


st.set_page_config(page_title="Amazon Review Assistant")
st.title("Amazon Review Assistant")
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
        st.session_state.last_review
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
        content = content[len("```json"):].strip()
    if content.startswith("```"):
        content = content[len("```"):].strip()
    if content.endswith("```"):
        content = content[:-len("```")].strip()
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
