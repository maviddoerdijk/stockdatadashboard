import streamlit as st
import os
from streamlit_extras.stylable_container import stylable_container


# Set the title of the page
st.title("Veelgestelde Vragen (FAQ)")

def a1():
    st.markdown("## Importeer je eigen DEGIRO data")
    st.markdown("*Via degiro kun je jouw volledige transactiegeschiedenis en -data uploaden naar dit dashboard.*")
    show_phone = st.toggle("Laat instructies zien voor laptop of telefoon", help="Kies of je de instructies voor laptop of telefoon wilt zien.")
    currently_selected_str = "telefoon" if show_phone else "laptop"
    st.info(f"Instructies worden laten zien voor op uw {currently_selected_str}.")
    st.markdown("**Stap 1:** Ga naar de [DEGIRO website](https://trader.degiro.nl/login) en log in.")
    st.markdown("**Stap 2:** Ga naar **'Inbox'** en klik op **'Rekeningoverzicht'**.")
    if show_phone:
        st.image(os.path.join('resources', 'images', 'FAQ', 'img1_rekeningoverzicht_telefoon.png'), use_column_width=True)
    else:
        st.image(os.path.join('resources', 'images', 'FAQ', 'img1_rekeningoverzicht_laptop.png'), use_column_width=True)
    st.markdown("**Stap 3:** Selecteer de begindatum dusdanig dat al je data en transacties worden meegenomen.")
    st.markdown("**Stap 4:** Klik op **'Exporteren'** en selecteer **'CSV'**.")
    if show_phone:
        st.image(os.path.join('resources', 'images', 'FAQ', 'img2_exporteren_telefoon.png'), use_column_width=True)
    else:
        st.image(os.path.join('resources', 'images', 'FAQ', 'img2_exporteren_laptop.png'), use_column_width=True)
    st.markdown(f"**Stap 5:** Upload het bestand naar [dit dashboard](/Degiro_Portfolio_Tracker) .")
    # link to 

def a2():
    st.markdown(" # Veiligheid van jouw data")
    st.markdown("*Alle data die je uploadt naar dit dashboard wordt lokaal opgeslagen en niet gedeeld met anderen.*")
    url = "https://www.degiro.nl/helpdesk/belasting/welke-rapportagemogelijkheden-zijn-er-en-waar-kan-ik-de-rapportages-vinden"
    st.markdown(f"Lees op de DEGIRO website voor meer informatie over het exporteren van jouw 'Portefeuille Overzicht': [DEGIRO Exporteren]({url})")


# List of FAQs
faqs = [
    {"question": "Hoe voeg ik mijn eigen DEGIRO data toe aan het dashboard?", "answer": a1},
    {"question": "Hoe weet ik dat mijn data veilig is?", "answer":a2}
]

# Display each FAQ using an expander
for faq in faqs:
    with st.expander(faq["question"]):
        faq["answer"]()

