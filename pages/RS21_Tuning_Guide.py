import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
from datetime import date
import os

st.set_page_config(page_title='RS21 Interactive Tuning Guide')
st.header('RS21 Tuning Guide')
# st.caption('App developed by Powder Monkey Sailing Team')
st.caption('Rig tension as per:')
st.caption('https://www.rssailing.com/rs21-tuning-guide/')
### --- LOAD DATAFRAME
excel_file = 'RS21Tuning Database.xlsx'
sheet_name_1 = 'Rig Tuning Database'
sheet_name_2 = 'JIB Tuning Database'
sheet_name_3 = 'Polars'

RIG_df = pd.read_excel(excel_file,
                            sheet_name=sheet_name_1,
                            usecols='A:H',
                            header=0,
                            converters={'KEY': str, 'UPPERS_TURNS': str, 'LOWERS_TURNS': str, 'TENSION_LOWERS': str,
                                        'TENSION UPPERS': str, 'VANG': str, 'WIND_SPEED': int, 'BACKSTAY': str}
                            )

JIB_df = pd.read_excel(excel_file,
                            sheet_name=sheet_name_2,
                            usecols='A:D',
                            header=0,
                            converters={'KEY': str, 'TACK_HEIGHT': str, 'HALYARD': str, 'WIND_SPEED': int, 'CAR_POSITION': str}
                            )
Polars_df = pd.read_excel(excel_file,
                            sheet_name=sheet_name_3,
                            usecols='A:C',
                            header=0,
                            # converters={'wind_speed': int, 'beat_target': str, 'HALYARD': str, 'JIB_CUT': str, 'WIND_SPEED': int, 'CAR_POSITION': str}
                            )
wind_speed_filter = st.slider("Wind Speed Filter (Kts)", 0, 23, 10)
    # st.number_input("Wind Speed Filter", min_value=0, max_value=20, value=0)
    # st.slider("Wind Speed Filter", 0, 20, (0, 20))
# jib_cut_filter = st.radio("Jib Cut Selection", ["J6","J2+"])


filtered_JIB_df = JIB_df[(JIB_df['WIND_SPEED'] == wind_speed_filter)]
filtered_RIG_df = RIG_df[(RIG_df['WIND_SPEED'] == wind_speed_filter)]
filtered_polars_df = Polars_df[(Polars_df['wind_speed'] == wind_speed_filter)]

# --- STREAMLIT SELECTION
st.subheader('Settings:')

col1, col2, col3 = st.columns (3)
col1.metric(label='Uppers Turns', value=filtered_RIG_df['UPPERS_TURNS'].max())
col1.metric(label='Lowers Turns', value=filtered_RIG_df['LOWERS_TURNS'].max())
col2.metric(label='Tack Height', value=filtered_JIB_df['TACK_HEIGHT'].max())
# col2.metric(label='Jib Halyard', value=filtered_JIB_df['HALYARD'].max())
col2.metric(label='Car Position', value=filtered_JIB_df['CAR_POSITION'].max())
# col3.metric(label='Upwind target Kts', value=filtered_polars_df['beat_target'])
# col3.metric(label='Downwind target Kts', value=filtered_polars_df['run_target'])


st.subheader('Solent Tide:')
def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')
    headers = [header.text for header in table.find_all('th')]
    # Rename duplicate headers
    seen = {}
    for i, header in enumerate(headers):
        if header not in seen:
            seen[header] = 1
        else:
            seen[header] += 1
            headers[i] = header + str(seen[header])

    rows = table.find_all('tr')
    data = []
    for row in rows[1:]:
        values = [value.text for value in row.find_all('td')]
        # If a row has fewer values than headers, fill the rest with None
        values += [None] * (len(headers) - len(values))
        data.append(values)

    df = pd.DataFrame(data, columns=headers)
    return df


url = "https://www.bbc.co.uk/weather/coast-and-sea/tide-tables/8/65"
df = scrape_data(url)

# Select the first two columns and rename them
df = df.iloc[:, :2]
df.columns = ['Time', 'Height']
# Convert the 'Height' column to float type
df['Height'] = df['Height'].astype(float)

# Add the 'Phase' column based on the conditions
df['Phase'] = df['Height'].apply(lambda x: 'High' if x >= 3 else 'Low')

# Convert the 'Time' column to datetime format
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time

# Display current time alongside data
now = datetime.now(pytz.timezone('GMT'))

# Format the time as a string
time_string = now.strftime("%H:%M")

# Calculate the difference between the current time and each time in the 'Time' column in seconds
df['TimeDifferenceHRS'] = df['Time'].apply(lambda x:
                                           -(datetime.combine(date.today(), x) - datetime.combine(date.today(),
                                                                                                  now.time())).total_seconds()
                                           if x > now.time()
                                           else (datetime.combine(date.today(), now.time()) - datetime.combine(
                                               date.today(), x)).total_seconds())
df['abstd'] = abs(df['Time'].apply(
    lambda x: (datetime.combine(date.today(), x) - datetime.combine(date.today(), now.time())).total_seconds()))
# Convert the 'Time' column back to 'HH:MM' format
df['Time'] = df['Time'].apply(lambda x: x.strftime('%H:%M'))

# Convert the 'TimeDifference' column to hours with one decimal place
df['TimeDifferenceHRS'] = (df['TimeDifferenceHRS'] / 3600).round(1)

# Filter the DataFrame to find the row with the 'High' phase and the smallest time difference
closest_high_tide = df[df['Phase'] == 'High'].nsmallest(1, 'abstd')
df_filtered = closest_high_tide.copy()
df_filtered = df_filtered.drop('abstd', axis=1)

# Tidal Flow Chart
# Define the path to the directory where the images are stored
image_dir = 'Images'

# Calculate the rounded time difference
rounded_time_difference = round(float(closest_high_tide['TimeDifferenceHRS'].values[0]) * 2) / 2

# Display final page

st.header('Tide Flow NOW')
# Add a radio button to the Streamlit app
option = st.radio(
    'Select Time:',
    ('Now', '+30', '+1Hr', '+1.5Hrs', "+2Hrs"), horizontal=True)
# Add either zero or 0.5 to the rounded_time_difference variable based on the selected option
if option == '+30':
    rounded_time_difference += 0.5
if option == '+1Hr':
    rounded_time_difference += 1.0
if option == '+1.5Hrs':
    rounded_time_difference += 1.5
if option == '+2Hrs':
    rounded_time_difference += 2.0
# Construct the path to the image
image_path = os.path.join(image_dir, f'{rounded_time_difference}.jpg')

# st.caption('Page will auto-refresh each minute')
st.image(image_path)
st.header('Tide Times Portsmouth TODAY')
st.write(f"Current time (GMT): {time_string}")
st.caption('Closest HW:')
st.write(df_filtered)
st.caption('Data Scraped live from BBC Weather presentation of UK Hydrographic Office Data')
st.caption('All Times quoted in GMT')

# Select the first two columns and rename them
df = df.iloc[:, :2]
df.columns = ['Time', 'Height']
# Convert the 'Height' column to float type
df['Height'] = df['Height'].astype(float)

# Add the 'Phase' column based on the conditions
df['Phase'] = df['Height'].apply(lambda x: 'High' if x >= 3 else 'Low' )
st.write(f"All Tide Times Today")
st.write(df)