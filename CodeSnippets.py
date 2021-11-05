code_snippet_data = '''
# store the AWS access keys from the secrets file into variables
ACCESS_KEY = st.secrets['AWS_ACCESS_KEY_ID']
SECRET_KEY = st.secrets['AWS_SECRET_ACCESS_KEY']

# use boto3 to connect to S3.
client = boto3.client('s3', aws_access_key_id=ACCESS_KEY , aws_secret_access_key=SECRET_KEY)
response = client.get_object(
    Bucket = 'my-streamlit-app-bucket',
    Key = 'cleaned_df_sample.csv'
)

dayOfWeek={0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
# function to load data into a pandas dataframe and apply some trasnformations that will be required later.
@st.cache(allow_output_mutation=True)
def load_data():
    

    df = pd.read_csv(response.get('Body'))

    # change all column names to lowercase if not already lowercase
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis='columns', inplace=True)

    # change the columns showing date and time to 'datetime' type
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['ended_at'] = pd.to_datetime(df['ended_at'])

    # rename the 'start_lat' and 'start_long' columns to 'lat' and 'long' as streamlit requires these columns 
    # for mapping 
    df.rename(columns={"start_lat":"lat","start_lng":"lon"},inplace=True)

    # Add weekday and hours column to the dataframe
    df['weekday'] = df['started_at'].dt.dayofweek.map(dayOfWeek)
    df['hour_of_the_day'] = df['started_at'].dt.hour

    # Add ride_duration column to the dataframe
    df['ride_duration'] = (df.ended_at - df.started_at)/np.timedelta64(1,'m')

    # filter out the rows where ride duration is negative
    df = df[df.ride_duration>0]

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

code_snippet_map = '''
# Chicago.geojson file was obtained from "https://opendata.arcgis.com/datasets/bfe6977cfd574c2b894cd67cf6a787c3_2.geojson"
# Load the geojson file into a json object
chicago_geojson = json.load(open("Chicago.geojson", "r"))

# build a backgrounp map https://altair-viz.github.io/gallery/airports_count.html
background = alt.Chart(alt.Data(values=chicago_geojson['features'])).mark_geoshape(
        stroke='white',
        fill='lightblue'
    ).encode(
    ).properties(
        width=600,
        height=500
    )
# Build a spatial map of the starting point markings
map=alt.Chart(df).mark_circle().encode(
    longitude='lon:Q',
    latitude='lat:Q',
    size=alt.value(30),
    color=alt.Color('member_casual:N',legend=alt.Legend(orient='top-right',strokeColor='gray',
    fillColor='#EEEEEE',
    padding=10,
    cornerRadius=10)),
    tooltip=['member_casual']
).project(
    "albersUsa"
).properties(
    width=600,
    height=500
)

# combine the above two maps
st.write(background+map)
'''

code_snippet_hourchart = '''
hour_chart = (alt.
  Chart(df).
  mark_line(size=4).
  encode(x=alt.X(
    'hour_of_the_day:N',
    axis=alt.Axis(title="Hour of the day",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)), 
  y=alt.Y('count(ride_id):Q',
  scale=alt.Scale(domain=(0, 700)),
  axis=alt.Axis(title="No of Rides",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)),
    color=alt.Color('member_casual:N',legend=alt.Legend(orient='top-right',strokeColor='gray',
    fillColor='#EEEEEE',
    padding=10,
    cornerRadius=10)),
    tooltip=['hour_of_the_day','count(ride_id)']).
  properties(height=500, width=600))

'''

code_snippet_weekdaychart = '''
weekday_chart = (alt.
  Chart(df).
  mark_line(size=4).
  encode(x=alt.X(
    'weekday:N',
    axis=alt.Axis(title="Day of the Week",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)), 
  y=alt.Y('count(ride_id):Q',
  scale=alt.Scale(domain=(0, 1200)),
  axis=alt.Axis(title="No of Rides",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)),
    color=alt.Color('member_casual:N',legend=alt.Legend(orient='bottom-right',strokeColor='gray',
    fillColor='#EEEEEE',
    padding=10,
    cornerRadius=10)),
    tooltip=['weekday','count(ride_id)'],
    order='weekday').
  properties(height=500, width=600))

st.altair_chart(weekday_chart)

'''

code_snippet_barchart = '''
bar_chart_ride_counts = alt.Chart(df).mark_bar(size=50).encode(
    x=alt.X('member_casual:N',
    axis=alt.Axis(title="Member vs Casual",titleFontSize=15,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)),
    y=alt.Y('count(ride_id):Q',
    axis=alt.Axis(title="No of Rides",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)),
    color=alt.Color('member_casual:N',legend=alt.Legend(orient='right',strokeColor='gray',
    fillColor='#EEEEEE',
    padding=10,
    cornerRadius=10)),
    column=alt.Column('rideable_type:N',
    title="Bike Type")).properties(
            height=500, 
            width=150)

st.altair_chart(bar_chart_ride_counts)
'''

code_snippet_ride_duration = '''
bar_chart_ride_duration = alt.Chart(df).mark_line(size=4).encode(
    x=alt.X('weekday:N',
    axis=alt.Axis(title="Day of the Week",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)),
    y=alt.Y('mean(ride_duration):Q',
    scale=alt.Scale(domain=(0, 40)),
    axis=alt.Axis(title="Avg Ride Duration",titleFontSize=20,titlePadding=15,tickSize=7,tickWidth=5,labelFontSize=15)),
    color=alt.Color('member_casual:N',legend=alt.Legend(orient='bottom-right',strokeColor='gray',
    fillColor='#EEEEEE',
    padding=10,
    cornerRadius=10))).properties(
            height=500, 
            width=600)

st.altair_chart(bar_chart_ride_duration)
'''