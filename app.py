import bcrypt
from flask import Flask, jsonify, request
from database import db
from models.User import User
from models.Meal import Meal
from datetime import datetime
from flask_login import LoginManager, current_user, login_required, login_user, logout_user


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

@app.route('/logout',methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({'message': 'Successfully loged out'})

@app.route('/users', methods=['POST'])
def create_user():
  data = request.get_json()

  username = data.get('username')
  password = data.get('password')

  missing_credentials = not username or not password

  if missing_credentials:
    return jsonify({'message': 'Please provide username and password'}), 400

  already_existent_username = User.query.filter_by(username=username).first()

  if already_existent_username:
    return jsonify({'message': 'Username already in use. Please choose another'})
  
  hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
  new_user = User(username=username, password=hashed_password)

  db.session.add(new_user)
  db.session.commit()

  return jsonify({'message': 'User successfully created'})

@app.route('/meals', methods=['POST'])
@login_required
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

@app.route('/meals/<int:id>', methods=['DELETE'])
def delete_meal(id):
  found_meal = Meal.query.get(id)

  if not found_meal:
    return jsonify({'message': 'Meal not found'})
  
  meal_does_not_belong_to_user = found_meal.user_id != current_user.id

  if meal_does_not_belong_to_user:
    return jsonify({'message': 'You are not allowed to delete other people`s meals'})
  
  db.session.delete(found_meal)
  db.session.commit()

  return jsonify({'message': 'Meal successfully deleted'})

@app.route('/meals/<int:id>', methods=['PUT'])
@login_required
def update_meal(id):
  data = request.get_json()

  found_meal = Meal.query.get(id)

  if not found_meal:
    return jsonify({'message': 'Meal not found'})
  
  if current_user.id != found_meal.user_id:
    return jsonify({'message': 'You can not update other people`s meals'})

  new_name = data.get('name')
  new_description = data.get('description')
  new_eaten_at = data.get('eaten_at') or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  new_is_in_diet = data.get('is_in_diet')

  found_meal.name = new_name or found_meal.name
  found_meal.description = new_description or found_meal.description
  found_meal.eaten_at = new_eaten_at or found_meal.eaten_at
  found_meal.is_in_diet = new_is_in_diet or found_meal.is_in_diet

  db.session.commit()

  return jsonify({'message': 'Meal successfully updated'})

@app.route('/meals', methods=['GET'])
@login_required
def list_meals():
  
  user_meals: list[Meal] = Meal.query.filter_by(user_id=current_user.id)

  dict_meals_list = [meal.to_dict() for meal in user_meals]

  return jsonify({'meals': dict_meals_list})

@app.route('/meals/<int:id>', methods=['GET'])
@login_required
def list_meal_by_id(id):
  found_meal: Meal | None = Meal.query.get(id)

  if not found_meal:
    return jsonify({'message': 'Meal not found'}), 404
  
  meal_does_not_belong_to_user = found_meal.user_id != current_user.id

  if meal_does_not_belong_to_user:
    return jsonify({'message': 'You are not allowed to view other people`s meals'})
  
  return jsonify({'meal': found_meal.to_dict()})

if __name__=='__main__':
  app.run(debug=True)