# Page inventory

One line per page: purpose → URL → template. Role: **P** public, **C** customer (logged-in, active), **A** admin (staff).

## Customer side (storefront)
| Page | Role | URL | Purpose |
|---|---|---|---|
| Home | P | `/` | Show what's worth buying today: hero offer, sponsored deals strip with quick view, the 10 categories, "Recommended for you" (personalised or popular), best sellers, new arrivals. |
| Categories | P | `/categories/` | All 10 categories as a grid with counts and a representative product image. |
| Category listing | P | `/category/<slug>/` | One category's products with filters (price, brand, in stock), sort and pagination. |
| Search / results | P | `/products/?product_name=&category=&min_price=&max_price=&sort=` | Search by name, category, price range (combinable); results grid, applied-filter chips, empty state. Also serves "View products". |
| Product detail | P | `/product/<slug>/` | Everything a buyer needs: image, name, brand, category, price, availability, average rating, description, quantity + Add to cart, reviews, similar products (AI). Logs a view. |
| Cart | C | `/cart/` | Review items, change quantity (bounded by stock), remove items, see totals, go to checkout. |
| Checkout | C | `/checkout/` | Confirm items, delivery address (from profile) and total; "Place order" submits the cart (creates Pending orders). |
| Payment | C | `/checkout/pay/<order_id>/` | Dummy payment: choose method, simulate Success or Failure; retry after failure. |
| Order confirmation | C | `/orders/<order_id>/confirmed/` | Thank-you page: order id, items, total, status Confirmed, email sent note. |
| Order history | C | `/orders/` | All the customer's orders grouped by order_id with status badges and totals. |
| Order details | C | `/orders/<order_id>/` | Rows of one order, status, payment, rating/review links for eligible items. |
| Profile | C | `/account/` | View and update name, email, mobile number, address; see registered date and status. |
| Queries | C | `/queries/` | The customer's own conversations with admin (subject, last message, unread). |
| New query | C | `/queries/new/` | Post a question to the store (starts a conversation). |
| Conversation | C | `/queries/<conversation_id>/` | Threaded messages + reply box. |
| AI recommendations | C | `/recommendations/` | "View AI Recommended Products": personalised picks with score and reason (popular for new customers). |
| AI Explainer | P (personal panel C) | `/ai/explainer/?product=<id>` | Step-by-step, animated: raw text → cleaned text → TF-IDF terms → cosine scores → top-N; plus how the customer's own recommendations were made. |
| Login | P | `/account/login/` | Customer login with email + password. |
| Register | P | `/account/register/` | Customer registration (all brief fields). |
| Rate/review (inline) | C | `/product/<slug>/review/` (POST) | Add/update rating and review for a purchased product (form lives on product detail). |
| 403 / 404 | P | — | Friendly, on-brand error pages with a way back. |

## Admin side (`/manage/`)
| Page | Role | URL | Purpose |
|---|---|---|---|
| Admin login | P | `/manage/login/` | Username + password for staff. |
| Dashboard | A | `/manage/` | total_customers, total_categories, total_products, total_orders, total_sales; recent orders; 14-day orders/sales chart. |
| Categories | A | `/manage/categories/` | List + search; add, edit, delete (blocked while products exist). |
| Category form | A | `/manage/categories/new/`, `/<id>/edit/` | Create/update a category (name, description, status). |
| Products | A | `/manage/products/` | List with filters (category, status, stock, sponsored, search); sponsored toggle; delete (soft when ordered). |
| Product form | A | `/manage/products/new/`, `/<id>/edit/` | All brief product fields + image upload + sponsored. |
| Customers | A | `/manage/customers/` | List with search/status filter; activate/deactivate. |
| Customer detail | A | `/manage/customers/<id>/` | Profile fields, orders, status toggle. |
| Orders | A | `/manage/orders/` | Orders grouped by order_id, expandable rows, filter by status; update status. |
| Order detail | A | `/manage/orders/<order_id>/` | Rows (id, order_id, customer_id, product_id, quantity, price, amount, order_date, order_status), payments, status form. |
| Ratings & reviews | A | `/manage/reviews/` | All ratings and reviews with product, customer and date. |
| Queries inbox | A | `/manage/queries/` | All conversations, unread first; post a new query to a customer. |
| New query | A | `/manage/queries/new/` | Admin starts a conversation with a chosen customer. |
| Conversation | A | `/manage/queries/<conversation_id>/` | Full thread + reply. |
| Test reports | A | `/manage/test-reports/` | Test runs (summaries), filter Passed/Failed/Skipped, timings, screenshots, link to HTML report. |
| Test run detail | A | `/manage/test-reports/<id>/` | Executions of one run with status, time, actual result, screenshot. |
