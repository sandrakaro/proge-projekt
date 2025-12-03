# ---Projekti pealkiri: kokteiliraamat??????????????
# ---Teema: kasutaja sisestab sobiva summa ning saab reaalajas Prisma hinnainfo kokteilide või shottide kohta,
# mida saab selle raha eest teha
# ---Autorid: Greteliis Kokk, Sandra Karo
# ---Eeskujuna kasutatud allikad: idee inspiratsiooniks eelmiste aastate energiajookide ja piima hindade projekt, tkinteri loomiseks TheCodex videod Youtube'is
# ---Muu oluline info: programmi kasutamiseks tuleb installida teegid bs4, selenium (pip3 install teeginimi või pip install teeginimi)

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

def kas_hinnad_veebist(kasKontroll):
    hinnaSõnastik = dict()
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
                else:
                    print('Hinda ei leitud, kontrolli otsingu parameetreid')
                    break
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
    # see error handling peaks guisse tulema:
    # else:
    #     print('Sisestasid ebasobiva väärtuse, programm lõpetab töö.')
    #     exit()
    global alkoSõnastik, pealekaSõnastik
    alkoSõnastik = {nimi:hind for nimi, hind in hinnaSõnastik.items() if nimi in alkoNimed}
    pealekaSõnastik = {nimi:hind for nimi,hind in hinnaSõnastik.items() if nimi in pealekaNimed}
    #return (alkoSõnastik, pealekaSõnastik)
    # ei tea kas seda returni vaja

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
# while True:
#     try:
#         eelarve = float(input('Mis on Sinu eelarve (€)? '))
#         break
#     except ValueError:
#         print('Sisesta palun arvuline väärtus.')

# print(f'\nShotid, mis sobituvad {eelarve} € sisse:\n')



# def leia_sobivad_shotid(eelarve):
#     sobiv_jook = False
#     global sobivad_shotid
#     sobivad_shotid = dict()
#     for nimi, hind in alkoSõnastik.items():
#         if hind <= eelarve:
#             print(f'{nimi} - {hind} €') #!!!!!
#             sobivad_shotid[nimi] = hind
#             sobiv_jook = True
#     if not sobiv_jook:
#         print('Sellise hinnaga shotte ei leitud :(')
#     return sobivad_shotid

# #Tsükkel, mis väljastab jookide kombinatsioonid, mis sobivad eelarvesse
# print(f'\nSobivad joogikombinatsioonid, mis sobituvad {eelarve} € sisse:\n')

# sobiv_kombo = False

# -------- !!!!!!!!!!!! siin (tglt varem) alustada kasutaja
# kokteilidest/shottidest järjendi vms andmehulga loomist !!!!!!!!!!!! -------
# ilmselt tasuks pigem funtksiooniks ka teha

# for alko_nimi, sobivad_pealekad in sobivused.items():
#     alko_hind = alkoSõnastik[alko_nimi]   
#     for pealeka_nimi in sobivad_pealekad:
#             pealeka_hind = pealekaSõnastik[pealeka_nimi]
#             kogu_hind = alko_hind + pealeka_hind
#     if kogu_hind <= eelarve:
#         print(f'{alko_nimi} + {pealeka_nimi} = {kogu_hind}€')
#         sobiv_kombo = True

# if not sobiv_kombo:
#     print(f'Ühtegi sobivat jookide kombinatsiooni selle eelarvega ei leitud :(')





def leia_sobivad_shotid(eelarve):
    shotid_eelarves = dict()
    for nimi, hind in alkoSõnastik.items():
        if hind <= eelarve:
            shotid_eelarves[nimi] = hind
    return shotid_eelarves


def leia_sobivad_kokteilid(eelarve):
    kokteilid_eelarves = {}
    for alko_nimi, sobivad_pealekad in sobivused.items():
        alko_hind = alkoSõnastik[alko_nimi]

        for pealeka_nimi in sobivad_pealekad:
            pealeka_hind = pealekaSõnastik[pealeka_nimi]
            kogu_hind = alko_hind + pealeka_hind

            if kogu_hind <= eelarve:
                kokteilid_eelarves[(alko_nimi, pealeka_nimi)] = kogu_hind
    return kokteilid_eelarves



#----------graafiline liides-------------
# see peaks olema main funktsioon ilmselt


# Me ei tea, mis summa kasutaja sisestab, seega elementide
# arv lehel peab olema dünaamiline


