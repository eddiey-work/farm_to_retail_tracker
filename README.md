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
Day 6: CropProduce model created with quantity, unit, price, harvest date, location, image; admin configured; sample seed command added.
Day 7: Order model created with retailer, farmer, crop FKs, status choices, admin actions. Database schema complete.
Day 8: Marketplace list view (search, filter, sort, pagination), crop detail page, navbar wired.
Day 9: Farmer my_crops view (read-only) with stats, dashboard stats wired, farmer URL namespace added.
Day 10: CropForm (ModelForm), crop_create view, image upload working, Add Crop button enabled.
Day 11: crop_update and crop_delete views with ownership checks; CRUD cycle complete for farmers.
Day 12: place_order view with transaction.atomic and select_for_update; stock deduction; order confirmation page; Order now button live.
Day 13: Order management complete. Retailer sees placed orders; farmer sees incoming orders; status transitions (confirm/complete/cancel) with atomic stock restoration on cancel.