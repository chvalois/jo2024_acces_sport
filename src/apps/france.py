import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from src.functions.functions import get_mappings
from src.functions.map_functions import display_france_map

def france():

    es_sports, fed_sports = get_mappings()
    fed_sports_list = fed_sports[fed_sports['sport'] != 'Divers']['federation'].to_list()
    fed_sports_list = sorted(fed_sports_list)

    stat_options = ["Nombre total de licenciés",
                    "Nombre de femmes licenciées",
                    "Pourcentage de femmes licenciées",
                    "Nombre d'hommes licenciés", 
                    "Pourcentage d'hommes licenciés"]

    st.title('Sportifs licenciés en France')
    st.write('Données 2021')

    with st.form('france'):
        col1, col2 = st.columns(2)
        with col1:
            fed = st.selectbox("Choisir une fédération", fed_sports_list)

        with col2:
            stat = st.selectbox("Choisir une statistique", stat_options)
        qpv = st.checkbox("Afficher les statistiques dans les QPV seulement")
        submitted = st.form_submit_button("Valider")

    if submitted:
        with st.spinner('Veuillez patienter ...'):

            st.subheader(f"{fed} | {stat} en France")           
            if qpv:
                st.write("Statistiques des quartiers prioritaires uniquement")
            st.write("Données de 2021")

            m = display_france_map(fed, stat, qpv)
            folium_static(m, height = 750)
