import streamlit as st
import pandas as pd
import numpy as np

st.title('BikeShare Analysis')

DATA_URL = ('https://my-streamlit-app-bucket.s3.us-east-2.amazonaws.com/cleaned_df.csv')

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

