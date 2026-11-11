# Requirements Matrix

Every item in `docs/PROJECT_BRIEF.md` → where it is implemented → which test covers it → status.
Status values: **Planned** → **Implemented** → **Tested** (implemented and covered by a passing test).
"Implemented in" and "Covered by test" are filled in as each phase lands.

## A. Stack (brief: Website / Database / AI / Testing)
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| STK-01 | Front end: HTML5, CSS3, JavaScript, Bootstrap 5 | `templates/` (HTML5), `static/css/` (custom system over Bootstrap 5.3.8), `static/js/` | full browser suite (runs 2 and 3) | Tested |
| STK-02 | Server side: Python (Django) | Django 6.1.3 project `config/` + 9 apps |  | Implemented |
| STK-03 | IDE: Visual Studio Code | Project set up and edited in VS Code (Windows + PowerShell) |  | Implemented |
| STK-04 | Web server: Django development server | `python manage.py runserver`; pytest-django `live_server` for the tests | every browser test runs against the Django server | Tested |
| STK-05 | Database: SQLite | `db.sqlite3` (shop) + `reports.sqlite3` (tests), `config/settings.py` |  | Implemented |
| STK-06 | AI technique: content-based product recommendation | `recommender/engine.py` (content-based: product text similarity) | `tests/unit/test_engine.py`, `tests/ai/test_ai.py` | Tested |
| STK-07 | ML library: scikit-learn | requirements.txt (scikit-learn 1.9.1) | `tests/unit/test_engine.py` | Tested |
| STK-08 | Data processing: Pandas | requirements.txt (pandas 3.1.1) | `tests/unit/test_engine.py::test_explain_payload` | Tested |
| STK-09 | Feature extraction: TF-IDF vectorization | `recommender/engine.py` Engine._fit (TfidfVectorizer) | `tests/unit/test_engine.py::test_feature_matrix_shape` | Tested |
| STK-10 | Similarity: cosine similarity | `recommender/engine.py` (cosine_similarity) | `tests/unit/test_engine.py::test_scores_sorted_desc_and_reason` | Tested |
| STK-11 | Testing tool: Playwright (Python) | requirements.txt (playwright 1.64.1, pytest-playwright 0.10) | 69 browser tests in `tests/admin`, `tests/customer`, `tests/ai`, `tests/e2e` | Tested |
| STK-12 | Testing framework: Pytest | requirements.txt (pytest 9.2), `pytest.ini` | 185 tests (runs 2 and 3) | Tested |
| STK-13 | Browser: Chrome / Chromium | Playwright's Chromium (`python -m playwright install chromium`) | runs 2 (headless) and 3 (headed) | Tested |
| STK-14 | Test reporting: pytest-html | `pytest.ini` addopts `--html=reports/report.html --self-contained-html` | report written on every run | Tested |
| STK-15 | Screenshot capture: Playwright | `tests/conftest.py` pytest_runtest_makereport (screenshot on failure) | verified with a deliberate failure (screenshots/phase10/reports-detail-failed-1440.jpg); run removed afterwards | Tested |

## B. Admin features
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| ADM-01 | Login (username, password) — default admin credentials | `accounts/forms.AdminLoginForm`, `adminpanel/views/auth.py`, `create_default_admin` (.env) | `tests/unit/test_auth.py::test_admin_login_with_username`, `::test_invalid_admin_login_and_customer_account_refused` | Tested |
| ADM-02 | Dashboard: total_customers, total_categories, total_products, total_orders, total_sales | `adminpanel/services.dashboard_stats`, `adminpanel/views/dashboard.py` | `tests/unit/test_admin_services.py::test_dashboard_totals_count_only_paid_uncancelled_sales` | Tested |
| ADM-03 | Add Category (id, category_name, description, status, created_date) | `adminpanel/forms.CategoryForm`, `views/categories.category_create` | `test_admin_services.py::test_admin_creates_category_and_rejects_bad_product` | Tested |
| ADM-04 | View Categories | `views/categories.category_list` (search, pagination) | `test_admin_services.py::test_admin_pages_render_and_are_staff_only` | Tested |
| ADM-05 | Update Category | `views/categories.category_edit` | TC-ADM-06 | Implemented |
| ADM-06 | Delete Category | `catalog/services.delete_category` (blocked while products exist), `views/categories.category_delete` | `test_admin_services.py::test_category_with_products_cannot_be_deleted`, `::test_empty_category_is_deleted` | Tested |
| ADM-07 | Add Product (id, category_id, product_name, brand, price, description, image, quantity, keywords, added_date, status) | `adminpanel/forms.ProductForm` (image upload, price>0, qty>=0, MRP, sponsored), `views/products.product_create` | `test_admin_services.py::test_admin_creates_category_and_rejects_bad_product` | Tested |
| ADM-08 | View Products | `views/products.product_list` (filters) + `product_detail` | `test_admin_services.py::test_admin_pages_render_and_are_staff_only` | Tested |
| ADM-09 | Update Product | `views/products.product_edit` | TC-ADM-10 | Implemented |
| ADM-10 | Delete Product | `catalog/services.delete_product` (soft delete when ordered), `views/products.product_delete` | `test_admin_services.py::test_delete_product_with_orders_soft_deletes`, `::test_delete_product_without_orders_hard_deletes` | Tested |
| ADM-11 | View Customers (id, name, email, mobile_number, address, registered_date, status) | `views/customers.customer_list` / `customer_detail` | `test_admin_services.py::test_admin_pages_render_and_are_staff_only` | Tested |
| ADM-12 | Activate / Deactivate Customer | `accounts/services.set_customer_status`, `views/customers.customer_set_status` | `test_admin_services.py::test_admin_deactivates_customer` | Tested |
| ADM-13 | View Orders (id, order_id, customer_id, product_id, quantity, price, amount, order_date, order_status) | `orders/services/queries.order_groups`, `views/orders.order_list` (grouped ledger with all brief fields) | `test_admin_services.py::test_admin_pages_render_and_are_staff_only` | Tested |
| ADM-14 | Update Order Status (Pending, Confirmed, Shipped, Delivered, Cancelled) | `orders/services/status.set_order_status` (transitions; cancel restores stock), `views/orders.order_update_status` | `test_admin_services.py::test_status_moves_forward`, `::test_invalid_transition_rejected`, `::test_cancel_restores_stock_once` | Tested |
| ADM-15 | View Product Ratings / Reviews | `views/reviews.review_list` | `test_admin_services.py::test_admin_pages_render_and_are_staff_only` | Tested |
| ADM-16 | View Queries | `messaging/services.conversations_for`, `views/queries.query_inbox` | `test_admin_services.py::test_customer_cannot_see_other_thread` | Tested |
| ADM-17 | Post Query / Reply Query (id, conversation_id, sender_id, sender_type, receiver_id, receiver_type, parent_message_id, subject, message, posted_date, status) | `messaging/services.start_conversation` / `reply`, `views/queries.query_new` / `query_thread` | `test_admin_services.py::test_new_conversation_has_null_parent_and_reply_reuses_id` | Tested |
| ADM-18 | View Conversation History | `messaging/services.thread`, `templates/partials/thread.html` | `test_reviews_queries.py::test_admin_reply_shows_in_customer_thread_and_marks_read`; TC-ADM-21 (Phase 10) | Tested |
| ADM-19 | Logout | `adminpanel/views/auth.admin_logout` (POST) | TC-ADM-22 | Implemented |

