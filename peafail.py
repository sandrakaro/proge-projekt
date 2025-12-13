# ---Projekti pealkiri: kokteiliraamat??????????????
# ---Teema: kasutaja sisestab sobiva summa ning saab reaalajas Prisma hinnainfo kokteilide
# või shottide kohta, mida saab selle raha eest teha
# ---Autorid: Greteliis Kokk, Sandra Karo
# ---Eeskujuna kasutatud allikad: idee inspiratsiooniks eelmiste aastate energiajookide ja piima hindade
# projekt, Tkinteri GUI loomiseks TheCodex videod Youtube'is
# ---Muu oluline info: programmi kasutamiseks tuleb installida teegid bs4, selenium, pillow
# (pip3 install teeginimi või pip install teeginimi), lisaks on vajalik Chrome brauser, kuid
# soovi korral võib ka koodis asendada leia_hinnad f-ni koodi oma brauserile mõelduga

# Prisma robots.txt lubab kõike kraapida
# Ühe URL-i requestimine võtab veits kaua aega, wait 10 s soovitas Gemini


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import *
from PIL import ImageTk, Image
from time import sleep
from math import floor

joogifail = open('jookide-lingid.txt',encoding='utf-8')
joogijärjend = [el.strip().split(';') for el in joogifail.readlines()]
joogifail.close()
joogisõnastik = {el[0]: el[1] for el in joogijärjend if '---' not in el[0]} # loome sõnastiku, kust saab otsida jookide linke joogi nime järgi; ei arvesta kolme sidekriipsuga tootekategooriaid

alko_nimed = []
pealeka_nimed = []
lipp = 0
for osa in joogijärjend:
    tekst = osa[0]
    if tekst != '---pealekas' and not lipp:
        if '---' not in tekst:
            alko_nimed.append(tekst)
    else:
        lipp = 1
        if '---' not in tekst:
            pealeka_nimed.append(tekst)

def leia_hinnad(kas_kontroll_veebist):
    hinnasõnastik = dict()
    if kas_kontroll_veebist == 'y':
        laadimisaken = kuva_sõnum('Kraabin hindu veebist, palun oota.') ####!!!!! Kuulub GUI koodi hulka !!!!!!
        hinnafail = open('jookide-hinnad-veebist.txt','w',encoding='utf-8')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # ei ava reaalset brauseri akent
        driver = webdriver.Chrome(options=options) # kasutab brauserina Google Chrome'i
        for nimi,link in joogisõnastik.items():
            try:
                driver.get(link) # avab soovitud joogi lingi
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-test-id='display-price']"))) # ootab kuni JavaScripti hind on lehel laetud
                päringu_sisu = driver.page_source
                supp = BeautifulSoup(päringu_sisu, 'html.parser')
                hinna_element = supp.find('span', attrs={'data-test-id': 'display-price'})
                if hinna_element:
                    hind = hinna_element.text.strip().split('€')[0] # ei anna liitrihinda ega euromärki
                    hind = float(hind.replace(',','.')) # teeme komaga hinna ujukomaarvuks
                    hinnasõnastik[nimi] = hind
                    hinnafail.write(f'{nimi};{hind}' + '\n')
                else:
                    print('Hinda ei leitud, kontrolli otsingu parameetreid')
                    break
            except Exception as viga:
                print(f'Päringu viga {viga}')
                break
            sleep(2) # ootame 2 s enne järgmist päringut, et päringuid ei lükataks tagasi
        driver.quit()
        hinnafail.close()
        if laadimisaken is not None:
            laadimisaken.destroy() ####!!!!! Kuulub GUI koodi hulka !!!!!!
    elif kas_kontroll_veebist == 'n': # Kasutame seda koodi testimisel, et mitte serverist bänni saada
        print('Selge! Võtan hinnad olemasolevast failist.\n')
        hinnafail = open('jookide-hinnad-veebist.txt','r',encoding='utf-8')
        hinnasõnastik = {nimi:float(hind) for nimi,hind in (rida.strip().split(';') for rida in hinnafail)}
        hinnafail.close()
    global alko_sõnastik, pealeka_sõnastik
    alko_sõnastik = {nimi:hind for nimi, hind in hinnasõnastik.items() if nimi in alko_nimed}
    pealeka_sõnastik = {nimi:hind for nimi,hind in hinnasõnastik.items() if nimi in pealeka_nimed}

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


def leia_sobivad_shotid(eelarve):
    shotid_eelarves = dict()
    for nimi, hind in alko_sõnastik.items():
        if hind <= eelarve:
            shotid_eelarves[nimi] = hind
    return shotid_eelarves


def leia_sobivad_kokteilid(eelarve):
    kokteilid_eelarves = {}
    for alko_nimi, sobivad_pealekad in sobivused.items():
        alko_hind = alko_sõnastik[alko_nimi]

        for pealeka_nimi in sobivad_pealekad:
            pealeka_hind = pealeka_sõnastik[pealeka_nimi]
            kogu_hind = alko_hind + pealeka_hind

            if kogu_hind <= eelarve:
                kokteilid_eelarves[(alko_nimi, pealeka_nimi)] = kogu_hind
    return kokteilid_eelarves



#----------graafilise liidese funktsioonid-------------

