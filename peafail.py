# ---Projekti pealkiri: kokteiliraamat??????????????
# ---Teema: kasutaja sisestab sobiva summa ning saab reaalajas Prisma hinnainfo kokteilide
# või shottide kohta, mida saab selle raha eest teha
# ---Autorid: Greteliis Kokk, Sandra Karo
# ---Eeskujuna kasutatud allikad: idee inspiratsiooniks eelmiste aastate energiajookide ja piima hindade
# projekt, Tkinteri GUI loomiseks TheCodex ning Codemy.com videod Youtube'is
# ---Muu oluline info: programmi kasutamiseks tuleb installida teegid bs4, selenium, pillow
# (pip3 install teeginimi või pip install teeginimi), lisaks on vajalik Chrome brauser, kuid
# soovi korral võib ka koodis asendada leia_hinnad f-ni koodi oma brauserile mõelduga


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import *
from PIL import ImageTk, Image
from time import sleep
from math import floor


#----------peaprogrammi funtksioonid-------------

def leia_hinnad(kas_kontroll_veebist, joogisõnastik, alko_nimed, pealeka_nimed, juuraken):
    hinnasõnastik = dict()
    if kas_kontroll_veebist == 'y':
        laadimisaken = kuva_sõnum('Kraabin hindu veebist, palun oota.', juuraken) ####!!!!! Kuulub GUI koodi hulka !!!!!!
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
        hinnafail = open('jookide-hinnad-veebist.txt','r',encoding='utf-8')
        hinnasõnastik = {nimi:float(hind) for nimi,hind in (rida.strip().split(';') for rida in hinnafail)}
        hinnafail.close()
    alko_sõnastik = {nimi:hind for nimi, hind in hinnasõnastik.items() if nimi in alko_nimed}
    pealeka_sõnastik = {nimi:hind for nimi,hind in hinnasõnastik.items() if nimi in pealeka_nimed}
    return alko_sõnastik, pealeka_sõnastik


def leia_sobivad_shotid(eelarve, alko_sõnastik):
    shotid_eelarves = dict()
    for nimi, hind in alko_sõnastik.items():
        if hind <= eelarve:
            shotid_eelarves[nimi] = hind
    return shotid_eelarves


def leia_sobivad_kokteilid(eelarve, alko_sõnastik, pealeka_sõnastik, sobivused):
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

def leia_pildi_tee(joogi_nimi):
    joogi_nimi = joogi_nimi.replace('ä', 'a').replace('ö', 'o').replace('ü', 'u').replace('õ', 'o')
    return 'pildid/' + joogi_nimi.lower().replace(' ', '-') + '.png'


def lisa_pilt(vanemraam, pildi_tee):
    try:
        pildifail = Image.open(pildi_tee)
        pildifail = pildifail.resize((80, 80), Image.LANCZOS)
        pilt = ImageTk.PhotoImage(pildifail)

        pealdis = Label(vanemraam, image=pilt)
        pealdis.image = pilt # viite salvestamine?
        pealdis.pack(side='left')
    except:
        pealdis = Label(vanemraam, text='[ Pilti ei leitud ]', width=10, height=4)
        pealdis.pack(side='left', padx=5, pady=5)


