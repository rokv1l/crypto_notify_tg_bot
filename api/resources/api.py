from flask_restful import reqparse
from flask_restful import Resource

from src.database import Tasks
from resources.parser import Parser


class RequestsHandler(Resource):
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('chat_id')
        parser.add_argument('name')
        parser.add_argument('time')
        data = parser.parse_args()
        Tasks().set_task(**data)

    @staticmethod
    def get():
        tasks = Tasks().get_tasks()
        data = Parser().get_data(tasks)
        response = {}
        for task in tasks.get('tasks'):
            _id = task.get('_id')
            response[_id] = {}
            for name in task.get('names'):
                if data.get(name) is not None:
                    response[_id][name] = data.get(name)
        return response
