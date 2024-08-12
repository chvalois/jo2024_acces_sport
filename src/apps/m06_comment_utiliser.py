import streamlit as st

def comment_utiliser():
    """ Page Streamlit qui donne des exemples d'usages de l'application """

    st.title('Comment utiliser Sportoo ?')
    st.write("Exemples d'analyses et d'insights")

    st.subheader("Dans quel département la part de femmes licenciées dans le football est-elle la plus faible ?")
    st.image('resources/demo/pct_femmes_basket.png', width=600)

    st.write("**Action possible**") 
    st.write("- Mener des campagnes de communication dans les départements où les femmes sont peu représentées dans le football")

    st.divider()

    st.subheader("Dans quel département les personnes de plus de 60 ans sont-elles le moins licenciées toutes fédérations confondues ?")
    st.image('resources/demo/ratio_licencies_60_sur_pop.png', width=600)

    st.write("**Action possible**") 
    st.write("- Favoriser le sport encadré des seniors dans le nord du pays")
    st.write("- Développer les infrastructures adaptées aux seniors dans les départements les plus en retard :")
    col1, col2 = st.columns(2)
    with col1:        
        st.write("Par exemple, en identifiant les fédérations où la part des licenciés du Nord de plus 60 ans est la plus importante : ")
        st.image('resources/demo/fed_populaires_pct_sup_60.png', width=600)
    with col2: 
        st.write("Ou en identifiant les fédérations où le nombre de licenciés du Nord est le plus conséquent : ")
        st.image('resources/demo/fed_populaires_nb_sup_60.png', width=600)


    st.divider()
    
    st.subheader("Dans quel département le % de bassins de natation est-il le moins pourvu d’accès handicapés ?")
    st.image('resources/demo/bassins_natation_handicap.png', width=600)

    st.write("**Action possible**") 
    st.write("- Mettre les bassins de natation aux normes d'accès aux personnes en situation de handicap dans les départements les plus en retard")
    st.write("Identifier les bassins nécessitant des travaux, par exemple en Charente :")
    st.image('resources/demo/bassins_natation_charente.png', width=600)
    st.write("Communiquer sur les autres équipements sportifs accessibles aux personnes en situation de handicap dans les communes : ")
    st.image('resources/demo/infra_acces_handi_angouleme.png', width=600)


    st.divider()
    
    st.subheader("Où concentrer les installations de nouveaux équipements sportifs ?")
    st.image('resources/demo/bassins_natation_handicap.png', width=600)

    st.write("**Action possible**") 
    st.write("- Prioriser les nouveaux équipements dans les départements où les équipements existants sont vieillissants, par exemple dans l'Essonne :")
    st.image('resources/demo/annee_mise_en_service_equipements.png', width=600)
    st.write("A Grigny par exemple, de nombreuses infrastructures datant de 1965-1974 : ")
    st.image('resources/demo/equipements_grigny.png', width=600)

    