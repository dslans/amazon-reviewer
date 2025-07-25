from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph_supervisor import create_supervisor, create_handoff_tool
from langgraph.prebuilt import create_react_agent

from tools import tools
import prompts

# Load environment variables from .env file
load_dotenv()

# Define the model
model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0
)

# agents - specializations by product category
generic_agent = create_react_agent(model, tools, name="generic_agent", prompt=prompts.prompt_amazon_review('generic'))
electronics_agent = create_react_agent(model, tools, name="electronics_agent", prompt=prompts.prompt_amazon_review('electronics'))
books_agent = create_react_agent(model, tools, name="books_agent", prompt=prompts.prompt_amazon_review('books'))
clothing_agent = create_react_agent(model, tools, name="clothing_agent", prompt=prompts.prompt_amazon_review('clothing'))
home_appliances_agent = create_react_agent(model, tools, name="home_appliances_agent", prompt=prompts.prompt_amazon_review('home_appliances'))
toys_agent = create_react_agent(model, tools, name="toys_agent", prompt=prompts.prompt_amazon_review('toys'))
sports_agent = create_react_agent(model, tools, name="sports_agent", prompt=prompts.prompt_amazon_review('sports'))
health_beauty_agent = create_react_agent(model, tools, name="health_beauty_agent", prompt=prompts.prompt_amazon_review('health_beauty'))
automotive_agent = create_react_agent(model, tools, name="automotive_agent", prompt=prompts.prompt_amazon_review('automotive'))
grocery_agent = create_react_agent(model, tools, name="grocery_agent", prompt=prompts.prompt_amazon_review('grocery'))
pet_supplies_agent = create_react_agent(model, tools, name="pet_supplies_agent", prompt=prompts.prompt_amazon_review('pet_supplies'))
tools_agent = create_react_agent(model, tools, name="tools_agent", prompt=prompts.prompt_amazon_review('tools'))
garden_agent = create_react_agent(model, tools, name="garden_agent", prompt=prompts.prompt_amazon_review('garden'))
baby_products_agent = create_react_agent(model, tools, name="baby_products_agent", prompt=prompts.prompt_amazon_review('baby_products'))
musical_instruments_agent = create_react_agent(model, tools, name="musical_instruments_agent", prompt=prompts.prompt_amazon_review('musical_instruments'))
furniture_agent = create_react_agent(model, tools, name="furniture_agent", prompt=prompts.prompt_amazon_review('furniture'))

# proofreading agent
proofreading_agent = create_react_agent(model, tools, name="proofreading_agent", prompt=prompts.prompt_proofreading())

# insight grader 
insightfulness_grader_agent = create_react_agent(model, tools, name="insightfulness_grader_agent", prompt=prompts.insightfulness_grader_prompt())

# supervisor
workflow = create_supervisor(
    model=model,
    agents=[
        generic_agent,
        electronics_agent,
        books_agent,
        clothing_agent,
        home_appliances_agent,
        toys_agent,
        sports_agent,
        health_beauty_agent,
        automotive_agent,
        grocery_agent,
        pet_supplies_agent,
        tools_agent,
        garden_agent,
        baby_products_agent,
        musical_instruments_agent,
        furniture_agent,
        proofreading_agent,
        insightfulness_grader_agent
    ],
    tools=[
        create_handoff_tool(agent_name="generic_agent", name="assign_to_generic_agent", description="Assign task to generic agent"),
        create_handoff_tool(agent_name="electronics_agent", name="assign_to_electronics_agent", description="Assign task to electronics agent"),
        create_handoff_tool(agent_name="books_agent", name="assign_to_books_agent", description="Assign task to books agent"),
        create_handoff_tool(agent_name="clothing_agent", name="assign_to_clothing_agent", description="Assign task to clothing agent"),
        create_handoff_tool(agent_name="home_appliances_agent", name="assign_to_home_appliances_agent", description="Assign task to home appliances agent"),
        create_handoff_tool(agent_name="toys_agent", name="assign_to_toys_agent", description="Assign task to toys agent"),
        create_handoff_tool(agent_name="sports_agent", name="assign_to_sports_agent", description="Assign task to sports agent"),
        create_handoff_tool(agent_name="health_beauty_agent", name="assign_to_health_beauty_agent", description="Assign task to health and beauty agent"),
        create_handoff_tool(agent_name="automotive_agent", name="assign_to_automotive_agent", description="Assign task to automotive agent"),
        create_handoff_tool(agent_name="grocery_agent", name="assign_to_grocery_agent", description="Assign task to grocery agent"),
        create_handoff_tool(agent_name="pet_supplies_agent", name="assign_to_pet_supplies_agent", description="Assign task to pet supplies agent"),
        create_handoff_tool(agent_name="tools_agent", name="assign_to_tools_agent", description="Assign task to tools agent"),
        create_handoff_tool(agent_name="garden_agent", name="assign_to_garden_agent", description="Assign task to garden agent"),
        create_handoff_tool(agent_name="baby_products_agent", name="assign_to_baby_products_agent", description="Assign task to baby products agent"),
        create_handoff_tool(agent_name="musical_instruments_agent", name="assign_to_musical_instruments_agent", description="Assign task to musical instruments agent"),
        create_handoff_tool(agent_name="furniture_agent", name="assign_to_furniture_agent", description="Assign task to furniture agent"),
        create_handoff_tool(agent_name="proofreading_agent", name="assign_to_proofreading_agent", description="Assign task to proofreading agent"),
        create_handoff_tool(agent_name="insightfulness_grader_agent", name="assign_to_insightfulness_grader_agent", description="Assign task to insightfulness grader agent")
    ],
    prompt=prompts.supervisor_prompt(),
    add_handoff_messages=True
)
runnable = workflow.compile()
