# Security check (Phase 12.4)

Date: 14 Nov 2026. Every item below was checked by a script or command on that date, not by reading the code.

| Check | How | Result |
|---|---|---|
| Secrets never committed | `git log --all -- .env`; every secret value in the local `.env` (SECRET_KEY, ADMIN_PASSWORD, DEMO_CUSTOMER_PASSWORD) searched across all 28 commits with `git grep` | `.env` never committed; no secret value anywhere in the history |
| `.env.example` complete | Every `os.getenv` / `env_bool` / `env_list` key read by the code compared with the keys in `.env.example` | All 15 keys present (the optional `ASSET_VERSION` added as a commented example) |
| SECRET_KEY | `config/settings.py` | Read from `.env`; the app refuses to start without one (no insecure default) |
| DEBUG | `config/settings.py` | Read from `.env` with `env_bool("DEBUG", False)`: off unless set |
| CSRF | `CsrfViewMiddleware` in settings; search for `csrf_exempt`; every `<form method="post">` in `templates/` | Middleware on; 0 exemptions; all 26 POST forms carry `{% csrf_token %}` (cart and quick-view fetch calls send the token too) |
| Role checks on every view | Walked all 55 URL patterns and read each view's decorator chain | 24 admin views behind `admin_required`, 17 customer views behind `customer_required`, 14 public by design (home, catalogue and product pages, quick view, AI Explainer, register, the two login pages, the two logout views, product photos) |
| Logout | `accounts/views.py`, `adminpanel/views/auth.py` | Both POST-only, so a link or prefetch can't sign anyone out |
| Customers vs admin | Browser tests TC-NEG-06 (customer on `/manage/` → 403), TC-NEG-07 (another customer's conversation → 403), `test_auth.py` | Pass (run 6) |
| Passwords | `tests/unit/test_auth.py::test_password_is_hashed` | Stored hashed by Django; plain text never stored |
| Report files | `adminpanel/views/reports.report_file`; `tests/unit/test_reports.py::test_report_file_view_stays_inside_reports` | Staff only; paths outside `reports/` are refused (404) |
| Django deployment check | `DEBUG=False python manage.py check --deploy` | Only the HTTPS warnings W004 (HSTS), W008 (SSL redirect), W012 (secure session cookie), W016 (secure CSRF cookie). Expected for a local HTTP demo; turning them on would break plain-HTTP use. A real deployment must enable them, as the README's limitations say. |
