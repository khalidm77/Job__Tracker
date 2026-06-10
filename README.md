# Job Tracker

A full stack web application to track job applications.

## Tech Stack
- Backend: Django, Django REST Framework
- Auth: JWT (djangorestframework-simplejwt)
- Database: SQLite
- Frontend: HTML, CSS, Vanilla JavaScript

## Features
- JWT Authentication (Register, Login, Token Refresh)
- Add, Edit, Delete job applications
- Filter by status (Applied, Interview, Offer, Rejected)
- Dashboard with stats overview
- Responsive UI

## Setup Instructions
```bash
git clone https://github.com/khalidm77/Job__Tracker.git
cd Job__Tracker
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/login.html`
