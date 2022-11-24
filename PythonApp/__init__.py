from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from urllib.parse import quote
from flask_login import LoginManager
from flask_babelex import Babel

app = Flask(__name__)
app.secret_key = 'abcs123jjdusu'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/cnpm_btl?charset=utf8mb4' % quote('Admin@123')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app = app)
login = LoginManager(app=app)
babel = Babel(app=app)


@babel.localeselector
def load_locale():
    return "vi"
