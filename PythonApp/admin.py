import sqlalchemy.sql
from flask import Flask, flash
from PythonApp import db, app, LoadData
from PythonApp.models import AirPort, StopOver, AirRoute, Rule, UserRole
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla.filters import FilterLike
from flask_admin.contrib.sqla import ModelView
from flask_admin.babel import gettext
from flask_login import logout_user, current_user
from flask import request, redirect
from datetime import datetime


def getAirPort():
    with app.app_context():
        return [(p.id, p.location) for p in AirPort.query.all()]


def getRule(i):
    with app.app_context():
        i = int(i)
        r = Rule.query.get(i)
        return r.max_stopover


class AuthModelView(ModelView):
    can_view_details = True
    named_filter_urls = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class AuthView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class AirPortView(AuthModelView):
    form_columns = ('name', 'location')



class AirRouteView(AuthModelView):
    # //column_list = []
    column_searchable_list = ['name']
    column_filters = [
        FilterLike(column=AirRoute.departure_id, name='Nơi đi', options=getAirPort()),
        FilterLike(column=AirRoute.destination_id, name='Nơi đến', options=getAirPort())]
    form_columns = ('name', 'departure', 'destination', 'stop_over', 'rule')

    def update_model(self, form, model):

        if len(form.stop_over.data) <= getRule(form.rule.data.id):  # kiem tra dung luat chua
            model.departure_id = form.departure.data.id
            model.destination_id = form.destination.data.id
            model.name = form.name.data
            model.rule_id = form.rule.data.id
            db.session.add(model)
            db.session.commit()
            if len(form.stop_over.data) < 1:
                st = StopOver.query.filter(StopOver.airroute_id == model.id).all()
                for i in st:
                    i.airroute_id = None
                    db.session.add(i)
                    db.session.commit()
            else:
                for i in form.stop_over.data:
                    stopover = StopOver.query.get(i)
                    stopover.airroute_id = None
                    db.session.add(stopover)
                    db.session.commit()
            for i in form.stop_over.data:
                stopover = StopOver.query.get(i)
                stopover.airroute_id = model.id
                db.session.add(stopover)
                db.session.commit()
            return True
        else:
            flash(gettext('Quá số lượng sân bay quá cảnh theo quy định'), 'error')

    def create_model(self, form):
        if len(form.stop_over.data) <= getRule(form.rule.data.id):
            new_ar = AirRoute(name=form.name.data, departure_id=form.departure.data.id,
                              destination_id=form.destination.data.id,
                              rule_id=form.rule.data.id)
            db.session.add(new_ar)
            db.session.commit()
            for i in form.stop_over.data:
                stopover = StopOver.query.get(i)
                stopover.airroute_id = new_ar.id
                db.session.add(stopover)
                db.session.commit()
            return True
        else:
            flash(gettext('Quá số lượng sân bay quá cảnh theo quy định'), 'error')


class StatsView(AuthView):
    @expose('/')
    def index(self):
        month = request.args.get('month')
        year = request.args.get('year')

        Fclass_ticket_stat = LoadData.ticket_first_class_stat(month=month, year=year)
        Sclass_ticket_stat = LoadData.ticket_second_class_stat(month=month, year=year)
        flight_stat = LoadData.flight_stat_by_air_route(month=month, year=year)
        ticket_amount_stat = LoadData.ticket_amount_stat(month=month, year=year)

        ticket_income_total = LoadData.convert_to_list_of_tuple(
            LoadData.combine_ticket_income_stats(Fclass_stat=Fclass_ticket_stat, Sclass_stat=Sclass_ticket_stat))

        total_stat = LoadData.convert_to_list_of_tuple(
            LoadData.add_ticket_stat(flight_stats=flight_stat, ticket_income_total=ticket_income_total))

        total_income = LoadData.get_total_income(total_stat=total_stat)

        return self.render('admin/stats.html', stats= total_stat, sum=total_income, current_year=datetime.year)


class LogoutView(AuthView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


admin = Admin(app=app, name='Quản trị sân bay', template_mode='bootstrap4')
admin.add_view(AirPortView(AirPort, db.session, name='Sân bay'))
admin.add_view(AirRouteView(AirRoute, db.session, name='Tuyến bay'))
admin.add_view(AuthModelView(StopOver, db.session, name='Trung chuyển'))
admin.add_view(StatsView(name='Thống kê - báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