## C. Customer features
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| CUS-01 | Registration (id, name, email, mobile_number, password, address, registered_date, status) | `accounts/forms.RegistrationForm`, `accounts/views.register`, `accounts/services.register_customer` | `tests/unit/test_auth.py::test_register_creates_active_customer` | Tested |
| CUS-02 | Login (email, password) | `accounts/backends.EmailBackend`, `accounts/views.login_view` | `tests/unit/test_auth.py::test_customer_login_with_email`, `::test_invalid_login_shows_generic_error` | Tested |
| CUS-03 | View Profile | `accounts/views.profile`, `templates/accounts/profile.html` | TC-CUS-04 | Implemented |
| CUS-04 | Update Profile | `accounts/forms.ProfileForm`, `accounts/views.profile_edit` | `tests/unit/test_auth.py::test_profile_update_keeps_email_unique` | Tested |
| CUS-05 | View Product Categories | `catalog/views.category_list`, `templates/catalog/categories.html` | `tests/unit/test_search.py::test_category_page_and_grid` | Tested |
| CUS-06 | Search Product (product_name, category, min_price, max_price) | `catalog/forms.ProductSearchForm`, `catalog/services.search_products` | `test_search.py::test_search_by_name_icontains`, `::test_search_by_category`, `::test_search_by_price_range`, `::test_combined_filters`, `::test_invalid_price_range_shows_error` | Tested |
| CUS-07 | View Products | `catalog/views.product_list` (pagination, sorting) | `test_search.py::test_sort_by_price`, `::test_empty_result_state` | Tested |
| CUS-08 | View Product Details (product_name, category, brand, price, description, image, available_quantity, rating) | `catalog/views.product_detail`, `templates/catalog/product_detail.html` | `test_search.py::test_product_detail_shows_fields_and_out_of_stock` | Tested |
| CUS-09 | View AI Recommended Products | `recommender/views.recommended` (/recommendations/) | `test_recommender_views.py`::test_recommended_requires_login, ::test_recommendations_follow_views_and_cart; TC-AI-03, TC-AI-04 | Tested |
| CUS-10 | Add to Cart (id, customer_id, product_id, quantity, added_date) | `orders/services/cart.add_to_cart`, `orders/views.cart_add` (JSON + form), `static/js/app.js` add-to-cart | `test_checkout_service.py::test_add_merges_lines_and_logs_cart_interaction`, `test_order_views.py::test_add_to_cart_json`; TC-CUS-12 (Phase 10) | Tested |
| CUS-11 | View Cart | `orders/services/cart.get_cart`, `orders/views.cart`, `templates/orders/cart.html` | `test_order_views.py::test_full_flow_pages`; TC-CUS-13 (Phase 10) | Tested |
| CUS-12 | Update Cart Quantity | `orders/services/cart.update_quantity`, `orders/views.cart_update` (live totals) | `test_checkout_service.py::test_cart_qty_cannot_exceed_stock`; TC-CUS-14 (Phase 10) | Tested |
| CUS-13 | Remove from Cart | `orders/services/cart.remove_item`, `orders/views.cart_remove` | `test_checkout_service.py::test_remove_item`; TC-CUS-15 (Phase 10) | Tested |
| CUS-14 | Submit Cart (id, order_id, product_id, customer_id, quantity, price, amount, order_date, order_status) | `orders/services/checkout.submit_cart`, `orders/views.checkout` | `test_checkout_service.py::test_submit_creates_one_row_per_item_with_shared_order_id`, `::test_amount_and_total`; TC-CUS-16 (Phase 10) | Tested |
| CUS-15 | Dummy Payment (id, order_id, customer_id, total_amount, payment_method, payment_status, payment_date) | `orders/services/payment.pay`, `orders/forms.PaymentForm`, `orders/views.payment` | `test_checkout_service.py::test_payment_success_confirms_and_clears_cart_and_emails`, `::test_payment_failure_keeps_pending`; TC-CUS-17 (Phase 10) | Tested |
| CUS-16 | View Order Confirmation | `orders/views.confirmation`, `templates/orders/confirmation.html` | `test_order_views.py::test_full_flow_pages`; TC-CUS-18 (Phase 10) | Tested |
| CUS-17 | Order Information Email | `orders/emails.send_order_email`, `templates/emails/order_confirmation.*` (file backend to `sent_emails/`) | `test_checkout_service.py::test_payment_success_confirms_and_clears_cart_and_emails`; E2E-01 (Phase 10) | Tested |
| CUS-18 | View Order History | `orders/views.history`, `orders/services/queries.order_groups` | `test_order_views.py::test_full_flow_pages`; TC-CUS-19 (Phase 10) | Tested |
| CUS-19 | View Order Details | `orders/views.detail` (+ `status_track`), `templates/orders/detail.html` | `test_order_views.py::test_full_flow_pages`, `::test_customer_cannot_open_another_customers_order`; TC-CUS-20 (Phase 10) | Tested |
| CUS-20 | Add Rating (id, product_id, customer_id, rating, posted_date) | `reviews/services.save_rating` (buyers only, update_or_create), `reviews/views.rate`, star picker in `templates/reviews/_feedback.html` | `test_reviews_queries.py::test_rating_is_updated_not_duplicated`, `::test_cannot_review_without_purchase`, `::test_rate_and_review_views`; TC-CUS-21 (Phase 10) | Tested |
| CUS-21 | Add Review (id, product_id, customer_id, review, posted_date) | `reviews/services.save_review` (buyers only, editable), `reviews/views.review`, `templates/reviews/_feedback.html` | `test_reviews_queries.py::test_review_is_updated_not_duplicated`, `::test_rate_and_review_views`; TC-CUS-22 (Phase 10) | Tested |
| CUS-22 | Post Query | `messaging/views.query_new` → `services.start_customer_query` (parent NULL, new conversation_id) | `test_reviews_queries.py::test_post_query_starts_a_conversation`, `::test_query_form_validates`; TC-CUS-23 (Phase 10) | Tested |
| CUS-23 | View Queries | `messaging/views.query_list` → `services.conversations_for` (own conversations, unread count) | `test_reviews_queries.py::test_customer_sees_only_own_conversations`; TC-CUS-24 (Phase 10) | Tested |
| CUS-24 | Reply Query | `messaging/views.query_thread` (POST) → `services.reply` | `test_reviews_queries.py::test_reply_reuses_conversation_id_and_points_to_parent`; TC-CUS-25 (Phase 10) | Tested |
| CUS-25 | View Conversation History | `messaging/views.query_thread` → `services.thread` + `mark_read`, `templates/messaging/thread.html` | `test_reviews_queries.py::test_admin_reply_shows_in_customer_thread_and_marks_read`; TC-CUS-26 (Phase 10) | Tested |
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
| AI-D1 | Product Features table (id, product_id, category, product_name, brand, description, keywords, price) | `recommender/models.py` ProductFeature | `test_engine.py`::test_feature_rows_follow_products | Tested |
| AI-D2 | Customer Product Interaction table (id, customer_id, product_id, interaction_type, interaction_date) | `recommender/models.py` CustomerProductInteraction; `recommender/interactions.log_interaction` (view) | `test_engine.py`::test_interest_weights_purchase_over_cart_over_view, `test_recommender_views.py`::test_recommendations_follow_views_and_cart | Tested |
| AI-F1 | Collect Product Information | `recommender/engine.py` build_frame, `recommender/features.py` (ProductFeature sync) | `test_engine.py`::test_feature_rows_follow_products; TC-AI-01 (Phase 10) | Tested |
| AI-F2 | Product Data Preprocessing | `recommender/engine.py` clean_text, weighted_document (Pandas) | `test_engine.py`::test_clean_text, ::test_explain_payload; TC-AI-01 | Tested |
| AI-F3 | Extract Product Features Using TF-IDF | `recommender/engine.py` Engine._fit (TfidfVectorizer), top_terms | `test_engine.py`::test_feature_matrix_shape, ::test_top_terms_include_keywords; TC-AI-01 | Tested |
| AI-F4 | Calculate Product Similarity Using Cosine Similarity | `recommender/engine.py` Engine (cosine_similarity matrix, cached by fingerprint) | `test_engine.py`::test_scores_sorted_desc_and_reason, ::test_engine_rebuilds_when_products_change; TC-AI-02 | Tested |
| AI-F5 | Identify Customer Interests (viewed_products, cart_products, purchased_products) | `recommender/engine.py` Engine.interests (purchase 3 > cart 2 > view 1, 14-day half-life) | `test_engine.py`::test_interest_weights_purchase_over_cart_over_view, `test_recommender_views.py`::test_recommendations_follow_views_and_cart; TC-AI-03/06/07 | Tested |
| AI-F6 | Generate Related Product Recommendations | `recommender/engine.py` Engine.similar | `test_engine.py`::test_similar_same_category_first; TC-AI-02 | Tested |
| AI-F7 | Generate Personalized Product Recommendations | `recommender/engine.py` Engine.personalized | `test_engine.py`::test_personalized_uses_interests_and_excludes_them; TC-AI-03 | Tested |
| AI-F8 | Display Recommended Products | `recommender/views.recommended`, home shelf (`core/views.home`), `templates/recommender/_rec_card.html` | `test_recommender_views.py`::test_recommendations_follow_views_and_cart, ::test_home_shows_popular_when_signed_out; TC-AI-04 | Tested |
| AI-F9 | View Similar Products | `templates/recommender/_similar.html` on the product page (`catalog/views.product_detail`) | `test_recommender_views.py`::test_product_page_shows_similar_products; TC-AI-02, E2E-02 | Tested |
| AI-O1 | Output: recommended product name | `_rec_card.html` (rec-name) | `test_recommender_views.py`::test_product_page_shows_similar_products; TC-AI-05 | Tested |
| AI-O2 | Output: product category | `_rec_card.html` (rec-category) | `test_recommender_views.py`::test_explainer_json; TC-AI-05 | Tested |
| AI-O3 | Output: product image | `_rec_card.html` (product image) | TC-AI-05 (Phase 10) | Implemented |
| AI-O4 | Output: product price | `_rec_card.html` (rec-price) | TC-AI-05 (Phase 10) | Implemented |
| AI-O5 | Output: product similarity score | `_rec_card.html` (rec-score bar + value, data-score) | `test_engine.py`::test_scores_sorted_desc_and_reason; TC-AI-05 | Tested |
| AI-O6 | Output: top recommended products | Top-N in `Engine.similar` / `personalized` (settings.RECOMMENDER) | `test_engine.py`::test_similar_same_category_first; TC-AI-04 | Tested |

