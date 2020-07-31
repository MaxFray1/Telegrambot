import requests
from bs4 import BeautifulSoup as bs


def checkIndex(soup):
    root = soup.findAll('meta')
    print(root[1])
    if(str(root[1]) == '<meta content="noindex" name="robots"/>'):
        return True
    return False


def getInfo(soup):
    info = []
    info.append(soup.find('title').text)
    info.append(soup.find(class_='article-stat__date').text)
    info.append(soup.find(class_='publisher-controls__subscribers').text)
    return info


def checkAll():
    text = []
    listArticles = ["https://zen.yandex.ru/media/id/5eeb593ff673b7793c0c7a6e/3-produkta-kotorye-zabivaiut-sosudy-i-vyzyvaiut-infarkt-5ef306ff6e647a0ec6b6d692", "https://zen.yandex.ru/media/id/5af45c6bdd248465f4efec36/podruga-agronom-iz-golandii-podelilas-hitrostiu-kak-navsegda-izbavitsia-ot-opasnyh-muravev-bez-himii-za-odin-den-5f186825995e2b7d97b28f08"]
    for i in listArticles:
        r = requests.get(i)
        soup = bs(r.text, 'html.parser')
        check = checkIndex(soup)
        info = getInfo(soup)
        text.append("test"  + "\n" + info[0] + "\n" + info[1] + "\n" + info[2] + "\n" + i)
    return text

def check(url):
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    return checkIndex(soup)