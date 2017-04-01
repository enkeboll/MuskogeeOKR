import os

from app import make_application

PORT = os.getenv('PORT', 5000)
application = make_application()

if __name__ == '__main__':
    application.run(port=PORT, debug=True)
