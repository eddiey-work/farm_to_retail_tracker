## Features Implemented

### Public
- Browse marketplace with search, location filter, sort, pagination
- View crop detail with farmer contact info

### Authentication
- Register as Farmer or Retailer
- Login / logout
- Role-based dashboards

### Farmer
- List, edit, delete own crops with optional images
- See incoming orders with status filters
- Confirm / Complete / Cancel orders
- Cancel restores stock atomically

### Retailer
- Search and browse marketplace
- Place orders with live stock validation
- Track order status (Pending / Confirmed / Completed / Cancelled)

### System
- Role-based access control (farmer / retailer)
- Owner-scoped queries (404 on foreign resources)
- Atomic order placement and cancellation
- Responsive Bootstrap 5 UI

## In Progress / Planned
- Automated tests (Week 6)
- Deployment to PythonAnywhere (Week 7)
- Final report and presentation (Week 7)

## Known Limitations (v1)
- No payments processed through the platform
- SQLite in development — `select_for_update` is a no-op; PostgreSQL required for full concurrency guarantee
- No email or SMS notifications
- Order lists are not paginated