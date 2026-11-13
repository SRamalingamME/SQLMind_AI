# Database Schema Context

The database contains the following relational tables for an e-commerce platform:

## Table: `customers`
**Columns:**
- `customer_id` (INTEGER) - NOT NULL
- `customer_name` (VARCHAR) - NOT NULL
- `email` (VARCHAR) - NULL
- `city` (VARCHAR) - NULL
- `signup_date` (DATE) - NULL

---

## Table: `orders`
**Columns:**
- `order_id` (INTEGER) - NOT NULL
- `customer_id` (INTEGER) - NULL
- `order_date` (DATE) - NULL
- `status` (VARCHAR) - NULL

**Foreign Keys:**
- `customer_id` -> `customers.customer_id`

---

## Table: `order_items`
**Columns:**
- `item_id` (INTEGER) - NOT NULL
- `order_id` (INTEGER) - NULL
- `product_id` (INTEGER) - NULL
- `quantity` (INTEGER) - NULL

**Foreign Keys:**
- `order_id` -> `orders.order_id`
- `product_id` -> `products.product_id`

---

## Table: `products`
> **CRITICAL NOTE:** `'category'` is a direct text column inside this products table (containing values like 'Electronics', 'Furniture'). There is **NO** separate `categories` relational table. Do **NOT** attempt to JOIN with a categories table.

**Columns:**
- `product_id` (INTEGER) - NOT NULL
- `product_name` (VARCHAR) - NOT NULL
- `category` (VARCHAR) - NULL
- `unit_price` (DOUBLE PRECISION) - NULL

---

