# Requirements Matrix

Every item in `docs/PROJECT_BRIEF.md` → where it is implemented → which test covers it → status.
Status values: **Planned** → **Implemented** → **Tested** (implemented and covered by a passing test).
"Implemented in" and "Covered by test" are filled in as each phase lands.

## A. Stack (brief: Website / Database / AI / Testing)
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| STK-01 | Front end: HTML5, CSS3, JavaScript, Bootstrap 5 | | | Planned |
| STK-02 | Server side: Python (Django) | Django 6.1.3 project `config/` + 9 apps |  | Implemented |
| STK-03 | IDE: Visual Studio Code | | | Planned |
| STK-04 | Web server: Django development server | | | Planned |
| STK-05 | Database: SQLite | `db.sqlite3` (shop) + `reports.sqlite3` (tests), `config/settings.py` |  | Implemented |
| STK-06 | AI technique: content-based product recommendation | | | Planned |
| STK-07 | ML library: scikit-learn | requirements.txt (scikit-learn 1.9.1) |  | Implemented |
| STK-08 | Data processing: Pandas | requirements.txt (pandas 3.1.1) |  | Implemented |
| STK-09 | Feature extraction: TF-IDF vectorization | | | Planned |
| STK-10 | Similarity: cosine similarity | | | Planned |
| STK-11 | Testing tool: Playwright (Python) | requirements.txt (playwright 1.64.1, pytest-playwright 0.10) |  | Implemented |
| STK-12 | Testing framework: Pytest | requirements.txt (pytest 9.2), `pytest.ini` |  | Implemented |
| STK-13 | Browser: Chrome / Chromium | | | Planned |
| STK-14 | Test reporting: pytest-html | requirements.txt (pytest-html 4.2.0) |  | Implemented |
| STK-15 | Screenshot capture: Playwright | | | Planned |

## B. Admin features
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| ADM-01 | Login (username, password) — default admin credentials | `accounts/forms.AdminLoginForm`, `adminpanel/views/auth.py`, `create_default_admin` (.env) | `tests/unit/test_auth.py::test_admin_login_with_username`, `::test_invalid_admin_login_and_customer_account_refused` | Tested |
| ADM-02 | Dashboard: total_customers, total_categories, total_products, total_orders, total_sales | | TC-ADM-03 | Planned |
| ADM-03 | Add Category (id, category_name, description, status, created_date) | | TC-ADM-04 | Planned |
| ADM-04 | View Categories | | TC-ADM-05 | Planned |
| ADM-05 | Update Category | | TC-ADM-06 | Planned |
| ADM-06 | Delete Category | | TC-ADM-07 | Planned |
| ADM-07 | Add Product (id, category_id, product_name, brand, price, description, image, quantity, keywords, added_date, status) | | TC-ADM-08 | Planned |
| ADM-08 | View Products | | TC-ADM-09 | Planned |
| ADM-09 | Update Product | | TC-ADM-10 | Planned |
| ADM-10 | Delete Product | | TC-ADM-11 | Planned |
| ADM-11 | View Customers (id, name, email, mobile_number, address, registered_date, status) | | TC-ADM-12 | Planned |
| ADM-12 | Activate / Deactivate Customer | | TC-ADM-13, TC-ADM-14 | Planned |
| ADM-13 | View Orders (id, order_id, customer_id, product_id, quantity, price, amount, order_date, order_status) | | TC-ADM-15 | Planned |
| ADM-14 | Update Order Status (Pending, Confirmed, Shipped, Delivered, Cancelled) | | TC-ADM-16 | Planned |
| ADM-15 | View Product Ratings / Reviews | | TC-ADM-17 | Planned |
| ADM-16 | View Queries | | TC-ADM-18 | Planned |
| ADM-17 | Post Query / Reply Query (id, conversation_id, sender_id, sender_type, receiver_id, receiver_type, parent_message_id, subject, message, posted_date, status) | | TC-ADM-19, TC-ADM-20 | Planned |
| ADM-18 | View Conversation History | | TC-ADM-21 | Planned |
| ADM-19 | Logout | `adminpanel/views/auth.admin_logout` (POST) | TC-ADM-22 | Implemented |

