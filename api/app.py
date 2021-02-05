from flask import Flask
from flask_restful import Api

from resources.api import RequestsHandler


app = Flask(__name__)
api = Api(app)

api.add_resource(RequestsHandler, '/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
