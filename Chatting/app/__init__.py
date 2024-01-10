from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO(logger=True, engineio_logger=True)

def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.config['JWT_SECRET_KEY'] = 'hard to guess...'
    
    socketio.init_app(app)

    from app.events import socketio_init
    socketio_init(socketio)    
    
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app