## C. Customer features
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| CUS-01 | Registration (id, name, email, mobile_number, password, address, registered_date, status) | `accounts/forms.RegistrationForm`, `accounts/views.register`, `accounts/services.register_customer` | `tests/unit/test_auth.py::test_register_creates_active_customer` | Tested |
| CUS-02 | Login (email, password) | `accounts/backends.EmailBackend`, `accounts/views.login_view` | `tests/unit/test_auth.py::test_customer_login_with_email`, `::test_invalid_login_shows_generic_error` | Tested |
| CUS-03 | View Profile | `accounts/views.profile`, `templates/accounts/profile.html` | TC-CUS-04 | Implemented |
| CUS-04 | Update Profile | `accounts/forms.ProfileForm`, `accounts/views.profile_edit` | `tests/unit/test_auth.py::test_profile_update_keeps_email_unique` | Tested |
| CUS-05 | View Product Categories | | TC-CUS-06 | Planned |
| CUS-06 | Search Product (product_name, category, min_price, max_price) | | TC-CUS-07, 08, 09 | Planned |
| CUS-07 | View Products | | TC-CUS-10 | Planned |
| CUS-08 | View Product Details (product_name, category, brand, price, description, image, available_quantity, rating) | | TC-CUS-11 | Planned |
| CUS-09 | View AI Recommended Products | | TC-AI-03, TC-AI-04 | Planned |
| CUS-10 | Add to Cart (id, customer_id, product_id, quantity, added_date) | | TC-CUS-12 | Planned |
| CUS-11 | View Cart | | TC-CUS-13 | Planned |
| CUS-12 | Update Cart Quantity | | TC-CUS-14 | Planned |
| CUS-13 | Remove from Cart | | TC-CUS-15 | Planned |
| CUS-14 | Submit Cart (id, order_id, product_id, customer_id, quantity, price, amount, order_date, order_status) | | TC-CUS-16 | Planned |
| CUS-15 | Dummy Payment (id, order_id, customer_id, total_amount, payment_method, payment_status, payment_date) | | TC-CUS-17 | Planned |
| CUS-16 | View Order Confirmation | | TC-CUS-18 | Planned |
| CUS-17 | Order Information Email | | E2E-01 | Planned |
| CUS-18 | View Order History | | TC-CUS-19 | Planned |
| CUS-19 | View Order Details | | TC-CUS-20 | Planned |
| CUS-20 | Add Rating (id, product_id, customer_id, rating, posted_date) | | TC-CUS-21 | Planned |
| CUS-21 | Add Review (id, product_id, customer_id, review, posted_date) | | TC-CUS-22 | Planned |
| CUS-22 | Post Query | | TC-CUS-23 | Planned |
| CUS-23 | View Queries | | TC-CUS-24 | Planned |
| CUS-24 | Reply Query | | TC-CUS-25 | Planned |
| CUS-25 | View Conversation History | | TC-CUS-26 | Planned |
| CUS-26 | Logout | `accounts/views.logout_view` (POST only) | `tests/unit/test_auth.py::test_logout_requires_post` | Tested |

## D. Product categories (exact names)
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| CAT-01 | Electronics | `catalog/seed_data.py` CATEGORIES, `core/demo.seed_catalog` |  | Implemented |
| CAT-02 | Fashion and Clothing | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-03 | Home and Furniture | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-04 | Books and Stationery | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-05 | Beauty and Personal Care | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-06 | Sports and Fitness | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-07 | Mobile Phones and Accessories | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-08 | Computers and Laptops | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-09 | Toys and Games | `catalog/seed_data.py` CATEGORIES |  | Implemented |
| CAT-10 | Kitchen and Home Appliances | `catalog/seed_data.py` CATEGORIES |  | Implemented |

## E. AI data, functionalities and output
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| AI-D1 | Product Features table (id, product_id, category, product_name, brand, description, keywords, price) | `recommender/models.py` ProductFeature | TC-AI-01 | Implemented |
| AI-D2 | Customer Product Interaction table (id, customer_id, product_id, interaction_type, interaction_date) | `recommender/models.py` CustomerProductInteraction | TC-AI-06, TC-AI-07 | Implemented |
| AI-F1 | Collect Product Information | | TC-AI-01 | Planned |
| AI-F2 | Product Data Preprocessing | | TC-AI-01 | Planned |
| AI-F3 | Extract Product Features Using TF-IDF | | TC-AI-01 | Planned |
| AI-F4 | Calculate Product Similarity Using Cosine Similarity | | TC-AI-02 | Planned |
| AI-F5 | Identify Customer Interests (viewed_products, cart_products, purchased_products) | | TC-AI-03, 06, 07 | Planned |
| AI-F6 | Generate Related Product Recommendations | | TC-AI-02 | Planned |
| AI-F7 | Generate Personalized Product Recommendations | | TC-AI-03 | Planned |
| AI-F8 | Display Recommended Products | | TC-AI-04 | Planned |
| AI-F9 | View Similar Products | | TC-AI-02, E2E-02 | Planned |
| AI-O1 | Output: recommended product name | | TC-AI-05 | Planned |
| AI-O2 | Output: product category | | TC-AI-05 | Planned |
| AI-O3 | Output: product image | | TC-AI-05 | Planned |
| AI-O4 | Output: product price | | TC-AI-05 | Planned |
| AI-O5 | Output: product similarity score | | TC-AI-05 | Planned |
| AI-O6 | Output: top recommended products | | TC-AI-04 | Planned |

