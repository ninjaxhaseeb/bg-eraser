from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'haseeb'
    
    
    from .views import views
    from .auth import auth
    from .bg import bg
    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(bg)
    CORS(app)
    return app
