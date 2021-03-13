# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json
from pprint import pprint

username = "4ezanik"
response = requests.get('http://api.github.com/users/'+username+'/repos')

for i in response.json():
    pprint(i['name'])

with open('repo_list.json', 'w') as f:
    json.dump(response.json(), f)