## F. Test cases — Test Case table (id, test_name, module, test_description, expected_result)
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| TST-00 | Test Case catalogue table (id, test_name, module, test_description, expected_result) | `testreports/models.py` TestCase (reports DB) |  | Implemented |
| TC-ADM-01 | Admin Login | `tests/admin/test_admin.py::test_admin_login` | `tests/admin/test_admin.py::test_admin_login` (passed, runs 2 and 3) | Tested |
| TC-ADM-02 | Invalid Admin Login | `tests/admin/test_admin.py::test_invalid_admin_login` | `tests/admin/test_admin.py::test_invalid_admin_login` (passed, runs 2 and 3) | Tested |
| TC-ADM-03 | View Dashboard | `tests/admin/test_admin.py::test_view_dashboard` | `tests/admin/test_admin.py::test_view_dashboard` (passed, runs 2 and 3) | Tested |
| TC-ADM-04 | Add Category | `tests/admin/test_admin.py::test_add_category` | `tests/admin/test_admin.py::test_add_category` (passed, runs 2 and 3) | Tested |
| TC-ADM-05 | View Categories | `tests/admin/test_admin.py::test_view_categories` | `tests/admin/test_admin.py::test_view_categories` (passed, runs 2 and 3) | Tested |
| TC-ADM-06 | Update Category | `tests/admin/test_admin.py::test_update_category` | `tests/admin/test_admin.py::test_update_category` (passed, runs 2 and 3) | Tested |
| TC-ADM-07 | Delete Category | `tests/admin/test_admin.py::test_delete_category` | `tests/admin/test_admin.py::test_delete_category` (passed, runs 2 and 3) | Tested |
| TC-ADM-08 | Add Product | `tests/admin/test_admin.py::test_add_product` | `tests/admin/test_admin.py::test_add_product` (passed, runs 2 and 3) | Tested |
| TC-ADM-09 | View Products | `tests/admin/test_admin.py::test_view_products` | `tests/admin/test_admin.py::test_view_products` (passed, runs 2 and 3) | Tested |
| TC-ADM-10 | Update Product | `tests/admin/test_admin.py::test_update_product` | `tests/admin/test_admin.py::test_update_product` (passed, runs 2 and 3) | Tested |
| TC-ADM-11 | Delete Product | `tests/admin/test_admin.py::test_delete_product` | `tests/admin/test_admin.py::test_delete_product` (passed, runs 2 and 3) | Tested |
| TC-ADM-12 | View Customers | `tests/admin/test_admin.py::test_view_customers` | `tests/admin/test_admin.py::test_view_customers` (passed, runs 2 and 3) | Tested |
| TC-ADM-13 | Activate Customer | `tests/admin/test_admin.py::test_activate_customer` | `tests/admin/test_admin.py::test_activate_customer` (passed, runs 2 and 3) | Tested |
| TC-ADM-14 | Deactivate Customer | `tests/admin/test_admin.py::test_deactivate_customer` | `tests/admin/test_admin.py::test_deactivate_customer` (passed, runs 2 and 3) | Tested |
| TC-ADM-15 | View Orders | `tests/admin/test_admin.py::test_view_orders` | `tests/admin/test_admin.py::test_view_orders` (passed, runs 2 and 3) | Tested |
| TC-ADM-16 | Update Order Status | `tests/admin/test_admin.py::test_update_order_status` | `tests/admin/test_admin.py::test_update_order_status` (passed, runs 2 and 3) | Tested |
| TC-ADM-17 | View Product Ratings / Reviews | `tests/admin/test_admin.py::test_view_ratings_and_reviews` | `tests/admin/test_admin.py::test_view_ratings_and_reviews` (passed, runs 2 and 3) | Tested |
| TC-ADM-18 | View Queries | `tests/admin/test_admin.py::test_view_queries` | `tests/admin/test_admin.py::test_view_queries` (passed, runs 2 and 3) | Tested |
| TC-ADM-19 | Post Query | `tests/admin/test_admin.py::test_post_query` | `tests/admin/test_admin.py::test_post_query` (passed, runs 2 and 3) | Tested |
| TC-ADM-20 | Reply Query | `tests/admin/test_admin.py::test_reply_query` | `tests/admin/test_admin.py::test_reply_query` (passed, runs 2 and 3) | Tested |
| TC-ADM-21 | View Conversation History | `tests/admin/test_admin.py::test_view_conversation_history` | `tests/admin/test_admin.py::test_view_conversation_history` (passed, runs 2 and 3) | Tested |
| TC-ADM-22 | Logout | `tests/admin/test_admin.py::test_admin_logout` | `tests/admin/test_admin.py::test_admin_logout` (passed, runs 2 and 3) | Tested |
| TC-CUS-01 | Customer Registration | `tests/customer/test_account.py::test_customer_registration` | `tests/customer/test_account.py::test_customer_registration` (passed, runs 2 and 3) | Tested |
| TC-CUS-02 | Customer Login | `tests/customer/test_account.py::test_customer_login` | `tests/customer/test_account.py::test_customer_login` (passed, runs 2 and 3) | Tested |
| TC-CUS-03 | Invalid Customer Login | `tests/customer/test_account.py::test_invalid_customer_login` | `tests/customer/test_account.py::test_invalid_customer_login` (passed, runs 2 and 3) | Tested |
| TC-CUS-04 | View Profile | `tests/customer/test_account.py::test_view_profile` | `tests/customer/test_account.py::test_view_profile` (passed, runs 2 and 3) | Tested |
| TC-CUS-05 | Update Profile | `tests/customer/test_account.py::test_update_profile` | `tests/customer/test_account.py::test_update_profile` (passed, runs 2 and 3) | Tested |
| TC-CUS-06 | View Product Categories | `tests/customer/test_shopping.py::test_view_product_categories` | `tests/customer/test_shopping.py::test_view_product_categories` (passed, runs 2 and 3) | Tested |
| TC-CUS-07 | Search Product by Name | `tests/customer/test_shopping.py::test_search_product_by_name` | `tests/customer/test_shopping.py::test_search_product_by_name` (passed, runs 2 and 3) | Tested |
| TC-CUS-08 | Search Product by Category | `tests/customer/test_shopping.py::test_search_product_by_category` | `tests/customer/test_shopping.py::test_search_product_by_category` (passed, runs 2 and 3) | Tested |
| TC-CUS-09 | Search Product by Price | `tests/customer/test_shopping.py::test_search_product_by_price` | `tests/customer/test_shopping.py::test_search_product_by_price` (passed, runs 2 and 3) | Tested |
| TC-CUS-10 | View Products | `tests/customer/test_shopping.py::test_view_products` | `tests/customer/test_shopping.py::test_view_products` (passed, runs 2 and 3) | Tested |
| TC-CUS-11 | View Product Details | `tests/customer/test_shopping.py::test_view_product_details` | `tests/customer/test_shopping.py::test_view_product_details` (passed, runs 2 and 3) | Tested |
| TC-CUS-12 | Add to Cart | `tests/customer/test_shopping.py::test_add_to_cart` | `tests/customer/test_shopping.py::test_add_to_cart` (passed, runs 2 and 3) | Tested |
| TC-CUS-13 | View Cart | `tests/customer/test_shopping.py::test_view_cart` | `tests/customer/test_shopping.py::test_view_cart` (passed, runs 2 and 3) | Tested |
| TC-CUS-14 | Update Cart Quantity | `tests/customer/test_shopping.py::test_update_cart_quantity` | `tests/customer/test_shopping.py::test_update_cart_quantity` (passed, runs 2 and 3) | Tested |
| TC-CUS-15 | Remove from Cart | `tests/customer/test_shopping.py::test_remove_from_cart` | `tests/customer/test_shopping.py::test_remove_from_cart` (passed, runs 2 and 3) | Tested |
| TC-CUS-16 | Submit Cart | `tests/customer/test_shopping.py::test_submit_cart` | `tests/customer/test_shopping.py::test_submit_cart` (passed, runs 2 and 3) | Tested |
| TC-CUS-17 | Dummy Payment | `tests/customer/test_shopping.py::test_dummy_payment` | `tests/customer/test_shopping.py::test_dummy_payment` (passed, runs 2 and 3) | Tested |
| TC-CUS-18 | View Order Confirmation | `tests/customer/test_shopping.py::test_view_order_confirmation` | `tests/customer/test_shopping.py::test_view_order_confirmation` (passed, runs 2 and 3) | Tested |
| TC-CUS-19 | View Order History | `tests/customer/test_shopping.py::test_view_order_history` | `tests/customer/test_shopping.py::test_view_order_history` (passed, runs 2 and 3) | Tested |
| TC-CUS-20 | View Order Details | `tests/customer/test_shopping.py::test_view_order_details` | `tests/customer/test_shopping.py::test_view_order_details` (passed, runs 2 and 3) | Tested |
| TC-CUS-21 | Add Rating | `tests/customer/test_feedback_queries.py::test_add_rating` | `tests/customer/test_feedback_queries.py::test_add_rating` (passed, runs 2 and 3) | Tested |
| TC-CUS-22 | Add Review | `tests/customer/test_feedback_queries.py::test_add_review` | `tests/customer/test_feedback_queries.py::test_add_review` (passed, runs 2 and 3) | Tested |
| TC-CUS-23 | Post Query | `tests/customer/test_feedback_queries.py::test_post_query` | `tests/customer/test_feedback_queries.py::test_post_query` (passed, runs 2 and 3) | Tested |
| TC-CUS-24 | View Queries | `tests/customer/test_feedback_queries.py::test_view_queries` | `tests/customer/test_feedback_queries.py::test_view_queries` (passed, runs 2 and 3) | Tested |
| TC-CUS-25 | Reply Query | `tests/customer/test_feedback_queries.py::test_reply_query` | `tests/customer/test_feedback_queries.py::test_reply_query` (passed, runs 2 and 3) | Tested |
| TC-CUS-26 | View Conversation History | `tests/customer/test_feedback_queries.py::test_view_conversation_history` | `tests/customer/test_feedback_queries.py::test_view_conversation_history` (passed, runs 2 and 3) | Tested |
| TC-CUS-27 | Logout | `tests/customer/test_account.py::test_customer_logout` | `tests/customer/test_account.py::test_customer_logout` (passed, runs 2 and 3) | Tested |
| TC-AI-01 | Verify Product Feature Extraction | `tests/ai/test_ai.py::test_product_feature_extraction` | `tests/ai/test_ai.py::test_product_feature_extraction` (passed, runs 2 and 3) | Tested |
| TC-AI-02 | Verify Similar Product Recommendations | `tests/ai/test_ai.py::test_similar_product_recommendations` | `tests/ai/test_ai.py::test_similar_product_recommendations` (passed, runs 2 and 3) | Tested |
| TC-AI-03 | Verify Customer-Based Recommendations | `tests/ai/test_ai.py::test_customer_based_recommendations` | `tests/ai/test_ai.py::test_customer_based_recommendations` (passed, runs 2 and 3) | Tested |
| TC-AI-04 | Verify Recommended Product Display | `tests/ai/test_ai.py::test_recommended_product_display` | `tests/ai/test_ai.py::test_recommended_product_display` (passed, runs 2 and 3) | Tested |
| TC-AI-05 | Verify Recommended Product Details | `tests/ai/test_ai.py::test_recommended_product_details` | `tests/ai/test_ai.py::test_recommended_product_details` (passed, runs 2 and 3) | Tested |
| TC-AI-06 | Verify Recommendation After Product View | `tests/ai/test_ai.py::test_recommendation_after_product_view` | `tests/ai/test_ai.py::test_recommendation_after_product_view` (passed, runs 2 and 3) | Tested |
| TC-AI-07 | Verify Recommendation After Adding Product to Cart | `tests/ai/test_ai.py::test_recommendation_after_adding_to_cart` | `tests/ai/test_ai.py::test_recommendation_after_adding_to_cart` (passed, runs 2 and 3) | Tested |
| TC-AI-08 | Verify Recommendation for New Customer | `tests/ai/test_ai.py::test_recommendation_for_new_customer` | `tests/ai/test_ai.py::test_recommendation_for_new_customer` (passed, runs 2 and 3) | Tested |

