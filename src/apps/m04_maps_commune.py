import streamlit as st
from folium import plugins
from streamlit_folium import folium_static
from src.functions.map_functions import get_map_allsports, get_df_for_maps, get_a_map
from src.functions.functions import get_dep_list, get_commune_list, get_mappings, display_licencies_barh, get_commune_code_list

def maps_commune(data_freshness):
    """ Formulaire Streamlit qui permet de visualiser les statistiques sur une ou plusieurs communes ainsi que les équipements sportifs associés """

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
            dep = st.selectbox("Choisir un département", dep_options)
            commune_df = get_commune_list(dep)
            commune_options = sorted(list(set(commune_df['commune'])))
            commune_list = st.multiselect("Choisir une ou plusieurs communes", commune_options, max_selections=10)        

        with col2:
            map_type = st.selectbox("Colorer la cartographie en fonction de", ['Nombre de licenciés', 'Ratio Nb licenciés / Nb habitants'])
            marker_type = st.selectbox("Colorer les marqueurs de cartographie en fonction du", ['Accès aux personnes en situation de handicap', 'Accès PMR', 'Infrastructure équipée de douches', 'Infrastructure équipée de sanitaires', "Sport pratiqué dans l'infrastructure", 
                                                                                            "Période de mise en service", "Période des derniers travaux"])

        submitted = st.button("Valider")

    if submitted:
        if commune_list == []:
            st.write("Veuillez sélectionner au moins une commune")

        commune_code_list = get_commune_code_list(commune_df, commune_list)
        print(commune_code_list)

        with st.spinner('Veuillez patienter ...'):

            tab1, tab2 = st.tabs(["🗺️ Cartographie", "📈 Pratique des sports sélectionnés"])

            df_licencies_france, df_licencies_dep, df_licencies_par_code, df_licencies_par_fed, df_equip_f, cities_f = get_df_for_maps(sport_list, dep, commune_code_list, entire_dep=False)

            with tab1:
                title = f"Infrastructures sportives vs. Licenciés | Département {dep} | {str(data_freshness)}"
                m = get_a_map(dep, map_type, df_equip_f, cities_f, marker_type, title)
                plugins.Fullscreen().add_to(m)

                st.subheader(f"Nb licenciés vs. Infrastructures | Département {dep}")
                folium_static(m, width=1200, height=800)                

            with tab2:

                if 'Tous les sports' in sport_list:
                    sport_list = sport_options
                    graph_height = 2000
                else:
                    nb_sports = len(sport_list)
                    graph_height = 150 * nb_sports

                fig1 = display_licencies_barh(df_licencies_par_fed, graph_height, detail="communes")
                st.plotly_chart(fig1)

                st.subheader('Comparaison avec les statistiques dans le département et en France')
                fig2 = display_licencies_barh(df_licencies_dep, graph_height, detail="dep")
                st.plotly_chart(fig2)                
                
                fig3 = display_licencies_barh(df_licencies_france, graph_height, detail="france")
                st.plotly_chart(fig3)
                
