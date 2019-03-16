import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
import time
from datetime import datetime
from pytz import timezone
import smtplib
import random

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.route("/")
def index():

    # Main page
    if session and not session['message'] == None:
        flash(session['message'])
    session['message'] = None
    return render_template("index.html")


@app.route("/add")
def add():
    # Addition page
    session['type1'] = 'Addition'
    session['message'] = None
    return render_template("add.html")


@app.route("/best", methods=["GET", "POST"])
def best():
    # The best results
    session['message'] = None

    if request.args.get('Type'):
        type1 = request.args.get('Type')
    elif request.form.get('Type'):
        type1 = request.form.get('Type')

    if request.form.get("numberOfItems"):
        if request.form.get("numberOfItems").isdigit():
            amount = request.form.get("numberOfItems")
        else:
            return apology("provide number", 400)
    else:
        amount = 10

    bestResults = db.execute("""SELECT * FROM records
                                WHERE type1 = :type1
                                ORDER BY correct DESC, numberofproblems ASC, time
                                LIMIT :amount""", amount=amount, type1=type1)

    return render_template("best.html", bestResults=bestResults, operation=type1)


@app.route("/changepas", methods=["GET", "POST"])
@login_required
def changepas():

    user_id = session.get('user_id')
    """Change password"""
    oldPas = db.execute("SELECT hash FROM users WHERE user_id = :user_id", user_id=user_id)

    if request.method == "POST":

        if not request.form.get("oldPassword"):
            return apology("Must provide old password", 400)
        elif not check_password_hash(oldPas[0]["hash"], request.form.get("oldPassword")):
            return apology("Old password is wrong", 400)
        elif not request.form.get("newPassword"):
            return apology("Must provide new password", 400)
        elif not request.form.get("confirmation"):
            return apology("Must provide password confirmation", 400)
        elif not request.form.get("newPassword") == request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        newHash = generate_password_hash(request.form.get("newPassword"))
        db.execute("UPDATE users SET hash = :newHash WHERE user_id = :user_id", user_id=user_id, newHash=newHash)
        session['message'] = "You have changed your password!"
        return redirect("/")

    else:
        return render_template("changepas.html")


@app.route("/changeemail", methods=["GET", "POST"])
@login_required
def changeemail():

    # Change email
    user_id = session.get('user_id')

    oldEmail = db.execute("SELECT email, hash FROM users WHERE user_id = :user_id", user_id=user_id)

    if request.method == "POST":
        if not request.form.get("newEmail"):
            return apology("Must provide new email", 400)
        elif not request.form.get("password"):
            return apology("Must provide password", 400)
        elif not check_password_hash(oldEmail[0]["hash"], request.form.get("password")):
            return apology("passwords is wrong", 400)

        db.execute("""UPDATE users SET email = :newEmail WHERE user_id = :user_id""", user_id=user_id,
                   newEmail=request.form.get("newEmail"))
        session['message'] = "You have changed your email to: " + request.form.get("newEmail") + "!"
        return redirect("/")

    else:
        return render_template("changeemail.html", oldEmail=oldEmail[0]["email"])


@app.route("/changeusername", methods=["GET", "POST"])
@login_required
def changeusername():

    # Change username
    user_id = session.get('user_id')

    oldUsername = db.execute("SELECT username, hash FROM users WHERE user_id = :user_id", user_id=user_id)

    if request.method == "POST":

        busyUsername = db.execute("""SELECT * FROM users WHERE username = :username""", username=request.form.get("newUsername"))

        if not request.form.get("newUsername"):
            return apology("Must provide new username", 400)
        elif busyUsername:
            return apology("the username is in use", 400)
        elif not request.form.get("password"):
            return apology("Must provide password", 400)
        elif not check_password_hash(oldUsername[0]["hash"], request.form.get("password")):
            return apology("passwords is wrong", 400)

        db.execute("""UPDATE users SET username = :newUsername WHERE user_id = :user_id""", user_id=user_id,
                   newUsername=request.form.get("newUsername"))
        db.execute("""UPDATE records SET username = :newUsername WHERE user_id = :user_id""", user_id=user_id,
                   newUsername=request.form.get("newUsername"))
        session["username"] = request.form.get("newUsername")
        session['message'] = "You have changed your username to: " + request.form.get("newUsername") + "!"
        return redirect("/")

    else:
        return render_template("changeusername.html", oldUsername=oldUsername[0]["username"])


@app.route("/deleteacc", methods=["GET", "POST"])
@login_required
def deleteacc():

    # Delete account
    user_id = session.get('user_id')

    if request.method == "POST":
        oldUsername = db.execute("SELECT hash FROM users WHERE user_id = :user_id", user_id=user_id)

        if not request.form.get("delete"):
            return apology("You should put tick!", 400)
        elif not request.form.get("password"):
            return apology("Must provide password!", 400)
        elif not check_password_hash(oldUsername[0]["hash"], request.form.get("password")):
            return apology("password is wrong!", 400)

        db.execute("""DELETE FROM users WHERE user_id = :user_id""", user_id=user_id)

        session.clear()
        session['message'] = 'You have deleted your account!'
        return redirect('/')

    return render_template("deleteacc.html")