## F. Test cases — Test Case table (id, test_name, module, test_description, expected_result)
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| TST-00 | Test Case catalogue table (id, test_name, module, test_description, expected_result) | `testreports/models.py` TestCase (reports DB) |  | Implemented |
| TC-ADM-01 | Admin Login | | | Planned |
| TC-ADM-02 | Invalid Admin Login | | | Planned |
| TC-ADM-03 | View Dashboard | | | Planned |
| TC-ADM-04 | Add Category | | | Planned |
| TC-ADM-05 | View Categories | | | Planned |
| TC-ADM-06 | Update Category | | | Planned |
| TC-ADM-07 | Delete Category | | | Planned |
| TC-ADM-08 | Add Product | | | Planned |
| TC-ADM-09 | View Products | | | Planned |
| TC-ADM-10 | Update Product | | | Planned |
| TC-ADM-11 | Delete Product | | | Planned |
| TC-ADM-12 | View Customers | | | Planned |
| TC-ADM-13 | Activate Customer | | | Planned |
| TC-ADM-14 | Deactivate Customer | | | Planned |
| TC-ADM-15 | View Orders | | | Planned |
| TC-ADM-16 | Update Order Status | | | Planned |
| TC-ADM-17 | View Product Ratings / Reviews | | | Planned |
| TC-ADM-18 | View Queries | | | Planned |
| TC-ADM-19 | Post Query | | | Planned |
| TC-ADM-20 | Reply Query | | | Planned |
| TC-ADM-21 | View Conversation History | | | Planned |
| TC-ADM-22 | Logout | | | Planned |
| TC-CUS-01 | Customer Registration | | | Planned |
| TC-CUS-02 | Customer Login | | | Planned |
| TC-CUS-03 | Invalid Customer Login | | | Planned |
| TC-CUS-04 | View Profile | | | Planned |
| TC-CUS-05 | Update Profile | | | Planned |
| TC-CUS-06 | View Product Categories | | | Planned |
| TC-CUS-07 | Search Product by Name | | | Planned |
| TC-CUS-08 | Search Product by Category | | | Planned |
| TC-CUS-09 | Search Product by Price | | | Planned |
| TC-CUS-10 | View Products | | | Planned |
| TC-CUS-11 | View Product Details | | | Planned |
| TC-CUS-12 | Add to Cart | | | Planned |
| TC-CUS-13 | View Cart | | | Planned |
| TC-CUS-14 | Update Cart Quantity | | | Planned |
| TC-CUS-15 | Remove from Cart | | | Planned |
| TC-CUS-16 | Submit Cart | | | Planned |
| TC-CUS-17 | Dummy Payment | | | Planned |
| TC-CUS-18 | View Order Confirmation | | | Planned |
| TC-CUS-19 | View Order History | | | Planned |
| TC-CUS-20 | View Order Details | | | Planned |
| TC-CUS-21 | Add Rating | | | Planned |
| TC-CUS-22 | Add Review | | | Planned |
| TC-CUS-23 | Post Query | | | Planned |
| TC-CUS-24 | View Queries | | | Planned |
| TC-CUS-25 | Reply Query | | | Planned |
| TC-CUS-26 | View Conversation History | | | Planned |
| TC-CUS-27 | Logout | | | Planned |
| TC-AI-01 | Verify Product Feature Extraction | | | Planned |
| TC-AI-02 | Verify Similar Product Recommendations | | | Planned |
| TC-AI-03 | Verify Customer-Based Recommendations | | | Planned |
| TC-AI-04 | Verify Recommended Product Display | | | Planned |
| TC-AI-05 | Verify Recommended Product Details | | | Planned |
| TC-AI-06 | Verify Recommendation After Product View | | | Planned |
| TC-AI-07 | Verify Recommendation After Adding Product to Cart | | | Planned |
| TC-AI-08 | Verify Recommendation for New Customer | | | Planned |

