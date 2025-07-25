from agent import runnable

# Initialize a list to store the conversation history
messages = []

while True:
    prompt = input("You: ")
    if prompt.lower() in ["exit", "quit"]:
        break
    
    # Use the existing history for the invocation
    response = runnable.invoke({"messages": messages + [("user", prompt)]})
    
    # The response contains the new state of the conversation.
    # We update our history to reflect this.
    messages = response["messages"]
    
    # The last message is the assistant's reply
    assistant_response = messages[-1].content
    print(f"Assistant: {assistant_response}")