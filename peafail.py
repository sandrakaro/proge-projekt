# Siin on meie peamine fail
# Siin on kirjeldus
# Siin on autorid
# vms siin olema peab

import requests
from bs4 import BeautifulSoup

lauaViinURL = 'https://www.selver.ee/laua-viin-liviko-50-cl'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
try:
    päring = requests.get(lauaViinURL, headers=HEADERS)
    if päring.status_code == 200:
        soup = BeautifulSoup(päring.content, 'html.parser')
        hind = soup.find('div',class_='ProductPrice#text')
        hind = soup.select_one('div.ProductPrice')
        if hind:
            hind = hind.text.strip()
            print(f'Praegune hind on {hind}')
        else:
            print('Hinda ei leitud, kontrolli klassi nime')
    else:
        print('Päring ebaõnnestus')
except requests.exceptions.RequestException as viga:
    print(f'Päringu viga {viga}')
