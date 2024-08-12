import pandas as pd
import polars as pl
import plotly.express as px
import geopandas as gpd
from shapely.geometry import Point


###### ----- Fonctions de transformation de données ----- ######

def transform_licencies_for_map(df_licencies, fed_list, dep):
    """
    Filtre un dataframe de statistiques de licenciés sur le département et la liste des fédérations sélectionnées par l'utilisateur
    Et renvoie un dataframe prêt à l'emploi

    Paramètres
    -------
    df_licencies : pd.Dataframe
    fed_list : list | liste de fédérations sportives
    dep : str | code département à deux chiffres

    Retourne
    -------
    pd.DataFrame
    """

    licencies_f = df_licencies[(df_licencies['Fédération'].isin(fed_list)) & (df_licencies['Département'] == int(dep))]
    licencies_f = licencies_f[['Code Commune', 'Commune', 'Total']]
    licencies_f = licencies_f.rename(columns = {'Code Commune': 'code', 'Commune': 'commune', 'Total': 'nb_licencies'})
    licencies_f = licencies_f.groupby(['code', 'commune'])['nb_licencies'].sum().reset_index()

    return licencies_f


def transform_licencies_for_graph(fed_sports, sport, dep):
    """
    Renvoie un dataframe de statistiques aggrégées de licenciés sur le département et la liste des sports sélectionnés par l'utilisateur
    Appelé par le menu m03_maps_dep.py

    Paramètres
    -------
    df_licencies : pd.Dataframe
    sport : list | liste de fédérations sportives
    dep : str | code département à deux chiffres

    Retourne
    -------
    pd.DataFrame
    """

    df_agg = pl.read_parquet('data/transformed/lic-data-latest_details_agg.parquet')
    
    fed_list = fed_sports[fed_sports['sport'] == sport]['federation'].to_list()

    condition = (pl.col("Département") == dep) & (pl.col("Fédération").is_in(fed_list)) & (pl.col("QPV_or_not") == False)

    df_agg_licencies = df_agg.filter(condition)
    df_agg_licencies = df_agg_licencies.group_by(['age', 'sexe'], maintain_order=True).agg(pl.sum("value")).to_pandas()

    return df_agg_licencies


def get_dep_list(include_all):
    """
    Renvoie une liste de codes département

    Paramètres
    -------
    include_all : bool | indique si la valeur "Tous les départements" est souhaitée en format de sortie

    Retourne
    -------
    dep_options : str | liste de départements pour formulaire
    """
        
    dep_options = ["0" + str(i+1) if len(str(i+1)) == 1 else str(i+1) for i in range(95)]
    dep_options = [x for x in dep_options if x != '20'] + ['2A', '2B']

    if include_all:
        dep_options = ['Tous les départements'] + dep_options

    return dep_options

def get_commune_list(dep):
    """
    Renvoie un dataframe contenant les codes communes et noms des communes relatives au département sélectionné

    Paramètres
    -------
    dep : str | code département (exemple "33" pour Gironde)

    Retourne
    -------
    df : pd.Dataframe
    """

    df = pd.read_csv('data/transformed/mapping_dep_communes.csv', dtype = {'code_commune': str})
    df = df[df['dep'] == dep]

    df = df.dropna()
    return df


def get_commune_code_list(commune_df, commune_list):
    """
    Renvoie une liste de codes communes à partir d'un dataframe et d'une liste de noms de commune

    Paramètres
    -------
    commune_df : pd.Dataframe | contient la liste des codes commune et des noms de commune
    commune_list : list | contient une liste de noms de communes

    Retourne
    -------
    commune_code_list : list | liste de codes commune
    """

    commune_code_list = commune_df[commune_df['commune'].isin(commune_list)]['code_commune'].to_list()
    return commune_code_list


def get_dep_centroid(dep):
    """
    Renvoie les coordonnées du centroïde du département sélectionné

    Paramètres
    -------
    dep : str | code département

    Retourne
    -------
    lat, lon : float, float | latitude et longitude au format WGS84 
    """

    df = pd.read_csv('data/transformed/dep_centroids.csv')
    lat = df[df['code'] == dep]['latitude'].values[0]
    lon = df[df['code'] == dep]['longitude'].values[0]
    return lat, lon




