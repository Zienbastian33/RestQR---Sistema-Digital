import sys
import traceback

try:
    from app import create_app, db, socketio

    app = create_app()

    if __name__ == '__main__':
        with app.app_context():
            db.create_all()
        socketio.run(app, debug=True)
except Exception:
    with open('startup_error.log', 'w') as f:
        traceback.print_exc(file=f)
    print("Startup failed. Check startup_error.log")
    sys.exit(1)
