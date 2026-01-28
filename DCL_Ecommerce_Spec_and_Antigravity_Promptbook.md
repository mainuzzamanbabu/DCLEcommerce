# DCL Ecommerce — Full Specification + Google Antigravity Promptbook (Django Templates + Bootstrap)

> **Project:** DCL Ecommerce  
> **Domain:** IT products (PCs, laptops, components, peripherals, networking, accessories, software license keys)  
> **Stack:** Django (Templates), Bootstrap 5, PostgreSQL, Redis (optional), Celery (optional)  
> **Goal:** A production-grade, modern-looking, full-feature eCommerce site with a powerful admin/CMS customization layer.

---

## 1) Product Vision

**DCL Ecommerce** is a modern IT-focused online store built with Django Templates and Bootstrap. It supports the full commerce lifecycle:

- Browse → Search/Filter → Product detail/variant selection → Cart → Checkout → Payment → Order fulfillment → Returns/refunds → Support
- Admin-managed catalog, inventory, pricing, promotions, CMS pages, homepage sections, banners, and customer management.

---

## 2) Core Requirements

### 2.1 Must-have
- Django template-based frontend (no SPA required)
- Responsive, modern UI using **Bootstrap 5**
- Full eCommerce functionality:
  - Product catalog, categories, brands, product variants
  - Stock/inventory tracking
  - Cart (guest + logged-in)
  - Checkout (address + shipping + payment)
  - Orders (status tracking, invoices)
  - Coupons/discounts
  - Reviews/ratings
  - Wishlist
- Authentication: register/login/logout/password reset
- Admin panel for:
  - CMS (pages, banners, menus, footer links, homepage sections)
  - Product management (CRUD, images, variants, stock)
  - User management
  - Orders, payments, shipping statuses
  - Promotions, coupons, featured products
- SEO-ready (meta tags, sitemap, clean URLs)
- Security best practices (CSRF, secure cookies, rate limiting, audit logs)

### 2.2 Nice-to-have (planned but designed into architecture)
- PC Builder / Custom PC configurator (compatibility rules)
- Compare products
- Multi-warehouse stock
- Digital product license keys (software keys) with auto-delivery on paid orders
- Blog/News (CMS)
- Analytics dashboard for admin
- Abandoned cart emails
- Multi-currency (at least structure-ready)

---

## 3) Tech Stack

### 3.1 Backend
- **Django (latest stable recommended for your environment)**
- Django Templates
- PostgreSQL (recommended) / SQLite (dev only)
- Redis + Celery (recommended for email jobs, payment webhooks processing, background tasks)

### 3.2 Frontend
- Bootstrap 5
- Bootstrap Icons
- Minimal vanilla JS for UI behavior (toasts, modals, variant selection, cart qty updates)

### 3.3 Storage
- Local media in development
- S3-compatible storage in production (optional)

### 3.4 Payments
Choose one primary provider and keep the architecture provider-agnostic:
- Stripe (global)
- SSLCommerz (Bangladesh-friendly)
- Cash on Delivery (COD)
- Bank Transfer (manual verification)

---

## 4) System Architecture

### 4.1 Django Project Layout (recommended)
```
dcl-ecommerce/
  manage.py
  pyproject.toml (or requirements.txt)
  README.md
  .env.example
  dcl_ecommerce/                # Django project settings
    settings/
      base.py
      dev.py
      prod.py
    urls.py
    wsgi.py
    asgi.py

  apps/
    core/                       # site settings, menus, homepage blocks
    accounts/                   # custom user, profile, addresses
    catalog/                    # categories, brands, products, variants, inventory
    pricing/                    # price rules, sale prices, tax
    cart/                       # session cart + persistent cart
    checkout/                   # shipping methods, checkout orchestration
    orders/                     # orders, order items, statuses, invoices
    payments/                   # payment intents, providers, webhooks
    promotions/                 # coupons, campaigns, featured, bundles
    cms/                        # pages, blog posts, banners, content blocks
    reviews/                    # product reviews & moderation
    wishlist/                   # wishlists
    support/                    # contact tickets, FAQs
    pc_builder/                 # optional flagship feature

  templates/
    base.html
    partials/
    pages/
    catalog/
    checkout/
    accounts/
    cms/
  static/
    css/
    js/
    img/
  media/
  locale/                       # optional i18n
  tests/
  docker/
  docker-compose.yml
  .agent/                       # Antigravity customizations (rules, workflows, skills)
```

