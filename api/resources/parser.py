import re
from requests import get
from bs4 import BeautifulSoup


class Parser:
    def __init__(self):
        self._headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/'
                                   'webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                         'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                                       '(KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

    def get_html(self):
        return get('https://bitinfocharts.com/ru/markets/all.html', headers=self._headers).content

    def get_data(self, tasks):
        """coins_info
            now: цена сейчас
            12_hours: изменение цены за 12ч
            7_days: изменение цены за 7д"""
        html = BeautifulSoup(self.get_html(), 'lxml')
        table = html.body.table.find_all('tr')
        names_set = set()
        for task in tasks.get('tasks'):
            for name in task.get('names'):
                names_set.add(name)
        coins_info = {}
        for name in names_set:
            coins_info[name] = {}
            for tr in table:
                pattern = re.compile(f'^{name}\\s\\s')
                data = tr.find('a', attrs={'title': pattern})
                if data:
                    coins_info[name]['now'] = data.text
                    data = data.parent
                    data = data.find_all('span')
                    coins_info[name]['12_hours'] = data[0].text
                    coins_info[name]['7_days'] = data[1].text
            if not coins_info.get(name):
                del coins_info[name]
        return coins_info
