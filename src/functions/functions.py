import pandas as pd
import polars as pl
import plotly.express as px

def transform_licencies_for_map(df_licencies, fed_list, dep):
    licencies_f = df_licencies[(df_licencies['Fédération'].isin(fed_list)) & (df_licencies['Département'] == int(dep))]
    licencies_f = licencies_f[['Code Commune', 'Commune', 'Total']]
    licencies_f = licencies_f.rename(columns = {'Code Commune': 'code', 'Commune': 'commune', 'Total': 'nb_licencies'})
    licencies_f = licencies_f.groupby(['code', 'commune'])['nb_licencies'].sum().reset_index()

    return licencies_f

def transform_licencies_for_graph(fed_sports, sport, dep):

    df_agg = pl.read_parquet('data/transformed/lic-data-2021_details_agg.parquet')
    fed_list = fed_sports[fed_sports['sport'] == sport]['federation'].to_list()

    condition = (pl.col("Département") == dep) & (pl.col("Fédération").is_in(fed_list)) & (pl.col("QPV_or_not") == False)

    df_agg_licencies = df_agg.filter(condition)
    df_agg_licencies = df_agg_licencies.group_by(['age', 'sexe'], maintain_order=True).agg(pl.sum("value")).to_pandas()

    return df_agg_licencies

def display_licencies_plotline(df, sport, dep):

    fig = px.line(df, x="age", y="value", color='sexe', 
                  color_discrete_map={
                      "H": "blue",
                      "F": "goldenrod"
                      })

    fig.update_layout(
        title = f"Nb licenciés H/F {sport} - Département {dep}"
    )

    return fig 

def display_licencies_barh(df):

    df = df.sort_values(by = 'nb_licencies')
    fig = px.bar(df, y="Fédération", x="nb_licencies", orientation='h', color='Commune', width=800, height=800)
    fig.update_xaxes(automargin=True)

    fig.update_layout(
        title = f"Nb total de licenciés par fédération dans les communes sélectionnées"
    )

    return fig 

def get_mappings():
    es_sports = pd.read_json('data/transformed/mapping_es_sports.json', orient='index')
    es_sports = es_sports.reset_index().rename(columns = {'index': 'equip_type_name', 0: 'sport'})

    fed_sports = pd.read_json('data/transformed/mapping_fed_sports.json', orient='index')
    fed_sports = fed_sports.reset_index().rename(columns = {'index': 'federation', 0: 'sport'})

    return es_sports, fed_sports

def get_dep_list(include_all):
    
    dep_options = ["0" + str(i+1) if len(str(i+1)) == 1 else str(i+1) for i in range(95)]
    dep_options = [x for x in dep_options if x != '20'] + ['2A', '2B']

    if include_all:
        dep_options = ['Tous les départements'] + dep_options

    return dep_options

def get_commune_list(dep):
    
    df = pd.read_csv('data/transformed/mapping_dep_communes.csv')
    df = df[df['dep'] == dep]
    df = df.dropna()
    return df

def get_dep_centroid(dep):
    df = pd.read_csv('data/transformed/dep_centroids.csv')
    lat = df[df['code'] == dep]['latitude'].values[0]
    lon = df[df['code'] == dep]['longitude'].values[0]
    return lat, lon

def get_column_mapping():
    col_to_display = {"Nombre total de licenciés": "nb_licencies",
                      "Nombre de femmes licenciées": "nb_licencies_F",
                      "Pourcentage de femmes licenciées": "pct_licencies_F",
                      "Nombre d'hommes licenciés": "nb_licencies_H",
                      "Pourcentage d'hommes licenciés": "pct_licencies_H"
                      }

    return(col_to_display)

def get_colors_mapping():
    
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

    return(color_mapping)

def pivot_lic_df():
    # Load dataframe
    df = pd.read_parquet('data/transformed/lic-data-2021_details_agg_hf.parquet')

    # Pivot dataframe containing nb licencies by Département, Fédération & QPV
    df = df.pivot_table(index=['Département', 'Fédération', 'QPV_or_not'],
                    columns='sexe',
                    values='value').reset_index()

    df = df.rename(columns = {'Département': 'code', 'F': 'nb_licencies_F', 'H': 'nb_licencies_H'})

    df['nb_licencies'] = df['nb_licencies_F'] + df['nb_licencies_H']
    df['pct_licencies_F'] = round((df['nb_licencies_F'] / df['nb_licencies'] * 100), 2)
    df['pct_licencies_H'] = round((df['nb_licencies_H'] / df['nb_licencies'] * 100), 2)

    return df

