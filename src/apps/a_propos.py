import streamlit as st

def a_propos():

    st.title('A propos')
    st.write("Ce projet de data visualisation a été réalisé dans le cadre du challenge 'Accès au sport' posté sur le site https://defis.data.gouv.fr/")

    st.subheader("Datasets utilisés : ")
    st.write("Equipements Sportifs: https://defis.data.gouv.fr/datasets/65b47fde1b55e035045aa480")    
    st.write("Quartiers prioritaires de la politique de la ville (QPV) : https://defis.data.gouv.fr/datasets/5a561801c751df42d7fca9b6")    
    st.write("Recensement des licences et clubs : https://defis.data.gouv.fr/datasets/53699ebba3a729239d205f58")    
    st.write("Population : https://defis.data.gouv.fr/datasets/53699d0ea3a729239d205b2e")    