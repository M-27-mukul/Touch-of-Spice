from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from dotenv import load_dotenv
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

# About Page
@app.route("/")
def about():
    return render_template("about.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if not session.get('user_id'):
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            if user:
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                return redirect(url_for("about"))
            else:
                flash("Invalid credentials")
            cursor.close()
            conn.close()
        return render_template("login.html")
    else:
        return redirect(url_for("about"))

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if not session.get('user_id'):
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
                conn.commit()
                return redirect(url_for("login"))
            except:
                flash("Email already exists")
            cursor.close()
            conn.close()
        return render_template("register.html")
    else:
        return redirect(url_for("about"))

# logout action
@app.route("/logout")
def logout():
    session['user_id'] = None
    session['user_name'] = None
    return redirect(url_for("login"))

# Search Page
@app.route("/search", methods=["GET", "POST"])
def search():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_query = request.args.get("recipe_name")
    if search_query:
        cursor.execute("SELECT id, recipe_name FROM recipes WHERE recipe_name LIKE %s order by id Limit 4", (f"%{search_query}%",))
    else:
        cursor.execute(" SELECT id, recipe_name from recipes order by id Limit 4")
    recipes_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("search recipe.html", recipes=recipes_items)

# Description Page
@app.route("/description/<int:recipe_id>", methods=["GET", "POST"])
def describe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM recipes WHERE id = "+ str(recipe_id)
    cursor.execute(query)
    recipe_item = cursor.fetchone()
    cursor.close()
    conn.close()
    if not recipe_item:
        return redirect(url_for("search"))
    recipe = {
        "id" : recipe_item["id"],
        "name" : recipe_item["recipe_name"],
        "desc" : recipe_item["recipe_desc"],
        "procedure" : json.loads(recipe_item["recipe_procedure"]),
    }
    return render_template("describe recipe.html", recipe=recipe)


# # Add Cart Action
@app.route("/add-to-cart/<int:recipe_id>")
def add_to_cart(recipe_id):
    if session.get('user_id'):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE id = "+ str(session["user_id"])
        cursor.execute(query)
        user = cursor.fetchone()
        if not user:
            logout()
        else:
            query = "SELECT * FROM recipes WHERE id = "+ str(recipe_id)
            cursor.execute(query)
            recipe_item = cursor.fetchone()
            if not recipe_item:
                return redirect(url_for("search"))
            else:
                query = "SELECT * FROM cart WHERE user_id = "+ str(session["user_id"])
                cursor.execute(query)
                user = cursor.fetchone()
                if not user:
                    cursor.execute("Insert into cart (user_id, items) Values (%s, %s)", (str(session["user_id"]), recipe_item["ingredients"]))
                    conn.commit()
                else:
                    items = json.loads(user["items"])
                    new_items = json.loads(recipe_item["ingredients"])
                    # Create a dictionary to sum quantities
                    data = {}

                    # Process the first list
                    for item in items:
                        data[item['id']] = data.get(item['id'], 0) + int(item['quantity'])

                    # Process the second list
                    for item in new_items:
                        data[item['id']] = data.get(item['id'], 0) + int(item['quantity'])

                    # Convert the result back to list of dictionaries
                    items = [{"id": k, "quantity": v} for k, v in data.items()]
                    
                    items = json.dumps(items)
                    
                    cursor.execute("Update cart set items=%s where user_id=%s", (items, str(session["user_id"])))
                    conn.commit()          
        cursor.close()
        conn.close()
        return redirect(url_for("describe", recipe_id=recipe_id))
    else:
        return redirect(url_for("login"))

# Cart Page
@app.route("/cart")
def cart():
    if session.get('user_id'):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM cart WHERE user_id = "+ str(session["user_id"])
        cursor.execute(query)
        user = cursor.fetchone()
        if not user:
            return render_template("cart.html", data= None)
        else:
            items = json.loads(user["items"])
            # Create a dictionary to sum quantities
            data = {}

            # Process the first list
            for item in items:
                data[item['id']] = data.get(item['id'], 0) + int(item['quantity'])
            query = "SELECT id, ingredient_name, price FROM ingredients WHERE id in "+ str(tuple(data.keys()))
            cursor.execute(query)
            item_details = cursor.fetchall()
            return render_template("cart.html", data=data, item_details= item_details)
            
    else:
        return redirect(url_for("login"))

# Contact Page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Profile Page
@app.route("/profile")
def profile():
    if session.get('user_id'):
        return render_template("profile.html")
    else:
        return redirect(url_for("login"))


if __name__ =="__main__":
    app.run(debug=True)
