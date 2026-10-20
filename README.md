# AI Agent

A simple public Python AI agent that can:
- answer general questions
- use tools when needed
- perform safe math calculations
- fetch and summarize URL content
- run from the command line

## Features

- OpenAI Chat Completions integration
- JSON tool-calling pattern
- Safe calculator using Python AST validation
- URL fetcher with HTML stripping
- Local CLI for interactive use

## Project structure

```bash
.
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
└── ai_agent
    ├── __init__.py
    └── agent.py
```

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Iliketocode676767/ai-agent.git
cd ai-agent
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file:

```bash
cp .env.example .env
```

5. Add your API key:

```env
OPENAI_API_KEY=your_key_here
MODEL=gpt-4o-mini
```

6. Run the agent:

```bash
python main.py
```

## Example prompts

- "What is 48 * 7?"
- "Fetch https://example.com and summarize it"
- "Plan a 3-day trip to Tokyo on a budget"
- "Explain the difference between AI and machine learning"

## Notes

- The calculator tool is intentionally restricted to safe math operations only.
- URL fetching is limited to fetching content and stripping HTML for readability.
- This project is intended as a starting point for building more advanced agents.

## License

This project is released under the MIT License.
