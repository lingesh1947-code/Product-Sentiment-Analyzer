from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

# -----------------------------
# FLASK APP
# -----------------------------

app = Flask(__name__)

CORS(app)

# -----------------------------
# DATABASE CONFIG
# -----------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -----------------------------
# DATABASE
# -----------------------------

DB = SQLAlchemy(app)

# -----------------------------
# PRODUCT MODEL
# -----------------------------

class Product(DB.Model):

    id = DB.Column(DB.Integer, primary_key=True)

    name = DB.Column(DB.String(100))

    category = DB.Column(DB.String(100))

    price = DB.Column(DB.Integer)

    rating = DB.Column(DB.Float)

    reviews = DB.Column(DB.Integer)

# -----------------------------
# CREATE DATABASE
# -----------------------------

with app.app_context():
    DB.create_all()

# -----------------------------
# HOME API
# -----------------------------

@app.route('/')
def home():

    return jsonify({
        "message": "Backend Running Successfully"
    })

# -----------------------------
# ADD SAMPLE DATA
# -----------------------------

@app.route('/add-sample-data')
def add_sample_data():

    if Product.query.count() > 0:

        return jsonify({
            "message": "Sample Data Already Exists"
        })

    products = [

        Product(
            name='Laptop',
            category='Electronics',
            price=50000,
            rating=4.5,
            reviews=120
        ),

        Product(
            name='Mobile',
            category='Electronics',
            price=25000,
            rating=4.2,
            reviews=90
        ),

        Product(
            name='Shoes',
            category='Fashion',
            price=3000,
            rating=4.0,
            reviews=60
        )
    ]

    for product in products:
        DB.session.add(product)

    DB.session.commit()

    return jsonify({
        "message": "Sample Data Added"
    })

# -----------------------------
# GET PRODUCTS
# -----------------------------

@app.route('/products')
def get_products():

    products = Product.query.all()

    result = []

    for product in products:

        result.append({

            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "rating": product.rating,
            "reviews": product.reviews

        })

    return jsonify(result)

# -----------------------------
# ADD PRODUCT
# -----------------------------

@app.route('/add-product', methods=['POST'])
def add_product():

    data = request.json

    product = Product(

        name=data['name'],
        category=data['category'],
        price=data['price'],
        rating=data['rating'],
        reviews=data['reviews']

    )

    DB.session.add(product)

    DB.session.commit()

    return jsonify({
        "message": "Product Added"
    })

# -----------------------------
# SEARCH PRODUCT
# -----------------------------

@app.route('/search')
def search_product():

    keyword = request.args.get('q', '').lower()

    products = Product.query.all()

    result = []

    for product in products:

        if keyword in product.name.lower():

            result.append({

                "id": product.id,
                "name": product.name,
                "price": product.price

            })

    return jsonify(result)

# -----------------------------
# PIE CHART API
# -----------------------------

@app.route('/pie-chart')
def pie_chart():

    data = [

        {
            "name": "Electronics",
            "value": 50
        },

        {
            "name": "Fashion",
            "value": 30
        },

        {
            "name": "Accessories",
            "value": 20
        }
    ]

    return jsonify(data)

# -----------------------------
# BAR GRAPH API
# -----------------------------

@app.route('/bar-chart')
def bar_chart():

    data = [

        {
            "name": "Laptop",
            "sales": 100
        },

        {
            "name": "Mobile",
            "sales": 150
        },

        {
            "name": "Shoes",
            "sales": 80
        }
    ]

    return jsonify(data)

# -----------------------------
# REVIEW TREND API
# -----------------------------

@app.route('/review-trend')
def review_trend():

    data = [

        {
            "month": "Jan",
            "reviews": 20
        },

        {
            "month": "Feb",
            "reviews": 40
        },

        {
            "month": "Mar",
            "reviews": 60
        }
    ]

    return jsonify(data)

# -----------------------------
# SENTIMENT ANALYSIS API
# -----------------------------

@app.route('/sentiment', methods=['POST'])
def sentiment():

    data = request.json

    text = data['text']

    analysis = TextBlob(text)

    polarity = analysis.sentiment.polarity

    if polarity > 0:
        result = "Positive"

    elif polarity < 0:
        result = "Negative"

    else:
        result = "Neutral"

    return jsonify({

        "text": text,
        "sentiment": result,
        "polarity": polarity

    })

# -----------------------------
# SCRAPING API
# -----------------------------

@app.route('/scrape')
def scrape():

    url = "https://example.com"

    response = requests.get(url)

    soup = BeautifulSoup(
        response.text,
        'html.parser'
    )

    titles = soup.find_all('h1')

    result = []

    for title in titles:
        result.append(title.text)

    return jsonify(result)

# -----------------------------
# FILE UPLOAD API
# -----------------------------

@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:

        return jsonify({
            "message": "No File Uploaded"
        })

    file = request.files['file']

    file.save(file.filename)

    return jsonify({
        "message": "File Uploaded Successfully"
    })

# -----------------------------
# STATUS API
# -----------------------------

@app.route('/status')
def status():

    return jsonify({

        "server": "Running",
        "database": "Connected"

    })

# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
  