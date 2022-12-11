from flask import render_template, request, redirect, url_for, make_response
import datetime
from datetime import timedelta
from PythonApp import app, admin, LoadData, login, models
from PythonApp.decorators import annonynous_user
from flask_login import login_user, logout_user, current_user
import pdfkit


def login_admin():
    username = request.form['username']
    passw = request.form['passw']
    user = LoadData.auth_user(username=username, passw=passw)
    if user:
        login_user(user)

    return redirect('/admin')


def index():
    location = LoadData.getLocation()
    des = request.args.get('destination')
    dep = request.args.get('departure')
    time = request.args.get('date')
    flight = LoadData.get_flight(departure=dep, destination=des, time=time)
    return render_template("Search.html", location=location, flight=flight)


def details(flight_id):
    f = LoadData.get_flight_by_id(flight_id)
    st = LoadData.get_stopover_by_airroute_id(f.air_route_id)
    Fseat_num = LoadData.get_remaining_seat(f_id=flight_id, sclass=1)
    Sseat_num = LoadData.get_remaining_seat(f_id=flight_id, sclass=2)
    option = request.args.get("seatclass")
    err_msg = ''
    try:
        Adult = int(request.args.get('adult'))
        Child = int(request.args.get('child'))
    except:
        Adult = Child = 0
    if Adult or Child:
        if f.schedule[0].time - datetime.datetime.now() > timedelta(hours=f.airroute.rule.selling_ticket_hour):
            if (LoadData.get_remaining_seat(f_id=flight_id, sclass=option) >= Adult + Child):
                return redirect(
                    url_for('ticket', Adult=Adult, Child=Child, f_id=flight_id, sclass=option))
            else:
                err_msg = 'Số lượng vé mua vượt quá số lượng vé còn'
        else:
            err_msg = 'Đã quá thời gian mua vé'
    return render_template('details.html', flight=f, stopover=st, Fseat_num=Fseat_num, Sseat_num=Sseat_num ,err_msg=err_msg)


def ticket(Adult, Child, f_id, sclass):
    TicketList = []
    f = LoadData.get_flight_by_id(f_id)
    err_msg = ""
    if sclass == 1:
        price = f.ticketprice.Fprice
    else:
        price = f.ticketprice.Sprice
    total_cost = (Adult + Child) * price
    if request.method == 'POST':
        TicketList.clear()
        adult_Fname = request.form.getlist('AFname')
        adult_Lname = request.form.getlist('ALname')
        adult_phone = request.form.getlist('APhone')
        adult_pp = request.form.getlist('APaper')
        pp_type = request.form.getlist('paperType')
        adult_DOB = request.form.getlist('ADOB')

        child_Fname = request.form.getlist('CFname')
        child_Lname = request.form.getlist('CLname')
        child_DOB = request.form.getlist('CDOB')
        child_pp = request.form.getlist('CPP')
        child_phone = request.form.getlist('CPhone')

        buyer_Fname = request.form.get('BuyerFname')
        buyer_Lname = request.form.get('BuyerLname')
        buyer_phone = request.form.get('BuyerPhone')
        buyer_pp = request.form.get('BuyerPaper')
        buyer_pp_type = request.form.get('BuyerpaperType')
        buyer_DOB = request.form.get('BuyerDOB')

        buyer = LoadData.get_customer_by_paper(buyer_pp)
        if not buyer:
            buyer = LoadData.get_customer_by_name_and_dob(Fname=buyer_Fname, Lname=buyer_Lname, dob=buyer_DOB)
            if not buyer:
                buyer = LoadData.create_customer(Fname=buyer_Fname, Lname=buyer_Lname, dob=buyer_DOB, phone=buyer_phone)
                LoadData.create_id_paper(code=buyer_pp, type=models.Papers.from_str(buyer_pp_type), u_id=buyer)

        for i in range(0, Adult):
            user1 = LoadData.get_customer_by_paper(adult_pp[i])
            if user1:
                LoadData.update_phone_number(adult_phone[i], user1)
                ticket = LoadData.create_ticket(owner_id=user1, sclass=sclass, flight_id=f_id, buyer_id=buyer,
                                                seller_id=current_user.id)
                TicketList.append(ticket)
            else:
                user1 = LoadData.get_customer_by_name_and_dob(adult_Fname[i], adult_Lname[i], adult_DOB[i])
                if user1:
                    LoadData.update_phone_number(adult_phone[i], user1)
                    ticket = LoadData.create_ticket(owner_id=user1, sclass=sclass,flight_id=f_id, buyer_id=buyer,
                                                    seller_id=current_user.id)
                    LoadData.create_id_paper(adult_pp[i], models.Papers.from_str(pp_type[i]), user1)
                    TicketList.append(ticket)
                else:
                    new_user = LoadData.create_customer(Fname=adult_Fname[i], Lname=adult_Lname[i],
                                                        phone=adult_phone[i],
                                                        dob=adult_DOB[i])
                    LoadData.create_id_paper(adult_pp[i], models.Papers.from_str(pp_type[i]), new_user)
                    ticket = LoadData.create_ticket(owner_id=new_user, sclass=sclass, flight_id=f_id, buyer_id=buyer,
                                                    seller_id=current_user.id)
                    TicketList.append(ticket)

        for i in range(0, Child):
            user1 = None
            if child_pp[i]:
                user1 = LoadData.get_customer_by_paper(child_pp[i])
            if user1:
                LoadData.update_phone_number(adult_phone[i], user1)
                ticket = LoadData.create_ticket(owner_id=user1, sclass=sclass, flight_id=f_id, buyer_id=buyer, seller_id=2)
                TicketList.append(ticket)
            else:
                user1 = LoadData.get_customer_by_name_and_dob(child_Fname[i], child_Lname[i], child_DOB[i])
                if user1:
                    LoadData.update_phone_number(child_phone[i], user1)
                    ticket = LoadData.create_ticket(owner_id=user1, sclass=sclass, flight_id=f_id, buyer_id=buyer,
                                                    seller_id=2)
                    if child_pp[i]:
                        LoadData.create_id_paper(child_pp[i], models.Papers.PASSPORT, user1)
                    TicketList.append(ticket)
                else:
                    new_user = LoadData.create_customer(Fname=child_Fname[i], Lname=child_Lname[i], dob=child_DOB[i],
                                                        phone=child_phone[i])
                    if child_pp[i]:
                        LoadData.create_id_paper(child_pp[i], models.Papers.PASSPORT, new_user.id)
                    ticket = LoadData.create_ticket(owner_id=new_user, sclass=sclass, flight_id=f_id, buyer_id=buyer,
                                                    seller_id=2)
                    TicketList.append(ticket)
        return redirect(url_for('previewTicket', list=TicketList))

    return render_template('/ticket.html', Adult=Adult, Child=Child, f=f, sclass=sclass, err_msg=err_msg,
                           cost=total_cost)


