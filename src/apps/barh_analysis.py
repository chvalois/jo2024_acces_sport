import streamlit as st
import geopandas as gpd
import pandas as pd
from src.functions.functions import get_dep_list, display_barh

def barh_analysis():

    stat_options = ["Nombre total de licenciés",
                    "Nombre de femmes licenciées",
                    "Pourcentage de femmes licenciées",
                    "Nombre d'hommes licenciés", 
                    "Pourcentage d'hommes licenciés"]

    dep_options = get_dep_list(include_all=True)

    st.title('Statistiques des licenciés par fédération')
    st.write('Données 2021')

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


if __name__ == '__main__':
    france()