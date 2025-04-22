from flask import session, request, jsonify
from functools import wraps

# Dummy in-memory user store
users = {'admin': 'password'}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


def login_handler():
    data = request.get_json() or {}
    uname = data.get('username')
    pwd = data.get('password')
    if users.get(uname) == pwd:
        session['username'] = uname
        return jsonify({'message': 'Logged in'})
    return jsonify({'error': 'Invalid credentials'}), 401


def logout_handler():
    session.pop('username', None)
    return jsonify({'message': 'Logged out'})