# Farm to Retail Tracker

A Django web application to connect farmers directly with retailers in Pakistan, reducing middlemen.

## Tech Stack
- Django
- SQLite for development
- Bootstrap 5
- HTML/CSS

## Setup

1. Clone the repository
2. Create virtual environment:
   `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   `pip install -r requirements.txt`
5. Run migrations:
   `python manage.py migrate`
6. Start server:
   `python manage.py runserver`

## Status

Day 1: Django project skeleton created.
Day 2: SRS, ERD, and use case diagrams finalized.
Day 3: Settings configured, base template + navbar/footer, home page live.
Day 4: UserProfile model created with role, phone, location; admin registered; auto-create signal wired.
Day 5: Full auth flow (register/login/logout), role-based dashboards, role_required decorator added.
