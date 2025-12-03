# ---Projekti pealkiri: kokteiliraamat??????????????
# ---Teema: kasutaja sisestab sobiva summa ning saab reaalajas Prisma hinnainfo kokteilide või shottide kohta,
# mida saab selle raha eest teha
# ---Autorid: Greteliis Kokk, Sandra Karo
# ---Eeskujuna kasutatud allikad: idee inspiratsiooniks eelmiste aastate energiajookide ja piima hindade projekt
# ---Muu oluline info: programmi kasutamiseks tuleb installida teegid bs4, selenium (pip3 install teeginimi)

# Prisma robots.txt lubab kõike kraapida
# Ühe URL-i requestimine võtab veits kaua aega, wait 10 s soovitas Gemini


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from tkinter import *

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
else:
    print('Sisestasid ebasobiva väärtuse, programm lõpetab töö.')
    exit()

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

#Tsükkel väljastab kõik shottideks sobivad joogid, mis mahuvad eelarvesse
while True:
    try:
        eelarve = float(input('Mis on Sinu eelarve (€)? '))
        break
    except ValueError:
        print('Sisesta palun arvuline väärtus.')

print(f'\nShotid, mis sobituvad {eelarve} € sisse:\n')



def leia_sobivad_shotid(eelarve):
    sobiv_jook = False
    global sobivad_shotid
    sobivad_shotid = dict()
    for nimi, hind in alkoSõnastik.items():
        if hind <= eelarve:
            print(f'{nimi} - {hind} €') #!!!!!
            sobivad_shotid[nimi] = hind
            sobiv_jook = True
    if not sobiv_jook:
        print('Sellise hinnaga shotte ei leitud :(')
    return sobivad_shotid

#Tsükkel, mis väljastab jookide kombinatsioonid, mis sobivad eelarvesse
print(f'\nSobivad joogikombinatsioonid, mis sobituvad {eelarve} € sisse:\n')

sobiv_kombo = False

# -------- !!!!!!!!!!!! siin (tglt varem) alustada kasutaja
# kokteilidest/shottidest järjendi vms andmehulga loomist !!!!!!!!!!!! -------
# ilmselt tasuks pigem funtksiooniks ka teha

for alko_nimi, sobivad_pealekad in sobivused.items():
    alko_hind = alkoSõnastik[alko_nimi]   
    for pealeka_nimi in sobivad_pealekad:
            pealeka_hind = pealekaSõnastik[pealeka_nimi]
            kogu_hind = alko_hind + pealeka_hind
    if kogu_hind <= eelarve:
        print(f'{alko_nimi} + {pealeka_nimi} = {kogu_hind}€')
        sobiv_kombo = True

if not sobiv_kombo:
    print(f'Ühtegi sobivat jookide kombinatsiooni selle eelarvega ei leitud :(')

#----------graafiline liides-------------
# see peaks olema main funktsioon ilmselt


# Me ei tea, mis summa kasutaja sisestab, seega elementide
# arv lehel peab olema dünaamiline, selleks funktsioon


root = Tk()
root.title('Kokteiliraamat')
root.geometry('400x300')
label = Label(root, text='Sisesta oma eelarve (€):')
label.pack(pady=10)
kasutaja_eelarve = Entry(root)
kasutaja_eelarve.pack(pady=5)

button = Button(root, text='Teen kokteile', command=näita_kokteile)
button.pack(pady=5)
button2 = Button(root, text='Teen shotte', command=näita_shotte)
button2.pack(pady=5)
button3 = Button(root, text='Teen mõlemat', command=näita_kõiki_jooke)
button3.pack(pady=5)

def näita_kokteile():
    eelarve = kasutaja_eelarve.get()
    # Siin peaks olema kood, mis leiab joogid ja kuvab tulemused
    result_label.config(text=f'Sobivad joodid summas {eelarve} €')

def näita_shotte():
    pass
def näita_kõiki_jooke():
    pass

root.mainloop()


# def jookide_paigutus(SIIA_MEIE_ANDMEHULK):
#     read = []
#     for kokteil in SIIA_MEIE_ANDMEHULK: #!!!!!!!!!!!!!!!
#         pass


# peaakna_paigutus = [
#     [sg.Text('Sisesta oma eelarve (€):')],
#     [sg.InputText(key='-EELARVE-')],
#     [sg.Button('Teen kokteili'), sg.Button('Teen shotte'), sg.Button('Teen mõlemat'), sg.Button('Sule programm')],
#     [sg.Text('Kas võtta hinnaandmed veebist või failist?')],
#     [sg.Combo(['Kraabi hinnaandmed veebist','Loe hinnaandmed failist'],default_value='Loe hinnaandmed failist',readonly=True)], # kasutaja ei saa ise valikukasti kirjutada
#     [sg.Output(size=(60, 20))]
# ]

# peaaken = sg.Window('Kokteiliraamat', peaakna_paigutus)

# kokteiliakna_paigutus = [
#     [sg.Text(f'Kokteilid {peaakna_paigutus["-EELARVE-"]} piires:')],
#     [sg.Output(size=(60, 20))], # väljundkasti suurus
#     [sg.Button('Tagasi pealehele')]
# ]

# kokteiliaken = sg.Window('Kokteilide valik', kokteiliakna_paigutus)

# while True:
#     sündmus, väärtused = peaaken.read()
#     if sündmus == sg.WINDOW_CLOSED or sündmus == 'Sule programm':
#         break

#     elif sündmus == 'Teen kokteili':
#         pass