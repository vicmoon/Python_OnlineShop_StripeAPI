
from flask import Flask, redirect, request, render_template
import stripe
import my_creds

app = Flask(__name__)

STRIPE_API_KEY = my_creds.STRIPE_API_KEY
stripe.api_key = STRIPE_API_KEY  # Initialize the Stripe API key
YOUR_DOMAIN = 'http://127.0.0.1:5000/'


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
    return render_template("index.html")

@app.route('/success.html')
def success():
    return render_template('success.html')

@app.route('/cancel.html')
def cancel():
    return render_template('cancel.html')   


if __name__ == "__main__":
    app.run(debug=True)
