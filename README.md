Secure Document and Resume Analysis API

<p align="center">
  <strong>A secure, interactive resume analysis platform for smarter job applications.</strong>
  <br>
  Upload a resume, analyze job requirements, identify skill gaps, and explore actionable insights through a modern web interface.
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react" alt="React">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Pytest-Tested-0A9EDC?logo=pytest" alt="Pytest">
</p>

---

Overview

The Secure Document and Resume Analysis API is a full-stack application that evaluates resumes against job descriptions and generates structured reports to help candidates understand their suitability for a particular role.

Users can upload resumes in PDF, DOCX, or TXT format, provide a job description, and receive insights into matching skills, missing skills, relevant experience, supporting evidence, and important keywords.

The application combines a FastAPI backend with a React frontend, database-backed analysis history, and security-focused document handling.

The analysis engine is rule-based and evaluated. It does not use an LLM.

Key Highlights

* Resume parsing and structured information extraction.
* Rule-based resume-to-job-description matching.
* Matched and missing skill identification.
* Estimated years of professional experience.
* Evidence lines extracted from resumes.
* Identification of repeated job-description keywords missing from resumes.
* User authentication and protected resources.
* Document validation, retention, and deletion controls.
* Automated testing and a skill-extraction evaluation framework.
* Responsive frontend with interactive analysis reports.

---

Features

📄 Resume Parsing

* Upload resumes in PDF, DOCX, and TXT formats.
* Extract readable text from supported documents.
* Identify relevant skills and experience.
* Extract evidence lines to support analysis results.
* Validate uploaded files before processing.

🎯 Job Description Matching

* Compare resume skills with job requirements.
* Identify matching and missing skills.
* Estimate relevant years of experience.
* Detect repeated keywords in job descriptions that are absent from resumes.
* Generate a structured report for further review.

📊 Interactive Dashboard

* Modern, responsive user interface.
* Improved resume upload workflow.
* Interactive analysis results and skill indicators.
* Clear presentation of matching and missing skills.
* Access to previous analyses.
* Responsive layouts for desktop, tablet, and mobile screens.

🔐 Authentication and Data Protection

* User registration and login.
* Password hashing and token-based authentication.
* Protected API endpoints.
* Document upload validation and size limits.
* Rate limiting.
* Privacy-conscious logging.
* Configurable document retention.
* Deletion of expired documents and associated analyses.

🧪 Testing and Evaluation

* Automated backend tests using Pytest.
* Test coverage reporting.
* Skill-extraction evaluation framework.
* Support for PostgreSQL-based testing.
* GitHub Actions workflow support.

Important: The match score is a rule-based estimate of resume alignment. It does not guarantee interview shortlisting or hiring success.

---

Technology Stack

Category	Technologies
Programming Language	Python 3.12
Backend Framework	FastAPI
Frontend	React, Vite, JavaScript, CSS
Database	PostgreSQL, SQLite
ORM	SQLAlchemy 2
Data Validation	Pydantic 2
PDF Parsing	pypdf
DOCX Parsing	python-docx
Authentication	JWT-based authentication and password hashing
API Architecture	REST API
Containerization	Docker, Docker Compose
Testing	Pytest, pytest-cov
Linting	Ruff
CI/CD	GitHub Actions
Version Control	Git, GitHub

---

## 📸 Application Preview

### 🔐 Login Page

A clean and modern authentication interface for secure access to the resume analysis platform.

![resumeIQ Login Page](docs/screenshots/login.png)

### 🏠 Interactive Dashboard

Upload your resume, enter a job description, and initiate the analysis workflow through an intuitive dashboard.

![resumeIQ Dashboard](docs/screenshots/dashboard.png)

### 📊 Resume Analysis Report

Explore your estimated match score, matched skills, missing skills, experience estimation, and supporting resume evidence.

![resumeIQ Analysis Report](docs/screenshots/analysis-report.png)

---



Architecture

                         ┌──────────────────────┐
                         │         User         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    React Frontend    │
                         │  Vite + Responsive UI│
                         └──────────┬───────────┘
                                    │
                               REST API
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         ├──────────────────────┤
                         │ Authentication       │
                         │ Document Management  │
                         │ Resume Parsing       │
                         │ Skill Extraction     │
                         │ Experience Analysis  │
                         │ Keyword Matching     │
                         │ Report Generation    │
                         │ Security Controls    │
                         └──────────┬───────────┘
                                    │
                          ┌─────────┴─────────┐
                          ▼                   ▼
                 ┌────────────────┐  ┌────────────────┐
                 │    Database    │  │ Document Store │
                 │ PostgreSQL /   │  │ Uploaded Files │
                 │ SQLite         │  │                │
                 └────────────────┘  └────────────────┘

