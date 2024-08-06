import pandas as pd
import polars as pl
import geopandas as gpd
import folium
from folium import plugins
import geopandas as gpd
from src.functions.functions import get_mappings, get_colors_mapping, get_dep_centroid, get_column_mapping, pivot_lic_df


def display_france_map(fed, stat, qpv):

    # Load GeoJSON file & dataframe
    dep_geojson = gpd.read_file('data/raw/departements.geojson')
    df = pivot_lic_df()
    df = df[df['Fédération'] == fed]

    # Create a map centered on France
    map_center = [46.494739, 2.602833] 
    m = folium.Map(location=map_center, zoom_start=6)
    folium.TileLayer('cartodbpositron').add_to(m)

    df_all_zones = df[df['QPV_or_not'] == False]
    df_qpv = df[df['QPV_or_not'] == True]

    if qpv == True:
        dep_f = dep_geojson.merge(df_qpv[['code', 'nb_licencies_F', 'nb_licencies_H', 'pct_licencies_F', 'pct_licencies_H', 'nb_licencies']], on = 'code', how = 'left')
    else:
        dep_f = dep_geojson.merge(df_all_zones[['code', 'nb_licencies_F', 'nb_licencies_H', 'pct_licencies_F', 'pct_licencies_H', 'nb_licencies']], on = 'code', how = 'left')

    dep_f = dep_f.reset_index()
    dep_f['id'] = dep_f.index

    # Convert the GeoDataFrame to a GeoJSON
    geojson_data = dep_f.to_json()

    col_to_display = get_column_mapping()

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

    # Add tooltips
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
        'fillColor': 'transparent',  # No fill color
        'color': '#007FFF',  # Border color
        'weight': 0.5,  # Border width
        'opacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['nom', 'nb_licencies', 'nb_licencies_F', 'pct_licencies_F', 'nb_licencies_H', 'pct_licencies_H'],
            aliases=['Commune:', "Nombre total de licenciés", "Nombre de femmes licenciées", "Pourcentage de femmes licenciées", "Nombre d'hommes licenciés", "Pourcentage d'hommes licenciés"],
            localize=True
        )
    ).add_to(m)


    # Display the map
    # Activer le bouton fullscreen sur Folium
    plugins.Fullscreen().add_to(m)
    return(m)

def get_a_map(dep, map_type, df_equip_f, cities_f):

    # Convert the GeoDataFrame to a GeoJSON
    geojson_data = cities_f.to_json()

    # Create a map centered on the department
    lat, lon = get_dep_centroid(dep)
    map_center = [lat, lon] 
    m = folium.Map(location=map_center, zoom_start=9)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Create popup content for map markers
    df_equip_f = df_equip_f.dropna(subset = ['equip_x', 'equip_y'])
    df_equip_f['label_html'] = df_equip_f.apply(lambda x: f"<b>{x['inst_nom']} - {x['equip_nom']}</b><br/> \
                                {x['equip_type_famille']} > {x['equip_type_name']} <br/> \
                                {x['inst_adresse']} {x['inst_cp']} {x['inst_com_nom']} <br/> \
                                {'En activité : Oui' if x['inst_actif'] else 'En activité : Non'}", axis = 1)
                                   
    # Add the choropleth layer

    if map_type == 'Nombre de licenciés':
        heatmap_field = 'nb_licencies'
        
    else:
        heatmap_field = 'pct_licencies'

    color_mapping = get_colors_mapping()

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

    # Add GeoJson with tooltips
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

    # Add sportive equipment markers to the map
    for _, equipment in df_equip_f.iterrows():
    
        iframe = folium.IFrame(equipment['label_html'])
        popup = folium.Popup(iframe,
                     min_height=100,
                     min_width=500,
                     max_height=100,
                     max_width=500)
        
        equipment_type = equipment['equip_type_name']
        color = color_mapping.get(equipment_type, 'black')
        print(color)
        folium.Marker(location=[equipment['equip_y'], equipment['equip_x']],
                    popup=popup,
                    icon=folium.Icon(color=color)).add_to(m)
        
    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    m.save('map.html')

    return m


