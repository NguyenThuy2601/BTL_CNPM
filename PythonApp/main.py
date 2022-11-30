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
    option = request.args.get("seatclass")
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
                    url_for('ticket', Adult=Adult, Child=Child, f_id=flight_id, sclass=option))
            else:
                err_msg = 'Số lượng vé mua vượt quá số lượng vé còn'
        else:
            err_msg = 'Đã quá thời gian mua vé'
    return render_template('details.html', flight=f, stopover=st, err_msg=err_msg)


@app.route("/ticket/<int:Adult>, <int:Child>, <int:f_id>, <int:sclass>", methods=['get','post'])
def ticket(Adult, Child, f_id, sclass):
    TicketList = []
    f = LoadData.get_flight_by_id(f_id)
    err_msg = ""
    if request.method == 'POST':
        adult_Fname = request.form.getlist('AFname')
        adult_Lname = request.form.getlist('ALname')
        adult_phone = request.form.getlist('APhone')
        adult_cccd = request.form.getlist('APaper')
        adult_pp = request.form.getlist('APP')
        adult_DOB = request.form.getlist('ADOB')

        child_Fname =request.form.getlist('CFname')
        child_Lname = request.form.getlist('CLname')
        child_DOB = request.form.getlist('CDOB')
        child_pp = request.form.getlist('CPP')
        child_phone = request.form.getlist('CPhone')

        for i in range(0, Adult):
            user = None
            if adult_cccd[0]:  # kiem tra co dien cccd khong
                user = LoadData.get_user_by_paper(adult_cccd[0])
            else:  # Neu khong dien cccd kiem tra co dien pp hay khong
                user = LoadData.get_user_by_paper(adult_pp[i])
            if user > -1:
                ticket = LoadData.create_ticket(owner_id=user, sclass= sclass, flight=f_id, buyer_id=user, seller_id=2)
                if not LoadData.get_user_by_paper(adult_cccd[i]):
                    LoadData.create_id_paper(adult_cccd[i], models.Papers.CCCD, user)
                if not LoadData.get_user_by_paper(adult_pp[i]):
                    LoadData.create_id_paper(adult_cccd[i], models.Papers.PASSPORT, user)
                TicketList.append(ticket)
            else:
                user = LoadData.get_user_by_name_and_dob(adult_Fname[i], adult_Lname[i], adult_DOB[i])
                if user > -1:
                    ticket = LoadData.create_ticket(owner_id=user, sclass= sclass, flight=f_id, buyer_id=user, seller_id=2)
                    if adult_cccd[i]:
                        LoadData.create_id_paper(adult_cccd[i], models.Papers.CCCD, user)
                    if adult_pp[i]:
                        LoadData.create_id_paper(adult_cccd[i], models.Papers.PASSPORT, user)
                    TicketList.append(ticket)
                else:
                    new_user = LoadData.create_customer(Fname=adult_Fname[i], Lname=adult_Lname[i], phone=adult_phone[i],
                                                    dob=adult_DOB[i])
                    if adult_cccd[i]:
                        LoadData.create_id_paper(adult_cccd[i], models.Papers.CCCD, new_user)
                    if adult_pp[i]:
                        LoadData.create_id_paper(adult_cccd[i], models.Papers.PASSPORT, new_user)
                    ticket = LoadData.create_ticket(owner_id=new_user, sclass= sclass, flight=f_id, buyer_id=new_user, seller_id=2)
                    TicketList.append(ticket)

        for i in range(0, Child):
            user = None
            if child_pp[i]:
                user = LoadData.get_user_by_paper(child_pp[i])
            if user > -1:
                ticket = LoadData.create_ticket(owner_id=user, sclass= sclass, flight=f_id, buyer_id=user, seller_id=2)
                TicketList.append(ticket)
            else:
                user = LoadData.get_user_by_name_and_dob(child_Fname, child_Lname, child_DOB)
                if user > -1:
                    ticket =LoadData.create_ticket(owner_id=user, sclass= sclass, flight=f_id, buyer_id=user, seller_id=2)
                    if child_pp[i]:
                        LoadData.create_id_paper(child_pp[i], models.Papers.PASSPORT, user)
                    TicketList.append(ticket)
                else:
                    new_user = LoadData.create_customer(Fname=child_Fname[i], Lname=child_Lname[i], dob=child_DOB[i],
                                                    phone=child_phone[i])
                    if child_pp[i]:
                        LoadData.create_id_paper(child_pp[i], models.Papers.PASSPORT, user.id)
                    ticket = LoadData.create_ticket(owner_id=new_user, sclass= sclass, flight=f_id, buyer_id=new_user, seller_id=2)
                    TicketList.append(ticket)
        return redirect(url_for('previewTicket', list = TicketList))
    return render_template('/ticket.html', Adult=Adult, Child=Child, f=f, sclass=sclass, err_msg=err_msg)

@app.route('/previewTicket/<list>')
def previewTicket(list):
    return render_template('/previewTicket.html', list=list)

@login.user_loader
def load_user(user_id):
    return LoadData.get_user_by_id(user_id)


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
