
from flask import Flask, redirect, request, render_template, session, url_for, flash
import stripe
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, UniqueConstraint
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import my_creds

app = Flask(__name__)

STRIPE_API_KEY = my_creds.STRIPE_API_KEY
stripe.api_key = STRIPE_API_KEY  # Initialize the Stripe API key
YOUR_DOMAIN = 'http://127.0.0.1:5000/'
app.config['SECRET_KEY'] = my_creds.SECRET_KEY



# Dummy product data (In real case, use a database)
#create DB

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
db = SQLAlchemy(app)

#define a Product 

class Product(db.Model):
    __tablename__ = "product"  # Optional, but good practice
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)  # Amount in cents (Stripe format)
    currency = db.Column(db.String(250), nullable=False, default="usd")
    img_url = db.Column(db.String(250), nullable=True)  # Allow nullable for images



#create table 

# with app.app_context():
#     db.create_all()

class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = StringField("Price", validators=[DataRequired()])
    currency = StringField("Currency (e.g., usd)", validators=[DataRequired()])
    img_url = StringField("Image URL")
    submit = SubmitField("Add Product")

    

@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            price=float(form.price.data),  
            currency=form.currency.data,
            img_url=form.img_url.data,
        )
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for("home"))
    
    return render_template("add_product.html", form=form)



@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    
                    'price': 'price_1QyuevGHVFgLkmFRUvh1iJ6x',
                    'quantity': 1,
                },
                # {
                    
                #     'price': 'price_1Qyv0iGHVFgLkmFRgnJepW5d',
                #     'quantity': 1,
                # },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)



@app.route("/")
def home():
    products= Product.query.all()
    return render_template("index.html", products=products)

@app.route("/add_to_cart/<product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    cart_items = session.get("cart", {})
    product_ids = cart_items.keys()
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    return render_template("cart.html", cart=cart_items, products=products)


@app.route('/success.html')
def success():
    return render_template('success.html')

@app.route('/cancel.html')
def cancel():
    return render_template('cancel.html')   


if __name__ == "__main__":
    app.run(debug=True)
