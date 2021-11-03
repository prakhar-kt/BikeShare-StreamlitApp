import streamlit as st
import pandas as pd
import numpy as np
import boto3
import altair as alt
import random
import os


st.title('BikeShare Analysis')

#https://towardsdatascience.com/reading-and-writing-files-from-to-amazon-s3-with-pandas-ccaf90bfe86c
ACCESS_KEY = st.secrets['AWS_ACCESS_KEY_ID']
SECRET_KEY = st.secrets['AWS_SECRET_ACCESS_KEY']
client = boto3.client('s3', aws_access_key_id=ACCESS_KEY , aws_secret_access_key=SECRET_KEY)
response = client.get_object(
    Bucket = 'my-streamlit-app-bucket',
    Key = 'cleaned_df_sample.csv'
)

@st.cache(allow_output_mutation=True)
def load_data():
    
    data = pd.read_csv(response.get('Body'))
   
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data['started_at'] = pd.to_datetime(data['started_at'])
    data['ended_at'] = pd.to_datetime(data['ended_at'])
    data.rename(columns={"start_lat":"lat","start_lng":"lon"},inplace=True)

    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

st.subheader('Raw data')
st.write(data)


# data['member_casual'] = data['member_casual'].astype(str)

st.subheader('Map of the starting locations')

# st.map(data,zoom=9,hue='member_casual')
map=alt.Chart(data).mark_circle().encode(
    longitude='lon:Q',
    latitude='lat:Q',
    size=alt.value(20),
    color='member_casual:N',
    tooltip=['member_casual']
).project(
    "albersUsa"
).properties(
    width=600,
    height=500
)

st.altair_chart(map)

st.subheader("No of rides by the hour")

# Add weekday and hours column to the dataframe

dayOfWeek={0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
data['weekday'] = data['started_at'].dt.dayofweek.map(dayOfWeek)


data['hour_of_the_day'] = data['started_at'].dt.hour

chart = (alt.
  Chart(data).
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

