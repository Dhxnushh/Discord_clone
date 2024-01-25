from flask import Flask, render_template, request, session, redirect, g
from flask_socketio import join_room,leave_room,SocketIO,send,emit
from cs50 import SQL
app = Flask(__name__)
app.config['DATABASE'] = 'user.db'
db = SQL("sqlite:///user.db")
app.config['SECRET_KEY'] = 'DISCORD'
socketio = SocketIO(app)

@app.route("/", methods=["POST", "GET"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("usernam")
        password = [request.form.get("passwor")]
        rows = db.execute('SELECT * FROM users WHERE username = ?', username)
        if len(rows)!=1:
            return render_template("login.html",error="Username is incorrect")
        passwordsql = (db.execute('SELECT password FROM users WHERE username = ?', username))
        passwordsql=list(passwordsql[0].values())
        if password==passwordsql:
            session["user_id"] = rows[0]["username"]
            session["id"] = rows[0]['id']
            print(rows)
            return redirect("/home")
        else:
            return render_template("login.html",error="Password is incorrect")
        
    else:
        return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("usernam")
        password = request.form.get("passwor")
        cpassword = request.form.get("cpassword")
        print(username)

        if cpassword != password:
            return render_template("register.html", error="Passwords do not match.")

        # Check if the username already exists
        row = db.execute('SELECT * FROM users WHERE Username = ?', (username,))
        if len(row)!=0:
                return render_template("register.html",error="username already exist")

        # Insert the new user into the database
        else:
            db.execute('INSERT INTO users (username, password) VALUES (?)', (username, password))
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/home", methods=["POST", "GET"])
def home():
    if session.get("user_id") is None:
        return redirect("/")
    username = session["user_id"]
    rows2 = db.execute('select * from users where username = ?', username)
    if request.method=="POST":
        friend = request.form.get("friend")

        rows=db.execute('select * from users where username = ?',friend)
        if len(rows)!=1:
            return render_template("layout2.html", error= "Username does not exist.",username=username)
        
        rows2 = db.execute('select * from users where username = ?', username)
        rows3=db.execute('select * from friends where friend = ? and id = ?', friend,rows2[0]['id'])
        if len(rows3)!=0:
            return render_template("layout2.html", error="Username already in your friends",username=username)
        
        rows4 = db.execute('select * from users where username = ?',friend)
        rows5 = db.execute('select * from friends where id = ? and friend = ?',rows4[0]['id'],username)
        if len(rows5)!=0:
            db.execute('insert into friends(id,friend,room) values(?,?,?)', rows2[0]['id'],friend,rows5[0]['room'])
        else:
            room = str(rows2[0]['id'])+str(friend)    
            db.execute('insert into friends(id,friend,room) values(?,?,?)', rows2[0]['id'],friend,room)


    fdict = db.execute('select friend from friends where id = ?',rows2[0]['id'] )
    flist=[]
    for i in fdict:
        print(i)
        flist+=(list(i.values()))            
    return render_template("layout2.html",username=username,flist=flist)


@socketio.on('connect', namespace='/room')
def connect():
    print("Connected")


@socketio.on('join_room', namespace='/room')
def joinroom(data):
    username = session["user_id"]
    friend = data['username']
    print(data.keys())
    rows = db.execute('select * from friends where id =? and friend = ?',session["id"],friend)
    room = rows[0]['room']
    join_room(room)
    print("joined room")


    
if __name__ == "__main__":
    socketio.run(app)


