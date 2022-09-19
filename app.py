from http.client import HTTPResponse
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import uuid
from yookassa import Configuration, Payment


dotenv_path = os.path.join(os.path.dirname(__file__), 'shop.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    host = os.environ.get('host')
    user = os.environ.get('user')
    password = os.environ.get('password')
    db_name = os.environ.get('db_name')
    return_url = os.environ.get('return_url')
    Configuration.account_id = os.environ.get('shop_id')  
    Configuration.secret_key = os.environ.get('secret_key')  
else:
    print("No configuration file!")
    exit()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    # text = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return self.title


@app.route('/')
def index():
    items = Shop.query.order_by(Shop.price).all()
    return render_template('index.html', data=items)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/buy/<int:id>/')
def buy_product(id):
    item = Shop.query.get(id)
    payment = Payment.create({
    "amount": {
        "value": item.price,
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": return_url
    },
    "capture": True,
    "description": item.title
    }, uuid.uuid4())
    return redirect(payment.confirmation.confirmation_url)


@app.route('/new_product/', methods=['POST', 'GET'])
def new_product():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        item = Shop(title=title, price=price)
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Error while adding new product :("
    else:
        return render_template('new_product.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15000, debug=True)
