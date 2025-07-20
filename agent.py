
from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from tools import tools
from prompts import prompt_amazon_review



# Load environment variables from .env file
load_dotenv()

# Define the model
model = init_chat_model(
    # "anthropic:claude-3-7-sonnet-latest",
    "google_genai:gemini-2.5-flash",
    temperature=0
)
# model = ChatOpenAI(temperature=0, streaming=True)

# Create the ReAct agent
runnable = create_react_agent(model, tools, prompt=prompt_amazon_review())
