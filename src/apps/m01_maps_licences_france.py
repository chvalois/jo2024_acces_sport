import streamlit as st
from streamlit_folium import folium_static
from src.functions.functions import get_mappings
from src.functions.map_functions import display_france_map

def maps_licences_france():
    """ Formulaire Streamlit qui permet de visualiser sur une cartographie des statistiques sur la pratique des licenciés en France métropolitaine par département """

    # Initialize the session state if it does not already exist
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False

    # Function to handle form submission
    def submit_form():
        st.session_state.form_submitted = True

    es_sports, fed_sports = get_mappings()
    fed_sports_list = fed_sports[fed_sports['sport'] != 'Divers']['federation'].to_list()
    fed_sports_list = sorted(fed_sports_list)

    fed_sports_all = ['Toutes les fédérations'] + fed_sports_list

    stat_options = ["Nombre total de licenciés",
                    "Ratio nombre de licenciés / population totale",
                    "Nombre de femmes licenciées",
                    "Pourcentage de femmes licenciées",
                    "Ratio nombre de femmes licenciées / population femmes",
                    "Pourcentage d'hommes licenciés", 
                    "Ratio nombre d'hommes licenciées / population hommes",
                    "Nombre de licenciés de moins de 15 ans",
                    "Pourcentage de licenciés de moins de 15 ans",
                    "Ratio nombre de licenciés de moins de 15 ans / population moins de 15 ans",
                    "Nombre de licenciés de plus de 60 ans",
                    "Pourcentage de licenciés de plus de 60 ans",
                    "Ratio nombre de licenciés de plus de 60 ans / population plus de 60 ans"
                    ]

    st.title('Sportifs licenciés en France')

    st.markdown(":bulb: Cet écran permet de visualiser sur une cartographie des statistiques sur la pratique des licenciés en France métropolitaine par département")

    with st.form('france'):
        col1, col2 = st.columns(2)
        with col1:
            fed = st.selectbox("Choisir une fédération", fed_sports_all, index = 12)

        with col2:
            stat = st.selectbox("Choisir une statistique", stat_options)
        submit_button = st.form_submit_button(label='Valider', on_click=submit_form)

    # Display a container if the form is not filled
    if not st.session_state.form_submitted:
        with st.container():
            st.subheader(f"Exemple | FF de Basketball | Part de femmes licenciées en France")    
            m, df = display_france_map("FF de Basketball", "Pourcentage de femmes licenciées")
            folium_static(m, height = 750)

    if st.session_state.form_submitted:
        with st.spinner('Veuillez patienter ...'):
            st.subheader(f"{fed} | {stat} en France")           

            st.write("Données de 2021")

            m, df = display_france_map(fed, stat)

            with st.expander("Explorer le jeu de données", expanded=False):
                st.dataframe(df)

            folium_static(m, height = 750)