def get_markers_html(df, marker_field, color_mapping):
    """
    Renvoie une string contenant le code CSS à afficher dans le bloc "Légende" correspondant à un marqueur de cartographie

    Paramètres
    -------
    df : pd.Dataframe |
    marker_field : str | champ correspondant au marqueur affiché sur la cartographie
    color_mapping : dict | dictionnaire contenant le mapping entre couleur et champ associé
    
    Retourne
    -------
    html_markers : str
    """

    markers_value = list(set(df[marker_field]))
    
    if marker_field in ['equip_service_periode', 'equip_travaux_periode']:
        markers_value = sorted(markers_value)

    html_markers = ""
    for marker in markers_value:
        color = color_mapping.get(marker)
        if marker == True:
            marker = "Oui"
        elif marker == False: 
            marker = "Non"
        html_markers += f"<i style='color:{color}; font-size:16px>'>&#9679;</i> {marker}<br>"

    return html_markers


def pivot_lic_df_genre():
    """
    Renvoie un dataframe contenant des statistiques sur le nombre de licenciés au format : 
    - Département, Fédération, QPV_or_not en ligne
    - Sexe (H/F) en colonne

    Paramètres
    -------
    Aucun
    
    Retourne
    -------
    df : pd.Dataframe
    """

    # Load dataframe
    df = pd.read_parquet('data/transformed/lic-data-latest_details_agg_hf.parquet')

    # Pivot dataframe containing nb licencies by Département, Fédération & QPV
    df = df.pivot_table(index=['Département', 'Fédération', 'QPV_or_not'],
                    columns='sexe',
                    values='value').reset_index()

    df = df.rename(columns = {'Département': 'code', 'F': 'nb_licencies_F', 'H': 'nb_licencies_H'})

    df['nb_licencies'] = df['nb_licencies_F'] + df['nb_licencies_H']
    df['pct_licencies_F'] = round((df['nb_licencies_F'] / df['nb_licencies'] * 100), 2)
    df['pct_licencies_H'] = round((df['nb_licencies_H'] / df['nb_licencies'] * 100), 2)

    return df


def pivot_lic_df_age():
    """
    Renvoie un dataframe contenant des statistiques sur le nombre de licenciés au format : 
    - Département, Fédération, QPV_or_not en ligne
    - Catégorie d'âge en colonne
    
    Paramètres
    -------
    Aucun
    
    Retourne
    -------
    df : pd.Dataframe
    """
    
    # Load dataframe
    df = pd.read_parquet('data/transformed/lic-data-2021_details_agg.parquet')

    mapping_age = {'01 à 04 ans' : 'Moins de 15 ans',
               '05 à 09 ans' : 'Moins de 15 ans', 
               '10 à 14 ans' : 'Moins de 15 ans',
               '15 à 19 ans' : 'Moins de 15 ans',
               '20 à 24 ans' : 'Entre 15 et 59 ans',
               '25 à 29 ans' : 'Entre 15 et 59 ans',
               '30 à 34 ans' : 'Entre 15 et 59 ans',
               '35 à 39 ans' : 'Entre 15 et 59 ans', 
               '40 à 44 ans' : 'Entre 15 et 59 ans',
               '45 à 49 ans' : 'Entre 15 et 59 ans',
               '50 à 54 ans' : 'Entre 15 et 59 ans',
               '55 à 59 ans' : 'Entre 15 et 59 ans',
               '60 à 64 ans' : 'Plus de 60 ans',
               '65 à 69 ans' : 'Plus de 60 ans',
               '70 à 74 ans' : 'Plus de 60 ans',
               '75 à 79 ans' : 'Plus de 60 ans',
               '80 à 99 ans' : 'Plus de 60 ans'
               }
    
    df['categorie_age'] = df['age'].apply(lambda x: mapping_age[x])

    df = df.groupby(['Département', 'Fédération', 'QPV_or_not', 'categorie_age']).sum().reset_index()
    df = df.drop(columns = {'sexe', 'age'})

    # Pivot dataframe containing nb licencies by Département, Fédération & QPV
    df = df.pivot_table(index=['Département', 'Fédération', 'QPV_or_not'],
                columns='categorie_age',
                values='value').reset_index()

    df = df.rename(columns = {'Département': 'code', 'Moins de 15 ans': 'nb_licencies_inf_15', 'Entre 15 et 59 ans': 'nb_licencies_15-59', 'Plus de 60 ans': 'nb_licencies_sup_60'})

    df['nb_licencies'] = df['nb_licencies_inf_15'] + df['nb_licencies_15-59'] + df['nb_licencies_sup_60']
    df['pct_licencies_inf_15'] = round((df['nb_licencies_inf_15'] / df['nb_licencies'] * 100), 2)
    df['pct_licencies_sup_60'] = round((df['nb_licencies_sup_60'] / df['nb_licencies'] * 100), 2)

    # Suppression de la colonne nb_licencies déjà présente dans le dataframe issu de la fonction pivot_lic_df_genre
    df = df.drop(columns = {'nb_licencies'})

    return df


