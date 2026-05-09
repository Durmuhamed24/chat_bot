# DeepSeek Chat Bot 🤖

A stateful chatbot built with **Chainlit** and **OpenAI Agents SDK**, featuring intelligent agent-based conversations with tool calling capabilities.

## ✨ Features

- **Stateful Conversations** - Chat history preserved throughout your session
- **Multi-Agent System** - Specialized agents for billing, refunds, and general inquiries
- **Tool Integration** - Built-in tools for time, profile lookup, and calculations
- **Model Flexibility** - Easy model switching via environment variables
- **Secure API Keys** - Environment-based configuration without hardcoding
- **Mobile-Responsive** - Fully responsive design for all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- DeepSeek API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Durmuhamed24/chat_bot.git
   cd chat_bot
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your DeepSeek API key
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the chatbot**
   ```bash
   chainlit run main.py -w
   ```
   The app will open at `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

- `DEEPSEEK_API_KEY` - Your DeepSeek API key (required)
- `DEEPSEEK_MODEL` - Model name (default: `deepseek-chat`)

### Using UV (Alternative)
```bash
uv sync
uv run chainlit run main.py -w
```

## 📝 Project Structure

```
chat_bot/
├── main.py              # Main chatbot application
├── agents.py            # Agent definitions and configurations
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── chainlit.md          # Welcome screen
└── public/
    └── style.css        # Custom styling (mobile-responsive)
```

## 🛠️ Technical Details

- **Framework**: Chainlit for UI
- **AI SDK**: OpenAI Agents SDK
- **Model**: DeepSeek (configurable)
- **Style**: Custom responsive CSS with dark theme

### Agent Types

- **General Agent** - Main conversational agent
- **Billing Agent** - Handles billing inquiries
- **Refund Agent** - Manages refund requests

### Available Tools

- **Time Tool** - Current date and time
- **Profile Tool** - User profile information
- **Calculator Tool** - Mathematical calculations

## 🎨 Customization

- Edit `chainlit.md` to modify the welcome screen
- Update `public/style.css` for styling changes
- Configure agents and tools in `main.py`

## 📱 Mobile Support

The application is fully responsive and works seamlessly on:
- Desktop computers
- Tablets
- Mobile phones

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements!

## 📄 License

This project is open source and available under the MIT License.

## 💡 Notes

- Chat history is maintained per session (not persisted after logout)
- API calls are made securely through environment variables
- Tool calling examples demonstrate agent capabilities
- Agent handoffs enable sophisticated conversation routing

---

**Built with ❤️ using Chainlit and DeepSeek AI**
