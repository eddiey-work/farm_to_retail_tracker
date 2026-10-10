# Software Requirements Specification (SRS)
## Farm to Retail Tracker

**Version:** 1.0  
**Date:** 28-Sept-2026
**Author:** Hafiz Muhammad Saad Ullah  
**Project Type:** Final Year Project (FYP-1)

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the functional and non-functional
requirements for the Farm to Retail Tracker web application. This system
connects small-scale farmers directly with urban retailers in Pakistan,
eliminating traditional agricultural middlemen (Aarthis).

### 1.2 Scope
The system is a monolithic Django web application accessible through a
standard web browser. It allows farmers to list their produce and retailers
to browse, search, and place bulk orders directly. Payment processing,
logistics, and mobile applications are out of scope for this version.

### 1.3 Definitions
- **Farmer:** A user who lists crops for sale.
- **Retailer:** A user who browses and orders crops in bulk.
- **Crop/Produce:** An agricultural item listed by a farmer.
- **Maund:** A traditional unit of weight used in Pakistan (1 Maund ≈ 40 kg).
- **Aarthi:** A traditional middleman in agricultural trade.

### 1.4 Intended Audience
- FYP supervisor and evaluation committee
- Development team
- Future maintainers

---

## 2. Overall Description

### 2.1 Product Perspective
This is a standalone web application. It does not integrate with any
external payment gateway, SMS service, or government database in version 1.

### 2.2 User Classes

| User Class | Description | Access Level |
|------------|-------------|--------------|
| Farmer | Lists crops, manages inventory, receives orders | Registered |
| Retailer | Browses marketplace, places orders, tracks status | Registered |
| Admin | Manages users and data through Django admin | Superuser |

### 2.3 Operating Environment
- Web browser (Chrome, Firefox, Edge)
- Server: PythonAnywhere / localhost
- Database: SQLite (development), PostgreSQL (production-ready)
- Framework: Django 5.x

### 2.4 Assumptions and Dependencies
- Users have access to the internet and a web browser.
- Farmers will keep listed quantities updated.
- No real payment is processed through the system in v1.

---

## 3. Functional Requirements

### 3.1 User Authentication (FR-1)
- FR-1.1: A visitor can register as a Farmer or a Retailer.
- FR-1.2: Registration requires username, email, password, phone, location.
- FR-1.3: A registered user can log in and log out.
- FR-1.4: Farmers and Retailers are redirected to their own dashboards after login.
- FR-1.5: Passwords are hashed using Django’s authentication system.

### 3.2 Crop & Produce Inventory (FR-2)
- FR-2.1: A farmer can create a crop listing with:
  crop name, quantity, unit (Kg/Maund), base price (PKR),
  harvest date, location, description, optional image.
- FR-2.2: A farmer can edit their own listings.
- FR-2.3: A farmer can delete their own listings.
- FR-2.4: A farmer can view all their own listings in a dashboard.
- FR-2.5: A farmer cannot edit or delete other farmers’ listings.
- FR-2.6: Farmers may only create, edit, or delete their own crop listings.
  Attempting to access another farmer's crop returns a 404 response to
  avoid leaking whether the resource exists.

### 3.3 Marketplace (FR-3)
- FR-3.1: Any visitor can view the public marketplace of available crops.
- FR-3.2: A visitor can search crops by name.
- FR-3.3: A visitor can filter crops by location.
- FR-3.4: Crops can be sorted by price and date.
- FR-3.5: Each crop has a detail page showing full info and farmer location.

### 3.4 Ordering System (FR-4)
- FR-4.1: Only a logged-in Retailer can place an order.
- FR-4.2: Ordering requires quantity; total price is calculated automatically.
- FR-4.3: System must prevent ordering more than available quantity.
- FR-4.4: Order status can be: Pending, Confirmed, Completed, Cancelled.
- FR-4.5: A retailer can view their order history.
- FR-4.6: A farmer can view incoming orders on their crops.
- FR-4.7: A farmer can update order status (Confirm / Complete / Cancel).
- FR-4.8: Cancelling an order restores crop quantity.
- FR-4.9: Order placement and cancellation use database-level row locking
  (`select_for_update`) inside a transaction to prevent overselling and
  ensure stock is restored correctly on cancellation.

### 3.5 Admin Panel (FR-5)
- FR-5.1: Admin can manage users, crops, and orders via Django admin.
- FR-5.2: Admin can filter, search, and view records.

---

## 4. Non-Functional Requirements

- NFR-1 (Usability): The interface must be responsive on mobile and desktop.
- NFR-2 (Performance): Pages must load in under 3 seconds on 3G.
- NFR-3 (Security): CSRF protection enabled; passwords hashed;
  permission checks on every protected view.
- NFR-4 (Reliability): Order creation must be atomic — no partial writes.
- NFR-5 (Maintainability): Code must follow Django best practices (MVT).
- NFR-6 (Portability): App must run on any system with Python 3.10+.

---

## 5. Out of Scope (Version 1)
- Real online payments or escrow
- SMS / push notifications
- Live chat between users
- Mobile applications
- GPS-based logistics or delivery tracking
- Recommendation engine / AI
- Multi-crop single checkout

---

## 6. Use Cases

### UC-1: Register Account
- **Actor:** Visitor
- **Precondition:** None
- **Main Flow:** Visitor opens register page → fills form → selects role →
  submits → system validates → creates user + profile → redirects to dashboard.
- **Postcondition:** User is logged in with correct role.

### UC-2: List a Crop
- **Actor:** Farmer
- **Precondition:** Logged in as Farmer
- **Main Flow:** Farmer opens “Add Crop” → fills form → submits →
  system validates → saves crop → shows in My Crops.
- **Postcondition:** Crop visible on marketplace.

### UC-3: Search Marketplace
- **Actor:** Any visitor
- **Main Flow:** User enters crop name and/or location → system filters →
  returns matching available crops.

### UC-4: Place Order
- **Actor:** Retailer
- **Precondition:** Logged in as Retailer; crop available
- **Main Flow:** Retailer opens crop detail → enters quantity →
  system validates stock → creates order atomically → reduces stock →
  shows confirmation.
- **Postcondition:** Order appears in retailer’s and farmer’s dashboards.

### UC-5: Update Order Status
- **Actor:** Farmer
- **Main Flow:** Farmer opens incoming order → selects new status →
  system updates → if Cancelled, restores stock.

---

## 7. Acceptance Criteria
The system is accepted when:
1. A farmer can register, log in, and list a crop.
2. A retailer can register, log in, and order that crop.
3. The farmer can confirm and complete the order.
4. Stock updates correctly and no overselling occurs.
5. All pages are responsive and protected by login where required.

---

## 8. References
- FYP Proposal: Farm to Retail Tracker
- Django Documentation: https://docs.djangoproject.com/
- Bootstrap 5 Documentation: https://getbootstrap.com/