def get_lic_stat_df(fed):
    """
    Renvoie un dataframe contenant des statistiques sur le nombre de licenciés au format : 
    - Département, Fédération, QPV_or_not en lignes
    - Sexe et Catégorie d'âge en colonnes

    Paramètres
    -------
    Aucun
    
    Retourne
    -------
    df : pd.Dataframe
    """

    df_genre = pivot_lic_df_genre()
    df_age = pivot_lic_df_age()

    if fed == "All":
        df = df_genre.merge(df_age, how = 'left', on = ['Fédération', 'code', 'QPV_or_not'])
    else:
        df_genre = df_genre[df_genre['Fédération'] == fed]
        df_age = df_age[df_age['Fédération'] == fed]
        df = df_genre.merge(df_age, how = 'left', on = ['Fédération', 'code', 'QPV_or_not'])
        df = df.drop(columns = {"Fédération"})

    return df







###### ----- Fonctions d'affichage de graphiques ----- ######

def display_licencies_plotline(df, sport, dep):
    """
    Génère un graphique Plotly Express qui va afficher le nombre de licenciés par tranche d'âge en fonction du sport et du département sélectionné par l'utilisateur
    Appelé par le menu m03_maps_dep.py

    Paramètres
    -------
    df : pd.Dataframe
    sport : str | sport sélectionné
    dep : str | code département à deux chiffres

    Retourne
    -------
    px.fig : graphique Plotly Express de type "Lineplot"
    """

    fig = px.line(df, x="age", y="value", color='sexe', 
                  color_discrete_map={
                      "H": "blue",
                      "F": "goldenrod"
                      })

    fig.update_layout(
        title = f"Nb licenciés H/F {sport} - Département {dep}"
    )

    return fig 


def display_licencies_barh(df, graph_height, detail):
    """
    Génère un graphique Plotly Express qui va afficher le nombre de licenciés par fédération
    Appelé par le menu m04_maps_commune.py

    Paramètres
    -------
    df : pd.Dataframe contenant des statistiques sur le nombre de licenciés par fédération dans les communes sélectionnées par l'utilisateur
    graph_height : str | sport sélectionné
    detail : str | maillage des statistiques souhaité pour le graphique (commune, département, ou France)

    Retourne
    -------
    px.fig : graphique Plotly Express de type "Barplot"
    """

    df = df.sort_values(by = 'nb_licencies')
    print(df.head())

    if detail == 'communes':
        fig = px.bar(df, y="Fédération", x="nb_licencies", orientation='h', color='Commune', width=800, height=graph_height, text_auto=True)
        fig.update_layout(title = f"Nb total de licenciés par fédération dans les communes sélectionnées")
        fig.update_xaxes(automargin=True)
        return fig 

    elif detail == 'dep':
        fig = px.bar(df, y="Fédération", x="nb_licencies", orientation='h', width=800, height=graph_height, text_auto=True)
        fig.update_layout(title = f"Nb total de licenciés par fédération dans le département")
        fig.update_xaxes(automargin=True)
        return fig 

    elif detail == 'france':
        fig = px.bar(df, y="Fédération", x="nb_licencies", orientation='h', width=800, height=graph_height, text_auto=True)
        fig.update_layout(title = f"Nb total de licenciés par fédération en France")
        fig.update_xaxes(automargin=True)
        return fig 


