> This is a 48-hour Cosmico hackathon project, not a finished product, so expect a functional prototype rather than a polished production app. The current version focuses on showcasing the core AI-native interview and anti-portfolio concept. 

---

# 🚀 JobFitIndex: AI-Native Anti-Portfolio

JobFitIndex is an AI-native "anti-portfolio": instead of displaying static job titles and CVs, it uses an AI-guided interview to reveal how you think, how you make decisions, how you handle failures, and where you generate the most value. The result is a narrative, interactive profile designed for a world where AI is taken for granted. 

***

## 🔒 Requirements

- Python 3.10+  
- pip (Python package manager)  
- Git installed (optional but recommended)  
- An **OpenRouter** API key (with at least some credits) to access LLM models. 

***

## 📦 Installation

### Clone the repository

```bash
git clone https://github.com/tommasofacchin/job-fit-index.git
cd job-fit-index
```

Alternatively, you can download the ZIP from GitHub and extract it. 

### Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### Install dependencies

Make sure you have a `requirements.txt` (e.g., with `streamlit`, `requests`, `sqlite3` built into Python, etc.), then:

```bash
pip install -r requirements.txt
```

***

## 🤖 LLM Configuration (OpenRouter)

### Create an API key on OpenRouter

1. Go to https://openrouter.ai  
2. Create an account and generate an **API key** (`sk-or-...`).  

### Configure Streamlit secrets

Create (or edit) the `.streamlit/secrets.toml` file in the project root:

```toml
LLM_API_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL   = "meta-llama/llama-3.3-8b-instruct:free"
LLM_API_KEY = "sk-or-..."
```

You can change the model to another `:free` model supported by OpenRouter. 

***

## 🏗️ Project Structure

```
├─ Home.py                    # Streamlit main entrypoint (landing + navigation)
├─ app/
│   ├─ __init__.py            # Package marker
│   ├─ llm/
│   │   ├─ client.py          # OpenRouter client, OpenAI-style chat completions [web:1]
│   │   ├─ plan.py            # Build AI interview plans from role profile [web:1]
│   │   ├─ questions.py       # Batch-generate concrete questions from the plan [web:1]
│   │   └─ judge.py           # Score answers + build signature summary (anti-portfolio core) [web:1]
│   └─ db/
│       ├─ roles.py           # CRUD for roles (company, title, context, must-haves, etc.) [web:1]
│       ├─ plans.py           # Persisted interview plans per role [web:1]
│       └─ evaluations.py     # Interviews, answers, and final evaluations storage [web:1]
├─ pages/
│   ├─ 0_Role_setup.py        # Define/manage roles and generate AI interview plans [web:1]
│   ├─ 1_Interview.py         # Run the AI-guided interview (chat-style UI) [web:1]
│   └─ 2_Score_Report.py      # Score breakdown + Markdown anti-portfolio export [web:1]
├─ jobfit.db                  # SQLite database (auto-created at runtime) [web:1]
├─ requirements.txt           # Python dependencies (Streamlit, requests, etc.) [web:1]
└─ README.md                  # Project description and usage guide [web:1]
```

***

## 🏃 Running the App

From the project root (with the virtual environment activated):

```bash
streamlit run Home.py
```

Streamlit will automatically open your browser at `http://localhost:8501`. 

***

## 🧪 How to Use JobFitIndex

### Creating a Role (Role Setup)

- Go to the **"Role setup"** page (0_Role_setup).  
- Click **"Create new role"**.  
- Fill in role details (company, role title, context, experience, degree, tools, must-haves, nice-to-haves, red flags, number of questions).  
- Click **"Save role profile"** to store the role and generate an AI-based interview plan. 

### Conducting an Interview

- Go to the **"Interview"** page (1_Interview).  
- Select a role.  
- Enter candidate info (name, email, phone, years of experience, tools used).  
- Click **"Start interview"** to generate and present questions (open text, multiple choice, 1–10 scale) one by one, storing answers in the session state and evaluating them at the end. 

### Viewing the Score and Generating the Anti-Portfolio

- Go to the **"Score Report"** page (2_Score_Report).  
- Select a completed **evaluation**.  
- View candidate data, total score (0–100), breakdown on 5 criteria (Evidence density, Decision quality, Failure intelligence, Context translation, Uniqueness signal), and the AI-generated signature summary.  
- Use the **Download anti-portfolio (.md)** button to export the AI-native anti-portfolio in Markdown format.   
