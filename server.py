from flask import Flask, render_template, request, redirect,session,flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt  

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "keep it secret"

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/create_user', methods=['POST'])
def create_user():
    if len(request.form['firstname']) < 2:
    	flash("Please enter a first name")
    if len(request.form['lastname']) < 2:
    	flash("Please enter a last name")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address!")
    if len(request.form['password']) < 5:
        flash("Password must be longe than 7 characters!")
    if request.form['cpassword'] != request.form['password']:
        flash('Passwords DO NOT Match!')
    if not '_flashes' in session.keys():
        flash("You Are Successfully Added!")
        pw_hash = bcrypt.generate_password_hash(request.form['password'])

        query= "INSERT INTO users(firstname, lastname, email, password, created_at, updated_at) VALUES (%(firstname)s,%(lastname)s,%(email)s,%(password)s,NOW(),NOW());"
        mysql=connectToMySQL("recipes")
        data = {
            'firstname': request.form['firstname'],
            'lastname': request.form['lastname'],
            'email': request.form['email'],
            'password': pw_hash
        }
        user_ = mysql.query_db(query,data)
        session['user_id']= user_
        return redirect("/welcome")
    else: 
        return redirect("/")

@app.route("/login", methods = ['POST','GET'])
def login():

    query = "SELECT * FROM users WHERE email = %(email)s;"
    data= {
        'email': request.form['email']
    }
    mysql=connectToMySQL("recipes")
    result = mysql.query_db(query, data)
    print(result)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['user_id'] = result[0]['id']
            return redirect("/welcome")
        else:
            flash("Password DOES NOT Match!")
            return redirect("/")
    else:
        flash("Could NOT Login!")
        return redirect("/")


@app.route("/welcome")
def welcome():
    wel = 'SELECT * FROM user'
    come =connectToMySQL('recipes')
    welcome = come.query_db(wel)
    query = 'SELECT * FROM recipe;'
    mysql= connectToMySQL('recipes')
    show=mysql.query_db(query)
    print(show)
    return render_template("dashbord.html", show = show,welcome=welcome )



@app.route("/showrecipe")
def showrecipe():
    query = "SELECT * FROM recipe;"
    mysql= connectToMySQL('recipes')
    recipes=mysql.query_db(query)
    return render_template("showrecipe.html", recipes = recipes)


@app.route("/add", methods=['POST'])
def add():
    query = "INSERT INTO recipe ( description,instructions,under,user_id,name,created_at,updated_at)VALUES(%(description)s,%(instructions)s, %(under)s, %(id)s,%(name)s,NOW(),NOW());"
    data = {
    'description':request.form['description'],
    'under':request.form['under'],
    'instructions':request.form['instructions'],
    'id':session['user_id'],
    'name':request.form['name']
    }
    bd=connectToMySQL('recipes')
    bd.query_db(query,data)
    print(bd)
    return redirect("/showrecipe")

@app.route('/addrec')
def addmag():
    return render_template('add.html')





@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




@app.route('/edit_page/<user_id>')
def edit_page(user_id):
    query = "SELECT * FROM recipe WHERE id= %(id)s;"
    data={
        'id': user_id
    }
    recipe= connectToMySQL('recipes').query_db(query,data)
    return render_template("edit.html",recipe=recipe[0])


 
@app.route('/veiw/<user_id>')
def user_page(user_id):
    mysql= connectToMySQL('recipes')
    data={
        'id': user_id
    }
    recipe = mysql.query_db ('SELECT * FROM recipe WHERE id= %(id)s;',data)
    return render_template('/showrecipe',recipe=recipe[0])





@app.route('/delete/<recipe_id>')
def delete(recipe_id):
    query = "DELETE FROM recipe WHERE id = %(id)s;"
    data={
        'id': recipe_id
    }
    connectToMySQL('recipes').query_db(query,data)
    print(users)
    return redirect('/welcome')

if __name__ == "__main__":
    app.run (debug=True)