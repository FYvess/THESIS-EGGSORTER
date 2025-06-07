from flask import Flask, redirect, render_template, jsonify, url_for
from db import modify_database, get_db_connection
from datetime import datetime, timedelta
from flask import request
from functools import wraps
from itertools import groupby

app = Flask(__name__)
modify_database()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        print(username, password)

        if username == "admin" and password == "admin":
            response = jsonify({"success": "Login successful"})
            response.set_cookie("current_user", username)
            return response
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    return redirect(url_for("index"))

@app.route("/logout", methods=["GET"])
def logout():
    response = redirect(url_for("index"))
    response.delete_cookie("current_user")
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = request.cookies.get("current_user")
        if not current_user:
            return render_template("login.html")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    conn = get_db_connection()
    # Fetch all eggs
    eggs = conn.execute("SELECT * FROM eggs_tbl").fetchall()
    
    # Calculate total eggs
    total_eggs = len(eggs)

    # Calculate weekly eggs
    one_week_ago = datetime.now() - timedelta(days=7)
    weekly_eggs = conn.execute(
        "SELECT COUNT(*) as count FROM eggs_tbl WHERE created_at >= ?", 
        (one_week_ago.strftime("%Y-%m-%d %H:%M:%S"),)
    ).fetchone()["count"]
    
    # Calculate monthly eggs
    one_month_ago = datetime.now() - timedelta(days=30)
    monthly_eggs = conn.execute(
        "SELECT COUNT(*) as count FROM eggs_tbl WHERE created_at >= ?", 
        (one_month_ago.strftime("%Y-%m-%d %H:%M:%S"),)
    ).fetchone()["count"]
    
    # Calculate daily eggs
    today = datetime.now().strftime("%Y-%m-%d")
    daily_eggs = conn.execute(
        "SELECT COUNT(*) as count FROM eggs_tbl WHERE DATE(created_at) = ?", 
        (today,)
    ).fetchone()["count"]
    
    conn.close()
    eggs = [dict(egg) for egg in eggs]
    print(eggs)


    for egg in eggs:
        weight = egg.get('weight')
        if weight is not None:
            # Ensure weight is treated as a float for comparison
            w = float(weight)
            if 41 <= w < 55:
                egg['size'] = 'Small'
            elif 56 <= w < 60:
                egg['size'] = 'Medium'
            elif 61 <= w < 65:
                egg['size'] = 'Large'
            elif 66 <= w < 70:
                egg['size'] = 'Extra Large'
            else:
                egg['size'] = 'Jumbo'

    
    return render_template(
        "dashboard.html", 
        eggs=eggs, 
        total_eggs=total_eggs, 
        weekly_eggs=weekly_eggs,
        monthly_eggs=monthly_eggs, 
        daily_eggs=daily_eggs
    )
    
@app.route("/chart-data")
def chart_data():
    conn = get_db_connection()
    eggs = conn.execute("SELECT weight FROM eggs_tbl").fetchall()
    conn.close()

    eggs = [dict(egg) for egg in eggs]

    for egg in eggs:
        weight = egg.get('weight')
        if weight is not None:
            # Ensure weight is treated as a float for comparison
            w = float(weight)
            if 41 <= w < 55:
                egg['size'] = 'Small'
            elif 56 <= w < 60:
                egg['size'] = 'Medium'
            elif 61 <= w < 65:
                egg['size'] = 'Large'
            elif 66 <= w < 70:
                egg['size'] = 'Extra Large'
            else:
                egg['size'] = 'Jumbo'

    size_counts = {'Small': 0, 'Medium': 0, 'Large': 0, 'Extra Large': 0, 'Jumbo': 0}
    for egg in eggs:
        size = egg.get('size')
        if size in size_counts:
            size_counts[size] += 1

    size_counts = [{"name": size, "value": count} for size, count in size_counts.items()]


    return jsonify(size_counts)

@app.route("/chart-data-2")
def chart_data_2():
    conn = get_db_connection()
    eggs = conn.execute("SELECT created_at FROM eggs_tbl").fetchall()
    conn.close()

    # Initialize counts for Monday (index 0) to Sunday (index 6)
    counts = [0, 0, 0, 0, 0, 0, 0]

    for egg in eggs:
        dt = datetime.strptime(egg["created_at"], "%Y-%m-%d %H:%M:%S")
        # weekday(): Monday is 0, Sunday is 6
        counts[dt.weekday()] += 1

    return jsonify({"data": counts})

@app.route("/Inventory")
@login_required
def inventory():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM eggs_tbl ORDER BY created_at DESC").fetchall()
    conn.close()

    eggs = []
    for egg in rows:
        created_date = datetime.strptime(
            egg["created_at"], "%Y-%m-%d %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")
        expiry_date = datetime.strptime(
            egg["expected_expiry"], "%Y-%m-%d %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")

        egg_dict = dict(egg)
        egg_dict["created_date"] = created_date
        egg_dict["expected_expiry"] = expiry_date
        eggs.append(egg_dict)

    # Group eggs into batches by created_date
    # Ensure sorted by date so groupby works
    eggs.sort(key=lambda x: x["created_date"], reverse=True)
    batches = [list(group) for _, group in groupby(eggs, key=lambda x: x["created_date"])]

    # Define size categories
    size_counts_per_batch = []
    for batch in batches:
        if not batch:
            continue
        date = batch[0]["created_date"]
        expected_expiry = (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")

        counts = {
            "Small": 0,
            "Medium": 0,
            "Large": 0,
            "Extra Large": 0,
            "Jumbo": 0,
        }
        for egg in batch:
            w = int(egg["weight"])
            if 41 <= w <= 55:
                size = "Small"
            elif 56 <= w <= 60:
                size = "Medium"
            elif 61 <= w <= 65:
                size = "Large"
            elif 66 <= w <= 70:
                size = "Extra Large"
            else:
                size = "Jumbo"
            counts[size] += 1
        size_counts_per_batch.append({"date": date, "expected_expiry": expected_expiry, **counts})
    
    return render_template("Inventory.html", eggs=size_counts_per_batch)

@app.route("/add-egg", methods=["POST"])
def add_egg():
    weight = request.form.get("weight")

    if not weight:
        return jsonify({"error": "Size and weight are required"}), 400
    try:
        weight = float(weight)
    except ValueError:
        return jsonify({"error": "Weight must be a number"}), 400
    
    conn = get_db_connection()
    conn.execute("INSERT INTO eggs_tbl (weight) VALUES (?)", (weight,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Egg added successfully"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
