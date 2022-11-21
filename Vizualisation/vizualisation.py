# Imports
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
from shapely.geometry import MultiPolygon

sys.path.append('/Users/rayanedonni/Documents/Projets_persos/News_by_ai')
#from sentiment_analysis.tools import COUNTRIES

sys.path.remove('/Users/rayanedonni/Documents/Projets_persos/News_by_ai')
import json


def generate_map(
    negativity_score_by_countries, 
    output_path,
    shapefile_path='/Users/rayanedonni/Downloads/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp',
    ):
    
    gdf = gpd.read_file(shapefile_path)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country', 'country_code', 'geometry']     
    gdf = customize_shapefile(gdf)
    
    # Remove unused countries
    gdf.drop([row for row in range(len(gdf)) if gdf.loc[row, 'country'] not in negativity_score_by_countries.keys()],
             axis = 0,
             inplace = True)
    gdf.index = [i for i in range(len(gdf))]
         
    # Merge the two dataframes
    neg_scores = [negativity_score_by_countries[gdf.loc[row,'country']] for row in gdf.index]

    gdf["score"] = pd.DataFrame(data = neg_scores)
    gdf = gdf.set_index("country")

    fig = px.choropleth(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        #marker_line_color='white',
        projection='mercator',
        color_continuous_scale='rdylgn',
        color="score",
        width=3200, height=1600
        )
    
    fig.update_geos(fitbounds="locations", visible=False)
        
    fig.update_layout(
        title_text='Twitter sentiment map <br>18-11-2022',
        coloraxis_showscale=False,
        title={
            "yref": "paper",
            "y" : 1,
            "yanchor" : "bottom"   
            }
        )
    
    fig.write_image(output_path)
    fig.show()


def reduce_by_length(polygon_shape, nb_polygon_to_keep):
    polygons_in_shape = list(polygon_shape)
    
    if len(polygons_in_shape) <= nb_polygon_to_keep:
        return polygon_shape
    else :
        polygons_length = [polygon.length for polygon in polygons_in_shape]
        polygons_indices_to_keep = arg_of_n_max(polygons_length, nb_polygon_to_keep)
        print("polygons_indices_to_keep =", polygons_indices_to_keep)
        
        if nb_polygon_to_keep==1:
            return polygons_in_shape[polygons_indices_to_keep[0]]
        else :
            reduced_polygon = MultiPolygon([polygons_in_shape[i] for i in polygons_indices_to_keep])
            return reduced_polygon
        
     
def arg_of_n_max(lst, n):
    ind = np.argpartition(lst, -n)[-n:]
    return ind

def customize_shapefile(gdf):
    gdf.at[43, 'geometry']=reduce_by_length(gdf.at[43, 'geometry'], 1)
    gdf.at[18, 'geometry']=reduce_by_length(gdf.at[18, 'geometry'], 2)
    
    return gdf
