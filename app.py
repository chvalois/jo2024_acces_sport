import streamlit as st
from src.apps.maps_licences_france import maps_licences_france
from src.apps.maps_equip_france import maps_equip_france
from src.apps.maps_dep import maps_dep
from src.apps.barh_analysis import barh_analysis
from src.apps.maps_commune import maps_commune
from src.apps.comment_utiliser import comment_utiliser
from src.apps.a_propos import a_propos


from streamlit_option_menu import option_menu

st.set_page_config(page_title="Sportoo - Sport Data Viz", page_icon=":checkered_flag:", layout="wide", initial_sidebar_state="auto", menu_items=None)

def main():

    with st.sidebar:
        selected = option_menu("Accès au sport en France", 
                               [
                                   "Cartographie des licenciés en France",
                                   "Statistiques des équipements en France",
                                   "Nb licenciés et équipements sportifs par sport dans le département", 
                                   "Statistiques des licenciés par fédération",
                                   "Pratique du sport dans ma commune",
                                   "Comment utiliser l'application ?",
                                   "A propos de Spartoo"], 
            icons=['hexagon', 'hexagon-fill', 'building', '123', 'geo-alt-fill', 'person-raised-hand', 'question-circle'], menu_icon="list", default_index=0)
        
        selected

    # Navigate to the selected page
    if selected == 'Cartographie des licenciés en France':
        maps_licences_france()

    if selected == 'Statistiques des équipements en France':
        maps_equip_france()

    if selected == "Nb licenciés et équipements sportifs par sport dans le département":
        maps_dep()

    if selected == "Statistiques des licenciés par fédération":
        barh_analysis()

    if selected == "Pratique du sport dans ma commune":
        maps_commune()

    if selected == "Comment utiliser l'application ?":
        comment_utiliser()

    if selected == "A propos de Spartoo":
        a_propos()

if __name__ == '__main__':
    main()