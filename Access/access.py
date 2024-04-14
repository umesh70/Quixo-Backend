from flask import Flask, request, jsonify, session
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi'
app.config['REDIS_URL'] = 'redis://localhost:6379/0'
redis_client = FlaskRedis(app)

# signup 
@app.route('/signup',methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username and password:
         return jsonify({'error': 'Username and password required'}), 400

    if redis_client.exists(username):
        return jsonify({'error': 'User already exists'}), 400
    
    redis_client.set(username,password)
    return jsonify({'success': 'User signed up successfully'}), 201


if __name__ == '__main__':
    app.run(debug=True)