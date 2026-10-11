# Testing Guide

## Running the tests

    python manage.py test

## Running with coverage

    coverage run --source='.' manage.py test
    coverage report
    coverage html

Open `htmlcov/index.html` for the detailed report.

## Test organization

| File | Coverage |
|------|----------|
| `accounts/tests.py` | UserProfile model, signals, RegistrationForm, auth views, role-based dashboard routing |
| `marketplace/tests.py` | CropProduce model, CropForm, marketplace search/filter/sort, CRUD ownership |
| `orders/tests.py` | Order model, place_order stock deduction, over-order rejection, status transitions, cancel + stock restoration |

## Key tests to note (for defense)

1. **`test_two_consecutive_orders_cannot_both_take_full_stock`** —
   proves overselling prevention. Two retailers compete for the last
   stock unit; the second is rejected.

2. **`test_cancel_restores_stock`** —
   proves that cancelling a pending order returns the quantity to
   the farmer's inventory.

3. **`test_crop_update_only_own` / `test_crop_delete_only_own`** —
   prove 404 for cross-farmer access.

4. **`test_order_detail_cross_user_404`** —
   proves order privacy between retailers and farmers.

## What is tested vs. not tested

**Tested:**
- Model methods and reverse relations
- Form validation (both valid and invalid inputs)
- View permissions (anonymous, wrong role, cross-user)
- Stock deduction, over-order rejection, stock restoration
- Status transition rules (only pending → confirmed, etc.)

**Not tested (out of scope for FYP):**
- Database-level concurrency (requires PostgreSQL)
- Template rendering internals
- File uploads (image storage is mocked via Django's default in-memory storage)
- Admin customizations