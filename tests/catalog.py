"""The test case catalogue (brief: Test Case table: id, test_name, module, test_description, expected_result).

Every automated test is linked to one entry with `@pytest.mark.tc("<id>")`. The catalogue is copied into the
TestCase table of the reports database by `python manage.py sync_test_catalog` (and on every recorded run), and the
admin "Test Reports" page shows each run against it.
"""

ADMIN, CUSTOMER, AI, E2E, NEGATIVE = "Admin", "Customer", "AI Recommendation", "End-to-End", "Negative"

_ROWS = [
    # ---------------- Admin (brief: Admin Testing) ----------------
    ("TC-ADM-01", "Admin Login", ADMIN, "Sign in on /manage/login/ with the admin username and password.", "The dashboard opens and shows the store totals."),
    ("TC-ADM-02", "Invalid Admin Login", ADMIN, "Sign in with a wrong admin password.", "An error is shown and the admin stays on the sign-in page."),
    ("TC-ADM-03", "View Dashboard", ADMIN, "Open the dashboard with known data.", "Total customers, categories, products, orders and sales match the data."),
    ("TC-ADM-04", "Add Category", ADMIN, "Create a category with a name and description.", "A success message appears and the category is listed and stored."),
    ("TC-ADM-05", "View Categories", ADMIN, "Open the category list.", "Every category is listed with its product count and status."),
    ("TC-ADM-06", "Update Category", ADMIN, "Edit a category's name and description.", "The new values are shown and stored."),
    ("TC-ADM-07", "Delete Category", ADMIN, "Delete an empty category after confirming.", "The category disappears from the list and the database."),
    ("TC-ADM-08", "Add Product", ADMIN, "Create a product with category, name, brand, price, description, quantity and keywords.", "The product is listed and stored with those values."),
    ("TC-ADM-09", "View Products", ADMIN, "Open the product list.", "Products are listed with category, price, stock and status."),
    ("TC-ADM-10", "Update Product", ADMIN, "Change a product's price and quantity.", "The list and the database show the new price and quantity."),
    ("TC-ADM-11", "Delete Product", ADMIN, "Delete a product that has no orders after confirming.", "The product is removed from the list and the database."),
    ("TC-ADM-12", "View Customers", ADMIN, "Open the customer list.", "Customers are listed with name, email, mobile, registered date and status."),
    ("TC-ADM-13", "Activate Customer", ADMIN, "Activate an inactive customer.", "The status changes to Active and the customer can sign in again."),
    ("TC-ADM-14", "Deactivate Customer", ADMIN, "Deactivate an active customer after confirming.", "The status changes to Inactive and the customer can no longer sign in."),
    ("TC-ADM-15", "View Orders", ADMIN, "Open the order list.", "Orders are grouped by order ID with customer, items, total and status."),
    ("TC-ADM-16", "Update Order Status", ADMIN, "Move a confirmed order to Shipped.", "Every row of the order shows Shipped, on screen and in the database."),
    ("TC-ADM-17", "View Product Ratings / Reviews", ADMIN, "Open ratings and reviews.", "Each review is listed with product, customer, rating and text."),
    ("TC-ADM-18", "View Queries", ADMIN, "Open the queries inbox.", "Customer conversations are listed with subject, customer and unread count."),
    ("TC-ADM-19", "Post Query", ADMIN, "Start a new conversation with a customer.", "A message with parent_message_id = NULL and a new conversation_id is stored."),
    ("TC-ADM-20", "Reply Query", ADMIN, "Reply to a customer's query.", "The reply reuses the conversation_id and points at the message it answers."),
    ("TC-ADM-21", "View Conversation History", ADMIN, "Open a conversation with several messages.", "All messages are shown in order with sender and time."),
    ("TC-ADM-22", "Logout", ADMIN, "Sign out of the admin panel.", "The admin is signed out and admin pages ask to sign in again."),
    # ---------------- Customer (brief: Customer Testing) ----------------
    ("TC-CUS-01", "Customer Registration", CUSTOMER, "Register with name, email, mobile, address and password.", "The account is created as Active and the customer is signed in."),
    ("TC-CUS-02", "Customer Login", CUSTOMER, "Sign in with email and password.", "The customer is signed in and sees their first name in the header."),
    ("TC-CUS-03", "Invalid Customer Login", CUSTOMER, "Sign in with a wrong password.", "An error is shown and the customer is not signed in."),
    ("TC-CUS-04", "View Profile", CUSTOMER, "Open the profile page.", "Name, email, mobile, address, registered date and status are shown."),
    ("TC-CUS-05", "Update Profile", CUSTOMER, "Change the mobile number and address.", "A success message appears and the new values are stored."),
    ("TC-CUS-06", "View Product Categories", CUSTOMER, "Open the categories page.", "Every active category is shown with its product count."),
    ("TC-CUS-07", "Search Product by Name", CUSTOMER, "Search for part of a product name.", "Only products whose name matches are listed."),
    ("TC-CUS-08", "Search Product by Category", CUSTOMER, "Filter the search by one category.", "Only products from that category are listed."),
    ("TC-CUS-09", "Search Product by Price", CUSTOMER, "Filter by a minimum and maximum price.", "Only products inside the price range are listed."),
    ("TC-CUS-10", "View Products", CUSTOMER, "Open the product list.", "Active products are listed with name, brand, price and image."),
    ("TC-CUS-11", "View Product Details", CUSTOMER, "Open a product page.", "Name, category, brand, price, description, image, available quantity and rating are shown."),
    ("TC-CUS-12", "Add to Cart", CUSTOMER, "Add a product with quantity 2.", "A confirmation appears, the cart badge shows 2 and a cart row is stored."),
    ("TC-CUS-13", "View Cart", CUSTOMER, "Open the cart with two products.", "Both lines, their amounts and the correct total are shown."),
    ("TC-CUS-14", "Update Cart Quantity", CUSTOMER, "Increase a cart line's quantity.", "The line amount and the total update and the new quantity is stored."),
    ("TC-CUS-15", "Remove from Cart", CUSTOMER, "Remove one cart line.", "The line disappears and the total drops by its amount."),
    ("TC-CUS-16", "Submit Cart", CUSTOMER, "Review the order and place it.", "One Pending order row per item is stored, all with one order_id, and stock is reserved."),
    ("TC-CUS-17", "Dummy Payment", CUSTOMER, "Pay a pending order with a simulated success.", "A Payment row is stored as Success and the order becomes Confirmed."),
    ("TC-CUS-18", "View Order Confirmation", CUSTOMER, "Open the confirmation after paying.", "The order ID, Confirmed status, items and total are shown."),
    ("TC-CUS-19", "View Order History", CUSTOMER, "Open the order history.", "Each order is listed once with its ID, total and status."),
    ("TC-CUS-20", "View Order Details", CUSTOMER, "Open one order.", "Its items, amounts, total, payment and status are shown."),
    ("TC-CUS-21", "Add Rating", CUSTOMER, "Rate a delivered product 4 stars.", "The rating is stored and the product's average shows 4.0."),
    ("TC-CUS-22", "Add Review", CUSTOMER, "Write a review of a delivered product.", "The review appears on the product page and is stored."),
    ("TC-CUS-23", "Post Query", CUSTOMER, "Send a new query with subject and message.", "The conversation opens with parent_message_id = NULL."),
    ("TC-CUS-24", "View Queries", CUSTOMER, "Open the list of own queries.", "Only the customer's own conversations are listed."),
    ("TC-CUS-25", "Reply Query", CUSTOMER, "Reply inside a conversation the admin answered.", "The reply is stored with the same conversation_id."),
    ("TC-CUS-26", "View Conversation History", CUSTOMER, "Open a conversation.", "The customer's and the admin's messages are shown in order."),
    ("TC-CUS-27", "Logout", CUSTOMER, "Sign out.", "The customer is signed out and the cart asks to sign in."),
    # ---------------- Negative extras ----------------
    ("TC-NEG-01", "Duplicate email registration", NEGATIVE, "Register with an email that is already used.", "An error explains the email is taken; no second account is created."),
    ("TC-NEG-02", "Deactivated customer login blocked", NEGATIVE, "Sign in as a deactivated customer.", "A clear message says the account is deactivated; no session is created."),
    ("TC-NEG-03", "Add out-of-stock product", NEGATIVE, "Open a product with zero stock.", "It shows Out of stock and offers no Add to cart button."),
    ("TC-NEG-04", "Cart quantity above stock", NEGATIVE, "Set a cart quantity higher than the stock.", "An error explains the limit and the stored quantity does not change."),
    ("TC-NEG-05", "Payment failure does not confirm", NEGATIVE, "Pay with a simulated failure.", "A failure message appears, the order stays Pending and the cart is kept."),
    ("TC-NEG-06", "Customer cannot open admin pages", NEGATIVE, "A signed-in customer opens /manage/.", "Access is refused (403)."),
    ("TC-NEG-07", "Customer cannot see another customer's conversation", NEGATIVE, "Open another customer's conversation URL.", "Access is refused (403) and nothing of it is shown."),
    ("TC-NEG-08", "Invalid price and negative quantity rejected", NEGATIVE, "Save a product with price 0 and quantity -1.", "Both fields show errors and nothing is stored."),
    # ---------------- AI (brief: AI Recommendation Testing) ----------------
    ("TC-AI-01", "Verify Product Feature Extraction", AI, "Open the AI Explainer for a product.", "Its ProductFeature text, cleaned text and top TF-IDF terms (including its keywords) are shown."),
    ("TC-AI-02", "Verify Similar Product Recommendations", AI, "Open a product page.", "Similar products are shown, never the product itself, highest score first, most from the same category."),
    ("TC-AI-03", "Verify Customer-Based Recommendations", AI, "Open Recommended for you after buying a product.", "Products similar to the purchase are listed with a 'Because you bought' reason."),
    ("TC-AI-04", "Verify Recommended Product Display", AI, "Open Recommended for you.", "Recommendation cards are shown, sorted by score, only active and in stock."),
    ("TC-AI-05", "Verify Recommended Product Details", AI, "Inspect one recommendation card.", "It shows the product name, category, image, price and similarity score."),
    ("TC-AI-06", "Verify Recommendation After Product View", AI, "View a product, then open Recommended for you.", "The top pick is similar to the viewed product with a 'Because you viewed' reason."),
    ("TC-AI-07", "Verify Recommendation After Adding Product to Cart", AI, "Add a product to the cart, then open Recommended for you.", "The top pick follows the cart product with a 'Because you added' reason; the cart product itself is not listed."),
    ("TC-AI-08", "Verify Recommendation for New Customer", AI, "Open Recommended for you as a brand-new customer.", "Popular products are shown, labelled Popularity."),
    # ---------------- End-to-end (brief: End-to-End Workflow Testing) ----------------
    ("E2E-01", "Customer Shopping Workflow", E2E, "Register, sign in, search, view a product, add to cart, submit, pay, see the confirmation, sign out.", "The order is Confirmed with the right total, stock is reduced, the cart is empty and an order email is written."),
    ("E2E-02", "AI Recommendation Workflow", E2E, "Sign in, view a product, open its similar products, open one and add it to the cart.", "The recommended product is in the cart."),
    ("E2E-03", "Admin Product Management Workflow", E2E, "Admin signs in, adds a category and a product, views, updates and deletes the product, signs out.", "Every step is reflected on screen and in the database."),
    ("E2E-04", "Order Management Workflow", E2E, "A customer places and pays an order, the admin ships it, the customer checks it.", "The customer sees the status the admin set."),
]

TEST_CASES: dict[str, dict] = {
    tc_id: {"test_name": name, "module": module, "test_description": description, "expected_result": expected}
    for tc_id, name, module, description, expected in _ROWS
}
