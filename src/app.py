import flask
from base_module.models.exception import ModuleException
from base_module.models.logger import setup_logging, LoggerConfig
from flask_cors import CORS
from injectors.connections import pg
from routers.users import users_bp
from routers.schedule_base import  schedule_base_bp
from routers.schedule_adjustments import  schedule_adjustments_bp

app = flask.Flask(__name__)

setup_logging(LoggerConfig(root_log_level='DEBUG'))
pg.setup(app)

app.register_blueprint(users_bp)
app.register_blueprint(schedule_base_bp)
app.register_blueprint(schedule_adjustments_bp)
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True,
    expose_headers=["Content-Disposition"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.errorhandler(ModuleException)
def handle_exception(error: ModuleException):
    response = flask.jsonify(error.json())
    response.status_code = error.code
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
