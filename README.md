## JobFitIndex – Anti-Portfolio AI-Native

JobFitIndex è un “anti-portfolio” AI-native: invece di mostrare job title e CV statici, usa un’intervista guidata dall’AI per far emergere come pensi, come prendi decisioni, come gestisci fallimenti e dove generi più valore. Il risultato è un profilo narrativo e interattivo, pensato per un mondo in cui l’AI è data per scontata.

***

## 1. Requisiti

- Python 3.10+  
- pip (gestore pacchetti Python)  
- Git installato (opzionale ma consigliato)  
- Una chiave API di **OpenRouter** (con almeno qualche credito) per accedere ai modelli LLM.

***

## 2. Installazione

### 2.1. Clona il repository

```bash
git clone https://github.com/tommasofacchin/job-fit-index.git
cd jobfitindex
```

Se preferisci, puoi anche scaricare lo ZIP da GitHub e scompattarlo.

### 2.2. Crea ed attiva un virtual environment (consigliato)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2.3. Installa le dipendenze

Assicurati di avere un `requirements.txt` (es. con `streamlit`, `requests`, `sqlite3` integrato in Python, ecc.), poi:

```bash
pip install -r requirements.txt
```

***

## 3. Configurazione LLM (OpenRouter)

### 3.1. Crea un’API key su OpenRouter

1. Vai su https://openrouter.ai  
2. Crea un account e genera una **API key** (`sk-or-...`).[1]
3. Aggiungi eventualmente crediti (es. 10$) per ottenere più richieste giornaliere sui modelli `:free`.[2][3]

### 3.2. Configura i secrets di Streamlit

Crea (o modifica) il file `.streamlit/secrets.toml` nella root del progetto:

```toml
LLM_API_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL   = "meta-llama/llama-3.3-8b-instruct:free"
LLM_API_KEY = "sk-or-..."
```

Puoi cambiare modello con un altro `:free` supportato da OpenRouter.[4][5]

***

## 4. Struttura del progetto

Le parti principali dell’app:

- `app/llm/client.py`  
  Wrapper per chiamare l’API OpenRouter in stile OpenAI (chat completions).

- `app/llm/plan.py`  
  Genera i **piani di intervista** (sequenza di domande) a partire dal profilo del ruolo.

- `app/llm/questions.py`  
  Prende il piano e genera le domande concrete, in un’unica call batch al modello.

- `app/llm/judge.py`  
  Valuta le risposte del candidato e produce lo **score** + **signature summary** (impronta professionale).

- `app/db/roles.py`, `app/db/plans.py`, `app/db/evaluations.py`  
  Gestiscono il database SQLite (`jobfit.db`): ruoli, piani per ruolo, interviste/evaluations.

- `pages/0_Role_setup.py`  
  UI per definire/gestire i **ruoli** (company, title, contesto, must-have, red flags, numero domande).

- `pages/1_Interview.py`  
  UI per l’intervista vera e propria (chat-style): il candidato risponde alle domande generate da JobFitIndex.

- `pages/2_Score_Report.py`  
  UI per vedere gli **score report**, il breakdown dei criteri e scaricare l’anti-portfolio in formato Markdown.

***

## 5. Avvio dell’app

Dalla root del progetto (con virtual env attivo):

```bash
streamlit run Home.py
```

Streamlit aprirà automaticamente il browser su `http://localhost:8501`.

***

## 6. Come usare JobFitIndex

### 6.1. Creare un ruolo (Role Setup)

1. Vai alla pagina **“Role setup”** (0_Role_setup).  
2. Clicca **“Create new role”**: i campi vengono azzerati.  
3. Compila:
   - Company name  
   - Role title  
   - Context (team, prodotto, incertezza, ecc.)  
   - Minimum years of experience  
   - Degree required (No / Bachelor / Master / PhD)  
   - Key tools / technologies  
   - Must-have behaviors / skills  
   - Nice-to-have skills  
   - Red flags  
   - Number of questions to ask (es. 5–10)  
4. Clicca **“Save role profile”**.  
   - Il ruolo viene salvato in `jobfit.db`.  
   - Viene generato e salvato un **interview plan** AI-based per quel ruolo (sequenza di focus/typo di domanda).

Puoi creare più ruoli (es. Data/ML Engineer, Product Designer, Growth Marketer) e selezionarli dalla colonna sinistra.

### 6.2. Lanciare un’intervista

1. Vai alla pagina **“Interview”** (1_Interview).  
2. Seleziona un **ruolo** dalla lista.  
3. Compila le **info base candidato**:
   - Full name  
   - Email  
   - Phone number  
   - Years of experience  
   - Tools usati  
4. Clicca **“Start interview”**.

L’app:

- carica il piano di intervista per quel ruolo,  
- genera le domande con una chiamata batch al modello,  
- presenta le domande una alla volta, con input:
  - testo libero (open)  
  - scelta multipla (mcq)  
  - scala 1–10 (scale)

Per ogni risposta:

- viene aggiornato lo stato (`st.session_state["answers"]`),  
- al termine viene chiamato il modulo `judge` per valutare e sintetizzare le risposte.

### 6.3. Vedere lo score e generare l’anti-portfolio

1. Vai alla pagina **“Score Report”** (2_Score_Report).  
2. Nella colonna sinistra, seleziona una **evaluation** (intervista completata).  
3. Nella colonna destra vedi:
   - dati candidato,  
   - score totale (0–100),  
   - breakdown sui 5 criteri:
     - Evidence density  
     - Decision quality  
     - Failure intelligence  
     - Context translation  
     - Uniqueness signal  
   - Signature summary (impronta professionale generata dall’AI).

In fondo, trovi il bottone per scaricare l’**anti-portfolio** in formato Markdown:

```python
st.download_button(
    label="Scarica anti-portfolio (.md)",
    data=md,
    file_name=f"jobfitindex_anti_portfolio_{ev['candidate_name'] or 'candidate'}.md",
    mime="text/markdown",
)
```

Questo file `.md` è uno dei deliverable richiesti: un anti-portfolio AI-native generato direttamente dal tool.

***