def näita_tulemuste_akent(pealkiri, read, sobivate_jookide_nimed, mida_näidata, juuraken):
    tulemuste_aken = Toplevel(juuraken)
    tulemuste_aken.title(pealkiri)
    tulemuste_aken.geometry('450x350')

    pealdis = Label(tulemuste_aken, text=pealkiri, font=('Arial', 12, 'bold'))
    pealdis.pack(pady=8)

    kanvas = Canvas(tulemuste_aken)

    kerimisriba = Scrollbar(tulemuste_aken)
    kerimisriba.config(command=kanvas.yview)
    kerimisriba_raam = Frame(kanvas)

    kerimisriba_raam.bind('<Configure>', lambda e: kanvas.configure(scrollregion=kanvas.bbox('all'))) # mis siin toimub

    kanvas.create_window((0,0), window=kerimisriba_raam, anchor=NW)
    kanvas.configure(yscrollcommand=kerimisriba.set)

    kanvas.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=5)
    kerimisriba.pack(side=RIGHT, fill=Y)

    if read:
        if mida_näidata == 'shotid':
            i=0
            for rida in read:
                rea_raam = Frame(kerimisriba_raam)
                rea_raam.pack(fill=X, padx=5, pady=5)
                lisa_pilt(rea_raam, leia_pildi_tee(sobivate_jookide_nimed[i]))

                teksti_väli = Label(rea_raam, text=rida, font=('Arial', 12))
                teksti_väli.pack(side=LEFT, padx=10, expand=True)
                i+=1

        elif mida_näidata == 'kokteilid':
            for i, rida in enumerate(read):
                rea_raam = Frame(kerimisriba_raam)
                rea_raam.pack(fill=X, padx=5, pady=5)
                lisa_pilt(rea_raam, leia_pildi_tee(sobivate_jookide_nimed[i][0]))
                lisa_pilt(rea_raam, leia_pildi_tee(sobivate_jookide_nimed[i][1]))
                teksti_väli = Label(rea_raam, text=rida, font=('Arial', 12))
                teksti_väli.pack(side=LEFT, padx=10, expand=True)

        elif mida_näidata == 'mõlemad':
            i=0
            shottide_arv = len(sobivate_jookide_nimed['shotid'])
            for rida in read[:shottide_arv+1]: # arvestab shotte
                rea_raam = Frame(kerimisriba_raam)
                rea_raam.pack(fill=X, padx=5, pady=5)
                if not '---' in rida and rida != '': # tähendab, et tegu on vahepealkirjaga / tühja reaga, kuhu pole pilti vaja
                    lisa_pilt(rea_raam, leia_pildi_tee(sobivate_jookide_nimed['shotid'][i]))
                    i+=1
                teksti_väli = Label(rea_raam, text=rida, font=('Arial', 12))
                teksti_väli.pack(side=LEFT, padx=10, expand=True)

            i=0
            for rida in read[shottide_arv+1:]: # arvestab kokteile
                rea_raam = Frame(kerimisriba_raam)
                rea_raam.pack(fill=X, padx=5, pady=5)
                if not '---' in rida and rida != '': # tähendab, et tegu on vahepealkirjaga / tühja reaga, kuhu pole pilti vaja
                    lisa_pilt(rea_raam, leia_pildi_tee(sobivate_jookide_nimed['kokteilid'][i][0]))
                    lisa_pilt(rea_raam, leia_pildi_tee(sobivate_jookide_nimed['kokteilid'][i][1]))
                    i+=1
                teksti_väli = Label(rea_raam, text=rida, font=('Arial', 12))
                teksti_väli.pack(side=LEFT, padx=10, expand=True)         
    else:
        Label(kerimisriba_raam, text='Ühtegi tulemust selle eelarvega ei leitud.')


def kuva_sõnum(sõnum, juuraken):
    aken = Toplevel(juuraken)
    aken.title('Teade')
    aken.geometry('300x120')
    Label(aken, text=sõnum, wraplength=280).pack(padx=10, pady=10)
    Button(aken, text='OK', command=aken.destroy).pack(pady=6)
    aken.update()
    return aken # nii on võimalik akent hiljem sulgeda, kontrollides, kas see on None või mitte


def näita_kokteile(kasutaja_eelarve, vali_kust_hinnad, joogisõnastik, alko_nimed, pealeka_nimed, sobivused, juuraken):
    alko_sõnastik, pealeka_sõnastik = leia_hinnad(vali_kust_hinnad.get(), joogisõnastik, alko_nimed, pealeka_nimed, juuraken)
    try:
        eelarve = float(kasutaja_eelarve.get())
        if floor(eelarve) == eelarve:
            vormistatud_eelarve = str(int(eelarve))
        else:
            vormistatud_eelarve = f'{eelarve:.2f}'
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.', juuraken)
        return
    
    sobivad_kokteilid = leia_sobivad_kokteilid(eelarve, alko_sõnastik, pealeka_sõnastik, sobivused)
    
    sobivate_kokteilide_nimed = []
    read = []
    for (alko_nimi, pealeka_nimi), koguhind in sobivad_kokteilid.items():
        read.append(f'{alko_nimi} + {pealeka_nimi} = {round(koguhind,2)} €')
        sobivate_kokteilide_nimed.append([alko_nimi, pealeka_nimi])
    
    näita_tulemuste_akent(f'Sobivad kokteilid eelarvega {vormistatud_eelarve} €', read, sobivate_kokteilide_nimed, 'kokteilid', juuraken)