| TC-NEG-01 | Duplicate email registration (extra negative) | `tests/customer/test_negative.py::test_duplicate_email_registration` | `tests/customer/test_negative.py::test_duplicate_email_registration` (passed, runs 2 and 3) | Tested |
| TC-NEG-02 | Deactivated customer login blocked (extra negative) | `tests/customer/test_negative.py::test_deactivated_customer_cannot_log_in` | `tests/customer/test_negative.py::test_deactivated_customer_cannot_log_in` (passed, runs 2 and 3) | Tested |
| TC-NEG-03 | Add out-of-stock product (extra negative) | `tests/customer/test_negative.py::test_out_of_stock_product_cannot_be_added` | `tests/customer/test_negative.py::test_out_of_stock_product_cannot_be_added` (passed, runs 2 and 3) | Tested |
| TC-NEG-04 | Cart quantity above stock (extra negative) | `tests/customer/test_negative.py::test_cart_quantity_cannot_exceed_stock` | `tests/customer/test_negative.py::test_cart_quantity_cannot_exceed_stock` (passed, runs 2 and 3) | Tested |
| TC-NEG-05 | Payment failure does not confirm (extra negative) | `tests/customer/test_negative.py::test_payment_failure_does_not_confirm` | `tests/customer/test_negative.py::test_payment_failure_does_not_confirm` (passed, runs 2 and 3) | Tested |
| TC-NEG-06 | Customer cannot open admin pages (extra negative) | `tests/customer/test_negative.py::test_customer_cannot_open_admin_pages` | `tests/customer/test_negative.py::test_customer_cannot_open_admin_pages` (passed, runs 2 and 3) | Tested |
| TC-NEG-07 | Customer cannot see another customer's conversation (extra negative) | `tests/customer/test_negative.py::test_customer_cannot_see_another_customers_conversation` | `tests/customer/test_negative.py::test_customer_cannot_see_another_customers_conversation` (passed, runs 2 and 3) | Tested |
| TC-NEG-08 | Invalid price and negative quantity rejected (extra negative) | `tests/customer/test_negative.py::test_invalid_price_and_negative_quantity_rejected` | `tests/customer/test_negative.py::test_invalid_price_and_negative_quantity_rejected` (passed, runs 2 and 3) | Tested |

