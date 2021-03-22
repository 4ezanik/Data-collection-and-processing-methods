# 1. Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# 2. Сложить собранные данные в БД

import requests
from lxml import html
import re
import datetime
from pymongo import MongoClient
import pymongo.errors


def _scrap_lenta():

# Сбор с lenta.ru
    main_link = 'https://lenta.ru'
    header = {
        'User-Agent': 'MMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415'}
    response = requests.get(main_link, headers=header)
    if response.ok:
        item = html.fromstring(response.text)
        news = item.xpath('.//div[@class="first-item" or @class="item"]')
        lenta_news = []
        for n in news:
            news_data = {}
            news_data['title'] = n.xpath("./descendant::a/text()")[0].replace(
                u'\xa0', ' ')
            link_text = n.xpath("./a/@href")[0]
            if 'https' not in link_text:
                news_data['source'] = 'Lenta.ru'
                news_data['link'] = main_link + link_text
                date_list = link_text.strip('/').split('/')[1:4]
                news_data['date'] = '-'.join(date_list[i] for i in range(3))
            else:
                news_data['source'] = link_text.split('/')[2]
                date_list = re.findall(r'\d{2}-\d{2}-\d{4}', link_text)[
                    0].split('-')
                news_data['link'] = link_text
                news_data['date'] = '-'.join(
                    date_list[::-1][i] for i in range(3))
            lenta_news.append(news_data)
        return lenta_news


def _scrap_yanews():

# Сбор с yandex-новости
    main_link = 'https://yandex.ru/news'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415'}
    response = requests.get(main_link, headers=header)
    if response.ok:
        item = html.fromstring(response.text)
        news = item.xpath(
            '//div[contains(@class, "news-top-flexible-stories" )]/div')
        yandex_news = []
        for n in news:
            news_data = {}
            news_data['title'] = n.xpath(".//h2/text()")[0].replace(u'\xa0',
                                                                    ' ')
            news_data['link'] = \
                n.xpath('.//*[contains(@class, "mg-card__")]/a/@href')[0]
            source_time = n.xpath(
                './/div[@class="mg-card-footer__left"]//text()')
            news_data['source'] = source_time[0]
            today = datetime.date.today()
            news_data['date'] = today.strftime('%Y-%m-%d') if \
                'Вчера' not in source_time[1] else today.replace(
                day=today.day - 1).strftime('%Y-%m-%d')
            yandex_news.append(news_data)
        return yandex_news


def _scrap_mail():

# Сбор с news.mail.ru
    main_link = 'https://news.mail.ru/'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415'}
    response = requests.get(main_link, headers=header)
    if response.ok:
        item = html.fromstring(response.text)
        news_links = set(item.xpath(
            '//div[@class="js-module" and @data-module="TrackBlocks"]//a/@href'))
        mail_news = []
        for link in news_links:
            inner_response = requests.get(link, headers=header)
            if inner_response.ok:
                new_item = html.fromstring(inner_response.text)
                news = new_item.xpath(
                    '//div[contains(@class, "js-article")]')
                for n in news:
                    news_data = {}
                    news_data['link'] = link
                    news_data['title'] = n.xpath('.//h1/text()')[0].replace(
                        u'\xa0', ' ')
                    news_data['source'] = n.xpath('.//a//text()')[0]
                    news_data['date'] = \
                        n.xpath('.//*/@datetime')[0].split('T')[0]
                    mail_news.append(news_data)
        return mail_news


def news_scrap(lenta=True, yandex=True, mail=True):

    all_news = []
    if lenta:
        all_news.extend(_scrap_lenta())
    if yandex:
        all_news.extend(_scrap_yanews())
    if mail:
        all_news.extend(_scrap_mail())
    return all_news


def add_news(lenta=True, yandex=True, mail=True, base_name=None):

    client = MongoClient('localhost', 27017)
    if not base_name:
        base_name = 'top_news'
    if base_name not in client.list_database_names():
        print(f'Создана база {base_name}!')
    db = client[base_name]
    news = db.news
    news.create_index('title', unique=True)
    print(f'База {base_name} обновлена!')
    count = 0
    total_count = 0
    for _ in news_scrap(lenta=lenta, yandex=yandex, mail=mail):
        try:
            news.insert_one(_)
            count += 1
            total_count += 1
        except pymongo.errors.DuplicateKeyError:
            total_count += 1
            continue
    print(f'Новостей найдено: {total_count}, новостей добавлено: {count}.')


add_news()