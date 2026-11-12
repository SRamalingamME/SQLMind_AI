from datetime import datetime
from dotenv import load_dotenv
import os

# Load .env variables first
load_dotenv()

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# Get DATABASE_URL directly from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define E-commerce Relational Schema
class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    city = Column(String)
    signup_date = Column(Date)

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    category = Column(String)
    unit_price = Column(Float)

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    order_date = Column(Date)
    status = Column(String)

class OrderItem(Base):
    __tablename__ = "order_items"
    item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)

def seed_database():
    print("Creating tables in PostgreSQL on Neon...")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # Check if data already exists
    if session.query(Customer).first():
        print("Database is already seeded!")
        session.close()
        return

    print("Inserting mock e-commerce records...")

    # Seed Customers
    c1 = Customer(customer_name="Aarav Sharma", email="aarav@example.com", city="Coimbatore", signup_date=datetime.strptime("2025-01-10", "%Y-%m-%d").date())
    c2 = Customer(customer_name="Priya Patel", email="priya@example.com", city="Chennai", signup_date=datetime.strptime("2025-02-15", "%Y-%m-%d").date())
    c3 = Customer(customer_name="Rahul Verma", email="rahul@example.com", city="Bengaluru", signup_date=datetime.strptime("2025-03-01", "%Y-%m-%d").date())
    session.add_all([c1, c2, c3])
    session.commit()

    # Seed Products
    p1 = Product(product_name="Wireless Mouse", category="Electronics", unit_price=25.99)
    p2 = Product(product_name="Mechanical Keyboard", category="Electronics", unit_price=75.50)
    p3 = Product(product_name="Ergonomic Office Chair", category="Furniture", unit_price=189.00)
    session.add_all([p1, p2, p3])
    session.commit()

    # Seed Orders
    o1 = Order(customer_id=1, order_date=datetime.strptime("2025-03-10", "%Y-%m-%d").date(), status="Completed")
    o2 = Order(customer_id=2, order_date=datetime.strptime("2025-03-12", "%Y-%m-%d").date(), status="Shipped")
    session.add_all([o1, o2])
    session.commit()

    # Seed Order Items
    oi1 = OrderItem(order_id=1, product_id=1, quantity=2)
    oi2 = OrderItem(order_id=1, product_id=2, quantity=1)
    oi3 = OrderItem(order_id=2, product_id=3, quantity=1)
    session.add_all([oi1, oi2, oi3])
    session.commit()

    print("Database seeding completed successfully!")
    session.close()

if __name__ == "__main__":
    seed_database()