### 4.2 App Boundaries (why this matters)
- **catalog** owns product truth: what exists, specs, variants, stock units
- **pricing** owns price computation: base price, sale price, coupon application hooks, tax, shipping price rules
- **cart** is a pure “intent”: items + quantities + chosen variants
- **checkout** validates cart, locks pricing snapshot, collects address & shipping
- **orders** is the “source of truth” after checkout: immutable snapshots
- **payments** coordinates provider integration & webhooks; never changes orders directly without service layer

---

## 5) Roles & Permissions

### 5.1 Roles
- **Customer**
- **Staff** (customer support / order processing)
- **Catalog Manager** (products, categories, inventory)
- **Marketing Manager** (coupons, banners, CMS)
- **Super Admin** (everything)

### 5.2 Permission Model
Use Django Groups + Permissions:
- Groups map to roles
- Admin UI checks permissions
- Staff-only custom dashboard pages require permission checks

---

## 6) Data Model (Database Schema)

> Keep models clean, normalized, and scalable. Use UUIDs for public-facing IDs (optional but recommended).

### 6.1 accounts app
**User (Custom)**
- email (unique), username (optional), phone (optional)
- is_verified_email, is_verified_phone
- is_active, is_staff, is_superuser
- date_joined, last_login

**CustomerProfile**
- user (OneToOne)
- full_name, avatar
- marketing_opt_in
- default_shipping_address (FK)
- default_billing_address (FK)

**Address**
- user (FK)
- label (Home/Office)
- full_name, phone
- country, city, area
- address_line1, address_line2
- postal_code
- is_default_shipping, is_default_billing

### 6.2 catalog app
**Category**
- name, slug, parent (self FK), is_active
- description, image
- seo_title, seo_description

**Brand**
- name, slug, logo, is_active

**Product**
- name, slug
- product_type: PHYSICAL | DIGITAL
- category (FK), brand (FK)
- short_description, description (HTML allowed or Markdown)
- is_active, is_featured
- warranty_months
- seo_title, seo_description
- created_at, updated_at

**ProductImage**
- product (FK)
- image
- alt_text
- sort_order
- is_primary

**ProductAttribute** (for IT specs)
- name (e.g., CPU, RAM, Storage, GPU, Display, PSU Wattage, Socket)
- data_type (text, int, decimal, bool, choice)
- unit (optional)

**ProductVariant**
- product (FK)
- sku (unique)
- variant_name (e.g., “16GB RAM / 512GB SSD”)
- attributes (JSONField or M2M to VariantAttributeValue)
- barcode (optional)
- is_active
- weight_kg (optional)

**VariantInventory**
- variant (OneToOne)
- stock_qty
- reserved_qty
- low_stock_threshold

**DigitalLicenseKey** (if DIGITAL)
- product (FK) or variant (FK)
- key (encrypted at rest if possible)
- is_assigned
- assigned_order_item (FK nullable)

### 6.3 pricing app
**Price**
- variant (OneToOne)
- currency (e.g., BDT)
- list_price (MRP)
- sale_price (nullable)
- cost_price (optional)
- tax_class

**TaxClass**
- name
- rate_percent
- country (optional)

### 6.4 cart app
**Cart**
- user (nullable FK)
- session_key (nullable)
- created_at, updated_at

**CartItem**
- cart (FK)
- variant (FK)
- quantity
- unit_price_snapshot (Decimal)
- subtotal_snapshot (Decimal)

### 6.5 checkout app
**ShippingMethod**
- name
- base_cost
- free_over_amount (nullable)
- estimated_days_min, estimated_days_max
- is_active

