import streamlit as st
import geopandas as gpd
import pandas as pd
from src.functions.functions import get_dep_list, display_barh

def barh_analysis():

    stat_options = ["Nombre total de licenciés",
                    "Nombre de femmes licenciées",
                    "Pourcentage de femmes licenciées",
                    "Nombre d'hommes licenciés", 
                    "Pourcentage d'hommes licenciés",
                    "Nombre de licenciés de moins de 15 ans",
                    "Pourcentage de licenciés de moins de 15 ans",
                    "Nombre de licenciés de plus de 60 ans",
                    "Pourcentage de licenciés de plus de 60 ans"]

    dep_options = get_dep_list(include_all=True)

    st.title('Statistiques des licenciés par fédération')

    st.markdown(":bulb: Cet écran permet de visualiser les statistiques comme par exemple le **pourcentage de femmes licenciées** par fédération sportive")

    with st.form('barh_form'):
        col1, col2 = st.columns(2)
        with col1:
            dep = st.selectbox("Choisir un département", dep_options)

        with col2:
            stat = st.selectbox("Choisir une statistique", stat_options)
        qpv = st.checkbox("Afficher les statistiques dans les QPV seulement")
        submitted = st.form_submit_button("Valider")

    if submitted:
        with st.spinner('Veuillez patienter ...'):
            st.subheader(f"{stat} par fédération")
            fig = display_barh(stat, dep, qpv)
            st.plotly_chart(fig)