How It Works

1. A user registers or logs in.
2. The user uploads a resume.
3. The backend validates the document and extracts its text.
4. The user submits a job description.
5. The analysis engine extracts relevant skills, experience, and keywords.
6. Resume information is compared with job requirements.
7. The system generates a structured analysis report.
8. The report is saved and can be retrieved through analysis history.
9. Document retention policies govern how long stored files and analyses remain available.

---

Project Structure

resume-analyzer/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── analyses.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── rate_limit.py
│   │   ├── data/
│   │   │   └── skills.json
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   ├── evaluation/
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── docs/
│   ├── architecture.md
│   ├── database-schema.md
│   ├── api-endpoints.md
│   ├── input-validation.md
│   ├── security.md
│   ├── test-cases.md
│   ├── evaluation.md
│   └── known-limitations.md
│
├── .github/
│   └── workflows/
├── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md

---

Getting Started

Prerequisites

Install the following tools:

* Python 3.12.
* Node.js and npm.
* Git.
* Docker and Docker Compose, if using the containerized setup.

VS Code is recommended for development.

Option A: Run with Docker

This setup is intended to run the application with PostgreSQL and a containerized frontend.

1. Clone the repository

git clone https://github.com/shanu454/resume-analyzer.git
cd resume-analyzer

Replace the repository URL if your GitHub repository uses a different name.

2. Configure environment variables

cp .env.example .env

Edit .env and configure a strong SECRET_KEY and POSTGRES_PASSWORD.

3. Start the application

docker compose up --build

4. Open the application

* Frontend: http://localhost:8080
* API through the frontend proxy: /api

The Docker configuration is intended to provide a production-like local environment. Actual deployment readiness depends on the application’s configuration and security review.

To stop the containers:

docker compose down

To stop the containers and remove the associated Compose-managed volumes:

docker compose down -v

Warning: Removing volumes can permanently delete local database data. Back up anything important first.

---

Option B: Local Development

This setup uses SQLite by default and does not require Docker or a separate PostgreSQL server.

1. Clone the Repository

git clone https://github.com/shanu454/resume-analyzer.git
cd resume-analyzer

If you already have the project, open its root directory in VS Code.

2. Set Up the Backend

From the project root:

cd backend
python3 -m venv .venv
source .venv/bin/activate

On Windows, activate the environment with:

.venv\Scripts\Activate.ps1

Install development dependencies:

pip install -r requirements-dev.txt

Create the local environment file:

cp .env.example .env

Review the environment settings before starting the application.

3. Start FastAPI

Run this command from the backend directory:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

The API should be available at:

Resource	URL
API server	http://127.0.0.1:8000
Interactive API documentation	http://127.0.0.1:8000/docs
Health check	http://127.0.0.1:8000/health

The health endpoint is available only if implemented in the current application.

Keep this terminal running.

4. Start the React Frontend

Open a second terminal and navigate to the frontend directory.

From the project root:

cd frontend

Install dependencies:

npm install

Start Vite:

npm run dev

Open:

http://localhost:5173

The Vite development server proxies API requests under /api to the backend on port 8000, according to the frontend configuration.

Important: Both the backend and frontend must be running for login, uploads, and resume analysis to work.

5. Use PostgreSQL Locally (Optional)

To use PostgreSQL instead of SQLite, configure DATABASE_URL in backend/.env:

DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dbname

Replace the sample credentials and database name with your actual PostgreSQL configuration.

Ensure the appropriate PostgreSQL driver is installed and the database exists before starting the backend.

---

Testing, Linting, and Evaluation

Run these commands from the backend directory.

Run Automated Tests

pytest

Run Tests with Coverage

pytest --cov=app

The project currently documents a suite of 95 tests. The actual test count and results should be verified against the current repository.

Run Ruff

ruff check .

Evaluate Skill Extraction

python -m evaluation.evaluate

This runs the project’s skill-extraction evaluation workflow.

Run Tests Against PostgreSQL

TEST_DATABASE_URL=postgresql+psycopg2://user:pass@localhost/test_db pytest

Replace the connection details with a dedicated test database.

Caution: Use a disposable test database, not a production database.

---

API Endpoints

The backend exposes REST endpoints for authentication, document management, and analysis.

