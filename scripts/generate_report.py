import requests
import pandas as pd
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring

# Fetch data from the Django API (users)
users_api_url = "http://127.0.0.1:8000/api/users/"
response_users = requests.get(users_api_url)
users_data = response_users.json()

# Fetch data from the Django API (items)
items_api_url = "http://127.0.0.1:8000/api/items/"
response_items = requests.get(items_api_url)
items_data = response_items.json()

print("Data fetched from Django API", users_data, items_data)

# Convert data to pandas DataFrames
df_users = pd.DataFrame(users_data)
df_items = pd.DataFrame(items_data)

print("Data converted to DataFrames", df_users.columns, df_items.columns)

# Data cleaning for users: Fill NaN values (if necessary)
df_users.fillna(value={'street': 'Unknown', 'suite': 'Unknown'}, inplace=True)

# Data cleaning for items: Fill NaN values and ensure data types
df_items.fillna(value={'description': 'No description', 'price': 0.0}, inplace=True)

# Ensure price column is float
df_items['price'] = df_items['price'].astype(float)

# Data transformation for users: Adding a calculated field for email domain (example)
df_users['email_domain'] = df_users['email'].apply(lambda x: x.split('@')[1])

# Data selection for users: Choose relevant columns
selected_columns_users = df_users[['id', 'name', 'username', 'email', 'street', 'suite', 'city', 'zipcode', 'email_domain']]

# Data aggregation for users: Group by city and count users
city_group = selected_columns_users.groupby('city').size().reset_index(name='user_count')

# Data merging: Merge city group data back to main DataFrame
merged_data = pd.merge(selected_columns_users, city_group, on='city', how='left')

# Data sorting: Sort data by user count and name
sorted_data = merged_data.sort_values(by=['user_count', 'name'], ascending=[False, True])

#print all the above datas 
print("Data cleaning for users", df_users.head())
print("Data cleaning for items", df_items.head())
print("Data transformation for users", df_users.head())
print("Data selection for users", selected_columns_users.head())
print("Data aggregation for users", city_group.head())
print("Data merging", merged_data.head())
print("Data sorting", sorted_data.head())


# Function to convert DataFrame to XML with indentation
def dataframe_to_xml(df, root_tag, row_tag):
    root = Element(root_tag)
    for index, row in df.iterrows():
        row_elem = SubElement(root, row_tag)
        for col, val in row.items():
            col_elem = SubElement(row_elem, col)
            col_elem.text = str(val)
    return root

# Convert the user DataFrame to XML
root = dataframe_to_xml(sorted_data, 'Users', 'User')

# Add items data to the XML
items_elem = SubElement(root, 'Items')
for index, item in df_items.iterrows():
    item_elem = SubElement(items_elem, 'Item')
    for col, val in item.items():
        col_elem = SubElement(item_elem, col)
        col_elem.text = str(val)

# Write XML to file
tree = ElementTree(root)
tree.write('report.xml', encoding='utf-8', xml_declaration=True)

print("XML report generated: report.xml")
