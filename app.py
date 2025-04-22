from flask import Flask, request, jsonify, session
from auth import login_required, login_handler, logout_handler
from query_processor import QueryProcessor

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Enable in production

processor = QueryProcessor()

# Auth endpoints
app.add_url_rule('/login', 'login', login_handler, methods=['POST'])
app.add_url_rule('/logout', 'logout', logout_handler, methods=['POST'])

@app.route('/query', methods=['POST'])
@login_required
def handle_query():
    data = request.get_json() or {}
    query = data.get('query', '')
    try:
        result = processor.process(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tables', methods=['GET'])
@login_required
def list_tables():
    return jsonify({'tables': list(processor.store.tables.keys())})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)