## G. End-to-end scenarios
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| E2E-01 | Customer Shopping: Registration → Login → Search → View Product → Add to Cart → Submit Cart → Dummy Payment → Order Confirmation → Logout | `tests/e2e/test_workflows.py::test_customer_shopping_workflow` | `tests/e2e/test_workflows.py::test_customer_shopping_workflow` (passed, runs 2 and 3) | Tested |
| E2E-02 | AI Recommendation: Login → View Product → Generate AI Recommendations → View Recommended Products → Select Recommended Product → Add to Cart | `tests/e2e/test_workflows.py::test_ai_recommendation_workflow` | `tests/e2e/test_workflows.py::test_ai_recommendation_workflow` (passed, runs 2 and 3) | Tested |
| E2E-03 | Admin Product Management: Login → Add Category → Add Product → View Product → Update Product → Delete Product → Logout | `tests/e2e/test_workflows.py::test_admin_product_management_workflow` | `tests/e2e/test_workflows.py::test_admin_product_management_workflow` (passed, runs 2 and 3) | Tested |
| E2E-04 | Order Management: Customer Places Order → Admin Views Order → Admin Updates Order Status → Customer Views Updated Order Status | `tests/e2e/test_workflows.py::test_order_management_workflow` | `tests/e2e/test_workflows.py::test_order_management_workflow` (passed, runs 2 and 3) | Tested |

