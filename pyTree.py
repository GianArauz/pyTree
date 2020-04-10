# %% LOADING PACKAGES =========================================================
# =============================================================================

# Importing supporting packages
import os

# Importing main packages
import pandas as pd

# Importing Bokeh packages
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import TextInput
from bokeh.layouts import column
from bokeh.tile_providers import CARTODBPOSITRON, get_provider

# Importing geo conversion
from pyproj import Proj, transform

# %% IMPORTING DATA ===========================================================
# =============================================================================

# Importing data
# df = pd.read_csv('arbrat_viari.csv')
df = pd.read_csv('2020_1T_arbrat_viari.csv')

# Selecting only those columns we need
col_list = ['LONGITUD_WGS84', 'LATITUD_WGS84', 'ADRECA', 'NOM_CIENTIFIC',
            'X_ETRS89', 'Y_ETRS89']
df = df[col_list].copy()
del col_list

# %% GETTING GEO MAP ==========================================================
# =============================================================================

# Initiating tile provider from CARTODBPOSITRON
tile_provider = get_provider(CARTODBPOSITRON)




lon_arr = df['LONGITUD_WGS84'].to_numpy()
lat_arr = df['LATITUD_WGS84'].to_numpy()
cosa = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), lon_arr, lat_arr)

df['x'] = cosa[0]
df['y'] = cosa[1]

  # longitude first, latitude second.
# output (meters east of 0, meters north of 0): (-14314.651244750548, 6711665.883938471)


del lon_arr, lat_arr, cosa

# %% PREPARING TOOLTIP LIST OF TUPLES =========================================
# =============================================================================

# Preparing the tooltips as a list of tuples
tooltips_list = [
                 ('Adress', '@{ADRECA}'),
                 ('Scientific name', '@{NOM_CIENTIFIC}'),
                 ]

# %% INITIATING COLUMN DATA SOURCE ============================================
# =============================================================================

# Initiating Column Data Source
cds = ColumnDataSource(df)

# %% INITIATING BOKEH APP =====================================================
# =============================================================================

# Cleaning current document to avoid app concatenation within the *.html file
curdoc().clear()

# Creating a hover tool legend
ht = HoverTool(tooltips=tooltips_list)

# %% PREPARING BOKEH FIGURES  =================================================
# =============================================================================

# Initiating Bokeh figure
fig = figure(
             x_axis_label='LONGITUDE',
             y_axis_label='LATITUDE',
             tools='pan,box_zoom,wheel_zoom,reset,save',
             # plot_width=1250, plot_height=400,
             title='Tree localization in Barcelona',
             x_axis_type='mercator',
             y_axis_type='mercator',
             )

# Adding the hover legend tool to the Bokeh figure
fig.add_tools(ht)

# Adding geo map tile to the Bokeh figure
fig.add_tile(tile_provider)

# Adding circle gliph to the Bokeh figure
fig.circle(
           x='x',
           y='y',
           source=cds,
           color='darkgreen',
           alpha=0.5,
           )

# %% INITIATING BOKEH WIDGETS =================================================
# =============================================================================

# Creating widgets: prot_ti_widget and gene_ti_widget
ti_wg = TextInput(
                  title='Scientific name search:',
                  value=None,
                  # width=904
                  )

# %% INITIATING BOKEH CALLBACKS ===============================================
# =============================================================================


# Defining callback for the Text Input widget
def ti_callback(attr, old, new):
    '''TODO'''

    # Getting the text input species as provided by the user
    species = ti_wg.value

    # Masking DataFrame with the species provided by the user
    μ = df['NOM_CIENTIFIC'].str.contains(species)

    # Getting the number of filtered-in trees of the given species
    trees = sum(μ)

    # Filtering both DataFrames and creating the CDSs in this callback
    cb_cds = ColumnDataSource(df[μ].copy())

    # Updating old CDSs data with new CDSs data
    cds.data.update(cb_cds.data)

    # Creating title with the number filtered-in trees of the given species
    fig.title.text = f'There are {trees} {species} in Barcelona.'


# %% ATTACHING BOKEH CALLBACKS ================================================
# =============================================================================

# Attaching the Text Input widget to the Text Input callback
ti_wg.on_change('value', ti_callback)

# %% CREATING BOKEH LAYOUT ====================================================
# =============================================================================

# Creating a layout combining the slider and the figure
layout = column(ti_wg, fig)

# Adding the layout to the current document
curdoc().add_root(layout)

# Defining a title for our current document
curdoc().title = 'pyTree dashboard'

# %% INVOKING BOKEH SERVER ====================================================
# =============================================================================

# To run this current document, we muts call 'bokeh serve --show myapp.py'
# using the cmd from the same folder where SAINTpy_Bokeh.py is located.

# Invoking server
os.system('bokeh serve --show pyTree.py')