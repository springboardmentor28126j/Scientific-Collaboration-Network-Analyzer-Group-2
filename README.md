# Scientific Collaboration Network Analyzer - Group 2

## Project Overview

The Scientific Collaboration Network Analyzer (SCNA) is a web-based platform designed to manage and analyze scientific research activities.

The system provides features for:

- User Authentication and Authorization
- Researchers
- Researcher Profiles
- User Settings
- Publications
- Citations
- Collaborations
- Conferences
- Institutions
- Notifications
- Reports and Exporting
- Research Network Analysis
- Dashboards
- Reviewer Dashboard
- User Management
- OTP Verification

---

# Implemented Modules

## 1. User Authentication

- User registration and login
- JWT-based authentication
- Role-based access control
- Supported user roles:
  - Researcher
  - Institution Admin
  - Reviewer
  - System Admin
- Session/local storage based authentication
- OTP verification

---

## 2. Researcher Management

Researchers can:

- Create researcher profiles
- View researcher profiles
- Edit researcher information
- Search researchers
- View research interests
- View skills
- View publications
- View collaboration information

### Researcher Profile

The researcher profile displays:

- First name
- Last name
- Biography
- Phone number
- Research experience
- Skills
- Research interests
- ORCID
- Google Scholar
- ResearchGate
- LinkedIn
- Publications

---

## 3. User Profile Dashboard

The user profile dashboard provides an overview of the logged-in researcher's information.

It displays:

- Researcher information
- Number of publications
- Number of citations
- Number of collaborators
- Biography
- Skills
- Research interests
- Social and research profiles
- Publications

### Frontend File

