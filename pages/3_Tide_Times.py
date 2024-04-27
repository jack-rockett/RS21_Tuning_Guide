import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz

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
df['Phase'] = df['Height'].apply(lambda x: 'High' if x >= 3 else 'Low' )

# Display current time alongside data
now = datetime.now(pytz.timezone('GMT'))

# Format the time as a string
time_string = now.strftime("%H:%M")


st.header('Tide Times Portsmouth TODAY')
st.caption('Data Scraped live from BBC Weather presentation of UK Hydrographic Office Data')
st.caption('All Times quoted in GMT')
st.write(f"Current time (GMT): {time_string}")
st.write(df)
st.caption('App developed by Powder Monkey Sailing Team')