def get_df_for_maps(sport_list, dep, commune_list, entire_dep = True):

    # Import dataframes
    df_equip = pl.read_parquet('data/transformed/equip_es.parquet')
    df_licencies = pl.read_parquet('data/transformed/lic-data-2021_total.parquet')
    cities_geojson = gpd.read_file('data/raw/communes.geojson')
    df_pop = pd.read_parquet('data/transformed/population_2021.parquet')

    # Get mappings
    es_sports, fed_sports = get_mappings()
    fed_list = fed_sports[fed_sports['sport'].isin(sport_list)]['federation'].to_list()
    equip_type_list = es_sports[es_sports['sport'].isin(sport_list)]['equip_type_name'].to_list()

    # Filter dataframe df_equip using Polars
    if entire_dep == True:
        condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("dep_code_filled") == dep)
    else:
        condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("inst_com_code").is_in(commune_list))

    df_equip_f = df_equip.filter(condition).to_pandas()

    # Filter dataframe df_licencies using Polars
    if entire_dep == True:
        condition = (pl.col('Fédération').is_in(fed_list)) & (pl.col("Département") == dep)
    else:
        condition = (pl.col('Fédération').is_in(fed_list)) & (pl.col("code").is_in(commune_list))

    df_licencies = df_licencies.filter(condition)
    df_licencies_par_code = df_licencies.group_by(['code'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()
    df_licencies_par_fed = df_licencies.group_by(['Commune', 'Fédération'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Filter Geo Dataframe & Add nb_licencies
    if entire_dep == True:
        cities_f = cities_geojson[cities_geojson['code'].str.startswith(dep)]
    else:
        cities_f = cities_geojson[cities_geojson['code'].isin(commune_list)]
    
    cities_f = cities_f.merge(df_licencies_par_code[['code', 'nb_licencies']], on = 'code', how = 'left')
    cities_f = cities_f.merge(df_pop[['code', 'nb_habitants']], on = 'code', how = 'left')
    cities_f['pct_licencies'] = cities_f.apply(lambda x: round(x['nb_licencies'] / x['nb_habitants'] * 100, 4) if x['nb_licencies'] > 0 else 0, axis = 1)

    cities_f['nb_licencies'] = cities_f['nb_licencies'].fillna(0)
    cities_f = cities_f.reset_index()
    cities_f['id'] = cities_f.index


    return df_licencies_par_code, df_licencies_par_fed, df_equip_f, cities_f


def get_map(sport, dep, map_type):

    # Import dataframes
    df_equip = pl.read_parquet('data/transformed/equip_es.parquet')
    df_licencies = pl.read_parquet('data/transformed/lic-data-2021_total.parquet')
    cities_geojson = gpd.read_file('data/raw/communes.geojson')
    df_pop = pd.read_parquet('data/transformed/population_2021.parquet')

    # Get mappings
    es_sports, fed_sports = get_mappings()
    fed_list = fed_sports[fed_sports['sport'] == sport]['federation'].to_list()
    equip_type_list = es_sports[es_sports['sport'] == sport]['equip_type_name'].to_list()

    # Filter dataframe df_equip using Polars
    condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("dep_code_filled") == dep)
    df_equip_f = df_equip.filter(condition).to_pandas()

    # Filter dataframe df_licencies using Polars
    df_licencies = df_licencies.filter(pl.col('Fédération').is_in(fed_list))
    df_licencies = df_licencies.group_by(['code'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Filter Geo Dataframe & Add nb_licencies
    cities_f = cities_geojson[cities_geojson['code'].str.startswith(dep)]
    cities_f = cities_f.merge(df_licencies[['code', 'nb_licencies']], on = 'code', how = 'left')
    cities_f = cities_f.merge(df_pop[['code', 'nb_habitants']], on = 'code', how = 'left')
    cities_f['pct_licencies'] = cities_f.apply(lambda x: round(x['nb_licencies'] / x['nb_habitants'] * 100, 4) if x['nb_licencies'] > 0 else 0, axis = 1)

    cities_f['nb_licencies'] = cities_f['nb_licencies'].fillna(0)
    cities_f = cities_f.reset_index()
    cities_f['id'] = cities_f.index

    # Convert the GeoDataFrame to a GeoJSON
    geojson_data = cities_f.to_json()

    # Create a map centered on the department
    lat, lon = get_dep_centroid(dep)
    map_center = [lat, lon] 
    m = folium.Map(location=map_center, zoom_start=9)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Create popup content for map markers
    df_equip_f = df_equip_f.dropna(subset = ['equip_x', 'equip_y'])
    df_equip_f['label_html'] = df_equip_f.apply(lambda x: f"<b>{x['inst_nom']} - {x['equip_nom']}</b><br/> \
                                {x['equip_type_famille']} > {x['equip_type_name']} <br/> \
                                {x['inst_adresse']} {x['inst_cp']} {x['inst_com_nom']} <br/> \
                                {'En activité : Oui' if x['inst_actif'] else 'En activité : Non'}", axis = 1)
                                   


    # Add the choropleth layer

    if map_type == 'Nombre de licenciés':
        heatmap_field = 'nb_licencies'
        
    else:
        heatmap_field = 'pct_licencies'

    color_mapping = get_colors_mapping()

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

    # Add GeoJson with tooltips
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

    # Add sportive equipment markers to the map
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
        
    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    m.save('map.html')

    return m



def get_map_allsports(sport_list, dep, commune_list, stat):

    # Import dataframes
    df_equip = pl.read_parquet('data/transformed/equip_es.parquet')
    df_licencies = pl.read_parquet('data/transformed/lic-data-2021_total.parquet')
    cities_geojson = gpd.read_file('data/raw/communes.geojson')
    df_pop = pd.read_parquet('data/transformed/population_2021.parquet')

    # Get mappings
    es_sports, fed_sports = get_mappings()
    fed_list = fed_sports[fed_sports['sport'].isin(sport_list)]['federation'].to_list()
    equip_type_list = es_sports[es_sports['sport'].isin(sport_list)]['equip_type_name'].to_list()

    # Filter dataframe df_equip using Polars
    condition = (pl.col("equip_type_name").is_in(equip_type_list)) & (pl.col("inst_com_code").is_in(commune_list))
    df_equip_f = df_equip.filter(condition).to_pandas()

    # Filter dataframe df_licencies using Polars
    condition = (pl.col('Fédération').is_in(fed_list)) & (pl.col("code").is_in(commune_list))
    df_licencies = df_licencies.filter(condition)
    df_licencies = df_licencies.group_by(['code'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()
    df_licencies_par_fed = df_licencies.group_by(['Commune', 'Fédération'], maintain_order=True).agg(pl.sum("nb_licencies")).to_pandas()

    # Filter Geo Dataframe & Add nb_licencies
    cities_f = cities_geojson[cities_geojson['code'].isin(commune_list)]
    cities_f = cities_f.merge(df_licencies[['code', 'nb_licencies']], on = 'code', how = 'left')
    cities_f = cities_f.merge(df_pop[['code', 'nb_habitants']], on = 'code', how = 'left')
    cities_f['pct_licencies'] = cities_f.apply(lambda x: round(x['nb_licencies'] / x['nb_habitants'] * 100, 2) if x['nb_licencies'] > 0 else 0, axis = 1)

    cities_f['nb_licencies'] = cities_f['nb_licencies'].fillna(0)
    cities_f = cities_f.reset_index()
    cities_f['id'] = cities_f.index

    # Convert the GeoDataFrame to a GeoJSON
    geojson_data = cities_f.to_json()

    # Create a map centered on the department
    lat, lon = get_dep_centroid(dep)
    map_center = [lat, lon] 
    m = folium.Map(location=map_center, zoom_start=9)
    folium.TileLayer('cartodbpositron').add_to(m)

    # Create popup content for map markers
    df_equip_f = df_equip_f.dropna(subset = ['equip_x', 'equip_y'])
    df_equip_f['label_html'] = df_equip_f.apply(lambda x: f"<b>{x['inst_nom']} - {x['equip_nom']}</b><br/> \
                                {x['equip_type_famille']} > {x['equip_type_name']} <br/> \
                                {x['inst_adresse']} {x['inst_cp']} {x['inst_com_nom']} <br/> \
                                {'En activité : Oui' if x['inst_actif'] else 'En activité : Non'}", axis = 1)
                                   


    # Add the choropleth layer

    if stat == 'Nombre de licenciés':
        heatmap_field = 'nb_licencies'
        
    else:
        heatmap_field = 'pct_licencies'

    color_mapping = get_colors_mapping()

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

    # Add GeoJson with tooltips
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

    # Add sportive equipment markers to the map
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
        
    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    m.save('map.html')

    return m, df_licencies_par_fed
