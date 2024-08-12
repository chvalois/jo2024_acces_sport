import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from src.functions.functions import get_mappings
from src.functions.map_functions import display_france_equip_map

def maps_equip_france(data_freshness):
    """ Formulaire Streamlit qui permet de visualiser sur une cartographie des statistiques sur les équipements sportifs en France métropolitaine par département """

    es_sports, fed_sports = get_mappings()
    equip_options = sorted(es_sports['equip_type_name'].to_list())
    equip_options_all = ['Tous les équipements'] + equip_options

    stat_options = ["Nb équipements", 
                    "Nb équipements pourvus d'un accès aux personnes en situation de handicap", 
                    "Pourcentage d'équipements pourvus d'un accès aux personnes en situation de handicap", 
                    "Nb équipements pourvus de douches", 
                    "Pourcentage d'équipements pourvus de douches",
                    "Nb équipements pourvus de sanitaires", 
                    "Pourcentage d'équipements pourvus de sanitaires",
                    'Année médiane de mise en service des équipements']

    st.title('Equipements sportifs en France')

    st.markdown(":bulb: Cet écran permet de visualiser sur une cartographie des statistiques sur les équipements sportifs en France métropolitaine par département")

    with st.form('infra_france'):
        col1, col2 = st.columns(2)
        with col1:
            equip_list = st.multiselect("Choisir un type d'équipement", equip_options_all)

        with col2:
            stat = st.selectbox("Choisir une statistique", stat_options)
        
        submitted = st.form_submit_button("Valider")

    if submitted:
        with st.spinner('Veuillez patienter ...'):
            title = f"{stat} en France | {str(data_freshness)}"
            st.subheader(title)
            st.write(f"{', '.join(equip_list)}")

            m, nb_total_equip, df = display_france_equip_map(equip_list, stat, title)
            
            st.write(f"Nombre total d'équipements comptabilisés en France : {nb_total_equip}")

            folium_static(m, width=1200, height=800)
