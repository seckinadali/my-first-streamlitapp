import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy


@st.cache_data
def load_data(path, file1, file2):
    # index_col=0 for volcano df
    volcano_df = pd.read_csv(path + file1, index_col=0)
    with open(path + file2) as f:
        volcano_geojson = json.load(f)
    return volcano_df, volcano_geojson

volcano_df_raw, volcano_geojson_raw = load_data(
    path="data/",
    file1="volcano_ds_pop.csv",
    file2="countries.geojson"
)

volcano_df = deepcopy(volcano_df_raw)
volcano_geojson = deepcopy(volcano_geojson_raw)


st.title("Volcanoes of the World")


# Show df
st.header("Data exploration")

if st.checkbox("Show dataframe"):
    st.subheader("The Volcanoes Dataset:")
    st.dataframe(data=volcano_df)


# Distributions
st.subheader("Distributions:")
left_col, middle_col, right_col = st.columns([2, 1, 1])

vars = ['Type', 'Status', 'Elev']
var = left_col.selectbox('Choose variable', vars)

color_choice = middle_col.color_picker(label='Choose a color')

plot_types = ['Plotly', 'Seaborn']
plot_type = right_col.radio('Choose plot type', plot_types)



# Seaborn
s_fig, ax = plt.subplots(figsize=(10, 8))
if var == 'Elev':
    sns.histplot(volcano_df[var])
    ax.set_title('Frequency of Elevation',
                 color=color_choice)
else:
    sns.countplot(volcano_df[var],
                  color=color_choice)
    ax.set_title(f"Frequency of {var}")

# Plotly
p_fig = px.histogram(volcano_df, var,
                     title=f"Frequency of {var}",
                     color_discrete_sequence=[color_choice])

if plot_type == 'Seaborn':
    st.pyplot(s_fig)
else:
    st.plotly_chart(p_fig)



# Other plots
plots = [
    "Volcanoes of the World by Elevation",
    "Volcanoes of the World by Type",
    "Volcanoes of the World by Status",
    "Volcanoes' Elevation by Type and Status",
    "Number of Volcanoes by Country"
]

plot_choice = st.selectbox('Choose plot:', plots)

if plot_choice == plots[0]:
    fig = px.scatter_geo(
        volcano_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='Volcano Name',
        hover_data=['Elev', 'Type', 'Status'],
        color='Elev',
        color_continuous_scale='Portland',
        title='Volcanoes of the World by Elevation'
    )

    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="GhostWhite"
        )
    )

    st.plotly_chart(fig)


elif plot_choice == plots[1]:
    fig = px.scatter_geo(
        volcano_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='Volcano Name',
        hover_data=['Elev', 'Type', 'Status'],
        color='Type',
        title='Volcanoes of the World by Type'
    )

    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="GhostWhite"
        )
    )

    st.plotly_chart(fig)

elif plot_choice == plots[2]:
    fig = px.scatter_geo(
        volcano_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='Volcano Name',
        hover_data=['Elev', 'Type', 'Status'],
        color='Status',
        title='Volcanoes of the World by Status'
    )

    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="GhostWhite"
        )
    )

    st.plotly_chart(fig)

elif plot_choice == plots[3]:
    def min_max(t, upper_bd=100):
        t_min, t_max = min(t), max(t)
        factor = (upper_bd - 0) / (t_max - t_min)
        return [(el - t_min) * factor for el in t]


    fig = px.scatter(
        volcano_df,
        x='Type', y='Status',
        hover_name='Volcano Name',
        hover_data=['Type', 'Status', 'Elev'],
        color='Elev',
        color_continuous_scale='Portland',
        range_color=[min(volcano_df['Elev']), max(volcano_df['Elev'])],
        size=min_max(volcano_df['Elev']),
        title="Volcanoes' Elevation by Type and Status"
    )

    st.plotly_chart(fig)

else:
    country_data = volcano_df.groupby('Country').agg(
        num_volcanoes=('Volcano Name', 'count'),
        mean_elevation=('Elev', 'mean'),
        population=('Population (2020)', 'last')
    ).reset_index()

    fig = px.choropleth(
        country_data,
        locations='Country',
        locationmode='country names',  # Ensure your 'Region' values match country names or ISO country codes
        color='num_volcanoes',
        color_continuous_scale='OrRd',
        hover_name='Country',
        hover_data=['num_volcanoes', 'mean_elevation', 'population'],
        title="Number of Volcanoes by Country"
    )

    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="GhostWhite"
        )
    )

    st.plotly_chart(fig)