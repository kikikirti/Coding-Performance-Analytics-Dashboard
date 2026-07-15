# Coding Performance Analytics Dashboard

## Overview

The Coding Performance Analytics Dashboard is a full-stack web application designed for students preparing for technical placements. It records coding-practice activity across different problem-solving platforms and converts that activity into clear performance analytics. Users can track coding problems, topics, difficulty levels, attempts, time spent, solving status, revision stages, solved dates, and daily targets from one authenticated dashboard.

The application is intended to make placement preparation measurable. Instead of maintaining disconnected notes or spreadsheets, a student can use structured records to identify progress by topic and difficulty, detect weak areas, plan revision, and monitor daily consistency.

## Problem Statement

Students preparing for software-development and data-structure interviews often solve problems across multiple platforms without maintaining a structured record of their work. This makes it difficult to determine how many problems have been solved, which topics remain weak, how many attempts are required, whether solved problems need revision, and whether daily practice targets are being achieved.

The project addresses this problem by providing a secure web application that stores coding-practice data and transforms it into simple, explainable analytics. The dashboard helps students understand their preparation status and make rule-based decisions about practice and revision.

## Objectives

* Provide secure user registration and token-based login.
* Maintain a user-specific coding-problem repository.
* Track topic, difficulty, platform, status, attempts, time spent, revision stage, and solved date.
* Support searching, filtering, creating, updating, and deleting problem records.
* Calculate topic-wise and difficulty-wise progress.
* Identify weak topics using transparent performance rules.
* Track revision stages and daily coding targets.
* Preserve data isolation so that each user can access only their own records.
* Present analytics in a clean Vue interface suitable for academic demonstration and viva explanation.

## Tech Stack

### Backend

* Flask
* SQLAlchemy
* Flask-Security-Too
* Flask-Migrate
* SQLite

### Frontend

* Vue 3
* Vue Router
* Axios

## Core Features

* User registration and login
* Token-based authentication
* Protected frontend routes and protected Flask APIs
* Add, update, and delete coding problems
* Search problems by title
* Filter problems by topic, difficulty, status, revision status, and platform
* Track topic, difficulty, platform link, status, attempts, time spent, solved date, notes, and revision status
* Mark problems as solved, unsolved, or revision-needed
* Topic-wise progress dashboard
* Difficulty-wise progress dashboard
* Weak-topic identification using fixed rules
* Revision-stage summary
* Daily target creation and update
* Seven-day target-performance history
* RESTful Flask APIs
* Vue frontend with Axios integration
* Consistent success and error response format
* User-specific data isolation
* Responsive tables, forms, navigation, loading states, and empty states

## Database Schema

### User

The `User` model stores application accounts. Important fields include:

* `id`: Primary key
* `email`: Unique login email
* `password`: Secure password hash
* `active`: Account status
* `fs_uniquifier`: Unique value required by Flask-Security-Too

A user can have multiple roles, coding problems, and daily targets. Password hashes are never returned through the API.

### Role

The `Role` model supports Flask-Security-Too authorization. The project creates roles such as `student` and `admin`. Registered and demo users receive the `student` role.

### CodingProblem

The `CodingProblem` model stores an individual coding-practice record. Important fields include:

* `id`
* `user_id`
* `title`
* `platform`
* `platform_link`
* `topic`
* `difficulty`
* `status`
* `attempts`
* `time_spent_minutes`
* `revision_status`
* `solved_date`
* `notes`
* `created_at`
* `updated_at`

The `user_id` foreign key ensures that every problem belongs to one user. API queries always filter by the authenticated user.

### DailyTarget

The `DailyTarget` model stores a user's target for a specific date. Important fields include:

* `id`
* `user_id`
* `target_date`
* `target_count`
* `solved_count`
* `created_at`
* `updated_at`

A unique database constraint on `user_id` and `target_date` ensures that a user can have only one target per date. The solved count is calculated from coding problems where `status` is `Solved` and `solved_date` equals the target date.

## API Endpoints

All protected endpoints require the following request header:

```text
Authentication-Token: <token returned by login>
```

### Authentication APIs

| Method | Endpoint      | Description                     | Authentication |
| ------ | ------------- | ------------------------------- | -------------- |
| `POST` | `/register`   | Register a student account      | No             |
| `POST` | `/login`      | Authenticate and return a token | No             |
| `GET`  | `/profile`    | Return the current user profile | Yes            |
| `GET`  | `/api/health` | Check backend health            | No             |

Logout is handled by removing the token and stored user information from the browser.

### Problem APIs

| Method   | Endpoint                     | Description                            |
| -------- | ---------------------------- | -------------------------------------- |
| `GET`    | `/api/problems`              | List the authenticated user's problems |
| `POST`   | `/api/problems`              | Create a coding problem                |
| `GET`    | `/api/problems/<problem_id>` | Retrieve one owned problem             |
| `PUT`    | `/api/problems/<problem_id>` | Update one owned problem               |
| `DELETE` | `/api/problems/<problem_id>` | Delete one owned problem               |

