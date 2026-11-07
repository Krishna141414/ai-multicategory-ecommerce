# PROJECT BRIEF (official, do not edit)

> Source: AI-Driven_Multi-Category_E-Commerce.docx. This file is the single source of truth for WHAT to build.

**AI-Driven Multi-Category E-Commerce System with End-to-End Web
Automation Using Playwright and Pytest**

**Website**

Front End: HTML5, CSS3, JavaScript, Bootstrap 5

Server Side: Python (Django)

Programming Language: Python

IDE: Visual Studio Code

Web Server: Django Development Server

**Database**

SQLite

**Artificial Intelligence**

AI Technique: Content-Based Product Recommendation

Machine Learning Library: Scikit-learn

Data Processing: Pandas

Feature Extraction: TF-IDF Vectorization

Similarity Algorithm: Cosine Similarity

**Automation Testing**

Testing Tool: Playwright

Testing Language: Python

Testing Framework: Pytest

Browser: Google Chrome / Chromium

Test Reporting: pytest-html

Screenshot Capture: Playwright

**Admin**

Login (username, password) --- Default Admin Credentials

Dashboard (total_customers, total_categories, total_products,
total_orders, total_sales)

Add Category (id, category_name, description, status, created_date)

View Categories

Update Category

Delete Category

Add Product (id, category_id, product_name, brand, price, description,
image, quantity, keywords, added_date, status)

View Products

Update Product

Delete Product

View Customers (id, name, email, mobile_number, address,
registered_date, status)

Activate / Deactivate Customer

View Orders (id, order_id, customer_id, product_id, quantity, price,
amount, order_date, order_status)

Update Order Status (Pending, Confirmed, Shipped, Delivered, Cancelled)

View Product Ratings / Reviews

View Queries

Post Query / Reply Query (id, conversation_id, sender_id, sender_type,
receiver_id, receiver_type, parent_message_id, subject, message,
posted_date, status)

View Conversation History

Logout

**Customer**

Registration (id, name, email, mobile_number, password, address,
registered_date, status)

Login (email, password)

View Profile

Update Profile

View Product Categories

Search Product (product_name, category, min_price, max_price)

View Products

View Product Details (product_name, category, brand, price, description,
image, available_quantity, rating)

View AI Recommended Products

Add to Cart (id, customer_id, product_id, quantity, added_date)

View Cart

Update Cart Quantity

Remove from Cart

Submit Cart (id, order_id, product_id, customer_id, quantity, price,
amount, order_date, order_status)

Dummy Payment (id, order_id, customer_id, total_amount, payment_method,
payment_status, payment_date)

View Order Confirmation

Order Information Email

View Order History

View Order Details

Add Rating (id, product_id, customer_id, rating, posted_date)

Add Review (id, product_id, customer_id, review, posted_date)

Post Query

View Queries

Reply Query

View Conversation History

Logout

**Product Categories**

1.  Electronics

2.  Fashion and Clothing

3.  Home and Furniture

4.  Books and Stationery

5.  Beauty and Personal Care

6.  Sports and Fitness

7.  Mobile Phones and Accessories

8.  Computers and Laptops

9.  Toys and Games

10. Kitchen and Home Appliances

**AI Product Recommendation**

Product Features (id, product_id, category, product_name, brand,
description, keywords, price)

Customer Product Interaction (id, customer_id, product_id,
interaction_type, interaction_date)

**AI Recommendation Functionalities**

Collect Product Information

Product Data Preprocessing

Extract Product Features Using TF-IDF

Calculate Product Similarity Using Cosine Similarity

Identify Customer Interests (viewed_products, cart_products,
purchased_products)

Generate Related Product Recommendations

Generate Personalized Product Recommendations

Display Recommended Products

View Similar Products

**AI Recommendation Output**

-   Recommended product name

-   Product category

-   Product image

-   Product price

-   Product similarity score

-   Top recommended products

**Playwright Automation Testing**

Test Case (id, test_name, module, test_description, expected_result)

**Admin Testing**

-   Admin Login

-   Invalid Admin Login

-   View Dashboard

-   Add Category

-   View Categories

-   Update Category

-   Delete Category

-   Add Product

-   View Products

-   Update Product

-   Delete Product

-   View Customers

-   Activate Customer

-   Deactivate Customer

-   View Orders

-   Update Order Status

-   View Product Ratings / Reviews

-   View Queries

-   Post Query

-   Reply Query

-   View Conversation History

-   Logout

**Customer Testing**

-   Customer Registration

-   Customer Login

-   Invalid Customer Login

-   View Profile

-   Update Profile

-   View Product Categories

-   Search Product by Name

-   Search Product by Category

-   Search Product by Price

-   View Products

-   View Product Details

-   Add to Cart

-   View Cart

-   Update Cart Quantity

-   Remove from Cart

-   Submit Cart

-   Dummy Payment

-   View Order Confirmation

-   View Order History

-   View Order Details

-   Add Rating

-   Add Review

-   Post Query

-   View Queries

-   Reply Query

-   View Conversation History

-   Logout

**AI Recommendation Testing**

-   Verify Product Feature Extraction

-   Verify Similar Product Recommendations

-   Verify Customer-Based Recommendations

-   Verify Recommended Product Display

-   Verify Recommended Product Details

-   Verify Recommendation After Product View

-   Verify Recommendation After Adding Product to Cart

-   Verify Recommendation for New Customer

**End-to-End Workflow Testing**

Test Scenario 1: Customer Shopping Workflow

