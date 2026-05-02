import functools

from flask import (
    Blueprint, request, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_jwt_extended import create_access_token

from task_manager.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')



@bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    db = get_db()
    error = None
    status_code = 201

    if not username:
        error = 'Username is required.'
        status_code = 400
    elif not password:
        error = 'Password is required.'
        status_code = 400

    if error is None:
        try:
            new_user_cursor = db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError:
            error = f"User {username} is already registered."
            status_code = 409
        else:
            result = {"message" : "user registered successfully",
                      "username" : username,
                      "user_id": new_user_cursor.lastrowid
                     }
            return (jsonify(result), status_code)

    return (jsonify({"error": error}), status_code)



@bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    db = get_db()

    error = None
    status_code = 200

    if not username or not password:
        error = 'Both username and password are not provided.'
        status_code = 400

    else:
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
            status_code = 401
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
            status_code = 401

        if error is None:
            access_token = create_access_token(identity=user["username"])
            result = {
                      "message": "login success",
                      "access_token": access_token,
                      "username": username
                     }
            return (jsonify(result), status_code)

    return ({"error": error}, status_code)
