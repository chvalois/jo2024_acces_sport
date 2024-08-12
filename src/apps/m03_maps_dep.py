import streamlit as st
import pandas as pd
from folium import plugins
from streamlit_folium import folium_static
from src.functions.map_functions import get_map
from src.functions.functions import get_mappings, transform_licencies_for_graph, display_licencies_plotline, get_dep_list

def maps_dep():
    """ Formulaire Streamlit qui permet de visualiser la répartition H/F et par tranche d'âge des licenciés, et d'afficher sur une cartographie des détails sur la pratique du sport sélectionné dans les communes du département """

    es_sports, fed_sports = get_mappings()
    es_sports_list = es_sports['sport'].to_list()
    fed_sports_list = fed_sports['sport'].to_list()

    sport_options = sorted(list(set(es_sports_list) & set(fed_sports_list)))

    dep_options = get_dep_list(include_all=False)

    st.title('Pratique du sport dans le département')

    st.markdown(":bulb: Cet écran permet de visualiser la répartition H/F et par tranche d'âge des licenciés, et d'afficher sur une cartographie des détails sur la pratique du sport sélectionné dans les communes du département")

    with st.form('maps_dep'):
        col1, col2 = st.columns(2)
        with col1:
            sport = st.selectbox("Choisir un sport", sport_options)
            dep = st.selectbox("Choisir un département", dep_options)

        with col2:
            map_type = st.selectbox("Colorer la cartographie en fonction de", ['Nombre de licenciés', 'Ratio Nb licenciés / Nb habitants'])
            marker_type = st.selectbox("Colorer les marqueurs de cartographie en fonction du", ['Accès aux personnes en situation de handicap', 'Accès PMR', 'Infrastructure équipée de douches', 'Infrastructure équipée de sanitaires', "Sport pratiqué dans l'infrastructure", 
                                                                                                "Période de mise en service", "Période des derniers travaux"])
        submitted = st.form_submit_button("Valider")

    if submitted:

        tab1, tab2 = st.tabs(["🗺️ Cartographie", "📈 Pratique par sexe et tranche d'âge"])
        with st.spinner('Veuillez patienter ...'):

            df_licencies_agg = transform_licencies_for_graph(fed_sports, sport, dep)

            with tab1:
                m = get_map(sport, dep, map_type, marker_type)
                plugins.Fullscreen().add_to(m)

                st.subheader(f"Nb licenciés vs. Infrastructures | {sport} | Département {dep}")
                folium_static(m, width=1200, height=800)                

            with tab2:
                st.subheader(f"Nb licenciés | {sport} | Département {dep}")
                fig = display_licencies_plotline(df_licencies_agg, sport, dep)
                st.plotly_chart(fig)
                    

