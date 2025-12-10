# Siin Claude'i kirjutatud kood piltide kuvamiseks,
# 2 pilti kõrvuti rea kohal ning shottide puhul 1
# kui pilti pole, kast [PILT]
# vajab kohandamist, timmimist, integreerimist
# lihtsalt baas peafailis realiseerimise põhjaks
# scrollimise jms lisas ka, need pigem Youtube'i onult võtta

from tkinter import *
from PIL import ImageTk, Image

def näita_tulemuste_akent_piltidega(pealkiri, tulemused):
    """
    tulemused: list tuplite või sõnastike kujul
    Näide: [
        {'tekst': 'Absolut + jõhvikamahl = 5.50 €', 'pilt1': 'absolut.jpg', 'pilt2': 'johvikas.jpg'},
        {'tekst': 'Bacardi + Coca-Cola = 6.20 €', 'pilt1': 'bacardi.jpg', 'pilt2': 'cola.jpg'}
    ]
    """
    tulemuste_aken = Toplevel()
    tulemuste_aken.title(pealkiri)
    tulemuste_aken.geometry('650x500')

    pealdis = Label(tulemuste_aken, text=pealkiri, font=('Arial', 12, 'bold'))
    pealdis.pack(pady=8)

    # Keritav raam tulemustele
    canvas = Canvas(tulemuste_aken)
    scrollbar = Scrollbar(tulemuste_aken, orient="vertical", command=canvas.yview)
    keritav_raam = Frame(canvas)

    keritav_raam.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=keritav_raam, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
    scrollbar.pack(side="right", fill="y")

    # Lisa tulemused piltidega
    if tulemused:
        for i, tulemus in enumerate(tulemused):
            rida_raam = Frame(keritav_raam, relief=RIDGE, borderwidth=1)
            rida_raam.pack(fill='x', padx=5, pady=5)

            # Vasak pilt
            if 'pilt1' in tulemus and tulemus['pilt1']:
                lisa_pilt(rida_raam, tulemus['pilt1'], side='left')

            # Tekst keskel
            tekst_label = Label(rida_raam, text=tulemus['tekst'], 
                               font=('Arial', 10), wraplength=250)
            tekst_label.pack(side='left', padx=10, expand=True)

            # Parem pilt
            if 'pilt2' in tulemus and tulemus['pilt2']:
                lisa_pilt(rida_raam, tulemus['pilt2'], side='left')
    else:
        Label(keritav_raam, text='Ühtegi tulemust selle eelarvega ei leitud.').pack(pady=20)


def lisa_pilt(parent, pildi_tee, size=(80, 80), side='left'):
    """Abifunktsioon pildi lisamiseks"""
    try:
        pilt = Image.open(pildi_tee)
        pilt = pilt.resize(size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(pilt)
        
        label = Label(parent, image=photo)
        label.image = photo  # Salvesta viide!
        label.pack(side=side, padx=5, pady=5)
    except Exception as e:
        # Kui pilti ei leita, näita platsholder
        label = Label(parent, text='[PILT]', width=10, height=4, 
                     relief=SUNKEN, bg='lightgray')
        label.pack(side=side, padx=5, pady=5)


# Näide kasutamisest sinu koodis:
def näita_kokteile_piltidega():
    # Sinu olemasolev loogika
    leia_hinnad(vali_kust_hinnad.get())
    try:
        eelarve = float(kasutaja_eelarve.get())
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.')
        return
    
    sobivad_kokteilid = leia_sobivad_kokteilid(eelarve)
    
    # Loo piltidega tulemuste list
    tulemused = []
    for (alko_nimi, pealeka_nimi), koguhind in sobivad_kokteilid.items():
        tulemused.append({
            'tekst': f'{alko_nimi} + {pealeka_nimi} = {koguhind} €',
            'pilt1': f'pildid/{alko_nimi.lower().replace(" ", "_")}.jpg',
            'pilt2': f'pildid/{pealeka_nimi.lower().replace(" ", "_")}.jpg'
        })
    
    näita_tulemuste_akent_piltidega(f'Sobivad kokteilid eelarvega {eelarve} €', tulemused)


# Sama loogika shottidele (1 pilt):
def näita_shotte_piltidega():
    leia_hinnad(vali_kust_hinnad.get())
    try:
        eelarve = float(kasutaja_eelarve.get())
    except ValueError:
        kuva_sõnum('Palun sisesta arvuline väärtus.')
        return
    
    sobivad_shotid = leia_sobivad_shotid(eelarve)
    
    tulemused = []
    for alko_nimi, hind in sobivad_shotid.items():
        tulemused.append({
            'tekst': f'{alko_nimi} — {hind} €',
            'pilt1': f'pildid/{alko_nimi.lower().replace(" ", "_")}.jpg',
            'pilt2': None  # Shotil ainult 1 pilt
        })
    
    näita_tulemuste_akent_piltidega(f'Sobivad shotid eelarvega {eelarve} €', tulemused)