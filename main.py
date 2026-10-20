from ai_agent.agent import AIAgent


def run_cli() -> None:
    agent = AIAgent()

    print("AI Agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        print("Agent: ")
        response = agent.run(user_input)
        print(response)


if __name__ == "__main__":
    run_cli()
