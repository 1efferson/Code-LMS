
# app.py


# from lms import create_app

# app = create_app()

# if __name__ == "__main__":
#     app.run(debug=False)


# app.py

from lms import create_app

app = create_app()

if __name__ == "__main__":
    import os
    # Read debug mode from environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)