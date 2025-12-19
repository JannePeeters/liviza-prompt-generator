import streamlit as st
import urllib.parse

st.set_page_config(page_title="Liviza Prompt Generator", layout="wide")

st.title("Liviza Prompt Generator (keukens)")

st.sidebar.header("Stappenplan")
st.sidebar.markdown(
    """
    1. Vul de gegevens per onderdeel in 
    2. Voeg overige opmerkingen toe indien nodig
    3. Vink aan welke bestanden je (in ChatGPT) wilt toevoegen en vul gegevens in
    5. Klik op 'Genereer prompt'
    6. Klik op 'Open in ChatGPT', hier wordt je visualisatie gemaakt!
    
    **BELANGRIJK:** Vergeet niet om je bestanden (plattegronden, tekeningen, afbeeldingen) in ChatGPT nog handmatig toe te voegen
        
    **WAARSCHUWING:** De gegenereerde afbeeldingen zijn vaak niet in één keer correct. Controleer kritisch voordat je ze toont aan klanten
    """
)

st.header('Checklist invullen')

LEVERANCIERS = [
    "",
    "Baars & Bloemhoff",
    "Kaindl",
    "Overige"
]

def onderdeel_blok(onderdeel):
    st.subheader(onderdeel)

    leverancier = st.selectbox(
        f"Leverancier",
        LEVERANCIERS,
        key = f"leverancier_{onderdeel}",
        format_func=lambda x: "Selecteer leverancier..." if x == "" else x
    )

    materiaal = st.text_input(
        f"Materiaal / productnaam",
        key = f"materiaal_{onderdeel}",
        placeholder = "Typ hier het materiaal of de productnaam..."
    )

    kleur = st.text_input(
        f"Kleur",
        key = f"kleur_{onderdeel}",
        placeholder = "Typ hier de gewenste kleur..."
    )

    if leverancier == "Baars & Bloemhoff":
        link = "https://www.baars-bloemhoff.nl/assortiment/"
    elif leverancier == "Kaindl":
        link = "https://www.kaindl.com/en/"
    else:
        link = None

    return {
        "leverancier": leverancier,
        "materiaal": materiaal,
        "kleur": kleur,
        "link": link
    }

style = st.selectbox('Stijl', ['','modern','klassiek','industrieel','landelijk','scandinavisch','minimalistisch'], format_func=lambda x: "Selecteer stijl..." if x == "" else x)
layout = st.selectbox('Indeling', ['','eilandkeuken', 'rechte keuken', 'L-vormige keuken', 'U-vormige keuken', 'parallel keuken'], format_func=lambda x: "Selecteer indeling..." if x == "" else x)
fronten = onderdeel_blok("Fronten")
corpus = onderdeel_blok("Corpus")
werkblad = onderdeel_blok("Werkblad")
handgrepen = onderdeel_blok("Handgrepen")

st.subheader("Overig")
extra_notes = st.text_area('Opmerkingen', placeholder="Typ hier overige opmerkingen...")

st.header('Welke bestanden wil je uploaden?')
input_types = {'Plattegrond': '', 'Tekening': '', 'Afbeelding': '', 'Transcript gesprek': ''}

for key in input_types.keys():
    checked = st.checkbox(f'{key}')
    if checked:
        if key == 'Transcript gesprek':
            input_types[key] = st.text_area(f'Plak {key.lower()} hier', height=150, placeholder='Met Leexi kun je het gesprek met de klant opnemen en laten transcriberen en samenvatten...')
        else:
            files = []
            n_files = st.number_input(f'Aantal {key.lower()} bestanden', min_value=1, max_value=10, step=1)
            for i in range(n_files):
                filename = st.text_input('Naam van het bestand', key=f'naam_{key.lower()}_{i}', placeholder='Typ hier de naam van je bestand...')
                context = st.text_area(f'Context (optioneel)', key=f'context_{key.lower()}_{i}', placeholder='Typ hier wat er in je bestand te zien is...')
                files.append({'filename': filename, 'context': context})
            input_types[key] = files

run_button = st.button('Genereer prompt')

if run_button:
    st.header('Gegenereerde prompt:')
    lines = [
        'Je bent een expert in 3D interieur rendering voor Liviza (https://liviza.nl/).',
        'Genereer één fotorealistische 3D render op basis van onderstaande specificaties.',
        'Voeg geen objecten toe die niet aanwezig zijn.\n'
    ]

    if style: lines.append(f'Stijl: {style}')
    if layout: lines.append(f'Indeling: {layout} \n')

    def add_information(label, data):
        lines.append(f'***{label}***')
        if data['leverancier']: lines.append(f'Leverancier: {data['leverancier']}')
        if data['materiaal']: lines.append(f'Materiaal: {data['materiaal']}')
        if data['kleur']: lines.append(f'Kleur: {data["kleur"]}')
        if data['link']: lines.append(f'Link: {data["link"]}')
        lines.append('\n')

    if fronten: add_information("Fronten", fronten)
    if corpus: add_information("Corpus (binnenkant kasten)", corpus)
    if werkblad: add_information("Werkblad", werkblad)
    if handgrepen: add_information("Handgrepen", handgrepen)

    if extra_notes:
        lines.append('\n Overige opmerkingen:')
        lines.append(extra_notes)
        lines.append('\n')

    for key, val in input_types.items():
        if val:
            if key == 'Transcript gesprek':
                if val.strip():
                    lines.append(f'{key}: {val} \n')
            else:
                lines.append(f'{key} bestanden:')
                for f in val:
                    context_str = f['context'] if f['context'] else 'Geen context opgegeven'
                    lines.append(f"- {f['filename']}: {context_str}")

    # Rendering instructies
    lines.append('\n Rendering vereisten: fotorealistisch, nauwkeurige kleuren en plaatsing van handgrepen, kranen en apparatuur, geen extra objecten toevoegen.')

    prompt_text = '\n'.join(lines)

    prompt_for_url = urllib.parse.quote(prompt_text)
    chatgpt_url = f"https://chat.openai.com/?prompt={prompt_for_url}"
    st.markdown(f"[Open in ChatGPT]({chatgpt_url})", unsafe_allow_html=True)

    st.code(prompt_text)
    st.download_button('Download prompt (.txt)', data=prompt_text, file_name='liviza_prompt.txt')

