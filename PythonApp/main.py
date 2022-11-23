
from selenium.webdriver.common.by import By
from flask import render_template, request, redirect, url_for
import datetime
from  datetime import timedelta
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


@app.route("/")
def index():
    location = LoadData.getLocation()
    des = request.args.get('destination')
    dep = request.args.get('departure')
    time = request.args.get('date')
    flight = LoadData.get_flight(departure=dep, destination=des, time=time)
    return render_template("Search.html", location = location, flight= flight)

@app.route('/flight/<int:flight_id>')
def details(flight_id):
    f = LoadData.get_flight_by_id(flight_id)
    t = LoadData.get_flight_time_by_id(flight_id)
    st = LoadData.get_stopover_by_airroute_id(f.air_route_id)
    remaining_Fseat = t.num_o_Fseat
    remaining_Sseat = t.num_o_Sseat
    flight_time = t.time
    err_msg = ''
    try:
        Adult1 = int(request.args.get('Fseat_adult'))
        Child1 = int(request.args.get('Fseat_child'))
        Adult2 = int(request.args.get('Sseat_adult'))
        Child2 = int(request.args.get('Sseat_child'))
    except:
        Adult1 = Child1 = Adult2 = Child2 = 0
    if Adult1 or Child1 or Adult2 or Child2:
        if flight_time - datetime.datetime.now() > timedelta(hours=f.airroute.rule.selling_ticket_hour):
            if (remaining_Fseat >= Adult1 + Child1) and (remaining_Sseat >= Adult2 + Child2):
                return redirect(url_for('ticket', Adult_Fseat=Adult1, Adult_Sseat=Adult2, Child_Fseat=Child1, Child_Sseat=Child2))
            else:
                err_msg = 'Số lượng vé mua vượt quá số lượng vé còn'
        else:
            err_msg = 'Đã quá thời gian mua vé'
    return render_template('details.html', flight=f, time=t, stopover=st, err_msg=err_msg)

@app.route("/ticket/<int:Adult_Fseat>, <int:Adult_Sseat>, <int:Child_Fseat>, <int:Child_Sseat>")
def ticket(Adult_Fseat, Adult_Sseat, Child_Fseat, Child_Sseat):
    list = request.args.get('a1')
    err_msg = 'he'
    err_msg=LoadData.getTicketInfo(list)
    return render_template('/ticket.html', Adult_Fseat=Adult_Fseat, Adult_Sseat=Adult_Sseat,
                           Child_Fseat= Child_Fseat, Child_Sseat=Child_Sseat, err_msg=err_msg)


@login.user_loader
def load_user(user_id):
    return LoadData.get_user_by_id(user_id)

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)