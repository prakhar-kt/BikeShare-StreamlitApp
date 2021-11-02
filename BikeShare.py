import streamlit as st
import pandas as pd
import numpy as np
import os


st.title('BikeShare Analysis')

# streamlit_app.py



# Create connection object.
# `anon=False` means not anonymous, i.e. it uses access keys to pull data.
# fs = s3fs.S3FileSystem(anon=False)

# # Retrieve file contents.
# # Uses st.cache to only rerun when the query changes or after 10 min.
# @st.cache(ttl=600)
# def read_file(filename):
#     with fs.open(filename) as f:
#         return f.read().decode("utf-8")

# content = read_file("testbucket-jrieke/myfile.csv")

# # Print results.
# for line in content.strip().split("\n"):
#     name, pet = line.split(",")
#     st.write(f"{name} has a :{pet}:")

DATA_URL = ('https://my-streamlit-app-bucket.s3.us-east-2.amazonaws.com/cleaned_df.csv')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

st.subheader('Raw data')
st.write(data)