## G. End-to-end scenarios
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| E2E-01 | Customer Shopping: Registration → Login → Search → View Product → Add to Cart → Submit Cart → Dummy Payment → Order Confirmation → Logout | | | Planned |
| E2E-02 | AI Recommendation: Login → View Product → Generate AI Recommendations → View Recommended Products → Select Recommended Product → Add to Cart | | | Planned |
| E2E-03 | Admin Product Management: Login → Add Category → Add Product → View Product → Update Product → Delete Product → Logout | | | Planned |
| E2E-04 | Order Management: Customer Places Order → Admin Views Order → Admin Updates Order Status → Customer Views Updated Order Status | | | Planned |

## H. Test execution reporting
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| REP-01 | Test Execution Report (id, test_case_id, execution_date, actual_result, status, execution_time, screenshot_path) | `testreports/models.py` TestExecution (reports DB) |  | Implemented |
| REP-02 | Test Summary Report (id, execution_date, total_tests, passed_tests, failed_tests, skipped_tests, total_execution_time, report_path) | `testreports/models.py` TestSummary (reports DB) |  | Implemented |
| REP-03 | Generate HTML Test Report | | | Planned |
| REP-04 | View Passed Test Cases | | | Planned |
| REP-05 | View Failed Test Cases | | | Planned |
| REP-06 | Capture Screenshots for Failed Test Cases | | | Planned |
| REP-07 | View Test Execution Summary | | | Planned |

