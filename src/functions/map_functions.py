import pandas as pd
import polars as pl
import geopandas as gpd
import folium
from folium import plugins
import geopandas as gpd
from src.functions.functions import get_mappings, get_colors_mapping, get_dep_centroid, get_column_mapping, get_lic_stat_df, get_markers_html, get_mapping_stats_equip
from src.functions import create_legend

def display_france_map(fed, stat):
    """
    Retourne une cartographie de type Folium affichant les statistiques relatives aux licenciés d'une ou de la totalité des fédérations sportives
    Utilisé par m01_maps_licencies_france

    Paramètres
    -------
    fed : str | Label de la fédération sportive souhaitée
    stat : str | Statistique utilisée pour colorer la heatmap
    
    Retourne
    -------
    m : Folium map
    df_export : pd.Dataframe | Dataframe contenant les informations relatives à la cartographie
    """ 

    # Chargement du fichier GeooJSON et du dataframe des équipements sportifs
    dep_geojson = gpd.read_file('data/raw/departements.geojson')
    df_pop = pd.read_parquet('data/transformed/population_2021_details_per_dep.parquet')
    df_pop = df_pop.rename(columns = {'DEP': 'code'})
    
    # Si l'utilisateur souhaite afficher des stats sur l'ensemble des fédérations, fed = 'All' pour plus de simplicité
    if fed == "Toutes les fédérations":
        fed = 'All'

    # Récupération et retraitement du dataframe des statistiques licenciés de la fédération sélectionnée
    df = get_lic_stat_df(fed)

    df = df.merge(df_pop, on = "code", how = "left")
    df['ratio_licencies_pop'] = round((df['nb_licencies'] / df['pop_total'] * 100), 2)
    df['ratio_licencies_F_pop'] = round((df['nb_licencies_F'] / df['pop_femmes'] * 100), 2)
    df['ratio_licencies_H_pop'] = round((df['nb_licencies_F'] / df['pop_hommes'] * 100), 2)
    df['ratio_licencies_inf_15_pop'] = round((df['nb_licencies_inf_15'] / df['pop_inf_15'] * 100), 2)
    df['ratio_licencies_sup_60_pop'] = round((df['nb_licencies_sup_60'] / df['pop_sup_60'] * 100), 2)

    if fed == 'All':
        df = df.groupby(['code', 'QPV_or_not']).sum().reset_index()
        df['pct_licencies_F'] = round((df['nb_licencies_F'] / df['nb_licencies'] * 100), 2)
        df['pct_licencies_H'] = round((df['nb_licencies_H'] / df['nb_licencies'] * 100), 2)
        df['pct_licencies_inf_15'] = round((df['nb_licencies_inf_15'] / df['nb_licencies'] * 100), 2)
        df['pct_licencies_sup_60'] = round((df['nb_licencies_sup_60'] / df['nb_licencies'] * 100), 2)

    # Exclusion des statistiques spécifiques aux QPV (quartiers prioritaires)
    df_all_zones = df[df['QPV_or_not'] == False]
    
    # Ajout des statistiques au dataframe geojson
    dep_f = dep_geojson.merge(df_all_zones, on = 'code', how = 'left')
    dep_f = dep_f.reset_index()
    dep_f['id'] = dep_f.index

    # Conversion du GeoDataFrame en GeoJSON
    geojson_data = dep_f.to_json()

    # Récupération des labels de colonnes 
    col_to_display = get_column_mapping()

    # Création de la map centrée sur la France (centroïde de la France métropolitaine)
    map_center = [46.494739, 2.602833] 
    m = folium.Map(location=map_center, zoom_start=6)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Création de la couche Choropleth (heatmap)
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=dep_f,
        columns=['id', col_to_display[stat]],
        key_on='feature.properties.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.1,
        line_weight=0.5,
        legend_name=col_to_display[stat]
    ).add_to(m)

    # Définition des labels qui seront affichés dans les tooltips (différents si la stat demandée est un ratio 
    # ou une autre statistique pour ne pas encombrer la lecture de la cartographie)
    if stat[:5] == 'Ratio':
        aliases_for_map = ['Département:', 
                           "Nombre total de licenciés", 
                           "Ratio nb licenciés / population totale",
                           "Nombre de femmes licenciées", 
                           "Ratio nb femmes licenciées / population femmes", 
                           "Nombre d'hommes licenciés", 
                           "Ratio nb hommes licenciées / population hommes", 
                           "Nombre de licenciés < 15 ans", 
                           "Ratio nb licenciés < 15 ans / population < 15 ans", 
                           "Nombre de licenciés > 60 ans", 
                           "Ratio nb licenciés > 60 ans / population > 60 ans"]

        fields_for_map = ['nom', 
                          'nb_licencies',
                          'ratio_licencies_pop',
                          'nb_licencies_F', 
                          'ratio_licencies_F_pop', 
                          'nb_licencies_H', 
                          'ratio_licencies_H_pop', 
                          'nb_licencies_inf_15', 
                          'ratio_licencies_inf_15_pop', 
                          'nb_licencies_sup_60', 
                          'ratio_licencies_sup_60_pop']
    else:
        aliases_for_map = ['Département:', 
                           "Nombre total de licenciés", 
                           "Nombre de femmes licenciées", 
                           "Pourcentage de femmes licenciées", 
                           "Nombre d'hommes licenciés", 
                           "Pourcentage d'hommes licenciés", 
                           "Nombre de licenciés de moins de 15 ans", 
                           "Pourcentage de licenciés de moins de 15 ans", 
                           "Nombre de licenciés de plus de 60 ans", 
                           "Pourcentage de licenciés de plus de 60 ans"]

        fields_for_map = ['nom', 
                          'nb_licencies', 
                          'nb_licencies_F', 
                          'pct_licencies_F', 
                          'nb_licencies_H', 
                          'pct_licencies_H', 
                          'nb_licencies_inf_15', 
                          'pct_licencies_inf_15', 
                          'nb_licencies_sup_60', 
                          'pct_licencies_sup_60']

    # Ajout des tooltips
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
        'fillColor': 'transparent',  # No fill color
        'color': '#007FFF',  # Border color
        'weight': 0.5,  # Border width
        'opacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            aliases=aliases_for_map,
            fields=fields_for_map,
            localize=True, 
            height=300
        )
    ).add_to(m)

    # Activer le bouton fullscreen sur Folium
    plugins.Fullscreen().add_to(m)

    # Suppression des colonnes inutiles pour exposition du dataframe sur l'application
    df_export = dep_f.drop(columns = {'geometry', 'QPV_or_not'})

    if fed == 'All':
        df_export = df_export.drop(columns = {'Fédération'})


    return(m, df_export)


