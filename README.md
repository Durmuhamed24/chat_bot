# DeepSeek Chat Bot

This project follows the practical work in the PDF and implements a stateful chatbot with Chainlit and the OpenAI Agents SDK.

## Setup

1. Create a `.env` file from `.env.example`.
2. Put your DeepSeek API key into `DEEPSEEK_API_KEY`.
3. Install dependencies with `uv sync` or `python3 -m pip install -r requirements.txt`.
4. Start the app with `uv run chainlit run main.py -w` or `chainlit run main.py -w`.

## Notes

- The chatbot keeps chat history in the current Chainlit session.
- The API key is read from the environment and is not hardcoded.
- You can switch models by setting `DEEPSEEK_MODEL`.
- Tool calling is included for time, profile, and calculator examples.
- Billing and refund prompts are routed through handoff agents.
# chat_bot