Method	Endpoint	Description
POST	/auth/register	Register a user
POST	/auth/login	Authenticate a user
GET	/auth/me	Retrieve the authenticated user’s profile
GET	/documents	List accessible documents
POST	/documents	Upload a resume
DELETE	/documents/{id}	Delete a document
POST	/analyses	Create an analysis
GET	/analyses	Retrieve analysis history
GET	/analyses/{id}	Retrieve an individual report
DELETE	/analyses/{id}	Delete an analysis

Consult the live API documentation for exact request schemas, response formats, and authentication requirements:

http://127.0.0.1:8000/docs

The endpoint list above should be checked against the current implementation before use.

---

Configuration

The project uses environment variables to configure the backend.

Variable	Default	Description
ENVIRONMENT	dev	Application environment
DATABASE_URL	sqlite:///./dev.db	SQLAlchemy database connection
SECRET_KEY	Development value	Secret used for signing authentication tokens
RETENTION_DAYS	30	Retention period for uploads and associated analyses
MAX_UPLOAD_BYTES	5242880	Maximum upload size in bytes
UPLOAD_DIR	./uploads	Document storage directory
RATE_LIMIT_ENABLED	true	Enables in-memory rate limiting
CORS_ORIGINS	http://localhost:5173	Comma-separated allowed origins

These defaults describe the documented configuration. Check .env.example and the backend configuration module for the exact names, supported values, and actual defaults.

Production Security

Before deploying publicly:

* Generate a strong, random secret key.
* Configure secure database credentials.
* Restrict CORS to trusted frontend origins.
* Use HTTPS.
* Review authentication and authorization behavior.
* Validate document storage permissions.
* Configure appropriate retention and deletion policies.
* Avoid exposing debug output or sensitive information.
* Review rate limiting and logging behavior.

---

Security Considerations

The application processes resumes containing personal and professional information.

Security controls include:

* Password hashing.
* Token-based authentication.
* Authorization for protected resources.
* File type and size validation.
* Input validation.
* Rate limiting.
* Privacy-conscious logging.
* Configurable document retention.
* Document and analysis deletion.

These controls should be verified through automated tests and security review before production deployment.

---

Evaluation Methodology

The analysis engine is rule-based and is designed to be evaluated using a labelled dataset.

Suggested evaluation measures include:

Metric	Purpose
Precision	Measures the relevance of extracted skills
Recall	Measures how many relevant skills are identified
F1-score	Balances precision and recall
Skill matching accuracy	Evaluates matching correctness
Processing time	Measures analysis performance

The evaluation dataset should include different document formats, technical domains, writing styles, and experience levels.

Reported metrics should come from actual evaluation runs rather than assumed results.

---

Known Limitations

* Rule-based matching may not fully understand semantic similarity.
* Skills expressed using unfamiliar synonyms may not be recognized.
* Scanned PDFs may require OCR support.
* Complex document layouts can affect text extraction.
* Estimated experience may be inaccurate when employment dates are ambiguous.
* Match scores do not guarantee recruitment outcomes.
* The analysis should support, not replace, human judgement.

---

Future Enhancements

Potential improvements include:

* Alembic database migrations.
* Redis-backed rate limiting.
* Sandboxed document parsing workers.
* OCR support for scanned resumes.
* Embedding-based matching compared with the rule-based engine.
* A larger labelled evaluation dataset.
* Downloadable analysis reports.
* More detailed skill-gap recommendations.
* Additional accessibility improvements.
* Cloud deployment with managed storage.

These are potential future improvements, not claims about existing functionality.

---

Documentation

Topic	Documentation
Architecture	docs/architecture.md
Database schema	docs/database-schema.md
API endpoints	docs/api-endpoints.md
Input validation	docs/input-validation.md
Security considerations	docs/security.md
Test cases	docs/test-cases.md
Evaluation methodology	docs/evaluation.md
Known limitations	docs/known-limitations.md

---

Development in VS Code

1. Open the project root directory in VS Code.
2. Select the Python interpreter from backend/.venv.
3. Install the recommended extensions.
4. Start FastAPI using the configured launch profile or terminal.
5. Start the frontend in a separate terminal.
6. Run backend tests from the Testing panel or terminal.

The repository’s existing VS Code configuration should be checked for the exact launch profile names.

---

Author

SK Shanu

B.Tech Computer Science and Engineering

Interests: Python Backend Development, Software Engineering, Cybersecurity, and Blockchain.

* GitHub: shanu454

---

License

Add the appropriate license to the repository before distributing the project.

If you choose the MIT License, include a LICENSE file containing the complete MIT license text.

---

<p align="center">
  <strong>Secure Document and Resume Analysis API</strong>
  <br>
  Building more transparent, secure, and useful resume analysis tools.
</p>