def display_france_equip_map(equip_list, stat):
    """
    Retourne une cartographie de type Folium affichant la liste des équipements par département et la statistique demandée sous forme de heatmap
    Utilisé par m02_maps_equip_france

    Paramètres
    -------
    equip_list : list | Liste des équipements sportifs souhaités par l'utilisateur 
    stat : str | Statistique utilisée pour colorer la heatmap
    
    Retourne
    -------
    m : Folium map
    nb_total_equip : int | Nb total d'équipements
    df_equip_f : pd.Dataframe | Dataframe contenant les statistiques des équipements après traitement
    """

    # Chargement du fichier GeooJSON et du dataframe des équipements sportifs
    dep_geojson = gpd.read_file('data/raw/departements.geojson')
    df_equip = pl.read_parquet('data/transformed/equip_es.parquet')
    
    # Récupération des mappings Equipements Sportifs et Fédérations Sportives
    es_sports, fed_sports = get_mappings()

    if 'Tous les équipements' in equip_list:
        equip_type_list = sorted(es_sports['equip_type_name'].to_list())
    else:
        equip_type_list = equip_list

    # Filtrage des dataframe sur les équipements
    df_equip_f = df_equip.filter(pl.col("equip_type_name").is_in(equip_type_list))
    nb_total_equip = df_equip_f['inst_nom'].count()

    mapping_equip_field = get_mapping_stats_equip()
    equip_field = mapping_equip_field[stat]
    
    # Préparation du dataframe et des champs affichés sur la cartographie si la statistique est la somme de champs booléens (exemple : nombre d'équipements pourvus de douches)
    if equip_field in ['inst_acc_handi_bool', 'equip_pmr_acc', 'equip_douche', 'equip_sanit']:
        df_equip_f = df_equip_f.group_by(['dep_code_filled'], maintain_order=True).agg(pl.sum(equip_field), pl.count('inst_nom')).to_pandas()
        df_equip_f = df_equip_f.rename(columns = {'dep_code_filled': 'code', equip_field: 'stat', 'inst_nom': 'nb_equip'})
        df_equip_f['pct_stat'] = round(df_equip_f['stat'] / df_equip_f['nb_equip'] * 100, 2)

        aliases_for_map = ['Département : ', "Nombre total d'équipement : ", "Nb équipements pourvus : ", "Pourcentage d'équipements pourvus : "]
        fields_for_map = ['nom', 'nb_equip', 'stat', 'pct_stat']

    # Préparation du dataframe et des champs affichés sur la cartographie si la statistique est la médiane d'un champ numérique (exemple : année médiane de mise en service de l'équipement)
    elif equip_field == 'equip_service_date_fixed':
        df_equip_f = df_equip_f.filter(pl.col(equip_field).is_not_nan())
        df_equip_f = df_equip_f.group_by(['dep_code_filled'], maintain_order=True).agg(pl.median(equip_field), pl.count('inst_nom')).to_pandas()
        df_equip_f = df_equip_f.rename(columns = {'dep_code_filled': 'code', equip_field: 'stat', 'inst_nom': 'nb_equip'})

        aliases_for_map = ['Département : ', "Nombre total d'équipements : ", "Année médiane de mise en service : "]
        fields_for_map = ['nom', 'nb_equip', 'stat']

    # Préparation du dataframe et des champs affichés sur la cartographie si la statistique est le nombre total d'équipements
    elif equip_field == 'inst_nom':
        df_equip_f = df_equip_f.group_by(['dep_code_filled'], maintain_order=True).agg(pl.count('inst_nom')).to_pandas()
        df_equip_f = df_equip_f.rename(columns = {'dep_code_filled': 'code', 'inst_nom': 'stat'})

        aliases_for_map = ['Département : ', "Nombre total d'équipements : "]
        fields_for_map = ['nom', 'stat']

    # Affichage de la colonne pct_stat si la statistique est un pourcentage, stat sinon
    if stat[:11] == 'Pourcentage':
        col_to_display = 'pct_stat'
    else:
        col_to_display = 'stat'

    # Ajout des statistiques au dataframe geojson
    dep_f = dep_geojson.merge(df_equip_f, on = 'code', how = 'left')
    dep_f = dep_f.reset_index()
    dep_f['id'] = dep_f.index

    # Conversion du GeoDataFrame en GeoJSON
    geojson_data = dep_f.to_json()

    # Création de la map centrée sur la France (centroïde de la France métropolitaine)
    map_center = [46.494739, 2.602833] 
    m = folium.Map(location=map_center, zoom_start=6)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Création de la couche Choropleth (heatmap)
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=dep_f,
        columns=['id', col_to_display],
        key_on='feature.properties.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.1,
        line_weight=0.5,
        legend_name=stat
    ).add_to(m)

    # Ajout des tooltips
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
        'fillColor': 'transparent',  # No fill color
        'color': '#007FFF',  # Border color
        'weight': 0.5,  # Border width
        'opacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            aliases=aliases_for_map,
            fields=fields_for_map,
            localize=True
        )
    ).add_to(m)

    # Activer le bouton fullscreen sur Folium
    plugins.Fullscreen().add_to(m)

    return(m, nb_total_equip, df_equip_f)


