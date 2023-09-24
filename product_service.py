import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))

#start using flask and create a database to store products in
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'products.sqlite')
db = SQLAlchemy(app)



# Describes all the products available in the store
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
with app.app_context():
    db.create_all()


# Endpoint 1: get all products
@app.route('/products', methods = ['GET'])
def get_groceries_list():
    products = Product.query.all()
    product_list = [{"id" : product.id, "name" : product.name, 
                     "price" : product.price, "quantity" : product.quantity
                     } for product in products
                    ]
    return jsonify({"product_info" : product_list})
    


# Endpoint 2: get specific product
@app.route('/products/<int:prod_id>', methods = ['GET'])
def get_product(prod_id):
    product = Product.query.get(prod_id)
    if product:
        return jsonify({"task": {"id" : product.id, "name" : product.name, 
                                 "price" : product.price, "quantity" : product.quantity}})
    else:
        return jsonify({"error": "Task not found"}), 404



# Endpoint 3: add a product to the database
#quantity could be negative
@app.route('/products', methods = ['POST'])
def post_products():
    data = request.json
    if not all(key in data for key in ["name", "price", "quantity"]):
        return jsonify({"error": "Missing a requirement"}), 400
    new_prod = Product(name = data['name'], price = data['price'], quantity = data['quantity'])
    db.session.add(new_prod)
    db.session.commit()

    return jsonify({"message": "Product created", "Product": {"id": new_prod.id, 
                                                        "name": new_prod.name, 
                                                        "price": new_prod.price, 
                                                        "quantity" : new_prod.quantity}}), 201



# Endpoint 4: add/remove a product from the database
@app.route('/products/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    
    quantity = request.json.get("quantity", 1)
    for prod in Product.query.all():
        if prod.id == product_id:
            if prod.quantity + quantity > 0:
                prod.quantity += quantity
                db.session.commit()
                return({"message" : f"Updated {quantity} units of product {product_id} to the store"})
            elif prod.quantity + quantity == 0:
                db.session.delete(prod)
                db.session.commit()
                return({"message" : f"Removed product {product_id} from the store"})
            else:
                return ({"message" : f"That many units of product {product_id} are not available"})
            break
    else:
            return({"message": f"Error product {product_id} was not found"})




if __name__ == '__main__':
    app.run()
    