# coding=utf-8
import requests
from lxml import etree
from collections import OrderedDict
import json
import time
import pickle

site_link = 'http://pilot-auto.su'

xpath_car_links = '//div[@id="ekonom-class" or @id="standart-class" or @id="business-class" or @id="lux-class"]/descendant::a[img]'

xpath_car_name = "//h1"
xpath_features = "//*[@class='tab_wex']/descendant::li"
xpath_price_table_header = '(//*[@class="MsoNormalTable"])[1]//td[@class="priceTableHead"]//b'
xpath_price_table_price = '(//*[@class="MsoNormalTable"])[1]//td[@class="priceTablePrice"]//b'


def get_car_links():
    r = requests.get(site_link)
    document = etree.HTML(r.text)
    car_links_nodes = document.xpath(xpath_car_links)
    car_links = [x.get("href") for x in car_links_nodes]
    return car_links


def get_car_info(path, keywords=(u"коробка передач", u"цвет", u"двигатель")):
    r = requests.get(path)
    document = etree.HTML(r.text)
    car_name = "".join(filter(None, [x.text for x in document.xpath(xpath_car_name)])).strip()
    car_features = [x.text.strip() for x in document.xpath(xpath_features) if x.text]
    car_interesting_features = OrderedDict()
    for word in keywords:
        feature = filter(lambda x: word.lower() in x.lower(), car_features)
        car_interesting_features[word.lower()] = ", ".join(feature)
    car_prices = OrderedDict()
    for price_type, price in zip(document.xpath(xpath_price_table_header), document.xpath(xpath_price_table_price)):
        car_prices[price_type.text.strip()] = etree.tostring(price, encoding="unicode", method="text").strip()
    result = OrderedDict()
    result[u"Марка"] = car_name
    result[u"Ссылка"] = path
    result.update(car_interesting_features)
    result.update(car_prices)
    return result


def build_list():
    print "loading car list"
    links = get_car_links()
    print "loading done. total cars: " + str(len(links))
    cars = []
    for index, link in enumerate(links):
        print str(index) + ") loading car info: " + link
        cars.append(get_car_info(link))
    pickle.dump(cars, open("cars.bin", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    headers = cars[0].keys()
    items = [[car.get(header, "") for header in headers] for car in cars]
    return headers, items


def write_json(headers, items):
    result = json.dumps({"header": headers, "properties": items}, ensure_ascii=False)
    with open("{0}.json".format(int(time.time())), "w") as j:
        j.write(result.encode("utf8"))
    return result


def print_table(j):
    result = json.loads(j, encoding="utf8")
    print " | ".join(result["header"])
    for row in result["properties"]:
        print " | ".join(row)


if __name__ == '__main__':
    headers, items = build_list()
    j = write_json(headers, items)
    print j
    print_table(j)