def näita_shotte(kasutaja_eelarve, vali_kust_hinnad, joogisõnastik, alko_nimed, pealeka_nimed, juuraken):
    alko_sõnastik, pealeka_sõnastik = leia_hinnad(vali_kust_hinnad.get(), joogisõnastik, alko_nimed, pealeka_nimed, juuraken)
    try:
        eelarve = float(kasutaja_eelarve.get())
        if floor(eelarve) == eelarve:
            vormistatud_eelarve = str(int(eelarve))
        else:
            vormistatud_eelarve = f'{eelarve:.2f}'
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.', juuraken)
        return
    
    sobivad_shotid = leia_sobivad_shotid(eelarve, alko_sõnastik)
    sobivate_shottide_nimed = [alko_nimi for alko_nimi in sobivad_shotid]

    read = [f'{alko_nimi} — {round(hind,2)} €' for alko_nimi, hind in sobivad_shotid.items()]
    näita_tulemuste_akent(f'Sobivad shotid eelarvega {vormistatud_eelarve} €', read, sobivate_shottide_nimed, 'shotid', juuraken)


def näita_kõiki_jooke(kasutaja_eelarve, vali_kust_hinnad, joogisõnastik, alko_nimed, pealeka_nimed, sobivused, juuraken):
    alko_sõnastik, pealeka_sõnastik = leia_hinnad(vali_kust_hinnad.get(), joogisõnastik, alko_nimed, pealeka_nimed, juuraken)
    try:
        eelarve = float(kasutaja_eelarve.get())
        if floor(eelarve) == eelarve:
            vormistatud_eelarve = str(int(eelarve))
        else:
            vormistatud_eelarve = f'{eelarve:.2f}'
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.', juuraken)
        return

    shotid = leia_sobivad_shotid(eelarve, alko_sõnastik)
    kokteilid = leia_sobivad_kokteilid(eelarve, alko_sõnastik, pealeka_sõnastik, sobivused)

    sobivate_shottide_nimed = list(shotid.keys())
    sobivate_kokteilide_nimed = list(kokteilid.keys())

    read = []
    read.append(f'--- Shotid eelarvega {vormistatud_eelarve} € ---')
    read += [f'{nimi} — {round(hind,2)} €' for nimi, hind in shotid.items()]
    read.append('')
    read.append(f'--- Kokteilid eelarvega {vormistatud_eelarve} € ---')
    read += [f'{alko_nimi} + {pealeka_nimi} = {round(hind,2)} €' for (alko_nimi, pealeka_nimi), hind in kokteilid.items()]

    näita_tulemuste_akent(f'Kõik sobivad joogid eelarvega {vormistatud_eelarve} €', read, {'shotid': sobivate_shottide_nimed, 'kokteilid': sobivate_kokteilide_nimed}, 'mõlemad', juuraken)


#----------peamine programmikood-------------

def main():
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

    #----------graafilise liidese kood-------------

    juuraken = Tk()
    juuraken.title('Kokteiliraamat')
    juuraken.geometry('600x300')
    juurakna_pealdis = Label(juuraken, text='Sisesta oma eelarve (€):')
    juurakna_pealdis.pack(pady=10)
    kasutaja_eelarve = Entry(juuraken)
    kasutaja_eelarve.pack(pady=5)

    pealeht = Frame(juuraken)
    pealeht.pack(pady=10)

    hinnavalikud = {'Kraabi hinnad veebist' : 'y', 'Võta hinnad failist' : 'n'}
    vali_kust_hinnad = StringVar(value='n')
    i = 0
    for nupu_tekst, väärtus in hinnavalikud.items():
        Radiobutton(pealeht, text=nupu_tekst, variable=vali_kust_hinnad, value=väärtus).grid(sticky='w', row = i, column = 1, padx=5, pady=5)
        i+=1

    kokteili_nupp = Button(pealeht, text='Teen kokteile', command=lambda: näita_kokteile(kasutaja_eelarve, vali_kust_hinnad, joogisõnastik, alko_nimed, pealeka_nimed, sobivused, juuraken))
    kokteili_nupp.grid(row=2, column=0, padx=5, pady=5)
    
    shoti_nupp = Button(pealeht, text='Teen shotte', command=lambda: näita_shotte(kasutaja_eelarve, vali_kust_hinnad, joogisõnastik, alko_nimed, pealeka_nimed, juuraken))
    shoti_nupp.grid(row=2, column=1, padx=5, pady=5)
    
    mõlema_valiku_nupp = Button(pealeht, text='Teen mõlemat', command=lambda: näita_kõiki_jooke(kasutaja_eelarve, vali_kust_hinnad, joogisõnastik, alko_nimed, pealeka_nimed, sobivused, juuraken))
    mõlema_valiku_nupp.grid(row=2, column=2, padx=5, pady=5)

    juuraken.mainloop()


if __name__ == '__main__':
    main()