## I. Implementation rules
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| R1.1 | New customers register with Active status by default | `accounts/models.py` default Active; `register_customer` | `tests/unit/test_auth.py::test_register_creates_active_customer` | Tested |
| R1.2 | Customer email addresses must be unique | UniqueConstraint(Lower(email)) + `RegistrationForm.clean_email` / `ProfileForm.clean_email` | `test_models.py::test_duplicate_email_case_insensitive`, `test_auth.py::test_duplicate_email_case_insensitive` | Tested |
| R1.3 | Passwords stored with Django's secure password hashing | Django `User.set_password` via `create_user` | `tests/unit/test_auth.py::test_password_is_hashed` | Tested |
| R1.4 | Only authenticated customers access cart, checkout, order history, profile | `core/permissions.customer_required` | `tests/unit/test_auth.py::test_profile_requires_login` | Tested |
| R1.5 | Deactivated customers cannot log in | `EmailBackend`, `login_error_for`, `set_customer_status`, `ActiveCustomerMiddleware` | `test_auth.py::test_inactive_customer_cannot_login`, `::test_deactivated_session_is_logged_out` | Tested |
| R2.1 | Only Admin can add/update/delete categories and products | | | Planned |
| R2.2 | Each product belongs to one category | `catalog/models.py` Product.category FK (PROTECT) |  | Implemented |
| R2.3 | Product price must be greater than zero | `catalog/models.py` CheckConstraint price>0 | `tests/unit/test_models.py::test_price_must_be_positive` | Tested |
| R2.4 | Product quantity cannot be negative | `catalog/models.py` CheckConstraint quantity>=0 | `tests/unit/test_models.py::test_quantity_cannot_be_negative` | Tested |
| R2.5 | Zero-quantity products cannot be added to the cart | | | Planned |
| R2.6 | Products with existing orders keep historical order info even if removed from listings | | | Planned |
| R3.1 | Engine uses category, name, brand, description, keywords | | | Planned |
| R3.2 | TF-IDF converts product text into numeric feature vectors | | | Planned |
| R3.3 | Cosine similarity calculates similarity between products | | | Planned |
| R3.4 | Recommends the most relevant products by similarity | | | Planned |
| R3.5 | Views, cart additions, purchases select products representing interests | | | Planned |
| R3.6 | Recommendations generated from products similar to those interests | | | Planned |
| R3.7 | Already selected products excluded from their own results | | | Planned |
| R3.8 | Only active and available products recommended | | | Planned |
| R3.9 | New customers get popular or category-based suggestions | | | Planned |
| R3.10 | Runs locally, no paid AI APIs | | | Planned |
| R4.1 | Customers can add multiple products to cart | | | Planned |
| R4.2 | Cart quantity cannot exceed available stock | | | Planned |
| R4.3 | Each cart product inserted as a separate orders record | | | Planned |
| R4.4 | All products of one checkout share a common order_id | | | Planned |
| R4.5 | Each order record has its own unique id | `orders/models.py` Order (one row, own id) |  | Implemented |
| R4.6 | amount = price × quantity | `orders/models.py` Order.save() | `tests/unit/test_models.py::test_order_amount_is_price_times_quantity` | Tested |
| R4.7 | Total order amount calculated from all cart items | | | Planned |
| R4.8 | Cart submission + stock reservation in one DB transaction | | | Planned |
| R4.9 | Payment confirmation must not create duplicate orders | | | Planned |
| R4.10 | Cart cleared after successful order confirmation | | | Planned |
| R5.1 | Payment simulated, no real financial transactions | | | Planned |
| R5.2 | No real payment gateway | | | Planned |
| R5.3 | Payment success and failure can be simulated | | | Planned |
| R5.4 | After successful payment, order status → Confirmed | | | Planned |
| R5.5 | Show order confirmation and send order info by email | | | Planned |
| R5.6 | Failed payments do not mark orders paid/confirmed | | | Planned |
| R6.1 | Single messages table stores queries and replies | `messaging/models.py` Message |  | Implemented |
| R6.2 | sender_type / receiver_type identify roles | `messaging/models.py` Message.sender_type / receiver_type |  | Implemented |
| R6.3 | conversation_id groups a conversation | | | Planned |
| R6.4 | parent_message_id identifies the message replied to | | | Planned |
| R6.5 | New conversation starts with parent_message_id = NULL | | | Planned |
| R6.6 | Customers view only their own conversations | | | Planned |
| R6.7 | Admin can view and respond to customer conversations | | | Planned |
| R7.1 | Playwright with Python automates browser functional tests | | | Planned |
| R7.2 | Pytest manages execution, fixtures, assertions | | | Planned |
| R7.3 | Tests verify expected vs actual behaviour | | | Planned |
| R7.4 | Positive and negative scenarios included | | | Planned |
| R7.5 | Reliable Playwright locators | | | Planned |
| R7.6 | Built-in waiting, no fixed delays | | | Planned |
| R7.7 | Tests run independently with controlled test data | | | Planned |
| R7.8 | Tests must not modify production data | | | Planned |
| R7.9 | Failed tests capture screenshots | | | Planned |
| R7.10 | Reports keep Pass/Fail status and execution details | | | Planned |
| R7.11 | HTML reports via pytest-html | | | Planned |
| R8.1 | E2E tests verify complete workflows | | | Planned |
| R8.2 | Verify visible behaviour and persisted results | | | Planned |
| R8.3 | Checkout tests verify order totals and confirmation | | | Planned |
| R8.4 | AI tests verify relevance to product / customer interests | | | Planned |
| R8.5 | Headed and headless modes supported | | | Planned |
| R8.6 | Repeatable on a local laptop | | | Planned |
| R9.1 | Django Authentication for login/password management | `django.contrib.auth` + `accounts/backends.EmailBackend` |  | Implemented |
| R9.2 | Role-based authorization (Admin vs Customer) | `core/permissions.py` customer_required / admin_required | `test_auth.py::test_customer_cannot_open_admin`, `::test_admin_cannot_use_customer_pages`, `::test_guest_is_sent_to_admin_login` | Tested |
| R9.3 | CSRF protection on form submissions | CsrfViewMiddleware + `{% csrf_token %}` on every form | `tests/unit/test_auth.py::test_forms_carry_csrf_tokens` | Tested |
| R9.4 | Server-side input validation | Django forms in `accounts/forms.py` (server-side clean_* methods) | `tests/unit/test_auth.py::test_registration_rejects_bad_mobile_and_mismatched_passwords` | Tested |
| R9.5 | No hardcoded credentials in public source | `.env` (git-ignored) + `.env.example`; `config/settings.py` |  | Implemented |
| R9.6 | Default admin credentials changed before deployment (documented) | | | Planned |
| R10.1 | Whole app runs locally with Django | | | Planned |
| R10.2 | SQLite stores data locally | `config/settings.py` DATABASES |  | Implemented |
| R10.3 | AI runs with locally installed Python libraries | | | Planned |
| R10.4 | Playwright + Pytest run on the same laptop | | | Planned |
| R10.5 | Browser visible during automation (headed mode) | | | Planned |
| R10.6 | HTML reports and failure screenshots stored locally | | | Planned |
| R10.7 | No internet needed during demo (email simulated locally) | | | Planned |

## J. Must-have extras (CLAUDE.md §2)
| ID | Item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| EXT-01 | Sponsored / featured deals carousel with hover quick-view card; admin sponsored toggle | | | Planned |
| EXT-02 | AI Explainer page (step-by-step, animated, Next/Back) | | | Planned |
| EXT-03 | Admin Test Reports page | | | Planned |
| EXT-04 | docs/CODE_MAP.md | | | Planned |
