from flask import Flask, request, jsonify
from db import db_ops  # Import your db_ops class from db.py

app = Flask(__name__)

# Initialize a global db_ops object so it can be reused in all routes
db = db_ops()

@app.route('/')
def home():
    return "Welcome to the Flask App!"


@app.route('/create_user', methods=['POST'])
def create_user():
    # Get JSON data from the incoming request
    data = request.get_json()
    
    # Extract user data from the request body
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    profile = data.get('profile')

    # Call the create_user_account method from db_ops
    user_id = db.create_user_account(username, password, name, profile)

    # Return a JSON response with user_id
    return jsonify({'status': 'success', 'user_id': user_id})

@app.route('/login', methods=['POST'])
def login_user():
    # Get JSON data from the incoming request
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the user credentials are correct using the db_ops method
    if db.check_user_account(username, password):
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure', 'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
