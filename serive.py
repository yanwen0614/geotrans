from os import environ
from views import app
from os import sep
from sys import path
import sys
# path.append(sep.join(__file__.split("\\")[:-1]))
if __name__ == '__main__':

    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT,threaded=True)