from flask import render_template, request, redirect
from PythonApp import app, admin, LoadData, login
from flask_login import login_user, logout_user
import cloudinary.uploader


@app.route('/login-admin', methods= ['post'])
def login_admin():
    username = request.form['username']
    passw = request.form['passw']
    user = LoadData.auth_user(username= username, passw= passw)
    if user:
        login_user(user)

    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return LoadData.get_user_by_id(user_id)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)