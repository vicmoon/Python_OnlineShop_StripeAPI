
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
import os

app = Flask(__name__)

# STRIPE_API_KEY = my_creds.STRIPE_API_KEY
# MY_DOMAIN= my_creds.MY_DOMAIN


STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
MY_DOMAIN=os.getenv("MY_DOMAIN")

stripe.api_key = STRIPE_API_KEY 
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")



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
    price = db.Column(db.Float, nullable=False)  # store as Float 
    currency = db.Column(db.String(250), nullable=False, default="usd")
    img_url = db.Column(db.String(250), nullable=True)  # Allow nullable for images


#create table 

with app.app_context():
    db.create_all()

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
    cart_items = session.get("cart", {})
    if not cart_items:
        return redirect(url_for("cart"))

    line_items = []
    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product:
            line_items.append({
                "price_data" : {
                    "currency": product.currency, 
                    "product_data": { "name" : product.name}, 
                    "unit_amount": int(product.price * 100),
                },
                "quantity" : quantity,
            })

    try:
       checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=MY_DOMAIN+ 'success.html',
            cancel_url=MY_DOMAIN+ 'cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)



@app.route("/")
def home():
    products= Product.query.all()
    return render_template("index.html", products=products)


@app.route("/cart")
def cart():
    cart_items = session.get("cart", {})

    # # Debugging: Print cart data
    # print("Cart contents:", cart_items)
    
    product_ids = cart_items.keys()

    products = Product.query.filter(Product.id.in_(product_ids)).all()

    return render_template("cart.html", cart=cart_items, products=products)


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


@app.route("/delete/<int:product_id>")
def delete_item(product_id):
    if "cart" in session:
        cart = session["cart"]

        product_id = str(product_id)  # Convert to string to match session keys

        if product_id in cart:
            del cart[product_id]  # Remove item from cart
            session["cart"] = cart  # Update session
            flash("Item removed from cart", "success")
        else:
            flash("Item not found in cart", "error")
    
    return redirect(url_for("cart"))



@app.route('/success.html')
def success():
    return render_template('success.html')

@app.route('/cancel.html')
def cancel():
    return render_template('cancel.html')   


if __name__ == "__main__":
    app.run(debug=True)
