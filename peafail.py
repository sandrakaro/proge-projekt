# Siin on meie peamine fail
# Siin on kirjeldus
# Siin on autorid
# vms siin olema peab

# Praegu on programm selline, et kasutaja sisestab joogi nime ja saab ainult selle joogi hinna
# Kui requestida kõiki URL-e korraga, siis Selver ei lasnud päringuid läbi
# Ja nende selver.ee/robots.txt ütles disallow price=
# Seega panin kõik lingid Prisma omadeks rn
# Prisma robots.txt lubab kõike kraapida
# Aga kõikide linkide korraga requestimist ikka ei luba
# Also see ühe URL-i requestimine võtab veits kaua aega, wait 10 s soovitas Gemini
# seega ma ei tea kas asi töötab, kui seda lühemaks panna
# Peaks välja mõtlema, mis see lõpplahendus olla võiks


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

joogiFail = open('jookide-lingid.txt',encoding='utf-8')
joogiJärjend = [el.strip().split(';') for el in joogiFail.readlines()]
joogiFail.close()
joogiSõnastik = {el[0]: el[1] for el in joogiJärjend if '---' not in el[0]} # loome sõnastiku, kust saab otsida jookide linke joogi nime järgi; ei arvesta kolme sidekriipsuga tootekategooriaid

options = webdriver.ChromeOptions()
options.add_argument('--headless') # ei ava reaalset brauseri akent
driver = webdriver.Chrome(options=options) # kasutab brauserina Google Chrome'i
### hinnad = set()

joogiSoov = input('Sisesta joogi nimi: ')
joogiSooviLink = joogiSõnastik[joogiSoov]

try:
    driver.get(joogiSooviLink) # avab soovitud joogi lingi
    wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-test-id='display-price']"))) # ootab kuni JavaScripti hind on lehel laetud
    päringuSisu = driver.page_source
    soup = BeautifulSoup(päringuSisu, 'html.parser')
    hinnaElement = soup.find('span', attrs={'data-test-id': 'display-price'})
    if hinnaElement:
        hind = hinnaElement.text.strip().split('€')[0] # ei anna liitrihinda ega euromärki
        hind = float(hind.replace(',','.')) # teeme komaga hinna ujukomaarvuks
        print(f'Selle joogi praegune hind on {hind} €')
    else:
        print('Hinda ei leitud, kontrolli klassi nime')
except Exception as viga:
    print(f'Päringu viga {viga}')
finally:
    driver.quit()