**CheckoutSession**
- cart (FK)
- shipping_address (FK)
- billing_address (FK)
- shipping_method (FK)
- coupon_code (nullable)
- totals_snapshot (JSON)
- status: DRAFT | READY | COMPLETED | EXPIRED

### 6.6 orders app
**Order**
- order_number (unique, human-friendly)
- user (nullable FK)
- email, phone
- shipping_address_snapshot (JSON)
- billing_address_snapshot (JSON)
- subtotal, discount_total, shipping_total, tax_total, grand_total
- payment_status: UNPAID | PAID | PARTIALLY_REFUNDED | REFUNDED | FAILED
- fulfillment_status: NEW | PROCESSING | PACKED | SHIPPED | DELIVERED | CANCELED | RETURN_REQUESTED | RETURNED
- notes (admin), customer_note
- created_at, updated_at

**OrderItem**
- order (FK)
- product_name_snapshot
- variant_name_snapshot
- sku_snapshot
- unit_price, quantity, line_total
- is_digital
- digital_delivery_status: PENDING | DELIVERED (if applicable)

**OrderStatusHistory**
- order (FK)
- from_status, to_status
- changed_by (FK user)
- note
- created_at

### 6.7 payments app
**PaymentTransaction**
- order (FK)
- provider: STRIPE | SSLCOMMERZ | COD | BANK
- provider_ref (payment intent id / transaction id)
- amount
- status: INITIATED | AUTHORIZED | CAPTURED | FAILED | REFUNDED
- raw_response (JSON)
- created_at, updated_at

**WebhookEvent**
- provider
- event_id
- payload (JSON)
- processed_at
- status: RECEIVED | PROCESSED | FAILED

### 6.8 cms app
**SiteSettings** (Singleton)
- site_name = “DCL Ecommerce”
- logo, favicon
- primary_color (optional), secondary_color (optional)
- top_announcement_text
- support_email, support_phone, address_text
- social_links (JSON)
- seo_default_title, seo_default_description

**Menu**
- name (Header/Main/Footer)
- is_active

**MenuItem**
- menu (FK)
- label
- url or page (FK)
- sort_order
- open_in_new_tab

**Page**
- title, slug
- content (rich text)
- is_published
- seo_title, seo_description

**Banner**
- title
- image
- link_url
- placement: HOME_HERO | HOME_MIDDLE | CATEGORY_TOP | FOOTER
- start_at, end_at
- is_active

**HomepageSection**
- title
- section_type: FEATURED_CATEGORIES | TRENDING | NEW_ARRIVALS | DEALS
- config (JSON: chosen categories/products)
- sort_order
- is_active

### 6.9 reviews app
**Review**
- user (FK)
- product (FK)
- rating (1-5)
- title, body
- is_approved
- created_at

### 6.10 wishlist app
**Wishlist**
- user (FK)
- name
- created_at

**WishlistItem**
- wishlist (FK)
- variant (FK)
- created_at

### 6.11 pc_builder app (optional flagship)
**ComponentType**
- name: CPU, GPU, RAM, Motherboard, PSU, Case, Storage
- sort_order

**CompatibilityRule**
- rule_type (e.g., SOCKET_MATCH, PSU_WATTAGE_MIN, RAM_TYPE_MATCH)
- config JSON
- is_active

**Build**
- user (nullable)
- name
- selected_components JSON (component_type -> variant_id)
- validation_result JSON
- created_at, updated_at

---

## 7) Business Logic & Key Flows

### 7.1 Catalog Browsing
- Category list → category detail with filters:
  - Brand
  - Price range
  - Rating
  - Key attributes (RAM, CPU, Storage, GPU, Screen size)
- Product detail:
  - Variant selection
  - Stock indicator
  - Warranty info
  - Shipping estimate
  - Related products (same category/brand)
  - Reviews summary + add review

### 7.2 Cart
- Guest cart in session
- Merge cart on login (guest items → user cart)
- Update qty, remove items, save for later (optional)
- Show shipping estimate & coupon input