def display_barh(stat, dep, qpv):
    """
    Renvoie un graphique Plotly Express

    Paramètres
    -------
    stat : str | Libellé de la statistique souhaitée
    dep : str | Code département
    qpv : bool | True si le graphique n'affiche que des données sur les Quartiers Prioritaires, False si le graphique affiche des données sur l'ensemble du département
    
    Retourne
    -------
    fig : px.fig | Graphique Plotly Express de type "Barplot"
    """

    # Load dataframe
    df = get_lic_stat_df(fed="All")

    if dep == 'Tous les départements':
        df = df.groupby(['Fédération', 'QPV_or_not']).sum().reset_index()
        df['pct_licencies_F'] = round((df['nb_licencies_F'] / df['nb_licencies'] * 100), 2)
        df['pct_licencies_H'] = round((df['nb_licencies_H'] / df['nb_licencies'] * 100), 2)
        df['pct_licencies_inf_15'] = round((df['nb_licencies_inf_15'] / df['nb_licencies'] * 100), 2)
        df['pct_licencies_sup_60'] = round((df['nb_licencies_sup_60'] / df['nb_licencies'] * 100), 2)

    else:
        df = df[df['code'] == dep]

    if qpv == True:
        df = df[df['QPV_or_not'] == True]
    else:
        df = df[df['QPV_or_not'] == False]

    col_to_display = get_column_mapping()

    df = df.dropna()
    df = df.sort_values(by = col_to_display[stat], ascending = True)

    fig = px.bar(df, y="Fédération", x=col_to_display[stat], orientation='h', width=800, height=3500, text_auto=True)
    fig.update_xaxes(automargin=True)

    return(fig)







###### ----- Fonctions de Mapping entre données ----- ######

def get_mappings():
    """
    Renvoie deux dataframes de mappings

    Paramètres
    -------
    Aucun

    Retourne
    -------
    es_sports : pd.Dataframe | mapping entre type d'équipement sportif et sport associé
    fed_sports : pd.Dataframe | mapping entre fédération sportive et sport associé
    """

    es_sports = pd.read_json('data/transformed/mapping_es_sports.json', orient='index')
    es_sports = es_sports.reset_index().rename(columns = {'index': 'equip_type_name', 0: 'sport'})

    fed_sports = pd.read_json('data/transformed/mapping_fed_sports.json', orient='index')
    fed_sports = fed_sports.reset_index().rename(columns = {'index': 'federation', 0: 'sport'})

    return es_sports, fed_sports


def get_column_mapping():
    """
    Renvoie un dictionnaire de mapping entre libellé de la statistique en relation avec le nombre de licenciés et nom du champ correspondant

    Paramètres
    -------
    Aucun

    Retourne
    -------
    col_to_display : dict
    """

    col_to_display = {"Nombre total de licenciés": "nb_licencies",
                      "Ratio nombre de licenciés / population totale": "ratio_licencies_pop",
                      "Nombre de femmes licenciées": "nb_licencies_F",
                      "Pourcentage de femmes licenciées": "pct_licencies_F",
                      "Ratio nombre de femmes licenciées / population femmes": 'ratio_licencies_F_pop',
                      "Nombre d'hommes licenciés": "nb_licencies_H",
                      "Pourcentage d'hommes licenciés": "pct_licencies_H",
                      "Ratio nombre d'hommes licenciées / population hommes": 'ratio_licencies_H_pop',
                      "Nombre de licenciés de moins de 15 ans": 'nb_licencies_inf_15',
                      "Pourcentage de licenciés de moins de 15 ans": 'pct_licencies_inf_15',
                      "Ratio nombre de licenciés de moins de 15 ans / population moins de 15 ans" : 'ratio_licencies_inf_15_pop',
                      "Nombre de licenciés de plus de 60 ans": 'nb_licencies_sup_60',
                      "Pourcentage de licenciés de plus de 60 ans": 'pct_licencies_sup_60',
                      "Ratio nombre de licenciés de plus de 60 ans / population plus de 60 ans" :'ratio_licencies_sup_60_pop'
                      }

    return(col_to_display)


