import streamlit as st
from src.apps.france import france
from src.apps.maps_dep import maps_dep
from src.apps.barh_analysis import barh_analysis
from src.apps.maps_commune import maps_commune
from src.apps.a_propos import a_propos

from streamlit_option_menu import option_menu


def main():

    with st.sidebar:
        selected = option_menu("Accès au sport en France", 
                               [
                                   "Cartographie des licenciés en France", 
                                   "Nb licenciés et infrastructures par sport dans le département", 
                                   "Statistiques des licenciés par fédération",
                                   "Pratique du sport dans ma commune",
                                   "A propos"], 
            icons=['hexagon', 'building', '123', 'geo-alt-fill', 'question-circle'], menu_icon="list", default_index=0)
        
        selected

    # Navigate to the selected page
    if selected == 'Cartographie des licenciés en France':
        france()

    if selected == "Nb licenciés et infrastructures par sport dans le département":
        maps_dep()

    if selected == "Statistiques des licenciés par fédération":
        barh_analysis()

    if selected == "Pratique du sport dans ma commune":
        maps_commune()

    if selected == "A propos":
        a_propos()

if __name__ == '__main__':
    main()