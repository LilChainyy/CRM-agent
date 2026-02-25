from dotenv import load_dotenv

load_dotenv()

from tools.linkedin_tool import init_linkedin
from agent.agent import create_crm_agent


def main():
    print("Loading LinkedIn connections...")
    init_linkedin()

    print("Initializing CRM agent...")
    agent = create_crm_agent()

    print("\nCRM Agent ready! Ask questions about your emails and LinkedIn connections.")
    print("Type 'quit' or 'exit' to stop.\n")

    thread_config = {"configurable": {"thread_id": "crm-session"}}

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=thread_config,
            )
            # Get the last AI message from the result
            messages = result["messages"]
            for msg in reversed(messages):
                if hasattr(msg, "type") and msg.type == "ai" and msg.content:
                    print(f"\nAssistant: {msg.content}\n")
                    break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
