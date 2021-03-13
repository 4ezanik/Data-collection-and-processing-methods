# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
# с сайтов Superjob и HH. Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
# * Наименование вакансии.
# * Предлагаемую зарплату (отдельно минимальную, максимальную и валюту).
# * Ссылку на саму вакансию.
# * Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести
# с помощью dataFrame через pandas.

import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd

def _scrap_hh(vacancy):
    offers = []
    main_link = 'https://hh.ru'
    params = {'L_is_autosearch': 'false',
              'clusters': 'true',
              'enable_snippets': 'true',
              'text': vacancy}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415'}
    check = True
    vacancy_list = []
    page = 0
    while check:
        params['page'] = str(page)
        response = requests.get(main_link + '/search/vacancy', params=params,
                                headers=headers)
        if response.ok:
            soup = bs(response.text, 'html.parser')
            vacancy_list += soup.findAll('div', {
                'class': 'vacancy-serp-item'})
            if not soup.findAll('a', {
                'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'}):
                check = False
        page += 1
    for items in vacancy_list:
        offers.append(_scrap_hh_res(items))
    return offers

def _scrap_hh_res(vacancy):
    vacancy_data = {}
    vacansy_source = 'HH.RU'
    vacancy_name = vacancy.find('span', {
        'class': 'g-user-content'}).findChild()
    vacancy_link = vacancy_name['href']
    vacancy_name = vacancy_name.getText()
    vacancy_city = vacancy.find('span', {
        'data-qa': 'vacancy-serp__vacancy-address'}).contents[0].strip(
        ', ')
    salary = vacancy.find('span', {
        'data-qa': 'vacancy-serp__vacancy-compensation'})
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary = salary.text.replace(u'\xa0', u'').replace('-',
                                                           ' ').split()
        if salary[0] == 'от':
            salary.remove('от')
            salary_min = float(salary.pop(0))
            salary_max = None
        elif salary[0] == 'до':
            salary.remove('до')
            salary_min = None
            salary_max = float(salary.pop(0))
        else:
            salary_min = float(salary.pop(0))
            salary_max = float(salary.pop(0))
        salary_currency = ' '.join(
            salary[i] for i in range(len(salary)))
    vacancy_data['name'] = vacancy_name
    vacancy_data['city'] = vacancy_city
    vacancy_data['source'] = vacansy_source
    vacancy_data['link'] = vacancy_link
    vacancy_data['min_salary'] = salary_min
    vacancy_data['max_salary'] = salary_max
    vacancy_data['currency'] = salary_currency
    return vacancy_data

def _scrap_sj(vacancy):
    offers = []
    main_link1 = 'https://www.superjob.ru'
    params = {'keywords': vacancy,
              'noGeo': '1'
              }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
    check = True
    vacancy_list = []
    page = 1
    while check:
        params['page'] = str(page)
        response = requests.get(main_link1 + '/vacancy/search/', params=params,
                                headers=headers)
        if response.ok:
            soup = bs(response.text, 'html.parser')
            vacancy_list += soup.findAll('div', {
                'class': 'Fo44F QiY08 LvoDO'})
            if not soup.findAll('a', {
                'rel': 'next'}):
                check = False
        page += 1
    for items in vacancy_list:
        offers.append(_scrap_sj_res(items))
    return offers

def _scrap_sj_res(vacancy):
    main_link1 = 'https://www.superjob.ru'
    vacancy_data = {}
    vacansy_source = 'SUPERJOB.RU'
    vacancy_name = vacancy.find('a')
    vacancy_link = main_link1 + vacancy_name['href']
    vacancy_name = vacancy_name.getText()
    vacancy_city = vacancy.find('span', {
        'class': 'f-test-text-company-item-location'}).findChildren()[2].text
    vacancy_city = vacancy_city.split(', ')[0]
    salary = vacancy.find('span', {
        'class': 'f-test-text-company-item-salary'}).findChild().text
    if salary == 'По договорённости':
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary = salary.replace(u'\xa0', ' ').split()
        salary_currency = salary.pop()
        if salary[0] == 'от':
            salary.remove('от')
            salary_min = float(''.join(salary[i] for i in range(len(salary))))
            salary_max = None
        elif salary[0] == 'до':
            salary.remove('до')
            salary_min = None
            salary_max = float(''.join(salary[i] for i in range(len(salary))))
        else:
            salary = ''.join(salary[i] for i in range(len(salary))).split('—')
            salary_min = float(salary[0])
            salary_max = float(salary[1]) if len(salary) > 1 else float(
                salary[0])
    vacancy_data['city'] = vacancy_city
    vacancy_data['name'] = vacancy_name
    vacancy_data['source'] = vacansy_source
    vacancy_data['link'] = vacancy_link
    vacancy_data['min_salary'] = salary_min
    vacancy_data['max_salary'] = salary_max
    vacancy_data['currency'] = salary_currency
    return vacancy_data

# объединяем результаты
def vacancy_finder(vacancy):
    result_list = []
    result_list.extend(_scrap_hh(vacancy))
    result_list.extend(_scrap_sj(vacancy))
    return result_list

offers = vacancy_finder('дворник')
with open('job_find_result.json', 'w') as outfile:
    json.dump(offers, outfile)
vacancyDf = pd.DataFrame(offers)
vacancyDf.to_csv('vacancy.csv', index=False, encoding='utf8')