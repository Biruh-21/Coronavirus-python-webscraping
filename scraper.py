from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import requests

url = 'https://www.worldometers.info/coronavirus/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

covid_table_id = []
for table in soup.find_all('table'):
    covid_table_id.append(table['id'])

# with open('covid.html', 'w+') as f:
#     resp = str(response.content).rstrip()
#     f.write(resp)

table = soup.find('table', id=covid_table_id[0])
column_names = []

# Get <thead> and extract column names
thead = table.find_all('thead')[0]
th_tags = thead.find_all('th')

for th in th_tags:
    col_name = []
    for item in th.contents:
        if isinstance(item, NavigableString):
            col_name.append(item.strip(',+').strip())
        elif item.get_text().strip():
            col_name.append(item.get_text().strip())
    column_names.append(' '.join(col_name))

# Get the first <tbody> and extract data
tbody = table.find_all('tbody')[0]
data = []
for row in tbody.find_all('tr'):
    row_data = []
    for td in row.find_all('td'):
        row_data.append(td.get_text().strip().replace(',', '').strip('+'))
    data.append(row_data)

# tbl_data = [[td.get_text().strip().replace(',', '').strip('+')
#            for td in row.find_all('td')] for row in tbody.find_all('tr')]

df = pd.DataFrame(data, columns=column_names)
TABLE_COLUMNS = ["Country", "Total Cases", "New Cases",
                 "Total Deaths", "New Deaths", "Total Recovered",
                 "Active Cases", "Serious", "Cases Per 1M",
                 "Deaths Per 1M", "Total Tests", "Tests Per 1M", "Continent"]

# Change column names
if len(df.columns) == len(TABLE_COLUMNS):
    df.columns = TABLE_COLUMNS

num_cols = ["Total Cases", "New Cases", "Total Deaths",
            "New Deaths", "Total Recovered", "Active Cases",
            "Serious", "Cases Per 1M", "Deaths Per 1M",
            "Total Tests", "Tests Per 1M"]

# Replace empty columns with 0
for col in num_cols:
    df[num_cols] = df[num_cols].replace('', 0).replace('N/A', 0)

# Change numerical columns to int
for col in num_cols:
    try:
        df[col] = df[col].astype(int)
    except Exception as error:
        print(f"Error on col[{col}]: {error}")

# Sort by Countries
# df = df.sort_values(by=['Country'])

# Sort by Total Deaths
df = df.sort_values(by=['Total Deaths'], ascending=False)

# Printing table
print(df)

# Export to CSV
df.to_csv('coronavirus.csv', encoding='utf-8')