def get_colors_mapping(type):
    """
    Renvoie un dictionnaire de mapping entre labal d'un champ et couleur associée à afficher sur une cartographie

    Paramètres
    -------
    type : str | nom du champ de données sur lequel le mapping est souhaité

    Retourne
    -------
    color_mapping : dict
    """

    if type == 'equip_type_name':

        # Define a color mapping based on the type of sportive equipment
        color_mapping = {
            'Terrain de pétanque': 'beige', 
            'Terrain de volley-ball': 'red', 
            "Piste d'athlétisme isolée": 'orange', 
            'Multisports/City-stades': 'orange', 
            'Skatepark': 'green', 
            'Salle multisports (gymnase)': 'green', 
            'Salle de tennis de table': 'green', 
            'Piste de bicross': 'green', 
            'Parcours sportif/santé': 'green', 
            'Court de tennis': 'red', 
            "Dojo / Salle d'arts martiaux": 'green', 
            "Pas de tir à l'arc": 'green', 
            'Terrain de football': 'blue', 
            'Terrain de hockey sur gazon': 'green'}

    elif type in ['inst_acc_handi_bool', 'equip_douche', 'equip_sanit', 'equip_pmr_acc']:

        # Define a color mapping based on access handisport
        color_mapping = {
            True: 'green', 
            False: 'red'
            }
    
    elif type in ['equip_service_periode', 'equip_travaux_periode']:
        color_mapping = {
            'Aucune date disponible': 'gray',
            'Aucun travaux': 'gray',
            '0_avant 1945': 'darkred',
            '1945-1964': 'red',
            '1965-1974': 'orange',
            '0_avant 1975': 'darkred',
            '1975-1984': 'beige',
            '1985-1994': 'lightgreen',
            '1995-2004': 'green',
            '2005 et après' : 'darkgreen'
            }

    return(color_mapping)


def get_mapping_stats_equip():
    """
    Renvoie un dictionnaire de mapping entre libellé de la statistique en relation avec les équipements sportifs et nom du champ correspondant

    Paramètres
    -------
    Aucun
    
    Retourne
    -------
    mapping : dict
    """

    mapping = {"Nb équipements": 'inst_nom', 
               "Nb équipements pourvus d'un accès aux personnes en situation de handicap": 'inst_acc_handi_bool',
               "Pourcentage d'équipements pourvus d'un accès aux personnes en situation de handicap": 'inst_acc_handi_bool',               
               "Nb équipements pourvus de douches": 'equip_douche', 
               "Pourcentage d'équipements pourvus de douches": 'equip_douche', 
               "Nb équipements pourvus de sanitaires": 'equip_sanit', 
               "Pourcentage d'équipements pourvus de sanitaires": 'equip_sanit', 
               "Année médiane de mise en service des équipements": 'equip_service_date_fixed',
    }

    return mapping






###### ----- Fonctions one-shot pour transformer données brut en cas d'update de fichiers ----- ######

def transform_dep_code_commune(year):
    """
    Enregistre un fichier CSV de mapping entre codes départements et codes communes

    Paramètres
    -------
    year : int | année du fichier pris en compte pour générer le mapping
    
    Retourne
    -------
    Fichier CSV dans data/transformed
    """   

    df = pd.read_csv(f'data/raw/lic-data-{str(year)}.csv', delimiter=';', dtype = {'Code Commune': str, 'Département': str})
    df = df[['Code Commune', 'Commune', 'Département']]
    df = df.drop_duplicates().reset_index().rename(columns = {'Code Commune': 'code_commune', 'Commune': 'commune', 'Département': 'dep'})
    df.to_csv('data/transformed/mapping_dep_communes.csv')


def transform_pop_df(year):
    """
    Enregistre deux fichiers Parquet qui vont contenir le nombre d'habitants par commune, et par département

    Paramètres
    -------
    year : int | année du fichier pris en compte pour générer le mapping
    
    Retourne
    -------
    Fichiers Parquet dans data/transformed
    """   

    insee_field = 'P' + year_2c + '_POP'

    pop = pd.read_csv(f'data/raw/base-cc-evol-struct-pop-{str(year)}.csv', delimiter = ';', dtype = {'CODGEO': str})
    pop = pop[['CODGEO', insee_field]]
    pop = pop.rename({'CODGEO': 'code', insee_field: 'nb_habitants'})
    pop.to_parquet(f'data/transformed/population_{str(year)}.parquet')

    pop['dep'] = pop['code'].str[:2]
    pop = pop.groupby('dep')['nb_habitants'].sum().reset_index()
    pop.to_parquet(f'data/transformed/population_{str(year)}_par_dep.parquet')


