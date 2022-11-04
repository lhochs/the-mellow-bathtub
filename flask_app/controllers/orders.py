from flask_app import app
from flask import redirect, render_template, request, session
from flask_app.models.order import Order
from flask_app.models.product import Product
from flask_app.models.user import User
from flask_app.models.payment import Payment


########################################
#### This is where we set the route ####
########################################

#this is where you can add to cart from dashboard
@app.route('/cart/add', methods=['POST'])
def addToCart():
    if 'user_id' not in session:
        return {
            "error": "Not logged in"
        }

    product_id = request.json["product_id"]
    product_name = request.json["product_name"]
    product_description = request.json["product_description"]
    price_per_unit = request.json["price_per_unit"]
    product_img = request.json["product_img"]

    product = {
        "product_id": product_id,
        "product_img": product_img,
        "product_name": product_name,
        "product_description": product_description,
        "price_per_unit": price_per_unit,
        "quantity": 1
    }
    print(product)
    # Add product to cart in session
    if 'cart' not in session:
        session["cart"] = {}
        session["cart"][product_id] = product
    else:
        cart = session['cart']
        if product_id in cart:
            cart[product_id]["quantity"] += 1
        else:
            cart[product_id] = product
        session['cart'] = cart
    
    return {
        "success": True
    }

# This route where user can view items he/she added to cart
@app.route("/cart")
def cart():
    tax_percent = 0.1025 #hard-code
    cart={}
    sub_total = 0.00
    tax_amount = 0
    shipping_cost = 0.00
    grand_total = 0

    if "cart" in session:
        cart = session["cart"]
        sub_total = 0.00
        grand_total = 0

        for product_id in cart:
            sub_total += round(int(cart[product_id]["price_per_unit"]) * int(cart[product_id]["quantity"]), 2)
        sub_total = round(sub_total, 2)
        if not cart == {}:
            shipping_cost = 8.00
        tax_amount = round(sub_total*tax_percent, 2)
        grand_total = sub_total + tax_amount + shipping_cost
    return render_template("cart.html", cart=cart, sub_total=sub_total, grand_total=grand_total, shipping_cost = shipping_cost, tax_amount=tax_amount)

#this is where the user can change the quantity of items in cart
@app.route("/cart/update/<int:product_id>", methods=["POST", "GET"])
def update_cart(product_id):
    if "cart" not in session:
        return redirect("/")

    if "cart" in session:
        cart = session['cart']
        print("BEFORE CART:", session["cart"])


        if request.method == "POST":
            quantity = request.form['product_quantity']
            # print("This is the product ID you're trying to access:", str(product_id))
            # print("This is the product quantity you're trying to change:", cart[product_id]['quantity'], "to", quantity)
            # print(product_id)
            # print(cart[str(product_id)]["product_name"])
            # print("This is the product quantity you're trying to change:", cart[str(product_id)]['quantity'], "to", quantity)
            if str(product_id) in cart:
                cart[str(product_id)]["quantity"] = int(quantity)
            print("CURRENT CART:", cart)
            session.modified = True
        return redirect('/cart')

@app.route('/cart/delete/<int:product_id>', methods=["POST", "GET"])
def delete_item(product_id):
    if "cart" in session:
        print("BEFORE CART:", session["cart"])
        session["cart"].pop(str(product_id))
        print("CURRENT CART:", session["cart"])
        session.modified = True
    return redirect("/cart")

@app.route("/clear_cart", methods=["GET"])
def clear_cart():
    if "cart" in session:
        # cart = session["cart"]
        # print(session["cart"])
        session.pop("cart")
    return redirect("/cart")

@app.route('/checkout/<int:user_id>')
def proceed_to_checkout(user_id):
    tax_percent = 0.1025

    if "cart" in session:
        cart = session["cart"]
        user_id = session["user_id"]
        sub_total = 0.00
        grand_total = 0
        total_quantity = 0

        for product_id in cart:
            sub_total += round(int(cart[product_id]["price_per_unit"]) * int(cart[product_id]["quantity"]), 2)
            total_quantity += cart[product_id]["quantity"]
        print("Total Number of items in the cart", total_quantity)
        sub_total = round(sub_total, 2)
        if not cart == {}:
            shipping_cost = 8.00
        tax_amount = round(sub_total*tax_percent, 2)
        grand_total = sub_total + tax_amount + shipping_cost

        print(user_id)
        data={
            "user_id": user_id
        }

        user = User.get_by_id(data)

        return render_template('checkout.html', cart = cart, sub_total = sub_total, grand_total = grand_total, shipping_cost = shipping_cost, tax_amount=tax_amount, total_quantity = total_quantity, user=user)

