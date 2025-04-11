"""The Basic Application of our project."""
from app import create_app, socketio

app = create_app()
"""CORS已经在init.py中配置过，如果还是不行尝试手动加response headers"""

if __name__ == '__main__':
    socketio.run(app, debug=True)