Customer Registration → Login → Search Product → View Product → Add to
Cart → Submit Cart → Dummy Payment → Order Confirmation → Logout

Test Scenario 2: AI Recommendation Workflow

Customer Login → View Product → Generate AI Recommendations → View
Recommended Products → Select Recommended Product → Add to Cart

Test Scenario 3: Admin Product Management Workflow

Admin Login → Add Category → Add Product → View Product → Update Product
→ Delete Product → Logout

Test Scenario 4: Order Management Workflow

Customer Places Order → Admin Views Order → Admin Updates Order Status →
Customer Views Updated Order Status

**Test Execution Report**

Test Execution Report (id, test_case_id, execution_date, actual_result,
status, execution_time, screenshot_path)

Test Summary Report (id, execution_date, total_tests, passed_tests,
failed_tests, skipped_tests, total_execution_time, report_path)

Generate HTML Test Report

View Passed Test Cases

View Failed Test Cases

Capture Screenshots for Failed Test Cases

View Test Execution Summary

**Important Implementation Rules**

**1. Customer Registration and Authentication**

-   New customers register with Active status by default.

-   Customer email addresses must be unique.

-   Passwords must be stored using Django\'s secure password hashing
    system.

-   Only authenticated customers can access cart, checkout, order
    history and profile operations.

-   Deactivated customers cannot log in.

**2. Product and Category Management**

-   Only Admin can add, update or delete categories and products.

-   Each product belongs to one category.

-   Product price must be greater than zero.

-   Product quantity cannot be negative.

-   Products with zero available quantity cannot be added to the cart.

-   Products associated with existing orders must retain their
    historical order information even if the product is removed from
    active listings.

**3. AI Product Recommendation**

-   The recommendation engine uses product information such as category,
    name, brand, description and keywords.

-   TF-IDF converts product text information into numerical feature
    vectors.

-   Cosine Similarity calculates similarity between products.

-   The system recommends the most relevant products based on product
    similarity.

-   Customer interactions such as product views, cart additions and
    purchases can be used to select products representing customer
    interests.

-   Recommendations are generated from similar products associated with
    those interests.

-   Already selected products should be excluded from their own
    recommendation results.

-   Only active and available products should be recommended.

-   New customers without interaction history can receive popular or
    category-based product suggestions.

-   The recommendation system runs locally without requiring paid AI
    APIs.

**4. Cart Submission**

-   Customers can add multiple products to their carts.

-   Cart quantity cannot exceed available product stock.

-   Each product in the submitted cart is inserted as a separate record
    in the orders table.

-   All products submitted in the same checkout share a common order_id.

-   Each order record has its own unique id.

-   The amount represents price × quantity.

-   The total order amount is calculated from all cart items.

-   Cart submission and stock reservation must be handled in one
    database transaction.

-   Payment confirmation must not create duplicate orders.

-   Cart items are cleared after successful order confirmation.

**5. Dummy Payment**

-   The system simulates payment without actual financial transactions.

-   No real payment gateway integration is required.

-   Payment success and failure can be simulated.

-   After successful dummy payment, the order status is updated to
    Confirmed.

-   The system displays order confirmation and sends order information
    through email.

-   Failed payments must not mark orders as paid or confirmed.

**6. Generic Query Management**

-   A single messages table stores queries and replies between Admin and
    Customer.

-   sender_type and receiver_type identify the user roles.

-   conversation_id groups messages belonging to the same conversation.

-   parent_message_id identifies the message being replied to.

-   A new conversation starts with parent_message_id = NULL.

-   Customers can view only their own conversations.

-   Admin can view and respond to customer conversations.

**7. Playwright Automation Testing**

-   Playwright with Python automates browser-based functional testing.

-   Pytest manages test execution, fixtures and assertions.

-   Tests must verify expected results against actual application
    behavior.

-   Positive and negative test scenarios must be included.

-   Browser automation must use reliable Playwright locators.

-   Playwright\'s built-in waiting mechanisms should be used instead of
    unnecessary fixed delays.

-   Test cases should run independently using controlled test data.

-   Automated tests must not modify production data.

-   Failed test cases should capture screenshots.

-   Test execution reports maintain Pass/Fail status and execution
    details.

-   HTML reports are generated using pytest-html.

**8. End-to-End Testing**

-   End-to-end tests verify complete workflows rather than isolated
    pages.

-   Tests should verify both visible application behavior and persisted
    results where appropriate.

-   Checkout tests must verify correct order totals and order
    confirmation.

-   AI recommendation tests must verify that recommended products are
    relevant to the selected product or customer interests.

-   Tests should support execution in both headed and headless browser
    modes.

-   Test execution must be repeatable on a local laptop.

**9. Authentication and Security**

-   Django Authentication is used for login and password management.

-   Role-based authorization restricts Admin and Customer operations.

-   Django CSRF protection must be enabled for applicable form
    submissions.

-   User input must be validated on the server side.

-   Sensitive credentials must not be hardcoded in publicly shared
    source code.

-   Default Admin credentials should be changed before deployment.

**10. Local Execution and College Demonstration**

-   The complete e-commerce application must run locally using Django.

-   SQLite stores application data locally.

-   The AI recommendation engine executes using locally installed Python
    libraries.

-   Playwright and Pytest execute automated tests on the same laptop.

-   The browser can be displayed during automation using headed mode.

-   HTML reports and failure screenshots are stored locally.

-   Internet access is not required during the demonstration after
    installing the necessary packages and browser binaries, provided
    email is simulated or handled locally.
