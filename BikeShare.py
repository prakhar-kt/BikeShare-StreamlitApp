import streamlit as st
import pandas as pd
import numpy as np
import boto3
import altair as alt
import json
import requests
import random
import os



'''
# $~~~~~$ BikeShare Ride Analysis App 
This is a very simple app that allows to see some visualisations about a BikeShare Company operating in Chicago , which showcase how the 
members and non-members differ in their riding patterns.
'''

#https://towardsdatascience.com/reading-and-writing-files-from-to-amazon-s3-with-pandas-ccaf90bfe86c

# store the AWS access keys from the secrets file into variables
ACCESS_KEY = st.secrets['AWS_ACCESS_KEY_ID']
SECRET_KEY = st.secrets['AWS_SECRET_ACCESS_KEY']

# use boto3 to connect to S3.
client = boto3.client('s3', aws_access_key_id=ACCESS_KEY , aws_secret_access_key=SECRET_KEY)
response = client.get_object(
    Bucket = 'my-streamlit-app-bucket',
    Key = 'cleaned_df_sample.csv'
)

# function to load data into a pandas dataframe and apply some trasnformations that will be required later.
@st.cache(allow_output_mutation=True)
def load_data():
    
    df = pd.read_csv(response.get('Body'))
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis='columns', inplace=True)
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['ended_at'] = pd.to_datetime(df['ended_at'])
    df.rename(columns={"start_lat":"lat","start_lng":"lon"},inplace=True)

    return df

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load  data into the dataframe.
df = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

# if checkbox is selected, display data 
if st.checkbox('Show dataframe'):
    st.write(df)



'''
### $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ Location Map 
This map shows the locations from where the rides were started with different markers for members and non-members

'''
# def download_json():
#     '''Downloads ANC JSON from Open Data DC'''
#     url = './Chicago.geojson'
#     resp = requests.get(url)
#     return resp.json
chicago_geojson = json.load(open("Chicago.geojson", "r"))
# chicago_geojson
background = alt.Chart(alt.Data(values=chicago_geojson['features'])).mark_geoshape(
        stroke='white',
        fill='lightblue'
    ).encode(
    ).properties(
        width=700,
        height=500
    )

map=alt.Chart(df).mark_circle().encode(
    longitude='lon:Q',
    latitude='lat:Q',
    size=alt.value(20),
    color='member_casual:N',
    tooltip=['member_casual']
).project(
    "albersUsa"
).properties(
    width=700,
    height=500
)

st.write(background+map)



# Add weekday and hours column to the dataframe

dayOfWeek={0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
df['weekday'] = df['started_at'].dt.dayofweek.map(dayOfWeek)


df['hour_of_the_day'] = df['started_at'].dt.hour

chart = (alt.
  Chart(df).
  mark_line(size=4).
  encode(x=alt.X(
    'hour_of_the_day:N',
    axis=alt.Axis(title="Hour of the day",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)), 
  y=alt.Y('count(ride_id):Q',
  scale=alt.Scale(domain=(0, 700)),
  axis=alt.Axis(title="No of Rides",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)),
    color=alt.Color('member_casual:N',legend=alt.Legend(orient='top-right')),
    tooltip=['hour_of_the_day','count(ride_id)']).
  properties(height=500, width=600).
  configure().
  configure_axis(grid=False).
  configure_view(strokeWidth=0))

 
# Plot!
st.altair_chart(chart, use_container_width=False)