### 7.3 Checkout
Steps:
1. Login/register or guest checkout
2. Shipping address
3. Billing address (same as shipping toggle)
4. Choose shipping method
5. Apply coupon
6. Choose payment method
7. Place order → create Order + OrderItems (snapshots)
8. Payment confirmation → update statuses
9. Confirmation page + email

### 7.4 Payments
- Provider-agnostic service interface:
  - create_payment(order) → returns redirect URL or payment intent
  - handle_webhook(payload) → updates PaymentTransaction + Order payment_status
- COD:
  - marks PaymentTransaction as INITIATED and Order as UNPAID but accepted
- Stripe/SSLCommerz:
  - webhook updates Order to PAID upon captured/paid event

### 7.5 Inventory Reservation
- On checkout confirmation:
  - reserve stock (increase reserved_qty)
- On payment success:
  - decrement stock_qty, decrement reserved_qty
- On payment failure/timeout:
  - release reserved_qty

---

## 8) UI/UX Pages (Bootstrap 5)

### 8.1 Public Pages
- Home
  - Hero slider (Banner HOME_HERO)
  - Featured categories
  - Trending products
  - Deals section
  - Brand logos strip
  - Newsletter signup
- Catalog
  - Category listing
  - Product grid with filters
  - Product detail page
- Search
  - Search bar + suggestions (optional)
- Cart
- Checkout
- Auth pages
- Account dashboard
  - Profile
  - Addresses
  - Orders list/detail
  - Wishlist
- CMS pages
  - About, Contact, Shipping Policy, Return Policy, Privacy Policy, Terms

### 8.2 Design Rules (Bootstrap)
- Use a consistent spacing scale (Bootstrap utilities)
- Use:
  - sticky navbar
  - mega menu for categories (optional)
  - offcanvas cart preview (optional)
  - toasts for “Added to cart”
- Product cards:
  - primary image, name, price, rating, quick add
- Ensure:
  - accessible labels
  - keyboard navigable menus/forms
  - proper contrast

---

## 9) Admin Panel & CMS Controls

### 9.1 Django Admin Enhancements
- Admin “dashboard” landing (custom AdminSite index)
- Inline editing:
  - Product images inline
  - Variants inline
  - Inventory inline
- Filters & search:
  - orders by status/date/payment status
  - products by category/brand/is_active/is_featured
- Bulk actions:
  - mark featured/unfeatured
  - export orders CSV
  - activate/deactivate banners
- Moderation queue:
  - reviews pending approval
  - contact requests/tickets

### 9.2 CMS (Admin-manageable “everything”)
- SiteSettings for:
  - name, logo, contact, SEO default
- Menus:
  - header/footer link management
- Pages:
  - create/edit/publish pages
- Homepage sections:
  - reorder sections
  - choose featured categories/products
- Banners:
  - schedule start/end
  - placement selection

---

## 10) SEO, Performance, and Security

### 10.1 SEO
- Clean slugs for product/category/page
- Meta title/description on:
  - product pages
  - categories
  - CMS pages
- XML sitemap
- robots.txt
- Canonical URLs
- OpenGraph tags for social sharing
- Structured data (JSON-LD) for Product

### 10.2 Performance
- Optimized images (use thumbnail generation)
- Cache:
  - homepage sections
  - category pages
- DB indexes:
  - Product.slug, Category.slug, Variant.sku, Order.order_number
- Static handling:
  - WhiteNoise (simple deployments)

### 10.3 Security
- CSRF enabled
- Secure cookie settings in production
- Rate limiting on login & checkout endpoints
- Validate webhook signatures for payment providers
- Audit logs for admin changes (optional but recommended)

---

## 11) Testing Strategy

### 11.1 Unit Tests
- Models:
  - slug generation
  - pricing computations
- Services:
  - cart merge
  - coupon application
  - inventory reservation
  - payment provider abstraction

### 11.2 Integration Tests
- Checkout flow end-to-end
- Payment webhook processing
- Admin permissions