def get_map(sport, dep, map_type, marker_type):
    """
    Retourne une cartographie des équipements sportifs sur un département
    Utilisé par m03_maps_dep

    Paramètres
    -------
    sport : str | Sport sélectionné par l'utilisateur
    dep : str | Code département à deux chiffres
    map_type : str | Cartographie de type statistique Nombre ou Ratio
    marker_type : str | Type de marqueur en fonction du type d'équipement

    Retourne
    -------
    m : Folium map
    """ 

    # Import des dataframes
    df_equip = pl.read_parquet('data/transformed/equip_es.parquet')
    df_licencies = pl.read_parquet('data/transformed/lic-data-2021_total.parquet')
    cities_geojson = gpd.read_file('data/raw/communes.geojson')
    df_pop = pd.read_parquet('data/transformed/population_2021.parquet')

    # Récupération des mappings Equipements Sportifs et Fédérations Sportives
    es_sports, fed_sports = get_mappings()
    fed_list = fed_sports[fed_sports['sport'] == sport]['federation'].to_list()
    equip_type_list = es_sports[es_sports['sport'] == sport]['equip_type_name'].to_list()

    # Filtrage du dataframe des équipements
    condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("dep_code_filled") == dep)
    df_equip_f = df_equip.filter(condition).to_pandas()

    ### Filtrage du dataframe des statistiques licenciés
    df_licencies = df_licencies.filter(pl.col('Fédération').is_in(fed_list))
    df_licencies = df_licencies.group_by(['code'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Filter Geo Dataframe & ajout des statistiques licenciés
    cities_f = cities_geojson[cities_geojson['code'].str.startswith(dep)]
    cities_f = cities_f.merge(df_licencies[['code', 'nb_licencies']], on = 'code', how = 'left')
    cities_f = cities_f.merge(df_pop[['code', 'nb_habitants']], on = 'code', how = 'left')
    cities_f['pct_licencies'] = cities_f.apply(lambda x: round(x['nb_licencies'] / x['nb_habitants'] * 100, 4) if x['nb_licencies'] > 0 else 0, axis = 1)

    cities_f['nb_licencies'] = cities_f['nb_licencies'].fillna(0)
    cities_f = cities_f.reset_index()
    cities_f['id'] = cities_f.index

    # Conversion du GeoDataFrame en GeoJSON
    geojson_data = cities_f.to_json()

    # Création d'une map centrée sur le département
    lat, lon = get_dep_centroid(dep)
    map_center = [lat, lon] 
    m = folium.Map(location=map_center, zoom_start=9)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Création du contenu du popup lorsque l'utilisateur clique sur un marqueur de la carto
    df_equip_f = df_equip_f.dropna(subset = ['equip_x', 'equip_y'])
    df_equip_f['label_html'] = df_equip_f.apply(lambda x: f"<b>{x['inst_nom']} - {x['equip_nom']}</b><br/> \
                                {x['equip_type_famille']} > {x['equip_type_name']} <br/> \
                                {x['inst_adresse']} {x['inst_cp']} {x['inst_com_nom']} <br/> \
                                Accès aux personnes en situation de handicap : {'Oui' if x['inst_acc_handi_bool'] == True else 'Non' if x['inst_acc_handi_bool'] == False else 'Non défini'} <br/> \
                                Accès PMR : {'Oui' if x['equip_pmr_acc'] == True else 'Non' if x['equip_pmr_acc'] == False else 'Non défini'} <br/> \
                                Infrastructure équipée de sanitaires : {'Oui' if x['equip_sanit'] == True else 'Non' if x['equip_sanit'] == False else 'Non défini'} <br/> \
                                Infrastructure équipée de douches : {'Oui' if x['equip_douche'] == True else 'Non' if x['equip_douche'] == False else 'Non défini'} <br/> \
                                Sport pratiqué dans l'infrastructure : {'Oui' if x['equip_type_name'] == True else 'Non' if x['equip_type_name'] == False else 'Non défini'} <br/> \
                                Période de mise en service : {x['equip_service_periode']} <br/> \
                                Période des derniers travaux : {x['equip_travaux_periode']} <br/> \
                                {'En activité : Oui' if x['inst_actif'] else 'En activité : Non'}", axis = 1)
                                   

    if map_type == 'Nombre de licenciés':
        heatmap_field = 'nb_licencies'
        
    else:
        heatmap_field = 'pct_licencies'

    marker_mapping = {"Accès aux personnes en situation de handicap": 'inst_acc_handi_bool',
                      "Accès PMR": 'equip_pmr_acc', 
                      "Infrastructure équipée de douches": 'equip_douche', 
                      "Infrastructure équipée de sanitaires": 'equip_sanit', 
                      "Sport pratiqué dans l'infrastructure": 'equip_type_name', 
                      "Période de mise en service": 'equip_service_periode',
                      "Période des derniers travaux": 'equip_travaux_periode'}
    
    marker_field = marker_mapping[marker_type]

    color_mapping = get_colors_mapping(marker_field)

    # Ajout d'une couche choropleth (heatmap)
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=cities_f,
        columns=['id', heatmap_field],
        key_on='feature.properties.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.1,
        line_weight=0.5,
        legend_name=heatmap_field
    ).add_to(m)

    # Ajout des tooltips
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
        'fillColor': 'transparent',  # No fill color
        'color': '#007FFF',  # Border color
        'weight': 0.5,  # Border width
        'opacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['nom', 'nb_licencies', 'nb_habitants', "pct_licencies"],
            aliases=['Commune:', 'Nb de licenciés:', 'Nb d\'habitants', 'Pourcentage de licenciés:'],
            localize=True
        )
    ).add_to(m)

    # Ajout des marqueurs d'équipements sportifs
    for _, equipment in df_equip_f.iterrows():
    
        iframe = folium.IFrame(equipment['label_html'])
        popup = folium.Popup(iframe,
                     min_height=100,
                     min_width=500,
                     max_height=100,
                     max_width=500)
        
        color = color_mapping.get(equipment[marker_field], 'gray')

        folium.Marker(location=[equipment['equip_y'], equipment['equip_x']],
                    popup=popup,
                    icon=folium.Icon(color=color)).add_to(m)



    # Ajout d'une légende customisée (HTML)
    html_markers = get_markers_html(df_equip_f, marker_field, color_mapping)
    m = create_legend.run(m, f"Infrastructures sportives vs. Licenciés | {sport} | Département {dep}", marker_type, html_markers)

    # Save the map to an HTML file
    m.save('map.html')

    return m


