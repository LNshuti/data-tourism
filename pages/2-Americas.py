import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import datashader as ds
import colorcet
import duckdb

# Initialize Streamlit app
st.title("Population Density Across Latin America")

# List of Latin American countries' ISO codes
countries_iso = ["SLV", "COL", "ECU", "VEN", "PER", "BOL", "ARG", "CHL", "URY", "PRY"]

# Database connection and data retrieval
@st.cache_data(ttl=3600)
def load_data(countries_iso):
    con = duckdb.connect()
    con.sql("""
        install spatial;
        load spatial;
        install httpfs;
        load httpfs;
        set s3_region='us-west-2';
    """)
    
    # Query for each country and combine into a single DataFrame
    dfs = []
    for iso in countries_iso:
        df = con.sql(f"""
            SELECT
                ST_X(ST_Centroid(ST_GeomFromWKB(geometry))) AS longitude,
                ST_Y(ST_Centroid(ST_GeomFromWKB(geometry))) AS latitude
            FROM read_parquet('s3://us-west-2.opendata.source.coop/vida/google-microsoft-open-buildings/geoparquet/by_country/country_iso={iso}/{iso}.parquet');
        """).df()
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

df = load_data(countries_iso)

# Create a Datashader canvas and aggregate points
@st.cache_data
def create_image(df):
    cvs = ds.Canvas(plot_width=690, plot_height=800)
    agg = cvs.points(df, 'longitude', 'latitude')
    img = ds.tf.shade(agg, cmap=colorcet.fire, how='log')
    return img

img = create_image(df)

# Convert the Datashader image to a NumPy array and display it
fire_cmap = LinearSegmentedColormap.from_list("fire", colorcet.fire)
img_np = np.array(img.to_pil())

fig, ax = plt.subplots(figsize=(6.9, 8), facecolor='black')
ax.imshow(img_np, cmap=fire_cmap)
ax.axis('off')
plt.tight_layout()

# Show the plot in Streamlit
st.pyplot(fig)