## H. Test execution reporting
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| REP-01 | Test Execution Report (id, test_case_id, execution_date, actual_result, status, execution_time, screenshot_path) | `testreports/models.py` TestExecution (reports DB) | `tests/unit/test_reports.py::test_record_run_creates_summary_and_executions` | Tested |
| REP-02 | Test Summary Report (id, execution_date, total_tests, passed_tests, failed_tests, skipped_tests, total_execution_time, report_path) | `testreports/models.py` TestSummary (reports DB) | `tests/unit/test_reports.py::test_record_run_creates_summary_and_executions` | Tested |
| REP-03 | Generate HTML Test Report | pytest-html via `pytest.ini`; a copy per run in `reports/runs/<run>/report.html`, linked from the admin page | runs 2 and 3 | Tested |
| REP-04 | View Passed Test Cases | `adminpanel/views/reports.report_detail` (?status=Passed) | `tests/unit/test_reports.py::test_report_pages` | Tested |
| REP-05 | View Failed Test Cases | `adminpanel/views/reports.report_detail` (?status=Failed) | `tests/unit/test_reports.py::test_report_pages` | Tested |
| REP-06 | Capture Screenshots for Failed Test Cases | `tests/conftest.py` (reports/screenshots/<run>/, embedded in the HTML report, path stored in TestExecution) | deliberate-failure check (Phase 10); `test_reports.py::test_report_pages` | Tested |
| REP-07 | View Test Execution Summary | `adminpanel/views/reports.report_list` (latest run summary + all runs) | `tests/unit/test_reports.py::test_report_pages` | Tested |

