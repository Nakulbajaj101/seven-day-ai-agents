import asyncio
import os

from pydantic_ai import Agent

# Mock/Minimal Agent Setup
# We don't need the full RAG setup to test history retention.
# We just need to verify that 'message_history' is correctly passed and used by pydantic_ai.

async def test_history_persistence():
    print("1. Initializing Agent...")
    agent = Agent(
        name="HistoryTester",
        model="gpt-4o-mini",
        instructions="You are a helpful assistant. You remember what the user says."
    )
    
    # Simulate Session State
    conversation_history = []
    
    # Turn 1
    print("\n2. Turn 1: User introduces themselves.")
    user_input_1 = "Hi, my name is Antigravity."
    result_1 = await agent.run(user_input_1)
    
    print(f"   User: {user_input_1}")
    # print(f"   Agent: {result_1.data}")
    # Handle response attribute differences
    if hasattr(result_1, 'data'):
        print(f"   Agent: {result_1.data}")
    elif hasattr(result_1, 'output'):
        print(f"   Agent: {result_1.output}")
    else:
        print(f"   Agent: {str(result_1)}")
    
    # Update History
    conversation_history.extend(result_1.new_messages())
    print(f"   History length: {len(conversation_history)} messages.")

    # Turn 2
    print("\n3. Turn 2: User asks for their name (testing memory).")
    user_input_2 = "What is my name?"
    
    # CRITICAL STEP: Passing the history
    result_2 = await agent.run(user_input_2, message_history=conversation_history)
    
    print(f"   User: {user_input_2}")
    # print(f"   Agent: {result_2.data}")
    if hasattr(result_2, 'data'):
        content = result_2.data
    elif hasattr(result_2, 'output'):
        content = result_2.output
    else:
        content = str(result_2)
    print(f"   Agent: {content}")
    
    # Assertions
    assert "Antigravity" in content, "Agent failed to remember the name from history!"
    print("\n✅ SUCCESS: Agent successfully recalled information from previous turn.")

if __name__ == "__main__":
    if "OPENAI_API_KEY" not in os.environ:
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        exit(1)
        
    asyncio.run(test_history_persistence())
