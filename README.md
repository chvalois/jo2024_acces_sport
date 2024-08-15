# JO 2024 - Défi Latitude Open Data - Accès au sport
==================================================

Ce projet de data visualisation via une application Streamlit a été réalisé dans le cadre du challenge 'Accès au sport' posté sur le site https://defis.data.gouv.fr/

Les travaux réalisés dans le cadre de ce projet permettront aux pouvoirs publics, notamment les collectivités territoriales, d'identifier les mesures adaptées pour corriger les inégalités sociales et territoriales pouvant exister
(construction et rénovation d'équipements, animations, aménagement de l'espace public, etc.) et de suivre les résultats de leurs politiques publiques d'accès au sport.

J'ai tenté d'adresser les problématiques suivantes :

- Inégalités territoriales via la visualisation des infrastructures sportives sur une cartographie
    - L'accès au sport est-il possible partout dans mon département ?
    - Quelles communes présentent le plus fort taux de licenciés parmi la population dans tel sport ?
    - Où sont les infrastructures sportives dans ma commune ?
    - Combien de licenciés y a t-il dans chaque commune de mon département ?
    - Où concentrer les installations de nouveaux équipements sportifs ?

- Inégalités sociales
    - Dans quels départements y a t-il le plus de licenciés de la fédération handisport ?
    - Quelles sont les fédérations sportives où la part de femmes licenciées est la plus faible ? 
    - Dans quel département la part de femmes licenciées dans le football est-elle la plus faible ?
    - Quels sont les départements où le ratio nombre de licenciés > 60 ans sur la population > 60 ans est le plus faible ?
    - Quelle est la répartition de l'âge des licenciés sportifs chez les hommes et les femmes pour une fédération donnée ?
    - Dans quel département le pourcentage de bassins de natation pourvu d’accès handicapés est-il le plus faible ?

Screenshot de l'application Sportoo
------------
![sportoo_screenshot](https://github.com/user-attachments/assets/01e75781-0c29-4852-aaef-95a932adb9b3)




Organisation du projet
------------

    ├── data                    <- data utilisée par l'application
    │   ├── raw                 <- data brute (telle que disponible sur data.gouv.fr)
    │   └── transformed         <- data retraitée pour les besoins de l'application        
    │
    ├── resources               
    │   └── demo                <- illustrations en image des data viz possibles via l'application
    │
    ├── src                     <- code source pour ce projet
    │   ├── apps                <- pages Streamlit de l'application
    │   └── functions           <- fonctions utilisées par l'application
    │       ├── create_legend.py         <- Fonctions pour générer les légendes sur les graphiques
    │       ├── functions.py             <- Fonctions de transformation de données, de création de graphiques
    │       └── map_functions.py         <- Fonctions de création de cartographies
    │   
    ├── .gitignore              
    ├── app.py                  <- page principale de l'application Streamlit
    └── requirements.txt        <- fichier requirements pour reproduire l'environnement de l'application
    
------------

## Installer les packages Python nécessaires au lancement de l'application

    `pip install -r requirements.txt`

## Pour lancer l'application

    `streamlit run app.py`