@app.route('/checkout/<int:user_id>/save_order_details', methods=["POST", "GET"])
def new_order(user_id):
    if "cart" in session:
        cart = session["cart"]
        user_id = session["user_id"]
        print(user_id)
        print("END END", cart)
        for product_id in cart:
            print("ENDENDEND", cart[str(product_id)]["product_name"])
        # print("ENDEND THIS IS THE PRODUCT ID", cart[str(product_id)])
        if request.method == "POST":
            sub_total = 0.00
            grand_total = 0
            total_quantity = 0
            tax_percent = 0.1025
            # products = {
            #         "product_id": product_id,
            #         "product_name": cart[str(product_id)]["product_name"],
            #         "product_quantity": cart[str(product_id)]["quantity"]
            #     },


            for product_id in cart:
                sub_total += round(int(cart[product_id]["price_per_unit"]) * int(cart[product_id]["quantity"]), 2)
                total_quantity += cart[product_id]["quantity"]
                # cart[str(product_id)]["product_id"] = products

            # print("Please check check", products)
            sub_total = round(sub_total, 2)
            if not cart == {}:
                shipping_cost = 8.00
            tax_amount = round(sub_total*tax_percent, 2)
            grand_total = sub_total + tax_amount + shipping_cost


            data = {
                "address": request.form["address"],
                "sub_total": sub_total,
                "taxes": tax_amount,
                "shipping": shipping_cost,
                "grand_total": grand_total,
                "total_quantity": total_quantity,
                "customer_id": user_id,
                "products": cart
            }

            session["cart"] = data
            print("UPDATED SESSION CART", session["cart"])
            session.modified = True
    # new_order = Order.add(data)
    # session["cart"] = {}
    return render_template("payment.html")#redirect("/", new_order, cart = cart, sub_total = sub_total, grand_total = grand_total, shipping_cost = shipping_cost, tax_amount=tax_amount)
@app.route('/payment', methods=['POST'])
def make_payment_save_order_details():

    if not Payment.validate(request.form):
        return redirect('/checkout/<int:user_id>/save_order_details')
    
    if "cart" in session:
        cart = session["cart"]
        print("THIS IS THE PAYMENT CART DATA:", cart)
        payment_data = {
        "credit_num":request.form["credit_num"],
        "billing_address":request.form["billing_address"],
        # "order_data": cart
        }
        # session["cart"] = payment_data
        # session.modified = True
        print("NEW NEW SESSION CART:", session["cart"])
        print("address in session:", session["cart"]["address"])

        payment_id = Payment.save(payment_data)

        order_data = {
            "address": cart['address'],
            "sub_total": cart['sub_total'],
            "taxes": cart['taxes'],
            "shipping": cart['shipping'],
            "grand_total": cart['grand_total'],
            "customer_id": cart['customer_id'],
            "payment_id": payment_id,
        } 
        order_id = Order.save(order_data)
        
        # print("Current Cart:", cart)
        # # print(cart['product_id']['quantity'])
        # print("PRODUCTS, PRODUCTS, PRODUCTS", cart['products'])
        # # id = cart['products'][]
        # print(cart["products"])
        #     # total_quantity = sum((cart[product_id]["quantity"]))
        # print("Total number of products in this order is:", cart['products'][('product_id')]['quantity'])
        # product_total_in_order = sum(session["cart"]["quantity"])
        # print("Total number of products in this order is:", product_total_in_order)
        
        order_details_data = {
            "order_id": order_id,
            "product_id": cart['products'],
            "product_quantity": cart["total_quantity"]
        }

        order_details_id = Order.save_order_details(order_details_data)

        session.pop("cart")
        return redirect('/')


@app.route('/orders/customer_id/order_id', methods=["GET"])
def get_order_for_customer(customer_id, order_id):
    # Check if user logs in and user has the same id as given customer_id
    if (not session):
        return {}

    # Only allow user to see his own orders
    if (session["user_id"] != customer_id):
        return {}

    data = {
        order_id: order_id
    }
    order = Order.get_order_by_id(data)

    return render_template("user_dashboard.html", order=order)

# @app.route("/submit_checkout", methods=["POST"])
# def submit_checkout():
#     data = {
#         "address": request.form["address"],
#         "sub_total": request.form["sub_total"],
#         "taxes": request.form["taxes"],
#         "shipping": request.form["shipping"],
#         "grand_total": request.form["grand_total"],
#         "customer_id": session["user_id"],
#         "products": request.form["products"]
#     }
#     new_order = Order.add(data)

#     return redirect("/customer_dashboard/" + new_order)
