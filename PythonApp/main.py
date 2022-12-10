from flask import session
from PythonApp import app, admin, LoadData, login, models, controllers


app.add_url_rule('/login-admin', 'login-admin', controllers.login_admin, methods=['post'])
app.add_url_rule('/', 'index', controllers.index)
app.add_url_rule('/flight/<int:flight_id>', 'details', controllers.details)
app.add_url_rule("/ticket/<int:Adult>, <int:Child>, <int:f_id>, <int:sclass>", 'ticket', controllers.ticket,
                   methods=['get', 'post'])
app.add_url_rule('/ticketPDF/<list>', 'convert_to_pdf' ,controllers.convert_to_pdf)
app.add_url_rule('/previewTicket/<list>', 'previewTicket', controllers.previewTicket,methods=['get', 'post'])
app.add_url_rule('/login', 'login_my_user', controllers.login_my_user,methods=['get', 'post'])
app.add_url_rule('/logout', 'logout_my_user',controllers.logout_my_user)
app.add_url_rule('/searchTicket/<int:flight_id>/<err_msg>', 'searchTicket', controllers.searchTicket)
app.add_url_rule('/updateTicket/<int:flight_id>/<int:ticket_id>','updateTicket', controllers.updateTicket)


@login.user_loader
def load_user(user_id):
    return LoadData.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
