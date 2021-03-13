# Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests
from pathlib import Path
import json

class ScrapGroupsVk:
    params = {
        'user_id': 23344143,
        'extended': 1,
        'v': 5.52,
        'access_token': 'a7afb6a51a4e119a43d92f759b81c487a4ee16fc4b248583bce33f912a81b401ea9953e519f6133bf0c27',
    }

    def __init__(self, start_url, headers, s_path):
        self.start_url = start_url
        self.headers = headers
        self.s_path = s_path

    def _get_response(self):
        response = requests.get(self.start_url, headers=self.headers, params=self.params)
        return response

    def _parse(self):
        data = self._get_response().json()
        print(data['response']['count'])
        groups = data['response']['items']
        return groups

    def go(self):
        for group in self._parse():
            try:
                group_path = self.s_path.joinpath(f'{group["screen_name"]}.json')
                self._save(group_path, group)
            except UnicodeEncodeError as err:
                print(err)
                pass

    def _save(self, file_path:Path, data:dict):
        file_path.write_text(json.dumps(data, ensure_ascii=False))

if __name__ == '__main__':

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.408'}
    url = 'https://api.vk.com/method/groups.get'
    p = Path('vk_user_groups')
    p.mkdir()

    groups_saver = ScrapGroupsVk(url, headers, p)
    groups_saver.go()