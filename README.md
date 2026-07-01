# GitDigest

> Turn any public GitHub repository into a professional PDF report in seconds.

**Live demo:** https://fauz-del.github.io/Gitdigest-/

---

## What it does

GitDigest connects to a public GitHub repository, analyzes its commit history, and generates a downloadable PDF report containing:

- **Repository overview** — description, language, stars, forks, open issues
- **Contributor activity** — visual bar chart showing commit distribution across all contributors
- **Commit history** — the 50 most recent commits with author, timestamp, and message
- **Bus Factor analysis** — flags any contributor who authored 80%+ of commits as a knowledge concentration risk, with plain-English recommendations
- **Risk summary** — overall health assessment with actionable insights for engineering leads

## Why it exists

Engineering managers spend hours every week manually compiling repository status updates for non-technical stakeholders. GitDigest automates that translation — from raw commit data into a document anyone can read and act on.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Tailwind CSS, Vite |
| Backend | Python, FastAPI, PyGithub |
| PDF generation | ReportLab |
| Hosting (frontend) | GitHub Pages |
| Hosting (backend) | Railway |

---

## Running locally

### Backend
```bash
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `localhost:5173` in your browser.

---

## Security

- GitHub tokens are **never stored** — passed per-request and used only to read public repo data
- Only `public_repo` read scope is required
- No database, no user accounts, no logging of tokens or repo contents

---

## How the Bus Factor works

The Bus Factor measures how many contributors a project critically depends on. GitDigest calculates what percentage of total commits each contributor authored:

- **80%+ → High Risk** — if this person becomes unavailable, critical parts of the codebase may be difficult to maintain
- **50–79% → Watch** — not critical yet, but knowledge sharing should be prioritized
- **Below 50% → Healthy** — knowledge is well distributed

---

## Roadmap (v2)

- [ ] Code churn detection — files rewritten repeatedly signal unstable design
- [ ] Stale branch tracking — branches untouched for 60+ days
- [ ] Date range filtering — analyze specific time windows
- [ ] Support for organization-level reports

---

## Author

Built by [@fauz-del](https://github.com/fauz-del)