## I. Implementation rules
| ID | Brief item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| R1.1 | New customers register with Active status by default | `accounts/models.py` default Active; `register_customer` | `tests/unit/test_auth.py::test_register_creates_active_customer` | Tested |
| R1.2 | Customer email addresses must be unique | UniqueConstraint(Lower(email)) + `RegistrationForm.clean_email` / `ProfileForm.clean_email` | `test_models.py::test_duplicate_email_case_insensitive`, `test_auth.py::test_duplicate_email_case_insensitive` | Tested |
| R1.3 | Passwords stored with Django's secure password hashing | Django `User.set_password` via `create_user` | `tests/unit/test_auth.py::test_password_is_hashed` | Tested |
| R1.4 | Only authenticated customers access cart, checkout, order history, profile | `core/permissions.customer_required` | `tests/unit/test_auth.py::test_profile_requires_login` | Tested |
| R1.5 | Deactivated customers cannot log in | `EmailBackend`, `login_error_for`, `set_customer_status`, `ActiveCustomerMiddleware` | `test_auth.py::test_inactive_customer_cannot_login`, `::test_deactivated_session_is_logged_out` | Tested |
| R2.1 | Only Admin can add/update/delete categories and products | `core/permissions.admin_required` on every catalogue view | `test_admin_services.py::test_admin_pages_render_and_are_staff_only` | Tested |
| R2.2 | Each product belongs to one category | `catalog/models.py` Product.category FK (PROTECT) |  | Implemented |
| R2.3 | Product price must be greater than zero | `catalog/models.py` CheckConstraint price>0 | `tests/unit/test_models.py::test_price_must_be_positive` | Tested |
| R2.4 | Product quantity cannot be negative | `catalog/models.py` CheckConstraint quantity>=0 | `tests/unit/test_models.py::test_quantity_cannot_be_negative` | Tested |
| R2.5 | Zero-quantity products cannot be added to the cart | `orders/services/cart.add_to_cart` (CartError on zero stock), Add-to-cart button disabled on the product page | `test_checkout_service.py::test_add_to_cart_blocks_zero_stock` | Tested |
| R2.6 | Products with existing orders keep historical order info even if removed from listings | `catalog/services.delete_product` + Order.product_name/price snapshot | `test_admin_services.py::test_delete_product_with_orders_soft_deletes` | Tested |
| R3.1 | Engine uses category, name, brand, description, keywords | `recommender/engine.py` weighted_document (all five fields) | `test_engine.py`::test_explain_payload | Tested |
| R3.2 | TF-IDF converts product text into numeric feature vectors | `recommender/engine.py` Engine._fit (TfidfVectorizer) | `test_engine.py`::test_feature_matrix_shape | Tested |
| R3.3 | Cosine similarity calculates similarity between products | `recommender/engine.py` cosine_similarity | `test_engine.py`::test_scores_sorted_desc_and_reason | Tested |
| R3.4 | Recommends the most relevant products by similarity | `recommender/engine.py` Engine.similar (highest scores first) | `test_engine.py`::test_similar_same_category_first | Tested |
| R3.5 | Views, cart additions, purchases select products representing interests | `recommender/engine.py` Engine.interests; logging in `recommender/interactions.py` (view, cart, purchase) | `test_recommender_views.py`::test_recommendations_follow_views_and_cart | Tested |
| R3.6 | Recommendations generated from products similar to those interests | `recommender/engine.py` Engine.personalized (weighted average similarity) | `test_engine.py`::test_personalized_uses_interests_and_excludes_them | Tested |
| R3.7 | Already selected products excluded from their own results | `recommender/engine.py` similar (self excluded), personalized (interests + cart excluded) | `test_engine.py`::test_similar_excludes_self, ::test_personalized_uses_interests_and_excludes_them | Tested |
| R3.8 | Only active and available products recommended | `recommender/engine.py` available_ids() read live | `test_engine.py`::test_similar_excludes_inactive_and_out_of_stock | Tested |
| R3.9 | New customers get popular or category-based suggestions | `recommender/engine.py` popular() fallback (most ordered, then best rated) | `test_engine.py`::test_new_customer_gets_popular | Tested |
| R3.10 | Runs locally, no paid AI APIs | scikit-learn + Pandas in-process; no network calls | `test_engine.py` (runs offline) | Tested |
| R4.1 | Customers can add multiple products to cart | `orders/models.CartItem` (one line per product), `orders/services/cart` | `test_checkout_service.py::test_submit_creates_one_row_per_item_with_shared_order_id` | Tested |
| R4.2 | Cart quantity cannot exceed available stock | `orders/services/cart.add_to_cart` / `update_quantity` + re-check in `checkout.submit_cart` | `test_checkout_service.py::test_cart_qty_cannot_exceed_stock`, `::test_submit_rolls_back_when_one_item_short` | Tested |
| R4.3 | Each cart product inserted as a separate orders record | `orders/services/checkout.submit_cart` (one Order row per CartItem) | `test_checkout_service.py::test_submit_creates_one_row_per_item_with_shared_order_id` | Tested |
| R4.4 | All products of one checkout share a common order_id | `orders/services/checkout.new_order_id` shared by all rows of a checkout | `test_checkout_service.py::test_submit_creates_one_row_per_item_with_shared_order_id` | Tested |
| R4.5 | Each order record has its own unique id | `orders/models.py` Order (one row, own id) | `test_checkout_service.py::test_submit_creates_one_row_per_item_with_shared_order_id` | Tested |
| R4.6 | amount = price × quantity | `orders/models.py` Order.save() | `tests/unit/test_models.py::test_order_amount_is_price_times_quantity` | Tested |
| R4.7 | Total order amount calculated from all cart items | `orders/services/checkout.order_total` | `test_checkout_service.py::test_amount_and_total` | Tested |
| R4.8 | Cart submission + stock reservation in one DB transaction | `orders/services/checkout.submit_cart` (`transaction.atomic`, `select_for_update`, conditional F() decrement) | `test_checkout_service.py::test_stock_reserved_on_submit_and_cart_kept`, `::test_submit_rolls_back_when_one_item_short` | Tested |
| R4.9 | Payment confirmation must not create duplicate orders | `checkout_key` idempotency in `submit_cart`; `Payment` one_success_per_order constraint; `pay` returns the existing success | `test_checkout_service.py::test_resubmit_same_key_returns_same_order`, `::test_pay_twice_is_idempotent` | Tested |
| R4.10 | Cart cleared after successful order confirmation | `orders/services/payment.pay` clears the cart only on success | `test_checkout_service.py::test_stock_reserved_on_submit_and_cart_kept`, `::test_payment_success_confirms_and_clears_cart_and_emails` | Tested |
| R5.1 | Payment simulated, no real financial transactions | `orders/services/payment.pay` (records a Payment row only) | `test_checkout_service.py::test_payment_success_confirms_and_clears_cart_and_emails` | Tested |
| R5.2 | No real payment gateway | `orders/forms.PaymentForm` (method + simulated outcome, no gateway) | `test_order_views.py::test_full_flow_pages` | Tested |
| R5.3 | Payment success and failure can be simulated | `orders/forms.PaymentForm` outcome success/failure | `test_checkout_service.py::test_payment_success_confirms_and_clears_cart_and_emails`, `::test_payment_failure_keeps_pending` | Tested |
| R5.4 | After successful payment, order status → Confirmed | `orders/services/payment.pay` sets all rows of the order_id to Confirmed | `test_checkout_service.py::test_payment_success_confirms_and_clears_cart_and_emails` | Tested |
| R5.5 | Show order confirmation and send order info by email | `orders/views.confirmation` + `orders/emails.send_order_email` (on commit) | `test_checkout_service.py::test_payment_success_confirms_and_clears_cart_and_emails`, `test_order_views.py::test_full_flow_pages` | Tested |
| R5.6 | Failed payments do not mark orders paid/confirmed | `orders/services/payment.pay` failure path (status stays Pending, Payment row Failed) | `test_checkout_service.py::test_payment_failure_keeps_pending` | Tested |
| R6.1 | Single messages table stores queries and replies | `messaging/models.py` Message |  | Implemented |
| R6.2 | sender_type / receiver_type identify roles | `messaging/models.py` Message.sender_type / receiver_type |  | Implemented |
| R6.3 | conversation_id groups a conversation | `messaging/services.new_conversation_id` / `reply` | `test_admin_services.py::test_new_conversation_has_null_parent_and_reply_reuses_id` | Tested |
| R6.4 | parent_message_id identifies the message replied to | `messaging/services.reply` (parent = latest message) | `test_admin_services.py::test_new_conversation_has_null_parent_and_reply_reuses_id` | Tested |
| R6.5 | New conversation starts with parent_message_id = NULL | `messaging/services.start_conversation` (parent_message=None) | `test_admin_services.py::test_new_conversation_has_null_parent_and_reply_reuses_id` | Tested |
| R6.6 | Customers view only their own conversations | `messaging/services.ensure_can_view` / `conversations_for` | `test_admin_services.py::test_customer_cannot_see_other_thread`, `test_reviews_queries.py::test_customer_sees_only_own_conversations` (403 on view and reply) | Tested |
| R6.7 | Admin can view and respond to customer conversations | `adminpanel/views/queries.py` | `test_reviews_queries.py::test_admin_reply_shows_in_customer_thread_and_marks_read`; verified in the browser (Gate 7) | Tested |
| R7.1 | Playwright with Python automates browser functional tests | `tests/admin`, `tests/customer`, `tests/ai`, `tests/e2e` (Playwright sync API) | 69 browser tests passing | Tested |
| R7.2 | Pytest manages execution, fixtures, assertions | `tests/conftest.py` fixtures, `pytest.ini` markers, `tests/factories.py` | 185 tests passing | Tested |
| R7.3 | Tests verify expected vs actual behaviour | Each test asserts the catalogue's expected result; `actual_result` stored per execution | runs 2 and 3 | Tested |
| R7.4 | Positive and negative scenarios included | Positive tests plus `tests/customer/test_negative.py` (TC-NEG-01 to 08), TC-CUS-03, TC-ADM-02 | all passing | Tested |
| R7.5 | Reliable Playwright locators | get_by_role / get_by_label / get_by_text / get_by_test_id only; checked by grep (no CSS/XPath) | rules check, Phase 10.9 | Tested |
| R7.6 | Built-in waiting, no fixed delays | `expect(...)` auto-waiting; no `time.sleep` or fixed waits (checked by grep) | rules check, Phase 10.9 | Tested |
| R7.7 | Tests run independently with controlled test data | `tests/factories.py`; live_server flushes the test DB between tests | single tests pass alone (`-k`), full suite passes in random order | Tested |
| R7.8 | Tests must not modify production data | Separate test databases (test_db.sqlite3, test_reports.sqlite3) | db.sqlite3 checksum and row counts identical before and after a full run | Tested |
| R7.9 | Failed tests capture screenshots | `tests/conftest.py` screenshot hook | deliberate-failure check (Phase 10) | Tested |
| R7.10 | Reports keep Pass/Fail status and execution details | `testreports` models + `record_test_run` | `tests/unit/test_reports.py` | Tested |
| R7.11 | HTML reports via pytest-html | pytest-html 4.2.0 | runs 2 and 3 | Tested |
| R8.1 | E2E tests verify complete workflows | `tests/e2e/test_workflows.py` (E2E-01 to 04) | all passing | Tested |
| R8.2 | Verify visible behaviour and persisted results | E2E and customer tests assert the page AND the database rows | all passing | Tested |
| R8.3 | Checkout tests verify order totals and confirmation | TC-CUS-13, 16, 17, 18 and E2E-01 assert line amounts and totals | all passing | Tested |
| R8.4 | AI tests verify relevance to product / customer interests | `tests/ai/test_ai.py` asserts same category / shared keywords first, sorted scores, self and unavailable excluded | all passing | Tested |
| R8.5 | Headed and headless modes supported | `run_tests.ps1 -Headed -SlowMo`; pytest-playwright `--headed` | run 3 headed, run 2 headless | Tested |
| R8.6 | Repeatable on a local laptop | Everything local: SQLite, live_server, Chromium | runs on the owner's Windows laptop in about 40 s | Tested |
| R9.1 | Django Authentication for login/password management | `django.contrib.auth` + `accounts/backends.EmailBackend` |  | Implemented |
| R9.2 | Role-based authorization (Admin vs Customer) | `core/permissions.py` customer_required / admin_required | `test_auth.py::test_customer_cannot_open_admin`, `::test_admin_cannot_use_customer_pages`, `::test_guest_is_sent_to_admin_login` | Tested |
| R9.3 | CSRF protection on form submissions | CsrfViewMiddleware + `{% csrf_token %}` on every form | `tests/unit/test_auth.py::test_forms_carry_csrf_tokens` | Tested |
| R9.4 | Server-side input validation | Django forms in `accounts/forms.py` (server-side clean_* methods) | `tests/unit/test_auth.py::test_registration_rejects_bad_mobile_and_mismatched_passwords` | Tested |
| R9.5 | No hardcoded credentials in public source | `.env` (git-ignored) + `.env.example`; `config/settings.py` |  | Implemented |
| R9.6 | Default admin credentials changed before deployment (documented) | | | Planned |
| R10.1 | Whole app runs locally with Django | Django dev server (`manage.py runserver`), SQLite, local static and media | every browser test runs against the local server (runs 2 and 3) | Tested |
| R10.2 | SQLite stores data locally | `config/settings.py` DATABASES |  | Implemented |
| R10.3 | AI runs with locally installed Python libraries | scikit-learn + Pandas installed in `.venv`; no network calls in `recommender/` | `tests/unit/test_engine.py`, `tests/ai/test_ai.py` | Tested |
| R10.4 | Playwright + Pytest run on the same laptop | `run_tests.ps1` | runs 2 and 3 | Tested |
| R10.5 | Browser visible during automation (headed mode) | `run_tests.ps1 -Headed` | run 3 | Tested |
| R10.6 | HTML reports and failure screenshots stored locally | `reports/` (git-ignored): report.html, runs/, screenshots/ | runs 2 and 3 | Tested |
| R10.7 | No internet needed during demo (email simulated locally) | File email backend writes to `sent_emails/`; Bootstrap, GSAP, fonts and icons served from `static/` (no CDN URLs, checked by grep) | Gate 6 (order email file); E2E-01 checks the email | Tested |