def näita_tulemuste_akent(pealkiri, read):
    tulemuste_aken = Toplevel(root)
    tulemuste_aken.title(pealkiri)
    tulemuste_aken.geometry('450x350')

    pealdis = Label(tulemuste_aken, text=pealkiri, font=('Arial', 12, 'bold'))
    pealdis.pack(pady=8)

    raam = Frame(tulemuste_aken)
    raam.pack(padx=10, pady=10, expand=True, fill='both')

    kerimisriba = Scrollbar(raam)
    kerimisriba.pack(side=RIGHT, fill=Y)

    sisutekst = Text(raam, wrap='word', height=15, width=60, yscrollcommand = kerimisriba.set)
    sisutekst.pack(padx=10, pady=5, expand=True, fill='both')

    kerimisriba.config(command=sisutekst.yview)

    sisutekst.config(state=NORMAL)
    if read:
        for rida in read:
            sisutekst.insert(END, rida + '\n')
    else:
        sisutekst.insert(END, 'Ühtegi tulemust selle eelarvega ei leitud.')
    
    sisutekst.config(state=DISABLED) # Kasutaja ei saa teksti muuta

def kuva_sõnum(sõnum):
    pealkiri = 'Teade'
    aken = Toplevel(root)
    aken.title(pealkiri)
    aken.geometry('300x120')
    Label(aken, text=sõnum, wraplength=280).pack(padx=10, pady=10)
    Button(aken, text='OK', command=aken.destroy).pack(pady=6)
    aken.update()
    return aken # nii on võimalik akent hiljem sulgeda

def näita_kokteile():
    leia_hinnad(vali_kust_hinnad.get())
    try:
        eelarve = float(kasutaja_eelarve.get())
        if floor(eelarve) == eelarve:
            vormistatud_eelarve = str(int(eelarve))
        else:
            vormistatud_eelarve = f'{eelarve:.2f}'
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.')
        return
    try:
        sobivad_kokteilid = leia_sobivad_kokteilid(eelarve)
    except NameError:
        kuva_sõnum('Viga: hinnad ei ole saadaval. Programm sulgub.')
        exit()

    read = []
    for (alko_nimi, pealeka_nimi), koguhind in sobivad_kokteilid.items():
        read.append(f'{alko_nimi} + {pealeka_nimi} = {round(koguhind,2)} €')

    näita_tulemuste_akent(f'Sobivad kokteilid eelarvega {vormistatud_eelarve} €', read)

def näita_shotte():
    leia_hinnad(vali_kust_hinnad.get())
    try:
        eelarve = float(kasutaja_eelarve.get())
        if floor(eelarve) == eelarve:
            vormistatud_eelarve = str(int(eelarve))
        else:
            vormistatud_eelarve = f'{eelarve:.2f}'
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.')
        return
    try:
        sobivad_shotid = leia_sobivad_shotid(eelarve)
    except NameError:
        kuva_sõnum('Viga: hinnad ei ole saadaval. Programm sulgub.')
        exit()

    read = [f'{alko_nimi} — {round(hind,2)} €' for alko_nimi, hind in sobivad_shotid.items()]
    näita_tulemuste_akent(f'Sobivad shotid eelarvega {vormistatud_eelarve} €', read)

def näita_kõiki_jooke():
    leia_hinnad(vali_kust_hinnad.get())
    try:
        eelarve = float(kasutaja_eelarve.get())
        if floor(eelarve) == eelarve:
            vormistatud_eelarve = str(int(eelarve))
        else:
            vormistatud_eelarve = f'{eelarve:.2f}'
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.')
        return

    try:
        shotid = leia_sobivad_shotid(eelarve)
        kokteilid = leia_sobivad_kokteilid(eelarve)
    except NameError:
        kuva_sõnum('Viga: hinnad ei ole saadaval. Programm sulgub.')
        exit()

    lines = []
    lines.append(f'--- Shotid eelarvega {vormistatud_eelarve} € ---')
    lines += [f'{nimi} — {round(hind,2)} €' for nimi, hind in shotid.items()]
    lines.append('')
    lines.append(f'--- Kokteilid eelarvega {vormistatud_eelarve} € ---')
    lines += [f'{alko_nimi} + {pealeka_nimi} = {round(hind,2)} €' for (alko_nimi, pealeka_nimi), hind in kokteilid.items()]

    näita_tulemuste_akent(f'Kõik sobivad joogid eelarvega {vormistatud_eelarve} €', lines)

#----------graafilise liidese kood-------------
# see peaks olema main funktsioon ilmselt??

root = Tk()
root.title('Kokteiliraamat')
root.geometry('600x300')
label = Label(root, text='Sisesta oma eelarve (€):')
label.pack(pady=10)
kasutaja_eelarve = Entry(root)
kasutaja_eelarve.pack(pady=5)

pealeht = Frame(root)
pealeht.pack(pady=10)

hinnavalikud = {'Kraabi hinnad veebist' : 'y', 'Võta hinnad failist' : 'n'}
vali_kust_hinnad = StringVar(value='n')
i = 0
for nupu_tekst, väärtus in hinnavalikud.items():
    Radiobutton(pealeht, text=nupu_tekst, variable=vali_kust_hinnad, value=väärtus).grid(sticky='w', row = i, column = 1, padx=5, pady=5)
    i+=1

kokteili_nupp = Button(pealeht, text='Teen kokteile', command=näita_kokteile).grid(row=2, column=0, padx=5, pady=5)
shoti_nupp = Button(pealeht, text='Teen shotte', command=näita_shotte).grid(row=2, column=1, padx=5, pady=5)
mõlema_valiku_nupp = Button(pealeht, text='Teen mõlemat', command=näita_kõiki_jooke).grid(row=2, column=2, padx=5, pady=5)

root.mainloop()