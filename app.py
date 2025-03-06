import bcrypt
from flask import Flask, jsonify, request
from database import db
from models.User import User
from models.Meal import Meal
from datetime import datetime
from flask_login import LoginManager, current_user, login_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-auth-challenge'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
  data = request.get_json()

  username = data.get('username')
  password = data.get('password')

  missing_credentials = not username or not password

  if missing_credentials:
    return jsonify({'message': 'Missing credentials' }), 400

  user = User.query.filter_by(username=username).first()

  user_not_found = not user
  user_password = getattr(user, "password", None)
  wrong_password = not bcrypt.checkpw(str.encode(password), str.encode(user_password))

  if user_not_found or wrong_password:
    return jsonify({'message': 'Invalid credentials' }), 400

  login_user(user)

  return jsonify({'message': 'Successfull login'})

@app.route('/meals', methods=['POST'])
def create_meal():
  data = request.get_json()

  name = data.get('name')
  description = data.get('description')
  eaten_at = data.get('eaten_at') or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  is_in_diet = data.get('is_in_diet')

  new_meal = Meal(name=name, description=description, eaten_at=eaten_at, is_in_diet=is_in_diet, user_id=current_user.id)

  db.session.add(new_meal)
  db.session.commit()

  return jsonify({'message': 'Meal successfully created'})

if __name__=='__main__':
  app.run(debug=True)