def display_barh(stat, dep, qpv):

    # Load dataframe
    df = pivot_lic_df()

    if dep == 'Tous les départements':
        df = df.groupby(['Fédération', 'QPV_or_not']).sum().reset_index()
        df['pct_licencies_F'] = round((df['nb_licencies_F'] / df['nb_licencies'] * 100), 2)
        df['pct_licencies_H'] = round((df['nb_licencies_H'] / df['nb_licencies'] * 100), 2)
    else:
        df = df[df['code'] == dep]

    if qpv == True:
        df = df[df['QPV_or_not'] == True]
    else:
        df = df[df['QPV_or_not'] == False]

    col_to_display = get_column_mapping()

    df = df.sort_values(by = col_to_display[stat], ascending = True)

    fig = px.bar(df, y="Fédération", x=col_to_display[stat], orientation='h', width=800, height=3500, text_auto=True)
    fig.update_xaxes(automargin=True)

    return(fig)

#### Fonctions one-shot pour transformer données brut en cas d'update de fichiers

def transform_dep_code_commune():
    df = pd.read_csv('data/raw/lic-data-2021.csv', delimiter=';', dtype = {'Code Commune': str, 'Département': str})
    df = df[['Code Commune', 'Commune', 'Département']]
    df = df.drop_duplicates().reset_index().rename(columns = {'Code Commune': 'code_commune', 'Commune': 'commune', 'Département': 'dep'})
    df.to_csv('data/transformed/mapping_dep_communes.csv')

def transform_pop_df():
    pop = pd.read_csv('data/raw/base-cc-evol-struct-pop-2021.csv', delimiter = ';', dtype = {'CODGEO': str})
    pop = pop[['CODGEO', 'P21_POP']]
    pop = pop.rename({'CODGEO': 'code', 'P21_POP': 'nb_habitants'})
    pop.to_parquet('../data/transformed/population_2021.parquet')


def transform_licencies_df():
    df = pd.read_csv('data/raw/lic-data-2021.csv', delimiter = ';', dtype = {'Code Commune': str, 'Département': str})
    
    df['QPV_or_not'] = df['Nom QPV'].fillna('0')
    df['QPV_or_not'] = df['QPV_or_not'].apply(lambda x: True if x != '0' else False)
    
    # Calcul du dataframe Total nb licencies
    df_total = df[df['QPV_or_not'] == False][['Code Commune', 'Commune', 'Département', 'Région', 'Fédération', 'F - NR', 'H - NR', 'NR - NR', 'Total']]
    df_total = df_total.rename(columns = {'Code Commune': 'code', 'Total': 'nb_licencies'})
    df_total.to_parquet('data/transformed/lic-data-2021_total.parquet')

    # Calcul du dataframe Nb licenciés par Sexe et Âge
    df = df.drop(columns = {'F - NR', 'H - NR', 'NR - NR', 'Total'})
    df = pd.melt(df, id_vars = ['Code Commune', 'Commune', 'Code QPV', 'Nom QPV', 'QPV_or_not', 'Département', 'Région', 'Statut géo', 'Code', 'Fédération'], var_name='category', value_name='value')
    df['sexe'] = df['category'].apply(lambda x: x[0])
    df['age'] = df['category'].apply(lambda x: x.split(' - ')[1])
    df['age'] = df['age'].str.replace('1 à 4 ans', '01 à 04 ans').replace('5 à 9 ans', '05 à 09 ans')
    df.to_parquet('data/transformed/lic-data-2021_details.parquet')

    # Calcul du dataframe Nb licenciés par Fédération et Département
    df_agg = df.groupby(['Fédération', 'Département', 'QPV_or_not', 'sexe', 'age'])['value'].sum().reset_index()
    df_agg.to_parquet('data/transformed/lic-data-2021_details_agg.parquet')

    # Calcul du dataframe Nb licenciés par Fédération et Département en fonction du sexe
    df_agg = df_agg.groupby(['Département', 'Fédération', 'QPV_or_not', 'sexe'])['value'].sum().reset_index()
    df_agg.to_parquet('../data/transformed/lic-data-2021_details_agg_hf.parquet')


def transform_equip_sportif_df():
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
    
    df = df[['inst_nom', 
         'inst_adresse',
         'inst_cp',
         'inst_com_code',
         'inst_com_nom',
         'inst_actif',
         'inst_etat',
         'inst_date_creation',
         'inst_date_etat',
         'inst_date_valid',
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
         'equip_aps_code',
         'equip_aps_nom',
         'epci_nom',
         'dep_code',
         'dep_code_filled',
         'dens_niveau',
         'dens_lib']]

    df.to_parquet('data/transformed/equip_es.parquet')