---
title: Advanced Account Management System
app_file: app.py
sdk: gradio
sdk_version: 5.14.0
---

# Advanced Account Management System

The **SDE_team project** is not just another app — it is a fully agentic AI system architected by the SDE_team collective. Every component, from orchestration to reproducibility, has been designed to showcase how autonomous agents can collaborate, delegate tasks, and generate meaningful outputs in real-world workflows. This project embodies the team’s vision of building scalable, intelligent, and reliable AI agents that can transform data and software engineering practices.  

By combining **crewAI**, modern frameworks, and reproducible environments, SDE_team demonstrates how agent-based systems can move beyond prototypes into production-ready solutions. It is both a technical showcase and a creative statement: proof that AI agents, when thoughtfully designed, can work together like a true team.


## ✨ Features
- Multi-agent orchestration with **crewAI**
- Configurable agents and tasks via YAML files
- Reproducible workflows using **UV** for dependency management
- Hugging Face Space integration with **Gradio** UI
- Scalable and reliable solutions for data & software engineering

---

## Usage

1. **Create Account**: Start by creating an account with an initial deposit.
2. **Manage Funds**: Deposit or withdraw money as needed.
3. **Trade Stocks**: Enter stock symbols and quantities to buy or sell shares.
4. **Monitor Portfolio**: Check your current holdings, total value, and profit/loss.
5. **Review History**: Access a complete log of all transactions.

## Technology Stack

- **Frontend**: Gradio (for the web interface)
- **Backend**: Python with custom account management classes
- **Data**: Real-time stock prices via external API integration
- **Deployment**: Hugging Face Spaces

## 📦 Installation
Ensure you have **Python >=3.10, <3.14** installed.

1. Install [uv](https://github.com/astral-sh/uv):
   ```bash
   pip install uv
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/Shakhthi/sde_team.git
   cd sde_team
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

(Optional) Lock dependencies:
   ```bash
   crewai install
   ```

---

## ⚙️ Configuration
- Add your `OPENAI_API_KEY` to a `.env` file.
- Define agents in `src/sde_team/config/agents.yaml`.
- Define tasks in `src/sde_team/config/tasks.yaml`.
- Customize logic/tools in `src/sde_team/crew.py`.
- Add custom inputs in `src/sde_team/main.py`.

---

## ▶️ Running the Project
Start your crew of AI agents:
```bash
crewai run
```

This will initialize the **SdeTeam Crew** and execute tasks as defined in your configuration.  
By default, it generates a `report.md` with research on LLMs.

---

## 🧠 Understanding Your Crew
- Agents are defined in `config/agents.yaml` with unique roles and tools.
- Tasks are defined in `config/tasks.yaml` to guide collaboration.
- The crew executes tasks collectively, producing reproducible outputs.

---


## 📜 License
This project is open-source under the MIT License.

---

**Let’s create wonders together with the power and simplicity of crewAI.**


This README highlights your project’s purpose, setup, and usage in a recruiter/client-friendly way while staying concise and professional.  

Would you like me to also craft a **short tagline + badges section** (e.g., Python version, Hugging Face Space link, build status) so your README looks visually engaging at the top?



## Deployment

This app is configured for deployment on Hugging Face Spaces. The `app.py` file serves as the entry point, and dependencies are listed in `requirements.txt`.

## 🤝 Support
- 📖 Documentation [(github.com in Bing)](https://www.bing.com/search?q="https%3A%2F%2Fgithub.com%2FShakhthi%2Fsde_team%2Fwiki")
- 💬 Join our Discord community
- 🛠️ Open issues or pull requests on GitHub

---

## 📬 Contact

Recruiters or anyone interested in collaborating are always welcome to reach out:

- **Email:** [MK](sakthikaliappan7797.com)  
- **LinkedIn:** [Mathanbabu Kaliappan](https://www.linkedin.com/in/mathanbabu-kaliappan-58b7171a3/)
- **Gradio app:** [MK's Alter Ego]( https://huggingface.co/spaces/Shakhthi/sde_team_agent) 

Happy to chat about opportunities, ideas, or feedback on this project – let’s connect!
Happy hacking!

**– MK**