## J. Must-have extras (CLAUDE.md §2)
| ID | Item | Implemented in | Covered by test | Status |
|---|---|---|---|---|
| EXT-01 | Sponsored / featured deals carousel with hover quick-view card; admin sponsored toggle | `templates/core/home.html` (Sponsored deals), `static/js/sponsored.js` (drift, pause on hover/focus/quick view, prev/next, pause button, reduced-motion rail), `static/js/quickview.js` + `catalog/views.quick_view` (hover quick-view card: image, price, rating, stock, Add to cart), admin toggle `adminpanel/views/products.product_toggle_sponsored` | `test_recommender_views.py::test_home_sections`; browser check Phase 9 (screenshots/phase9/home-quickview-1440.jpg); Playwright test in Phase 10 | Implemented |
| EXT-02 | AI Explainer page (step-by-step, animated, Next/Back) | `recommender/views.explainer`, `templates/recommender/explainer.html`, `static/js/explainer.js` (GSAP, Back/Next, step buttons, arrow keys, Play/Pause, reduced motion) | `test_recommender_views.py`::test_explainer_page_is_public_and_follows_the_choice, ::test_explainer_json | Tested |
| EXT-03 | Admin Test Reports page | `adminpanel/views/reports.py`, `templates/adminpanel/reports/` (runs, filters, timings, screenshots, HTML report links) | `tests/unit/test_reports.py` (4 tests); screenshots/phase10/ | Tested |
| EXT-04 | docs/CODE_MAP.md | | | Planned |
