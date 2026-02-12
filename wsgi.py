"""
WSGI entry point for Vercel deployment
"""
from app import create_app, socketio

app = create_app()

# For Vercel, we need to expose the app object
# SocketIO will be handled differently in production
if __name__ == "__main__":
    socketio.run(app)