### 11.3 UI/Smoke Tests
- Run Django test client
- Optional Playwright for UI

---

## 12) Deployment Strategy (Production Ready)

### 12.1 Recommended
- Docker + docker-compose:
  - web (Django + Gunicorn)
  - db (Postgres)
  - redis
  - worker (celery)
  - nginx (static/media reverse proxy)

### 12.2 Environment Variables
- DJANGO_SECRET_KEY
- DJANGO_DEBUG=false
- DJANGO_ALLOWED_HOSTS
- DATABASE_URL
- REDIS_URL
- EMAIL_HOST/EMAIL_USER/EMAIL_PASS
- STRIPE_PUBLIC_KEY / STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET (if Stripe)
- SSLCOMMERZ_STORE_ID / SSLCOMMERZ_STORE_PASS / SSLCOMMERZ_SANDBOX (if SSLCommerz)

---

# 13) Google Antigravity Promptbook (How to build this with agent skills)

This section is written so you can paste prompts into Antigravity and let agents build the full system.

## 13.1 Recommended Antigravity Working Style
1. Start in **Planning** mode:
   - Ask for a full implementation plan + task breakdown
2. Approve the plan
3. Let the agent implement in small batches:
   - “Build catalog models + admin + templates”
   - “Then build cart”
   - “Then build checkout”
4. After each major feature:
   - Run tests
   - Run dev server
   - Do a short UI review

---

## 13.2 Master “Spec Prompt” (Paste this first)

**Prompt:**
You are building a full Django Template-based eCommerce site named “DCL Ecommerce” (IT products).
Follow this spec exactly:
- Use Django templates + Bootstrap 5 for UI (modern design, responsive)
- Implement apps: accounts, catalog, pricing, cart, checkout, orders, payments, promotions, cms, reviews, wishlist, support (pc_builder optional)
- Implement full admin customization:
  - Products/variants/images/inventory
  - Orders/payment tracking
  - CMS pages, menus, banners, homepage sections, site settings
- Use service layer patterns for pricing, checkout, inventory reservation, payment provider interface
- Use Postgres-ready schema; dev can run on sqlite
- Implement SEO basics (meta tags, sitemap, robots.txt)
- Deliver code with tests and clean structure

Output requirements:
1) A complete implementation plan (phases, milestones)
2) A precise file/folder structure
3) Step-by-step tasks the agent will execute
4) Then start implementing immediately, running migrations and tests as you go.

---

## 13.3 Phase Prompts (Use after the Master Prompt)

### Phase A — Project scaffold + core settings
**Prompt:**
Scaffold the Django project and apps. Set up:
- custom user model (email login)
- settings split (dev/prod)
- base templates + Bootstrap integration
- static/media setup
- initial home page route
- create superuser and confirm admin works

Acceptance: I can run server, see home page, login admin.

---

### Phase B — Catalog (products, categories, variants, inventory) + Admin
**Prompt:**
Implement catalog domain:
- Category, Brand, Product, ProductVariant, ProductImage, Inventory models
- Admin with inlines and filters
- Public pages:
  - category listing
  - product listing with pagination
  - product detail with variant selection and add-to-cart

Acceptance: I can add products in admin and view them on the site.

---

### Phase C — Cart (guest + user merge)
**Prompt:**
Implement cart:
- session cart for guests
- persistent cart for logged-in users
- merge cart on login
- cart page with update qty/remove
- bootstrap toasts for add-to-cart feedback

Acceptance: cart works for guest, persists after login.

---

### Phase D — Checkout → Orders
**Prompt:**
Implement checkout and order creation:
- address management
- shipping method selection
- coupon input hook (even if promotions app comes later)
- create order + order items snapshot
- order confirmation page
- order history in account dashboard

Acceptance: placing an order creates correct order record.

---

### Phase E — Payments (COD + provider-ready)
**Prompt:**
Implement payments:
- PaymentTransaction model
- Provider interface
- COD flow
- Add Stripe OR SSLCommerz integration behind the interface (choose one)
- Webhook endpoint + signature verification + order payment status updates

