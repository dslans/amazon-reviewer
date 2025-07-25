
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from tools import tools
from prompts import prompt_amazon_review

# Load environment variables from .env file
load_dotenv()

# Define the model
model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0
)

# Create the ReAct agent
valid_product_prompt = 'If the URL is not for an amazon product, inform the user that the review cannot be processed and ask for a valid Amazon product URL or name.'
single_agent_prompt = prompt_amazon_review(specialization='generic') + f'\n{valid_product_prompt}'
runnable = create_react_agent(model, tools, prompt=single_agent_prompt)

if __name__ == "__main__":
    print(single_agent_prompt)