def transform_pop_df_with_details(year):
    """
    Enregistre deux fichiers Parquet qui vont contenir le nombre d'habitants par tranche d'âge par commune, et par département

    Paramètres
    -------
    year : int | année du fichier pris en compte pour générer le mapping
    
    Retourne
    -------
    Fichiers Parquet dans data/transformed
    """  

    insee_fields = ['POP', 'POP0014', 'POP1529', 'POP3044', 'POP4559', 'POP6074', 'POP7589', 'POP90P',
                 'POPF', 'F0014', 'F1529', 'F3044', 'F4559', 'F6074', 'F7589', 'F90P',
                 'POPH', 'H0014', 'H1529', 'H3044', 'H4559', 'H6074', 'H7589', 'H90P']

    insee_fields_with_year = ['CODGEO']
    year_2c = str(year)[:-2]

    for field in insee_fields:
        insee_fields_with_year.append(f"P{year_2c}_{field}")

    df_pop = pd.read_csv(f'data/raw/base-cc-evol-struct-pop-{str(year)}.csv', sep = ';', dtype = {'CODGEO': str})
    df_pop = df_pop[insee_fields_with_year]

    df_pop['pop_total'] = df_pop[f'P{year_2c}_POP']
    df_pop['pop_inf_15'] = df_pop[f'P{year_2c}_POP0014']
    df_pop['pop_15_59'] = df_pop[f'P{year_2c}_POP1529'] + df_pop[f'P{year_2c}_POP3044'] + df_pop[f'P{year_2c}_POP4559']
    df_pop['pop_sup_60'] = df_pop[f'P{year_2c}_POP6074'] + df_pop[f'P{year_2c}_POP7589'] + df_pop[f'P{year_2c}_POP90P']
    df_pop['pop_femmes'] = df_pop[f'P{year_2c}_POPF']
    df_pop['pop_femmes_inf_15'] = df_pop[f'P{year_2c}_F0014']
    df_pop['pop_femmes_15_59'] = df_pop[f'P{year_2c}_F1529'] + df_pop[f'P{year_2c}_F3044'] + df_pop[f'P{year_2c}_F4559']
    df_pop['pop_femmes_sup_60'] = df_pop[f'P{year_2c}_F6074'] + df_pop[f'P{year_2c}_F7589'] + df_pop[f'P{year_2c}_F90P']
    df_pop['pop_hommes'] = df_pop[f'P{year_2c}_POPH']
    df_pop['pop_hommes_inf_15'] = df_pop[f'P{year_2c}_H0014']
    df_pop['pop_hommes_15_59'] = df_pop[f'P{year_2c}_H1529'] + df_pop[f'P{year_2c}_H3044'] + df_pop[f'P{year_2c}_H4559']
    df_pop['pop_hommes_sup_60'] = df_pop[f'P{year_2c}_H6074'] + df_pop[f'P{year_2c}_H7589'] + df_pop[f'P{year_2c}_H90P']                    
                      
    df_pop = df_pop.drop(columns = {f'P{year_2c}_POP', f'P{year_2c}_POP0014', f'P{year_2c}_POP1529', f'P{year_2c}_POP3044',
       f'P{year_2c}_POP4559', f'P{year_2c}_POP6074', f'P{year_2c}_POP7589', f'P{year_2c}_POP90P', f'P{year_2c}_POPF',
       f'P{year_2c}_F0014', f'P{year_2c}_F1529', f'P{year_2c}_F3044', f'P{year_2c}_F4559', f'P{year_2c}_F6074',
       f'P{year_2c}_F7589', f'P{year_2c}_F90P', f'P{year_2c}_POPH', f'P{year_2c}_H0014', f'P{year_2c}_H1529',
       f'P{year_2c}_H3044', f'P{year_2c}_H4559', f'P{year_2c}_H6074', f'P{year_2c}_H7589', f'P{year_2c}_H90P'})                  

    df_pop.to_parquet(f"data/transformed/population_{str(year)}_details_per_commune.parquet")

    df_pop['DEP'] = df_pop['CODGEO'].str[:2]
    df_pop = df_pop.groupby('DEP').sum().drop(columns = {'CODGEO'})
    df_pop = df_pop.round(0).astype(int).reset_index()
    df_pop.to_parquet(f"data/transformed/population_{str(year)}_details_per_dep.parquet")


