# Siin on meie peamine fail
# Siin on kirjeldus
# Siin on autorid
# vms siin olema peab

# Prisma robots.txt lubab kõike kraapida
# Also see ühe URL-i requestimine võtab veits kaua aega, wait 10 s soovitas Gemini


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

joogiFail = open('jookide-lingid.txt',encoding='utf-8')
joogiJärjend = [el.strip().split(';') for el in joogiFail.readlines()]
joogiFail.close()
joogiSõnastik = {el[0]: el[1] for el in joogiJärjend if '---' not in el[0]} # loome sõnastiku, kust saab otsida jookide linke joogi nime järgi; ei arvesta kolme sidekriipsuga tootekategooriaid

alkoNimed = []
pealekaNimed = []
lipp = 0
for osa in joogiJärjend:
    tekst = osa[0]
    if tekst != '---pealekas' and not lipp:
        if '---' not in tekst:
            alkoNimed.append(tekst)
    else:
        lipp = 1
        if '---' not in tekst:
            pealekaNimed.append(tekst)


hinnaSõnastik = dict()
kasKontroll = input('Kas kraabin hinnad veebist (y/n)? ') # Valik, kas leida hinnad reaalajas (aeglane) või failist (kiire, aga info võib olla aegunud)

if kasKontroll == 'y':
    hinnaFail = open('jookide-hinnad-veebist.txt','w',encoding='utf-8')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # ei ava reaalset brauseri akent
    driver = webdriver.Chrome(options=options) # kasutab brauserina Google Chrome'i
    for nimi,link in joogiSõnastik.items():
        try:
            driver.get(link) # avab soovitud joogi lingi
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-test-id='display-price']"))) # ootab kuni JavaScripti hind on lehel laetud
            päringuSisu = driver.page_source
            soup = BeautifulSoup(päringuSisu, 'html.parser')
            hinnaElement = soup.find('span', attrs={'data-test-id': 'display-price'})
            if hinnaElement:
                hind = hinnaElement.text.strip().split('€')[0] # ei anna liitrihinda ega euromärki
                hind = float(hind.replace(',','.')) # teeme komaga hinna ujukomaarvuks
                hinnaSõnastik[nimi] = hind
                hinnaFail.write(f'{nimi};{hind}' + '\n')
                print('Päring õnnestus, hind lisatud faili ja sõnastikku')
            else:
                print('Hinda ei leitud, kontrolli otsingu parameetreid')
        except Exception as viga:
            print(f'Päringu viga {viga}')
            break
        sleep(2) # ootame 2 s enne järgmist päringut, et päringuid ei lükataks tagasi
    driver.quit()
    hinnaFail.close()
elif kasKontroll == 'n': # Kasutame seda koodi testimisel, et mitte serverist bänni saada
    print('Selge! Võtan hinnad olemasolevast failist.\n')
    hinnaFail = open('jookide-hinnad-veebist.txt','r',encoding='utf-8')
    hinnaSõnastik = {nimi:hind for nimi,hind in (rida.strip().split(';') for rida in hinnaFail)}
    hinnaFail.close()

alkoSõnastik = {nimi:hind for nimi, hind in hinnaSõnastik.items() if nimi in alkoNimed}
pealekaSõnastik = {nimi:hind for nimi,hind in hinnaSõnastik.items() if nimi in pealekaNimed}