Supported `GET /api/problems` query parameters:

* `search`
* `topic`
* `difficulty`
* `status`
* `revision_status`
* `platform`

### Daily Target APIs

| Method   | Endpoint                            | Description                            |
| -------- | ----------------------------------- | -------------------------------------- |
| `GET`    | `/api/daily-targets`                | List all owned daily targets           |
| `POST`   | `/api/daily-targets`                | Create a daily target                  |
| `GET`    | `/api/daily-targets/today`          | Return today's target                  |
| `GET`    | `/api/daily-targets/history?days=7` | Return calendar-day target performance |
| `PUT`    | `/api/daily-targets/<target_id>`    | Update an owned target                 |
| `DELETE` | `/api/daily-targets/<target_id>`    | Delete an owned target                 |

### Dashboard APIs

| Method | Endpoint                              | Description                                        |
| ------ | ------------------------------------- | -------------------------------------------------- |
| `GET`  | `/api/dashboard/summary`              | Overall problem, attempt, and time metrics         |
| `GET`  | `/api/dashboard/topic-progress`       | Topic-wise progress                                |
| `GET`  | `/api/dashboard/difficulty-progress`  | Difficulty-wise progress                           |
| `GET`  | `/api/dashboard/weak-topics`          | Rule-based weak-topic analysis and recommendations |
| `GET`  | `/api/dashboard/revision-summary`     | Revision-stage counts                              |
| `GET`  | `/api/dashboard/daily-target-summary` | Today's target completion summary                  |

## API Response Format

Successful and failed API responses use a consistent structure.

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {},
  "errors": {}
}
```

For validation or authorization failures, `success` is `false`, `data` remains an object, and `errors` contains field-specific or operation-specific messages.

## Dashboard Metrics

### Total Problems

The number of coding problems stored by the authenticated user.

### Solved Problems

The number of problems whose status is `Solved`.

### Solved Percentage

The percentage of total problems marked as solved:

```text
Solved Percentage = (Solved Problems / Total Problems) × 100
```

### Topic-wise Progress

For every topic, the dashboard displays:

* Total problem count
* Solved count
* Pending count
* Revision-needed count
* Solved percentage

### Difficulty-wise Progress

The dashboard reports total, solved, pending, and solved percentage values for Easy, Medium, and Hard problems.

### Weak Topics

A topic is identified as weak when at least one rule is satisfied:

* Solved percentage is below 60 percent
* Revision-needed count is at least 2
* Average attempts are greater than 2

The API returns fixed recommendations based on the triggered rule. These recommendations are deterministic and are not AI-generated.

### Revision Summary

The dashboard counts problems in the following revision stages:

* Not Started
* First Revision
* Second Revision
* Mastered

### Daily Target Completion

Daily completion is calculated by matching solved problems to the target date:

```text
Solved Count = Problems where status = Solved and solved_date = target_date
```

The completion percentage is capped at 100 percent, while the raw solved count remains visible.

## Setup Instructions

### Prerequisites

Install the following software:

* Python 3.10 or later
* Node.js 20 or later
* npm
* Git

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd Coding-Performance-Analytics-Dashboard
```

### Backend Setup

Open a terminal in the `backend` directory:

```bash
cd backend
```

Create a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Set the Flask application.

Windows PowerShell:

```powershell
$env:FLASK_APP = "run.py"
```

Linux or macOS:

```bash
export FLASK_APP=run.py
```

Run database migrations:

```bash
flask db upgrade
```

Load the demo account and sample analytics data:

```bash
python seed.py
```

Start the Flask server:

```bash
python run.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

### Frontend Setup

Open a second terminal and enter the frontend directory:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Create a local environment file if a custom API URL is required.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Start the Vue development server:

```bash
npm run dev
```

The frontend normally runs at:

```text
http://127.0.0.1:5173
```

To verify the production build:

```bash
npm run build
```

## Demo Login

```text
Email: student@example.com
Password: student123
```

Run `python seed.py` before using the demo login. The seed operation resets only the demo user's sample problems and targets; it does not delete other users' data.

## Project Structure

```text
Coding-Performance-Analytics-Dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api_utils.py
│   │   ├── auth_routes.py
│   │   ├── daily_targets_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── models.py
│   │   └── problems_routes.py
│   ├── migrations/
│   ├── requirements.txt
│   ├── run.py
│   └── seed.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   └── views/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Future Scope

* LeetCode API integration
* Streak tracking
* Weekly progress reports
* Chart-based analytics
* AI-based problem recommendation
* Revision reminders using Celery
* Redis caching for dashboard analytics
* Email reminders for missed targets
* Import and export of coding-practice records
* Additional platform integrations