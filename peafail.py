# Siin on meie peamine fail
# Siin on kirjeldus
# Siin on autorid
# vms siin olema peab

# Prisma robots.txt lubab kõike kraapida
# Mitme URL-i requestimine korras
# Ühe URL-i requestimine võtab veits kaua aega, wait 10 s soovitas Gemini


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
    hinnaSõnastik = {nimi:float(hind) for nimi,hind in (rida.strip().split(';') for rida in hinnaFail)}
    hinnaFail.close()

alkoSõnastik = {nimi:hind for nimi, hind in hinnaSõnastik.items() if nimi in alkoNimed}
pealekaSõnastik = {nimi:hind for nimi,hind in hinnaSõnastik.items() if nimi in pealekaNimed}

sobivused = {
# Viinad ja pealekas
"Laua Viin":  ["jõhvikamahl", "apelsinimahl", "multimahl"],
"Absolut": ["jõhvikamahl", "apelsinimahl", "multimahl"],
"Viru Valge":  ["jõhvikamahl", "apelsinimahl", "multimahl"],

#Rumm ja pealekas
"Bacardi": ["Coca-Cola", "apelsinimahl","Limpa"],
"Captain Morgan": ["Coca-Cola","apelsinimahl","Limpa"],

#Džinn ja pealekas
"Beefeater": ["toonik","apelsinimahl","Limpa"],
"Saaremaa rabarber": ["toonik","apelsinimahl","Limpa"],

#Jääger ja coca
"Jägermeister": ["Coca-Cola"]
}

#Tsükkel väljastab kõik joogid, mis sobivad eelarvesse
while True:
    try:
        eelarve = float(input('Mis on Sinu eelarve (€):'))
        break
    except ValueError:
        print('Sisesta palun arvuline väärtus')

print(f'\nJoogid, mis sobituvad {eelarve} € sisse:\n')

sobiv_jook = False

for nimi, hind in hinnaSõnastik.items():
    if hind <= eelarve:
        print(f'{nimi} - {hind:.2f} €')
        sobiv_jook = True

if not sobiv_jook:
    print('Sellise hinnaga jooke ei leitud :(')

#Tsükkel, mis väljastab jookide kombinatsioonid, mis sobivad eelarvesse
print(f'\nSobivad joogikombinatsioonid, mis mahuvad {eelarve:.2f} € sisse:\n')

sobiv_kombo = False

for alko_nimi, sobivad_pealekad in sobivused.items():
   if alko_nimi in alkoSõnastik:
            alko_hind = alkoSõnastik[alko_nimi]
            
            for pealeka_nimi in sobivad_pealekad:
                if pealeka_nimi in pealekaSõnastik:
                    pealeka_hind = pealekaSõnastik[pealeka_nimi]
                    kogu_hind = alko_hind + pealeka_hind

            if kogu_hind <= eelarve:
                print(f'{alko_nimi} + {pealeka_nimi} = {kogu_hind:.2f}€')
                sobiv_kombo = True

if not sobiv_kombo:
    print(f'Ühtegi sobivat jookide kombinatsiooni selle eelarvega ei leitud:(')
