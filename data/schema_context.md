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
**Columns:**
- `product_id` (Integer, Primary Key)
- `product_name` (String)
- `category` (String) -> **Note: This is a direct text column containing category names like 'Electronics' or 'Furniture'. Do NOT attempt to join with a separate categories table.**
- `unit_price` (Float)

---