def transform_licencies_df(filepath, year, latest=True):
    """
    Enregistre 4 fichiers Parquet qui vont contenir des statistiques sur le nombre de licenciés dans différents formats

    Paramètres
    -------
    filepath : str | chemin du fichier de données bruts "lic-data_[YEAR].csv"
    year : int | année indiquée dans le titre du fichier de données brutes
    latest : bool | indique si les fichiers transformés doivent avoir comme suffixe l'année ou "latest"
    
    Retourne
    -------
    Fichiers Parquet dans data/transformed
    """ 

    df = pd.read_csv(filepath, delimiter = ';', dtype = {'Code Commune': str, 'Département': str})

    if latest:
        suffix = "latest"
    else:
        suffix = str(year)
    
    df['QPV_or_not'] = df['Nom QPV'].fillna('0')
    df['QPV_or_not'] = df['QPV_or_not'].apply(lambda x: True if x != '0' else False)
    
    # Calcul du dataframe Total nb licencies
    df_total = df[df['QPV_or_not'] == False][['Code Commune', 'Commune', 'Département', 'Région', 'Fédération', 'F - NR', 'H - NR', 'NR - NR', 'Total']]
    df_total = df_total.rename(columns = {'Code Commune': 'code', 'Total': 'nb_licencies'})
    df_total.to_parquet(f'data/transformed/lic-data-{suffix}_total.parquet')

    # Calcul du dataframe Nb licenciés par Sexe et Âge
    df = df.drop(columns = {'F - NR', 'H - NR', 'NR - NR', 'Total'})
    df = pd.melt(df, id_vars = ['Code Commune', 'Commune', 'Code QPV', 'Nom QPV', 'QPV_or_not', 'Département', 'Région', 'Statut géo', 'Code', 'Fédération'], var_name='category', value_name='value')
    df['sexe'] = df['category'].apply(lambda x: x[0])
    df['age'] = df['category'].apply(lambda x: x.split(' - ')[1])
    df['age'] = df['age'].str.replace('1 à 4 ans', '01 à 04 ans').replace('5 à 9 ans', '05 à 09 ans')
    df.to_parquet(f'data/transformed/lic-data-{suffix}_details.parquet')

    # Calcul du dataframe Nb licenciés par Fédération et Département
    df_agg = df.groupby(['Fédération', 'Département', 'QPV_or_not', 'sexe', 'age'])['value'].sum().reset_index()
    df_agg.to_parquet(f'data/transformed/lic-data-{suffix}_details_agg.parquet')

    # Calcul du dataframe Nb licenciés par Fédération et Département en fonction du sexe
    df_agg = df_agg.groupby(['Département', 'Fédération', 'QPV_or_not', 'sexe'])['value'].sum().reset_index()
    df_agg.to_parquet(f'data/transformed/lic-data-{suffix}_details_agg_hf.parquet')


def transform_equip_sportif_df():
    """
    Enregistre 1 fichier Parquet qui va contenir les informations processées issues des données brutes des équipements sportifs

    Paramètres
    -------
    Aucun
    
    Retourne
    -------
    Fichiers Parquet dans data/transformed
    """ 

    df = pd.read_csv('data/raw/fr-en-data-es-base-de-donnees.csv', delimiter = ';', dtype = {'inst_cp': str,
                                                                                        'inst_com_nom': str,
                                                                                        'inst_com_code': str,
                                                                                        'equip_service_date': str,
                                                                                        'equip_homo_date': str,
                                                                                        'equip_sae_haut': str,
                                                                                        'equip_url': str,
                                                                                        'epci_nom': str,
                                                                                        'lib_bdv': str,
                                                                                        'arr_name': str,
                                                                                        'dep_code': str,
                                                                                        'dep_code_filled': str
                                                                                        })
    
    # On ne conserve que ces colonnes
    df = df[['inst_nom', 
         'inst_adresse',
         'inst_cp',
         'inst_com_code',
         'inst_com_nom',
         'inst_actif',
         'inst_etat',
         'inst_acc_handi_bool',
         'inst_part_type_filter',
         'equip_numero',
         'equip_nom',
         'equip_type_code',
         'equip_type_name',
         'equip_type_famille',
         'equip_x',
         'equip_y',
         'equip_douche',
         'equip_sanit',
         'equip_pmr_acc',
         'equip_surf',
         'equip_service_date',
         'equip_service_periode',
         'equip_travaux_periode',
         'equip_aps_code',
         'equip_aps_nom',
         'epci_nom',
         'dep_code',
         'dep_code_filled',
         'dens_niveau',
         'dens_lib']]

    # Remplissage des NA des champs equip_service_periode et equip_travaux_periode
    df['equip_service_periode'] = df['equip_service_periode'].fillna('Aucune date disponible')
    df['equip_travaux_periode'] = df['equip_travaux_periode'].fillna('Aucun travaux')

    # Application d'un mapping sur les champs equip_service_periode et equip_travaux_periode
    mapping_periodes = {
        'Avant 1945': '0_avant 1945',
        '1945 - 1964': '1945-1964',
        '1945-1964': '1945-1964',
        '1965 - 1974': '1965-1974',
        '1965-1974': '1965-1974',
        '1975 - 1984': '1975-1984', 
        '1975-1984': '1975-1984', 
        '1985 - 1994': '1985-1994',
        '1985-1994': '1985-1994', 
        '1995 - 2004': '1995-2004',
        '1995-2004': '1995-2004', 
        'A partir de 2005': '2005 et après',
        'Avant 1975': '0_avant 1975',
        'Aucun travaux': 'Aucun travaux',
        'Aucune date disponible': 'Aucune date disponible',
        None: None
    }

    df['equip_service_periode'] = df['equip_service_periode'].apply(lambda x: mapping_periodes[x])
    df['equip_travaux_periode'] = df['equip_travaux_periode'].apply(lambda x: mapping_periodes[x])

    # Retraitement de la date de mise en service de l'équipement
    date_list = [str(x) for x in range(1900, 2050)]
    df['equip_service_date_fixed'] = df['equip_service_date'].fillna(0)
    df['equip_service_date_fixed'] = df['equip_service_date_fixed'].apply(lambda x: int(x) if x in date_list else "invalid")

    df.to_parquet('data/transformed/equip_es.parquet')