Acceptance: COD works; provider flow stubs run and webhooks update orders.

---

### Phase F — CMS customization
**Prompt:**
Implement CMS:
- SiteSettings singleton
- Menus + MenuItems
- Pages (About/Privacy/Terms/Contact)
- Banners + HomepageSections
Integrate with templates so admin can fully customize home page and header/footer.

Acceptance: I can edit menus/banners/pages in admin and see changes instantly.

---

### Phase G — Reviews + Wishlist + Support
**Prompt:**
Add:
- reviews with moderation
- wishlist
- contact form → support ticket inbox in admin
Add UI everywhere with Bootstrap.

Acceptance: customers can wishlist and review; admin can moderate.

---

### Phase H — SEO + Performance + Testing
**Prompt:**
Implement:
- SEO tags, sitemap, robots.txt
- caching for homepage sections
- tests for pricing/cart/checkout
- run formatting and add minimal documentation

Acceptance: tests pass and SEO basics exist.

---

# 14) Antigravity Skills + Rules + Workflows (Workspace setup)

## 14.1 Rules (workspace)
Create workspace rules so agents always follow your standards.

**Folder**
`.agent/rules/`

**Suggested rule file:** `.agent/rules/django-dcl.md`
- Use Django best practices and app boundaries defined in this spec
- Keep business logic in service modules (not in views)
- Templates must be Bootstrap 5 and accessible
- Always add admin config for any model
- Always run migrations and tests after model changes
- Do not generate “toy/demo-only” code; make production-grade

---

## 14.2 Workflows (workspace)
Workflows are “slash commands” you can trigger (example: `/ship-it` or `/generate-tests`).

**Folder**
`.agent/workflows/`

Suggested workflows (create as markdown files):
- `idea-to-django-ecommerce.md` → implements this spec end-to-end
- `generate-unit-tests.md` → generate pytest tests for changed modules
- `admin-polish.md` → improve Django admin usability + filters + bulk actions
- `ui-polish-bootstrap.md` → improve templates, spacing, components, responsiveness

---

## 14.3 Skills (workspace)
Skills are reusable instruction packs for the agent.

**Folder**
`.agent/skills/`

Create these skill folders (each contains a `SKILL.md`):
1. `django-ecommerce-architect/`
2. `bootstrap-ui-designer/`
3. `checkout-and-payments/`
4. `cms-admin-customizer/`
5. `qa-test-engineer/`

### Example SKILL.md template (copy this into each skill)
---
name: django-ecommerce-architect
description: Builds Django template-based ecommerce architecture for DCL Ecommerce. Use for models, app boundaries, service layers, and scalable structure.
---

## How to use this skill
When building or modifying the project:
1. Keep domains separated: catalog vs cart vs checkout vs orders vs payments.
2. Put business logic in `services.py` or `services/` modules.
3. Use Django admin inlines for relational edits (products → variants → images → inventory).
4. Always:
   - create/adjust migrations
   - update admin
   - update templates/views/urls
   - add tests for critical logic

## Conventions
- apps live in `apps/`
- templates use `templates/` with partials in `templates/partials/`
- do not hardcode homepage content; use CMS models

## Done criteria
- feature works end-to-end
- admin supports managing the feature
- tests cover core logic
- UI is responsive and looks modern with Bootstrap 5

---

# 15) Definition of Done (Release Checklist)

## Functional
- Full browse/search/filter
- Cart + checkout + orders
- Payment flows (at least COD + one provider)
- Admin manages everything (catalog, CMS, users, orders)
- Emails: order confirmation, password reset

## Quality
- No server errors in normal flows
- Tests pass
- Security settings reasonable
- Clean UI (mobile-first)
- SEO basics included

---

## 16) Optional Enhancements (Phase 2+)
- PC Builder (compatibility engine)
- Compare products
- Abandoned cart emails
- Recommendations (“Customers also bought”)
- Blog and content marketing
- Multi-warehouse stock
- Staff dashboard (non-admin UI for fulfillment)

---

End of Spec.