def get_a_map(dep, map_type, df_equip_f, cities_f, marker_type):
    """
    Retourne une cartographie de type Folium affichant les équipements et statistiques relatives à une ou plusieurs communes d'un département sélectionné par l'utilisateur
    Utilisé par m04_maps_commune

    Paramètres
    -------
    dep : str | Code département à deux chiffres
    map_type : str | Cartographie de type statistique Nombre ou Ratio
    df_equip_f : pd.Dataframe | Dataframe contenant les équipements sportifs correspondant à la sélection
    cities_f : GeoJson Dataframe | Dataframe contenant les informations et polygones des communes
    marker_type : str | Type de marqueur en fonction du type d'équipement
    
    Retourne
    -------
    m : Folium map
    """ 

    # Conversion du GeoDataFrame en GeoJSON
    geojson_data = cities_f.to_json()

    # Création du contenu du popup lorsqu'on clique sur un marker de la map
    df_equip_f = df_equip_f.dropna(subset = ['equip_x', 'equip_y'])
    df_equip_f['label_html'] = df_equip_f.apply(lambda x: f"<b>{x['inst_nom']} - {x['equip_nom']}</b><br/> \
                                {x['equip_type_famille']} > {x['equip_type_name']} <br/> \
                                {x['inst_adresse']} {x['inst_cp']} {x['inst_com_nom']} <br/> \
                                Accès aux personnes en situation de handicap : {'Oui' if x['inst_acc_handi_bool'] == True else 'Non' if x['inst_acc_handi_bool'] == False else 'Non défini'} <br/> \
                                Accès PMR : {'Oui' if x['equip_pmr_acc'] == True else 'Non' if x['equip_pmr_acc'] == False else 'Non défini'} <br/> \
                                Infrastructure équipée de sanitaires : {'Oui' if x['equip_sanit'] == True else 'Non' if x['equip_sanit'] == False else 'Non défini'} <br/> \
                                Infrastructure équipée de douches : {'Oui' if x['equip_douche'] == True else 'Non' if x['equip_douche'] == False else 'Non défini'} <br/> \
                                Sport pratiqué dans l'infrastructure : {'Oui' if x['equip_type_name'] == True else 'Non' if x['equip_type_name'] == False else 'Non défini'} <br/> \
                                Période de mise en service : {x['equip_service_periode']} <br/> \
                                Période des derniers travaux : {x['equip_travaux_periode']} <br/> \
                                {'En activité : Oui' if x['inst_actif'] else 'En activité : Non'}", axis = 1)


    if map_type == 'Nombre de licenciés':
        heatmap_field = 'nb_licencies'
        
    else:
        heatmap_field = 'pct_licencies'

    marker_mapping = {"Accès aux personnes en situation de handicap": 'inst_acc_handi_bool',
                      "Accès PMR": 'equip_pmr_acc', 
                      "Infrastructure équipée de douches": 'equip_douche', 
                      "Infrastructure équipée de sanitaires": 'equip_sanit', 
                      "Sport pratiqué dans l'infrastructure": 'equip_type_name', 
                      "Période de mise en service": 'equip_service_periode',
                      "Période des derniers travaux": 'equip_travaux_periode'}

    marker_field = marker_mapping[marker_type]

    color_mapping = get_colors_mapping(marker_field)

    # Création d'une cartographie centrée sur le département
    lat, lon = get_dep_centroid(dep)
    map_center = [lat, lon] 
    m = folium.Map(location=map_center, zoom_start=9)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Ajout d'une couche choropleth (heatmap) basée sur le heatmap_field défini plus haut
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=cities_f,
        columns=['id', heatmap_field],
        key_on='feature.properties.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.1,
        line_weight=0.5,
        legend_name=heatmap_field
    ).add_to(m)

    # Ajout des tooltips
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
        'fillColor': 'transparent',  # No fill color
        'color': '#007FFF',  # Border color
        'weight': 0.5,  # Border width
        'opacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['nom', 'nb_licencies', 'nb_habitants', "pct_licencies"],
            aliases=['Commune:', 'Nb de licenciés:', 'Nb d\'habitants', 'Pourcentage de licenciés:'],
            localize=True
        )
    ).add_to(m)

    # Ajouts des marqueurs d'équipements sportifs
    for _, equipment in df_equip_f.iterrows():
    
        iframe = folium.IFrame(equipment['label_html'])
        popup = folium.Popup(iframe,
                     min_height=100,
                     min_width=500,
                     max_height=100,
                     max_width=500)
        
        color = color_mapping.get(equipment[marker_field], 'gray')

        folium.Marker(location=[equipment['equip_y'], equipment['equip_x']],
                    popup=popup,
                    icon=folium.Icon(color=color)).add_to(m)


    # Ajout d'une légende customisée (HTML)
    html_markers = get_markers_html(df_equip_f, marker_field, color_mapping)
    m = create_legend.run(m, f"Infrastructures sportives vs. Licenciés | Département {dep}", marker_type, html_markers)

    # Sauvegarde de la map au format HTML à la racine du projet
    m.save('map.html')

    return m


