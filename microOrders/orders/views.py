from flask import Flask
from orders.controllers.order_controller import order_controller
from db.db import db
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'secret123'
CORS(app)
app.config.from_object('config.Config')
db.init_app(app)

app.register_blueprint(order_controller)
CORS(app, supports_credentials=True)

@app.route('/healthcheck')
def health_check():
    return '', 200