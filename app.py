from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def add_customers():
    for _ in range(100):
        customer = Customer(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            address=fake.street_address(),
            city=fake.city(),
            email=fake.email()
        )
        db.session.add(customer)
        db.session.commit()

def add_orders():
    customers = Customer.query.all()
    for _ in range(1000):

        customer = random.choice(customers)
        ordered_date = fake.date_time_this_year()
        shipped_date = random.choices([None, fake.date_time_between(start_date=ordered_date)], [10, 90])[0]
        delivered_date=None,
        if shipped_date:
            delivered_date = random.choices([None, fake.date_time_between(start_date=shipped_date)])
        coupon_code = random.choices([None, "Premium", "Discount"],[70,20,10])[0]

        order = Order(
            customer_id=customer.id,
            order_date=ordered_date,
            shipped_date=shipped_date,
            coupon_code=coupon_code
        )
        db.session.add(order)
        db.session.commit()

def add_products():
    for _ in range(10):
        product = Product(
            name=fake.color_name(),
            price=random.randint(1,500),
        )
        db.session.add(customer)
        db.session.commit()

def add_order_products():
    orders = Order.query.all()
    products = Product.query.all()

    for order in orders:
        k = random.randint(1,3)
        purchase_products = random.sample(products, k)
        order.products.extend(purchase_products)

        db.session.commit()

def create_random_data():
    db.create_all()
    add_customers()
    add_orders()
    add_products()
    add_order_products()

def orders_by(customer_id=1):
    customer_orders = Order.query.filter_by(customer_id=customer_id).all()
    for order in customer_orders:
        print(order.customer.first_name)

def pending_orders(customer_id=1):
    pending_orders = Order.query.filter(Order.shipped_date.is_(None)).all()
    for order in pending_orders:
        print(order.order_date)

def customer_count():
    print(Customer.query.count())

def orders_with_code():
    orders = Order.query.filter(Order.coupon_code.isnot(None)).all()
    for order in orders:
        print(order.coupon_code)

def revenue(x_days=30):
    print(db.session.query(db.func.sum(Product.price)).join(order_product).join(Order).filter(Order.order_date > (datetime.now() - timedelta(days=x_days))).all())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)

    orders = db.relationship('Order', backref='customer')

order_product = db.Table("order_product",
                         db.Column('order.id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
                         db.Column('product.id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                         )

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shipped_date = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    coupon_code = db.Column(db.String(50))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    products = db.relationship('Product', secondary=order_product)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