def convert_to_pdf(list):
    Tlist = list.strip('][').split(',')
    for i in range(0, len(Tlist)):
        Tlist[i] = LoadData.get_ticket_by_id(Tlist[i])

    rendered = render_template("/ticketPDF.html", list=Tlist, name='Thuy')
    pdf = pdfkit.from_string(rendered)

    response = make_response(pdf, False)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=ticket.pdf'

    return response


def previewTicket(list):
    Tlist = list.strip('][').split(',')
    for i in range(0, len(Tlist)):
        Tlist[i] = LoadData.get_ticket_by_id(Tlist[i])

    if request.method == 'POST':
        return redirect(url_for('convert_to_pdf', list=list))

    return render_template('/previewTicket.html', list=Tlist)


@annonynous_user
def login_my_user():
    err_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = LoadData.auth_user(username=username, passw=password)
        if user and user.user_role == models.UserRole.EMPLOYEE:
            login_user(user=user)
            return redirect('/')
        else:
            if user and user.user_role == models.UserRole.ADMIN:
                login_user(user=user)
                return redirect('/admin')
            else:
                err_msg = 'Không tìm thấy người dùng'
    return render_template('login.html', err_msg=err_msg)


def logout_my_user():
    logout_user()
    return redirect('/login')


def searchTicket(flight_id, err_msg=None):
    ticket_id = request.args.get('TicketID')
    ticket = LoadData.get_ticket(ticket_id)
    flight = LoadData.get_flight_by_id(flight_id)

    return render_template('searchTicket.html', ticket=ticket, f=flight, err_msg=err_msg)


def updateTicket(flight_id, ticket_id):
    ticket = LoadData.get_ticket_by_id(ticket_id)
    err_msg = ''
    if LoadData.get_remaining_seat(f_id=flight_id, sclass=ticket.seat_class):
        Tlist = []
        ticket = LoadData.updateTicket(flight_id=flight_id, ticket_id=ticket_id)
        Tlist.append(ticket)
        return redirect(url_for('previewTicket', list=Tlist))
    else:
        err_msg = 'Đã hết vé tương ứng cho chuyến này'
        return redirect(url_for('searchTicket', err_msg=err_msg))
