import streamlit as st
from src.apps.m01_maps_licences_france import maps_licences_france
from src.apps.m02_maps_equip_france import maps_equip_france
from src.apps.m03_maps_dep import maps_dep
from src.apps.m04_maps_commune import maps_commune
from src.apps.m05_stats_fed import barh_analysis
from src.apps.m06_comment_utiliser import comment_utiliser
from src.apps.m07_a_propos import a_propos

from streamlit_option_menu import option_menu

st.set_page_config(page_title="Sportoo - Sport Data Viz", page_icon=":checkered_flag:", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.logo("resources/logo_sportoo_2_300_100_transparent.png", link='https://sportoo.streamlit.app', icon_image=None)

# Adapte la taille du logo et les couleurs de la sidebar
st.html("""
    <style>
    [alt=Logo] {
        height: 80px;
    }
        
    .menu .nav-item .nav-link.active[data-v-5af006b8] {
        background-color: var(--primary-color);
    }
        
    iframe {
        width: 100%;
        max-width: 1000px;
        min-height: 800px;
        height: 100%;
    </style>
        """)

def main():

    data_freshness = 2021
    data_es_freshness = 2024

    with st.sidebar:
        selected = option_menu("", 
                               [
                                   "Cartographie des licenciés en France",
                                   "Statistiques des équipements en France",
                                   "Nb licenciés et équipements sportifs par sport dans le département", 
                                   "Pratique du sport dans ma commune",
                                   "Statistiques des licenciés par fédération",
                                   "Comment utiliser l'application ?",
                                   "A propos de Spartoo"], 
            icons=['hexagon', 'hexagon-fill', 'building', 'geo-alt-fill', '123', 'person-raised-hand', 'question-circle'], menu_icon="list", default_index=0)
        
        selected

    # Naviguer vers la page sélectionnée
    if selected == 'Cartographie des licenciés en France':
        maps_licences_france(data_freshness)

    if selected == 'Statistiques des équipements en France':
        maps_equip_france(data_es_freshness)

    if selected == "Nb licenciés et équipements sportifs par sport dans le département":
        maps_dep(data_freshness)

    if selected == "Pratique du sport dans ma commune":
        maps_commune(data_freshness)

    if selected == "Statistiques des licenciés par fédération":
        barh_analysis(data_freshness)

    if selected == "Comment utiliser l'application ?":
        comment_utiliser(data_freshness)

    if selected == "A propos de Spartoo":
        a_propos(data_freshness)

if __name__ == '__main__':
    main()