def get_df_for_maps(sport_list, dep, commune_code_list, entire_dep = True):
    """
    Retourne des dataframes pour la génération de cartographies
    Utilisé par m04_maps_commune

    Paramètres
    -------
    sport_list : list | Liste de sports
    dep : str | Code département à deux chiffres
    commune_code_list : list | liste de codes communes
    entire_dep : bool | True si l'utilisateur a sélectionné "Tous les départements"
    
    Retourne
    -------
    df_licencies_france : pd.Dataframe | contient les statistiques des licenciés à la maille France
    df_licencies_dep : pd.Dataframe | contient les statistiques des licenciés à la maille département
    df_licencies_par_code : pd.Dataframe | contient les statistiques des licenciés par code commune
    df_licencies_par_fed : pd.Dataframe | contient les statistiques des licenciés par fédération
    df_equip_f : pd.Dataframe | contient les informations relatives aux équipements sportifs de la zone géo sélectionnée
    cities_f : GeoJSON Dataframe
    """ 

    # Import des dataframes de départ (format Polars pour les dataframes plus complexes pour gain de performance)
    df_equip = pl.read_parquet('data/transformed/equip_es.parquet')
    df_licencies = pl.read_parquet('data/transformed/lic-data-2021_total.parquet')
    cities_geojson = gpd.read_file('data/transformed/communes_with_arr.geojson')
    df_pop = pd.read_parquet('data/transformed/population_2021.parquet')

    # Récupération des mappings Equipements Sportifs et Fédérations Sportives
    es_sports, fed_sports = get_mappings()
    fed_list = fed_sports[fed_sports['sport'].isin(sport_list)]['federation'].to_list()

    # Liste des équipements correspondant aux sports sélectionnés
    if 'Tous les sports' in sport_list:
        equip_type_list = sorted(es_sports['equip_type_name'].to_list())
    else:
        equip_type_list = es_sports[es_sports['sport'].isin(sport_list)]['equip_type_name'].to_list()

    # Filtrage du dataframe des équipements
    if entire_dep == True:
        condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("dep_code_filled") == dep)
    else:
        condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("inst_com_code").is_in(commune_code_list))

    df_equip_f = df_equip.filter(condition).to_pandas()

    ### Filtrage du dataframe des statistiques licenciés
    # Filtrage des statistiques sur la France
    df_licencies_france = df_licencies.filter(pl.col('Fédération').is_in(fed_list))
    df_licencies_france = df_licencies_france.group_by(['Fédération'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Filtrage des statistiques sur le départements
    condition = (pl.col('Fédération').is_in(fed_list)) & (pl.col("Département") == dep)
    df_licencies_dep = df_licencies.filter(condition)
    df_licencies_dep = df_licencies_dep.group_by(['Fédération'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    if entire_dep == True:
        df_licencies = df_licencies_dep
    else:
        condition = (pl.col('Fédération').is_in(fed_list)) & (pl.col("code").is_in(commune_code_list))
        df_licencies = df_licencies.filter(condition)

    # Création d'un dataframe contenant les statistiques par code commune
    df_licencies_par_code = df_licencies.group_by(['code'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Création d'un dataframe contenant les statistiques par commune et fédération
    df_licencies_par_fed = df_licencies.group_by(['Commune', 'Fédération'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Filtrage du GeoDataframe sur le département ou sur un ensemble de commune
    if entire_dep == True:
        cities_f = cities_geojson[cities_geojson['code'].str.startswith(dep)]
    else:
        cities_f = cities_geojson[cities_geojson['code'].isin(commune_code_list)]
    
    # Ajout des statistiques licenciés au GeoDataframe
    cities_f = cities_f.merge(df_licencies_par_code[['code', 'nb_licencies']], on = 'code', how = 'left')
    cities_f = cities_f.merge(df_pop[['code', 'nb_habitants']], on = 'code', how = 'left')
    cities_f['pct_licencies'] = cities_f.apply(lambda x: round(x['nb_licencies'] / x['nb_habitants'] * 100, 4) if x['nb_licencies'] > 0 else 0, axis = 1)

    cities_f['nb_licencies'] = cities_f['nb_licencies'].fillna(0)
    cities_f = cities_f.reset_index()
    cities_f['id'] = cities_f.index

    return df_licencies_france, df_licencies_dep, df_licencies_par_code, df_licencies_par_fed, df_equip_f, cities_f


def get_map_allsports(sport_list, dep, commune_list, stat):
    """
    Retourne une cartographie de type Folium affichant les équipements et statistiques relatives à une ou plusieurs communes d'un département sélectionné par l'utilisateur sur tous les sports
    Utilisé par m04_maps_commune

    Paramètres
    -------
    sport_list : str | Sport sélectionné par l'utilisateur
    dep : str | Code département à deux chiffres
    commune_list : str | Cartographie de type statistique Nombre ou Ratio
    stat : str | Type de marqueur en fonction du type d'équipement

    Retourne
    -------
    m : Folium map
    """ 

    # Import des dataframes
    df_equip = pl.read_parquet('data/transformed/equip_es.parquet')
    df_licencies = pl.read_parquet('data/transformed/lic-data-2021_total.parquet')
    cities_geojson = gpd.read_file('data/raw/communes.geojson')
    df_pop = pd.read_parquet('data/transformed/population_2021.parquet')

    # Récupération des mappings équipements sportifs et fédérations sportives
    es_sports, fed_sports = get_mappings()
    fed_list = fed_sports[fed_sports['sport'].isin(sport_list)]['federation'].to_list()
    equip_type_list = es_sports[es_sports['sport'].isin(sport_list)]['equip_type_name'].to_list()

    # Filtrage du dataframe df_equip
    condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("inst_com_code").is_in(commune_list))
    df_equip_f = df_equip.filter(condition).to_pandas()

    # Filtrage du dataframe df_licencies
    condition = (pl.col('Fédération').is_in(fed_list)) & (pl.col("code").is_in(commune_list))
    df_licencies = df_licencies.filter(condition)
    df_licencies = df_licencies.group_by(['code'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()
    df_licencies_par_fed = df_licencies.group_by(['Commune', 'Fédération'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Filtrage du Geo Dataframe & ajout des stats licenciés
    cities_f = cities_geojson[cities_geojson['code'].isin(commune_list)]
    cities_f = cities_f.merge(df_licencies[['code', 'nb_licencies']], on = 'code', how = 'left')
    cities_f = cities_f.merge(df_pop[['code', 'nb_habitants']], on = 'code', how = 'left')
    cities_f['pct_licencies'] = cities_f.apply(lambda x: round(x['nb_licencies'] / x['nb_habitants'] * 100, 2) if x['nb_licencies'] > 0 else 0, axis = 1)

    cities_f['nb_licencies'] = cities_f['nb_licencies'].fillna(0)
    cities_f = cities_f.reset_index()
    cities_f['id'] = cities_f.index

    # Conversion du GeoDataFrame en GeoJSON
    geojson_data = cities_f.to_json()

    # Création d'une map centrée sur le département
    lat, lon = get_dep_centroid(dep)
    map_center = [lat, lon] 
    m = folium.Map(location=map_center, zoom_start=9)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Création du contenu des popups
    df_equip_f = df_equip_f.dropna(subset = ['equip_x', 'equip_y'])
    df_equip_f['label_html'] = df_equip_f.apply(lambda x: f"<b>{x['inst_nom']} - {x['equip_nom']}</b><br/> \
                                {x['equip_type_famille']} > {x['equip_type_name']} <br/> \
                                {x['inst_adresse']} {x['inst_cp']} {x['inst_com_nom']} <br/> \
                                {'En activité : Oui' if x['inst_actif'] else 'En activité : Non'}", axis = 1)
                                   
    if stat == 'Nombre de licenciés':
        heatmap_field = 'nb_licencies'
        
    else:
        heatmap_field = 'pct_licencies'

    color_mapping = get_colors_mapping()

    # Ajout de la couche choropleth (heatmap)
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=cities_f,
        columns=['id', heatmap_field],
        key_on='feature.properties.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.1,
        line_weight=0.5,
        legend_name=heatmap_field
    ).add_to(m)

    # Ajout des tooltips
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
        'fillColor': 'transparent',  # No fill color
        'color': '#007FFF',  # Border color
        'weight': 0.5,  # Border width
        'opacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['nom', 'nb_licencies', 'nb_habitants', "pct_licencies"],
            aliases=['Commune:', 'Nb de licenciés:', 'Nb d\'habitants', 'Pourcentage de licenciés:'],
            localize=True
        )
    ).add_to(m)

    # Ajout des équipements sportifs à la cartographie
    for _, equipment in df_equip_f.iterrows():
    
        iframe = folium.IFrame(equipment['label_html'])
        popup = folium.Popup(iframe,
                     min_height=100,
                     min_width=500,
                     max_height=100,
                     max_width=500)
        
        equipment_type = equipment['equip_type_name']
        color = color_mapping.get(equipment_type, 'black')
        folium.Marker(location=[equipment['equip_y'], equipment['equip_x']],
                    popup=popup,
                    icon=folium.Icon(color=color)).add_to(m)
        
    # Sauvegarde de la map au format HTML
    m.save('map.html')

    return m, df_licencies_par_fed
