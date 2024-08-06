import streamlit as st

def a_propos():

    st.title('A propos de Sportoo')
    st.write("Ce projet de data visualisation a été réalisé dans le cadre du challenge 'Accès au sport' posté sur le site https://defis.data.gouv.fr/")

    st.divider()

    st.subheader("Objectif du challenge tel que décrit sur le site du gouvernement")
    
    with st.container(border=True):
        st.write("*La politique publique du sport entend donc en « favoriser l'accès […] pour toutes et tous, à tous les âges de la vie et sur l'ensemble du territoire hexagonal et ultramarin », \
             notamment à travers l'accompagnement des fédérations et le développement des équipements. \
             A ce titre, le plan « 5 000 équipements sportifs Génération 2024 » prévoit la création de 5 000 équipements supplémentaires entre 2024 et 2026, dont un tiers dans des quartiers prioritaires de la politique de la ville (QPV).*")

        st.write("*Les travaux réalisés dans le cadre de ce projet permettront aux pouvoirs publics, notamment les collectivités territoriales, d'identifier les mesures adaptées pour corriger les inégalités sociales et territoriales pouvant exister \
             (construction et rénovation d'équipements, animations, aménagement de l'espace public, etc.) et de suivre les résultats de leurs politiques publiques d'accès au sport.*")

    st.divider()

    st.subheader("Problématiques adressées par ce projet")
    st.write("J'ai tenté d'adresser les problématiques suivantes : ")

    st.markdown("""
    * Inégalités territoriales via la visualisation des infrastructures sportives sur une cartographie
        * L'accès au sport est-il possible partout dans mon département ?
        * Quelles communes présentent le plus fort taux de licenciés parmi la population dans tel sport ?
        * Où sont les infrastructures sportives dans ma commune ?
        * Combien de licenciés y a t-il dans chaque commune de mon département ?
    * Inégalités sociales 
        * Quelles sont les fédérations sportives où la part de femmes licenciées est la plus faible ? 
        * Quel est la répartition de l'âge des licenciés sportifs chez les hommes et les femmes pour un sport donné ?
    """)
    
    st.write("**Ce projet est un travail en cours de réalisation, il ne contient donc pas encore tous les éléments permettant d'adresser l'intégralité de la problématique posée par le challenge.**")

    st.divider()

    st.subheader("Datasets utilisés")
    st.write("*Les données utilisées datent toutes de 2021 (les dernières disponibles à ce jour)*")
    st.write("- Equipements Sportifs: https://defis.data.gouv.fr/datasets/65b47fde1b55e035045aa480")    
    st.write("- Quartiers prioritaires de la politique de la ville (QPV) : https://defis.data.gouv.fr/datasets/5a561801c751df42d7fca9b6")    
    st.write("- Recensement des licences et clubs : https://defis.data.gouv.fr/datasets/53699ebba3a729239d205f58")    
    st.write("- Population : https://defis.data.gouv.fr/datasets/53699d0ea3a729239d205b2e")    