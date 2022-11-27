from flask import render_template, request, redirect, url_for
import datetime
from datetime import timedelta
from PythonApp import app, admin, LoadData, login, models
from flask_login import login_user, logout_user
import cloudinary.uploader


@app.route('/login-admin', methods=['post'])
def login_admin():
    username = request.form['username']
    passw = request.form['passw']
    user = LoadData.auth_user(username=username, passw=passw)
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
    return render_template("Search.html", location=location, flight=flight)


@app.route('/flight/<int:flight_id>')
def details(flight_id):
    f = LoadData.get_flight_by_id(flight_id)
    st = LoadData.get_stopover_by_airroute_id(f.air_route_id)
    remaining_Fseat = f.schedule[0].num_o_Fseat
    remaining_Sseat = f.schedule[0].num_o_Sseat
    flight_time = f.schedule[0].time
    err_msg = ''
    try:
        Adult = int(request.args.get('adult'))
        Child = int(request.args.get('child'))
    except:
        Adult = Child = 0
    if Adult or Child:
        if flight_time - datetime.datetime.now() > timedelta(hours=f.airroute.rule.selling_ticket_hour):
            if (remaining_Fseat >= Adult + Child) and (remaining_Sseat >= Adult + Child):
                return redirect(
                    url_for('ticket', Adult=Adult, Child = Child,
                            f_id=flight_id))
            else:
                err_msg = 'Số lượng vé mua vượt quá số lượng vé còn'
        else:
            err_msg = 'Đã quá thời gian mua vé'
    return render_template('details.html', flight=f, stopover=st, err_msg=err_msg)


@app.route("/ticket/<int:Adult>, <int:Child>, <int:f_id>")
def ticket(Adult_Fseat, Adult_Sseat, Child_Fseat, Child_Sseat, f_id):
    TicketList = []
    f = LoadData.get_flight_by_id(f_id)
    return render_template('/ticket.html', Adult_Fseat=Adult_Fseat, Adult_Sseat=Adult_Sseat,
                           Child_Fseat=Child_Fseat, Child_Sseat=Child_Sseat, f = f)


@login.user_loader
def load_user(user_id):
    return LoadData.get_user_by_id(user_id)

<<<<<<< HEAD
=======

# <<<<<<< HEAD
@app.route("/login")
def login():
    return render_template("login.html")

# =======
# >>>>>>> ba4d3624c944c978b2d92b44b74553e5c8c9ca49
>>>>>>> b44ee81bb7922b93e1672927fc056bdc12d7deec
if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
