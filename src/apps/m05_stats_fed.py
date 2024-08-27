import streamlit as st
import geopandas as gpd
import pandas as pd
from src.functions.functions import get_dep_list, display_barh, get_df_licencies_age_joyplot, display_joyplot

def barh_analysis(data_freshness):
    """ Formulaire Streamlit qui permet de visualiser les statistiques du nombre de licenciés par fédération sportive """

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

        tab1, tab2 = st.tabs(["📈 Par fédération", "👧 Répartition des licenciés par âge et fédération"])
        with st.spinner('Veuillez patienter ...'):

            with tab1:

                st.subheader(f"{stat} par fédération | {str(data_freshness)}")
                fig = display_barh(stat, dep, qpv)
                st.plotly_chart(fig)

            with tab2: 

                df = get_df_licencies_age_joyplot(dep, qpv)
                plt = display_joyplot(df)  

                if dep == 'Tous les départements':
                    dep_txt = "France entière"
                else:
                    dep_txt = f"Département {dep}"

                st.subheader(f"Répartition des licenciés par âge pour top 20 fédérations - {dep_txt}")
                if qpv == True:
                    st.write('QPV uniquement')
                st.pyplot(plt, clear_figure=None, use_container_width=True)

                st.write("*Les fédérations suivantes ont été exclues car non liées à un sport en particulier et réservées exclusivement aux plus jeunes :*")
                st.write("  * *F Sportive Educative de l'Enseignement Catholique (UGSEL)*")
                st.write("  * *Union Nationale du Sport Scolaire (UNSS)*")
                st.write("  * *Union Sportive de l'Enseignement du Premier Degré*")