def create_mapping_idcarnat_dep():
    """
    Enregistre un fichier parquet contenant le mapping entre le champ "idcar_nat" (données carroyées de l'INSEE) et le département associé

    Paramètres
    -------
    Aucun
    
    Retourne
    -------
    Fichier Parquet dans data/transformed
    """ 

    # Récupération des identifiants de carreaux
    df = gpd.read_file('data/raw/carreaux_nivNaturel_met.gpkg')
    df = df[['idcar_nat']]
    df['coord_N'] = df['idcar_nat'].str[-15:-8]
    df['coord_E'] = df['idcar_nat'].str[-7:]

    # Transformation des identifiants en coordonnées GPS WGS84
    df_mapping_idcarnat = df[['idcar_nat', 'coord_N', 'coord_E']]
    df_mapping_idcarnat['geometry'] = df_mapping_idcarnat.apply(lambda x: Point(x['coord_E'], x['coord_N']), axis = 1)
    df_mapping_idcarnat = gpd.GeoDataFrame(df_mapping_idcarnat[['idcar_nat', 'coord_N', 'coord_E', 'geometry']], crs="EPSG:3035")
    df_mapping_idcarnat = df_mapping_idcarnat.to_crs('epsg:4326')

    # Chargement des départements au format geojson
    dep_geojson = gpd.read_file('data/raw/departements.geojson')

    # Jointure géospatiale permettant de faire le croisement entre coordonnées des carreaux et limites des départements
    df_mapping_idcarnat = gpd.sjoin(df_mapping_idcarnat, dep_geojson, how='left', predicate='within')

    # Enregistrement au format parquet
    df_mapping_idcarnat.to_parquet('data/transformed/mapping_idcarnat_dep.parquet')


def concat_communes_arr_geojson():
    """
    Enregistre un fichier GeoJSON contenant les polygones correspondant aux communes de France ET EGALEMENT aux arrondissements de Paris, Lyon et Marseille

    Paramètres
    -------
    Aucun
    
    Retourne
    -------
    Fichier GeoJSON dans data/transformed
    """ 

    communes_geojson = gpd.read_file('data/raw/communes.geojson')
    marseille_geojson = gpd.read_file('data/raw/communes-13-bouches-du-rhone.geojson')
    lyon_geojson = gpd.read_file('data/raw/communes-69-rhone.geojson')
    paris_geojson = gpd.read_file('data/raw/communes-75-paris.geojson')

    marseille_geojson = marseille_geojson[marseille_geojson['code'].str.startswith('132')]
    lyon_geojson = lyon_geojson[lyon_geojson['code'].str.startswith('693')]

    communes_with_arr_geojson = gpd.GeoDataFrame(pd.concat([communes_geojson, paris_geojson, lyon_geojson, marseille_geojson], ignore_index=True))
    communes_with_arr_geojson.to_file('data/transformed/communes_with_arr.geojson', driver='GeoJSON')