```text
frontend/src/pages/Profile.jsx
4. User Settings

The User Settings module allows authenticated researchers to manage and update their personal and research-related information.

Features
View account email
View user role
Update first name
Update last name
Update phone number
Update biography
Update research experience
Update skills
Update research interests
Update ORCID
Update Google Scholar profile
Update ResearchGate profile
Update LinkedIn profile
Frontend File
frontend/src/pages/Settings.jsx
5. Publications

The publication module allows researchers to manage their scientific publications.

Features
Create publications
View publications
Edit publications
Delete publications
Upload publication files
View publication details
Manage publication information
Associate publications with researchers
6. Citation Management

The citation module provides functionality for managing citation relationships between publications.

Features
Add citations
View citations
Manage citation relationships
Track citation information
Display citation statistics
7. Collaboration Management

The collaboration module allows researchers to connect and collaborate with other researchers.

Features
Search researchers
Send collaboration requests
Receive collaboration requests
Accept collaboration requests
Reject collaboration requests
View collaboration relationships
Manage collaboration status
8. Notifications

The notification module keeps users informed about important activities in the system.

Features
Collaboration request notifications
Notification status tracking
Read/unread notifications
Mark notifications as read
Delete notifications
Real-time notification support
WebSocket-based notifications
9. Conferences

The conference module allows users to manage scientific conferences and registrations.

Features
Create conferences
View conferences
View conference details
Register for conferences
Manage conference registrations
Manage conference participants
Track conference information
10. Institutions

The institution module manages institutions and their associated departments and researchers.

Features
View institutions
Create institutions
Manage institution information
Manage departments
Associate researchers with institutions
11. Research Network Analysis

The research network module provides visualization and analysis of researcher collaboration relationships.

Features
Collaboration network visualization
Researcher connections
Collaboration relationships
Network statistics
Research collaboration analysis
Frontend Directory
frontend/src/pages/network/
12. Dashboards

The dashboard provides an overview of research activities and statistics.

Dashboard Information
Publication statistics
Citation statistics
Collaboration statistics
Research network information
Recent activities
Researcher statistics
13. Reviewer Dashboard

The reviewer dashboard provides functionality for reviewers to manage research-related review activities.

Features
Reviewer-specific dashboard
Review-related information
Research submission information
Reviewer role-based access
Frontend File
frontend/src/pages/ReviewerDashboard.jsx
14. Reports and Exporting

The reporting module provides research-related reports and data export functionality.

Features
Generate research reports
View research statistics
Export research-related information
Analyze publication and collaboration data
Technology Stack
Frontend

The frontend of SCNA is developed using:

React.js
JavaScript
React Router
Axios
Bootstrap
Bootstrap Icons
Lucide React
Vite
Frontend Development Server
http://localhost:5173
Backend

The backend is developed using:

Python
FastAPI
Uvicorn
Pydantic
SQLAlchemy
Alembic
Backend Development Server
http://127.0.0.1:8000
Database

The application uses:

PostgreSQL
Neon PostgreSQL

Database migrations are managed using Alembic.

Authentication

The authentication system uses:

JWT
Bearer Token Authentication
Role-Based Access Control
OTP Verification

Protected API requests use:

Authorization: Bearer <access_token>
Real-Time Communication

Real-time notifications are implemented using:

WebSocket

WebSocket functionality is used to deliver notifications to authenticated users.

Development Tools

The project can be developed and tested using:

Visual Studio Code
Git
GitHub
PowerShell
npm
Python Virtual Environment
Swagger UI
Postman
Project Structure
Scientific-Collaboration-Network-Analyzer-Group-2/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies.py
│   │   └── users.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   ├── models/
│   │
│   ├── repositories/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── package.json
│   └── vite.config.js
│
├── migrations/
│   └── versions/
│
├── uploads/
│   └── publications/
│
├── requirements.txt
├── README.md
└── .env
How to Fetch the Project
Clone the Repository

Clone the project repository using Git:

git clone <repository-url>

Navigate to the project directory:

cd Scientific-Collaboration-Network-Analyzer-Group-2
Check Available Branches
git branch -a

To switch to a required branch:

git checkout <branch-name>

To get the latest changes from the remote repository:

git pull
Backend Setup
Step 1: Open the Project

Open the project folder in Visual Studio Code.

code .
Step 2: Create a Python Virtual Environment

From the project root directory:

python -m venv venv
Step 3: Activate the Virtual Environment
Windows PowerShell
.\venv\Scripts\Activate.ps1

After activation, the terminal should show:

(venv)
Step 4: Install Backend Dependencies

Install the required Python packages:

pip install -r requirements.txt
Step 5: Configure Environment Variables

Create a .env file in the project root directory.

Example configuration:

DATABASE_URL=your_postgresql_database_url
FRONTEND_URL=http://localhost:5173
SECRET_KEY=your_secret_key

Add any other environment variables required by the project configuration.

Do not commit passwords, API keys, database credentials, JWT secrets, or other sensitive information to GitHub.

Database Setup

The project uses PostgreSQL/Neon PostgreSQL.

Make sure the database connection string is correctly configured in the .env file.

After configuring the database, run the migrations:

alembic upgrade head

This applies the available database migrations to the configured database.

Start the Backend

From the project root directory with the virtual environment activated:

uvicorn app.main:app --reload

The backend will normally be available at:

http://127.0.0.1:8000
Backend API Documentation

FastAPI provides interactive Swagger API documentation.

Open the following URL in a browser:

http://127.0.0.1:8000/docs

Swagger UI can be used to:

View available API endpoints
Test API endpoints
Check request parameters
Check response formats
Test authenticated APIs
Provide Bearer authentication tokens
Frontend Setup

Open a second terminal while keeping the backend running.

Navigate to the frontend directory:

cd frontend
Step 1: Install Node Dependencies

Run:

npm install

This installs all frontend dependencies defined in package.json.

Step 2: Start the Frontend

Run:

npm run dev

The frontend will normally be available at:

http://localhost:5173
Running the Complete Project

The backend and frontend should run simultaneously.

Terminal 1 - Backend

From the project root:

.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000
Terminal 2 - Frontend

Navigate to the frontend:

cd frontend
npm install
npm run dev

Frontend:

http://localhost:5173

Open the frontend URL in the browser:

http://localhost:5173
Authentication and Protected APIs

The application uses JWT authentication for protected resources.

After successful login, the access token is stored by the frontend.

Axios automatically adds the token to API requests.

Example:

Authorization: Bearer <access_token>

If the token is missing or invalid, protected API requests return an authentication error and the user is redirected to the login page.
API Services

The frontend communicates with the FastAPI backend using Axios.

The main API configuration is located at:

frontend/src/api/api.js

Researcher-related API operations are handled through:

frontend/src/services/researcherService.js

Other services are organized inside:

frontend/src/services/
Git Development Workflow

Before starting work, get the latest changes:

git pull

Check the current branch:

git branch

Check the working tree:

git status
Create or Switch to a Branch

To create a new branch:

git checkout -b <branch-name>

To switch to an existing branch:

git checkout <branch-name>
Save Changes

After completing your work, check the modified files:

git status

Add only the files related to your work:

git add <file-name>

Commit the changes:

git commit -m "Describe your changes"

Push the branch:

git push origin <branch-name>
Important Git Guidelines
Always check the current branch before making changes.
Run git status before staging files.
Avoid using git add . when the working tree contains other team members' changes.
Commit only the files related to your task.
Pull the latest changes before starting new work when appropriate.
Do not directly overwrite or force-push shared branches.
Resolve merge conflicts carefully before committing.
Keep sensitive files and credentials out of Git.
Important Environment Notes

Before running the project, make sure:

Python is installed.
Node.js and npm are installed.
PostgreSQL/Neon PostgreSQL is available.
The .env file is configured correctly.
Backend dependencies are installed.
Frontend dependencies are installed.
Database migrations have been applied.
Backend is running before testing frontend API functionality.
Troubleshooting
Backend Connection Error

If the frontend shows a network or connection error, make sure the FastAPI backend is running:

uvicorn app.main:app --reload
Frontend Dependency Error

If a frontend dependency is missing, run:

cd frontend
npm install

Then restart the development server:

npm run dev
Database Error

If database-related errors occur:

Check the DATABASE_URL in .env
Make sure the database is accessible
Run:
alembic upgrade head
Authentication Error

If a protected API returns 401 Unauthorized:

Log in again
Check that a valid access token is available
Check that the backend is running
Verify the Authorization header
Make sure the token has not expired
Final Application Flow

The general application flow is:

User
  |
  v
Registration / Login
  |
  v
Authentication
  |
  v
Dashboard
  |
  +----> Researcher Profile
  |
  +----> User Settings
  |
  +----> Publications
  |
  +----> Citations
  |
  +----> Collaborations
  |
  +----> Conferences
  |
  +----> Institutions
  |
  +----> Notifications
  |
  +----> Research Network
  |
  +----> Reports
  |
  +----> Reviewer Dashboard
Project Outcome

The Scientific Collaboration Network Analyzer provides a centralized platform for managing scientific research activities.

The system integrates researcher profile management, publications, citations, collaborations, conferences, institutions, notifications, reports, dashboards, and research network analysis into a single web-based application.

The platform helps researchers manage their research information, discover potential collaborators, track scientific publications and citations, and understand collaboration relationships through network analysis.

The project demonstrates the integration of a React-based frontend, FastAPI backend, PostgreSQL database, JWT authentication, WebSocket-based real-time notifications, and role-based access control into a complete research collaboration management system.

Conclusion

The Scientific Collaboration Network Analyzer (SCNA) provides an integrated environment for researchers and administrators to manage scientific research activities efficiently.

The implemented modules support researcher management, user profiles, settings, publications, citations, collaborations, conferences, institutions, notifications, reports, dashboards, reviewer activities, and research network analysis.

The project uses modern web technologies including React.js, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, Axios, and WebSocket communication to provide a scalable and interactive research collaboration platform.