def näita_kõiki_jooke():
    try:
        eelarve = float(kasutaja_eelarve.get())
    except ValueError:
        show_message('Palun sisesta arvuline väärtus.')
        return
    try:
        sobivad_kokteilid = leia_sobivad_kokteilid(eelarve)
    except NameError:
        show_message('Viga: hinnad ei ole saadaval. Programm sulgub.')
        exit()

    read = []
    for (alko_nimi, pealeka_nimi), koguhind in sobivad_kokteilid.items():
        read.append(f'{alko_nimi} + {pealeka_nimi} = {koguhind} €')

    show_results_window(f'Sobivad kokteilid eelarvega {eelarve} €', read)

def näita_shotte():
    try:
        eelarve = float(kasutaja_eelarve.get())
    except ValueError:
        show_message('Palun sisesta arvuline väärtus.')
        return
    try:
        sobivad_shotid = leia_sobivad_shotid(eelarve)
    except NameError:
        show_message('Viga: hinnad ei ole saadaval. Programm sulgub.')
        exit()

    read = [f'{alko_nimi} — {hind} €' for alko_nimi, hind in sobivad_shotid.items()]
    show_results_window(f'Sobivad shotid eelarvega {eelarve} €', read)

#------siin AI kood veel kontrollimata
def näita_kõiki_jooke():
    try:
        eelarve = float(kasutaja_eelarve.get())
    except ValueError:
        show_message('Viga', 'Sisesta kehtiv arv eelarve jaoks.')
        return

    try:
        shotid = leia_sobivad_shotid(eelarve)
        kokteilid = leia_sobivad_kokteilid(eelarve)
    except NameError:
        show_message('Viga', 'Hinnad ei ole saadaval. Käivita hindade laadimine.')
        return

    lines = []
    lines.append('--- Shotid ---')
    lines += [f'{nimi} — {hind:.2f} €' for nimi, hind in sorted(shotid.items(), key=lambda x: x[1])]
    lines.append('')
    lines.append('--- Kokteilid ---')
    lines += [f'{alko} + {pealekas} = {hind:.2f} €' for (alko, pealekas), hind in sorted(kokteilid.items(), key=lambda x: x[1])]

    show_results_window(f'Kõik sobivad joogid — {eelarve:.2f} €', lines)


def show_results_window(title, lines):
    win = Toplevel(root)
    win.title(title)
    win.geometry('450x350')

    header = Label(win, text=title, font=('Arial', 12, 'bold'))
    header.pack(pady=8)

    text = Text(win, wrap='word', height=15, width=60)
    text.pack(padx=10, pady=5, expand=True, fill='both')

    if lines:
        for line in lines:
            text.insert(END, line + '\n')
    else:
        text.insert(END, 'Ühtegi tulemust ei leitud.')

    close = Button(win, text='Sulge', command=win.destroy)
    close.pack(pady=6)


def show_message(title, message):
    win = Toplevel(root)
    win.title(title)
    win.geometry('300x120')
    Label(win, text=message, wraplength=280).pack(padx=10, pady=10)
    Button(win, text='OK', command=win.destroy).pack(pady=6)

#---------- siin AI kood veel kontrollimata

root = Tk()
root.title('Kokteiliraamat')
root.geometry('400x300')
label = Label(root, text='Sisesta oma eelarve (€):')
label.pack(pady=10)
kasutaja_eelarve = Entry(root)
kasutaja_eelarve.pack(pady=5)

pealeht = Frame(root)
pealeht.pack(pady=10)

hinnavalikud = {'Kraabi hinnad veebist' : 'y', 'Võta hinnad failist' : 'n'}
vali_kust_hinnad = StringVar(value='n')
for nupu_tekst, väärtus in hinnavalikud.items():
    Radiobutton(pealeht, text=nupu_tekst, variable=vali_kust_hinnad, value=väärtus).grid(sticky='w')

kokteili_nupp = Button(pealeht, text='Teen kokteile', command=näita_kokteile).grid(row=0, column=0, padx=5, pady=5)
shoti_nupp = Button(pealeht, text='Teen shotte', command=näita_shotte).grid(row=0, column=1, padx=5, pady=5)
mõlema_valiku_nupp = Button(pealeht, text='Teen mõlemat', command=näita_kõiki_jooke).grid(row=0, column=2, padx=5 pady=5)

root.mainloop()