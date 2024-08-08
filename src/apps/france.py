import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from src.functions.functions import get_mappings
from src.functions.map_functions import display_france_map

def france():

    # Initialize the session state if it does not already exist
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False

    # Function to handle form submission
    def submit_form():
        st.session_state.form_submitted = True

    es_sports, fed_sports = get_mappings()
    fed_sports_list = fed_sports[fed_sports['sport'] != 'Divers']['federation'].to_list()
    fed_sports_list = sorted(fed_sports_list)

    stat_options = ["Nombre total de licenciés",
                    "Nombre de femmes licenciées",
                    "Pourcentage de femmes licenciées",
                    "Nombre d'hommes licenciés", 
                    "Pourcentage d'hommes licenciés",
                    "Nombre de licenciés de moins de 20 ans",
                    "Pourcentage de licenciés de moins de 20 ans",
                    "Nombre de licenciés de plus de 60 ans",
                    "Pourcentage de licenciés de plus de 60 ans"
                    ]

    st.title('Sportifs licenciés en France')

    st.markdown(":bulb: Cet écran permet de visualiser sur une cartographie des statistiques sur la pratique des licenciés en France métropolitaine par département")

    with st.form('france'):
        col1, col2 = st.columns(2)
        with col1:
            fed = st.selectbox("Choisir une fédération", fed_sports_list, index = 11)

        with col2:
            stat = st.selectbox("Choisir une statistique", stat_options)
        qpv = st.checkbox("Afficher les statistiques dans les QPV seulement", help = "QPV = Quartiers Prioritaires de la Politique de la Ville")
        submit_button = st.form_submit_button(label='Valider', on_click=submit_form)

    # Display a container if the form is not filled
    if not st.session_state.form_submitted:
        with st.container():
            st.subheader(f"Exemple | FF de Basketball | Pourcentage de femmes licenciées en France")    
            m = display_france_map("FF de Basketball", "Pourcentage de femmes licenciées", qpv=False)
            folium_static(m, height = 750)

    if st.session_state.form_submitted:
        with st.spinner('Veuillez patienter ...'):
            st.subheader(f"{fed} | {stat} en France")           
            if qpv:
                st.write("Statistiques des quartiers prioritaires uniquement")
            st.write("Données de 2021")

            m = display_france_map(fed, stat, qpv)
            folium_static(m, height = 750)

