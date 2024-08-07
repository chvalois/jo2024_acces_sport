import streamlit as st
from folium import plugins
from streamlit_folium import folium_static
from src.functions.map_functions import get_map_allsports, get_df_for_maps, get_a_map
from src.functions.functions import get_dep_list, get_commune_list, get_mappings, display_licencies_barh, get_commune_code_list

def maps_commune():

    es_sports, fed_sports = get_mappings()
    es_sports_list = es_sports['sport'].to_list()
    fed_sports_list = fed_sports['sport'].to_list()

    sport_options = sorted(list(set(es_sports_list) & set(fed_sports_list)))
    sport_options_all = ['Tous les sports'] + sport_options

    dep_options = get_dep_list(include_all=False)

    st.title('Pratique du sport dans ma commune')

    st.markdown(":bulb: Cet écran permet de visualiser les statistiques sur une ou plusieurs communes")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            sport_list = st.multiselect("Choisir un sport", sport_options_all)
        with col2:
            dep = st.selectbox("Choisir un département", dep_options)
            commune_df = get_commune_list(dep)
            commune_options = sorted(list(set(commune_df['commune'])))
            commune_list = st.multiselect("Choisir une ou plusieurs communes", commune_options, max_selections=10)
        
        map_type = st.selectbox("Colorer la cartographie en fonction de", ['Nombre de licenciés', 'Ratio Nb licenciés / Nb habitants'])
        
        submitted = st.button("Valider")

    if submitted:
        if commune_list == []:
            st.write("Veuillez sélectionner au moins une commune")

        commune_code_list = get_commune_code_list(commune_df, commune_list)
        print(commune_code_list)

        tab1, tab2 = st.tabs(["📈 Pratique des sports sélectionnés", "🗺️ Cartographie"])
        with st.spinner('Veuillez patienter ...'):

            with tab1:
                if 'Tous les sports' in sport_list:
                    sport_list = sport_options
                    graph_height = 2000
                else:
                    graph_height = 800

                df_licencies_par_code, df_licencies_par_fed, df_equip_f, cities_f = get_df_for_maps(sport_list, dep, commune_code_list, entire_dep=False)
                fig = display_licencies_barh(df_licencies_par_fed, graph_height)
                st.plotly_chart(fig)

            with tab2:
                m = get_a_map(dep, map_type, df_equip_f, cities_f)
                plugins.Fullscreen().add_to(m)

                st.subheader(f"Nb licenciés vs. Infrastructures | Département {dep}")
                folium_static(m)
               