
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from tables import BlogTable

app = Flask(__name__)
db = BlogTable()


@app.route('/raw_entries', methods=['GET'])

def raw_entries():
    db.execute_query('''SELECT * FROM blog_posts''')
    posts = db.cursor.fetchall()
    print(posts)
    print(session['user_id'])
    return jsonify({"message": "from raw entries"})



@app.route('/view_blog_posts', methods=['GET'])

def view_blog_posts():
    user_id = session['user_id']
    db.execute_query('''SELECT * FROM blog_posts WHERE user_id = ?''', (user_id,))
    blog_posts = db.cursor.fetchall()
    # db.execute_query("SELECT * FROM blog_posts")
    # all_posts = db.cursor.fetchall()
    print(blog_posts)

    if len(blog_posts) == 0:
        return jsonify({"message": "User has not made any posts yet"})
    else:
        return blog_posts


@app.route('/create_blog_post', methods=['POST'])

def create_blog_post():
    # each blog post will have a delete button with a path to delete itself
    data = request.get_json()

    # post_id is autogenerated
    # user_id should already be part of the session so let's get it from there
    user_id = session['user_id']
    title = data.get('title')
    content = data.get('content')
    # created_at is autogenerated
    print(f"INSIDE CREATE POST: USER ID: {user_id}")
    db.execute_query('''INSERT INTO blog_posts (user_id, title, content) VALUES (?,?,?)''', (user_id, title, content))
    print(f"DATA: {title, content}")
    return jsonify({"message": "blog post entered successfully"})


@app.route('/create_account', methods=['GET', 'POST'])

def create_account():
    if request.method == 'GET':
        return render_template("create_account.html")
    elif request.method == 'POST':
        #password_hash is the table column name
        data = request.get_json()

        username = data.get('username')
        entered_password = data.get('entered_password') # password entered from form before hash
        email = data.get('email')

        # are the username and email already taken?
        has_username = db.execute_query('''SELECT * FROM users WHERE username = ?''', (username,))
        has_email = db.execute_query('''SELECT * FROM users WHERE email = ? ''', (email,))

        if has_username:
            return jsonify({"message": "Username has already been taken"}), 400
        elif has_email:
            return jsonify({"message": "Email has already been taken"}), 400
        else:
            password_hash = generate_password_hash(entered_password)
            db.execute_query('''INSERT INTO users (username, password_hash, email) VALUES (?,?,?)''', (username, password_hash, email,))
            print("account created successfully")
            return redirect('/homepage')
    





@app.route('/login', methods=['GET', 'POST'])

def login():
    # lets get the login data from the JS file
    # The JS file should have sent us a JSON object with:
    # username and password
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':

        data = request.get_json()

        username = data.get('username')
        entered_password = data.get('entered_password')

        user = db.execute_query('''SELECT * FROM users WHERE username = ?''', (username,))

        if user:
            print(f"...user found: {username}...")
            user_data = user[0]
            stored_password_hash = user_data[2]
            is_password = check_password_hash(stored_password_hash, entered_password)

            if not is_password:
                return jsonify({"error": "Invalid password"}), 401
            else:
                session['user_id'] = user_data[0]
                session['username'] = username
                print(f"welcome, {username}")
                return redirect('/homepage')
        


@app.route('/logout', methods=['GET'])

def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/homepage', methods=['GET'])

def homepage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('homepage.html', username=session['username'], user_id=session['user_id'])
    




if __name__ == '__main__':
    app.run(debug=True)
    db.close_database()