@app.route("/div")
def div():
    # Division page
    session['type1'] = 'Division'
    session['message'] = None
    return render_template('div.html')


@app.route('/forgotpas', methods=['GET', 'POST'])
def forgotpas():
    # Forget password
    session['message'] = None

    if request.method == 'POST':
        user = db.execute("""SELECT * FROM users WHERE username = :username OR email=:email""",
                          email=request.form.get('usernameOrEmail'), username=request.form.get('usernameOrEmail'))
        if user:
            newPas = ''
            for i in range(5):
                newPas += chr(random.randint(49, 123))

            db.execute("""UPDATE users SET hash = :hash WHERE user_id=:user_id""",
                       hash=generate_password_hash(str(newPas)), user_id=user[0]["user_id"])

            text = "Dear " + user[0]['username'] + ", your new password is: " + str(newPas) + """\n
            Please, open Log In page, provide your username and new password!"""
            SUBJECT = 'new password'
            message = 'Subject: {}\n\n{}'.format(SUBJECT, text)
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("askchecker@gmail.com", "1A2b3C4g")
            server.sendmail("askchecker@gmail.com", user[0]["email"], message)
            session['message'] = 'New password has been sent to your email!'
            return redirect('/')

    return render_template('forgotpas.html')


@app.route('/history')
@login_required
def history():

    # History page
    user_id = session.get('user_id')
    session['message'] = None
    history = db.execute("""SELECT * FROM records WHERE user_id= :user_id ORDER BY date DESC""", user_id=user_id)
    return render_template('history.html', history=history)


@app.route('/lineareq')
def linearEq():

    # Linear equation page
    session['message'] = None
    session['type1'] = 'Linear Equations'
    return render_template('lineareq.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        session["username"] = rows[0]["username"]

        session['message'] = 'You have logged in!'
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    session['message'] = 'You have logged out!'
    # Redirect user to main page
    return redirect("/")


@app.route("/mul")
def mul():

    # Multiplication page
    session['type1'] = 'Multiplication'
    session['message'] = None
    return render_template("mul.html")


@app.route("/mulTab")
def multab():

    # Shows the multiplication table
    return render_template("multab.html")


@app.route('/quadrateq')
def quadratEq():

    # Quadratic equation page
    session['message'] = None
    session['type1'] = 'Quadratic Equations'
    return render_template('quadrateq.html')


@app.route("/records", methods=['GET', 'POST'])
def records():

    # Inserts a result in database and gives a place in overall table
    username = ''
    user_id = session.get('user_id')
    if user_id:
        user = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=user_id)
        username = user[0]['username']
    else:
        username = 'anonymous'
        user_id = None
    numberofprobl = request.args.get('numberOfProblems')
    correct = request.args.get('correct')
    time = round(float(request.args.get('time')), 3)
    type1 = session['type1']

    db.execute("""INSERT INTO records (user_id, numberofproblems, correct, time, username, type1, date2)
                  VALUES(:user_id, :numberofprobl, :correct, :time, :username, :type1, :date2)""",
               numberofprobl=numberofprobl, correct=correct, time=time, username=username, user_id=user_id, type1=type1,
               date2=datetime.now(timezone('Europe/Kiev')))

    bestResults = db.execute("""SELECT * FROM records WHERE type1 = :type1
                               ORDER BY correct DESC, numberofproblems ASC, time""", type1=type1)

    session['message'] = None

    place = 0
    for res in bestResults:
        place = place + 1

        if float(time) == float(res["time"]) and int(correct) == int(res["correct"]):
            return jsonify(place)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username!", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure second password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure email was submitted
        elif not request.form.get("email"):
            return apology("must provide email", 400)

        # Compare passwords
        elif not(request.form.get("password") == request.form.get("confirmation")):
            return apology("passwords do not match", 400)

        result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        result2 = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        # Check for the username used by other user
        if result:
            return apology("such user exists", 400)
        if result2:
            return apology("user with the given email exists", 400)

        hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash, email) VALUES(:username, :hash, :email)",
                   username=request.form.get("username"), hash=hash,
                   email=request.form.get("email"))

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["user_id"]
        session["username"] = request.form.get("username")

        session['message'] = 'You have registered!'

        message = "Dear " + request.form.get("username") + """, you are registered on a website elementary.math!\n
        Your login: """ + request.form.get("username") + ", your password: " + request.form.get("password") + "."
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("askchecker@gmail.com", "1A2b3C4g")
        server.sendmail("askchecker@gmail.com", request.form.get("email"), message)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sub")
def sub():

    # Subtraction page
    session['type1'] = 'Subtraction'
    session['message'] = None
    return render_template("sub.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)