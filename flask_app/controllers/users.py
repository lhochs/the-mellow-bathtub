from flask_app import app
from flask import redirect, render_template, request, session, flash
from flask_app.models.user import User
from flask_app.models.order import Order
from flask_app.models.product import Product
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

########################################
#### This is where we set the route ####
########################################

@app.route("/")
def index():
    # user_id = session["user_id"]
    return render_template("index.html", all_products = Product.get_all())

@app.route("/company")
def our_team():
    return render_template("our_team.html")

@app.route("/login_and_register")
def login_and_register():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# user dashboard - show all the orders they have
@app.route("/customer_dashboard")
def user_dashboard():
    # Check if user logs in and user has the same id as given customer_id
    if (not session):
        return redirect("/login_and_register")

    user_data = {
        "customer_id": session["user_id"]
    }
    orders = Order.get_all_orders_by_customer_id(user_data)

    return render_template("user_dashboard.html", orders=orders)


# seller dashboard - show all the products they have
@app.route("/seller_dashboard")
def seller_dashboard():
    if (not session):
        return redirect("/login_and_register")
    print(session)
    if (session["role_type"] != "seller"):
        flash("Only registered sellers can access the Seller Dashboard.")
        return redirect("/")
    products = Product.get_all_products_with_users()
    user = User.get_by_id(session)
    return render_template("seller_dashboard.html",  all_products = products, users = user)

#####################################
#### This is where the API stays ####
#####################################

@app.route("/register", methods=["POST"])
def register():
    if not User.validate_register(request.form):
        return redirect("/login_and_register")
    pw_hash = bcrypt.generate_password_hash(request.form["password"])
    data = {
        "first_name":request.form["first_name"],
        "last_name":request.form["last_name"],
        "role_type":request.form.get("role_type"),
        "email":request.form["email"],
        "password":pw_hash,
        "role_type":request.form["role_type"]
    }
    user_id = User.save(data)
    session["user_id"] = user_id
    session["role_type"] = request.form.get("role_type") 
    if session["role_type"]== "customer":
        return redirect('/')

    if session["role_type"]== "seller":
        return redirect('/seller_dashboard')

@app.route("/login", methods=["POST"])
def login():
    # if not User.validate_login(request.form):
    #     return redirect("/login_and_register")
    user = User.get_by_email(request.form)

    if not user:
        flash("The email you entered isn't connected to an account. Find your account and log in.")
        return redirect("/login_and_register")
    # print(user)

    if user:
        if not bcrypt.check_password_hash(user.password, request.form["password"]):
            flash("The password you've entered is incorrect.")
            return redirect("/login_and_register")

    session["user_id"] = user.user_id
    session["role_type"] =  user.role_type

    # print("the role is " + role)

    if session["role_type"]== "customer":
        # print("GOT HERE !!!!!!!!!!!!")
        return redirect('/')
        # return render_template("user_dashboard.html")
    
    if session["role_type"]== "seller":
        return redirect('/seller_dashboard')

# @app.route("/signup")
# def signup():
#     return render_template("signup.html")

# This route can be used for both seller and buyer, based on user role
@app.route("/user/dashboard")
def dashboard():
    return render_template("dashboard.html")