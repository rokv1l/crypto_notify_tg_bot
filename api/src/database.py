from pymongo import MongoClient

import config


class Tasks:
    """Структура БД
    _id является id чата в телеграмме
    names является списком криптовалют
    times является словалём для расчёта времени
    static_time это константа времени для уведомлений текущего юзера в часах
    time это колличество времени до следующего уведомления
    P.s. технически time равен не часу, а абстрактному представлению единицы времени
    которое равняется одному запросу к api, с каждым запросом time будет уменьшаться на единицу"""

    def __init__(self):
        client = MongoClient(config.MONGO_IP, config.MONGO_PORT)
        self._database = client.users_notifier_list.test

    def clear(self):
        for i in self._database.find():
            self._database.delete_one(i)

    def show(self):
        for i in self._database.find():
            print(i)

    def get_tasks(self):
        """notify_list
        tasks:
            _id: индентификатор чата
            names: имена криптовалют для уведомления"""
        notify_list = {'tasks': list()}
        for task in self._database.find():
            time = int(task.get('times').get('time')) - 1
            if time:
                self._database.update_one({'_id': task.get('_id')},
                                          {'$set': {
                                              'times': {
                                                  'static_time': task.get('times').get('static_time'),
                                                  'time': time}}})
            else:
                notify_list['tasks'].append({'_id': task.get('_id'),
                                             'names': task.get('names')})
                self._database.update_one({'_id': task.get('_id')},
                                          {'$set': {
                                              'times': {
                                                  'static_time': task.get('times').get('static_time'),
                                                  'time': task.get('times').get('static_time')}}})
        return notify_list

    def set_task(self, chat_id, name, time):
        task = self._database.find_one({'_id': chat_id})
        name = name.title()
        if task:
            names = task.get('names')
            if name not in names and name is not None:
                names.append(name)
                self._database.update_one({'_id': chat_id}, {'$set': {'names': names}})
            if time != task.get('times').get('time') and time is not None:
                self._database.update_one({'_id': chat_id},
                                          {'$set': {
                                              'times': {
                                                  'static_time': time,
                                                  'time': time}
                                          }})
        else:
            self._database.insert_one({
                '_id': chat_id,
                'names': [name, ],
                'times': {'static_time': 1,
                          'time': 1}
            })
