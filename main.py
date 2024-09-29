import pandas as pd
import numpy as np
import json
import ast

# Load and explore the data

# Read orders data from a CSV file
orders = pd.read_csv('orders.csv', sep=';')
print(orders)

# Load invoicing data from a JSON file
with open('invoicing_data.json', 'r') as i:
    invoicing = json.load(i)
print(invoicing)

# Normalize the JSON data into a DataFrame
invoicing_df = pd.json_normalize(invoicing['data']['invoices'])
print(invoicing_df)

# Display the columns of both DataFrames
print(invoicing_df.columns)
print(orders.columns)

# Display summary information about both DataFrames
print(invoicing_df.info())
print(orders.info())

##### Calculate the number of orders by crate type and company #########

def crate_type(orders):
    # Group by crate type and company ID, counting the number of orders
    crate_type_company = orders.groupby(['crate_type', 'company_id'], dropna=False)[['order_id']].count().reset_index()
    return crate_type_company

# Get results for crate type analysis
results = crate_type(orders) 
print(results)

###### Extract contact information #####

def extract_contact_data(contact_data):
    try:
        # If the contact data is null or NaN, return a default name
        if pd.isnull(contact_data):
            return 'John Doe'

        # Evaluate the string into a Python structure (list or dict)
        contact_data_value = ast.literal_eval(contact_data)
        
        # If it's a list, take the first element; if it's a dict, use it directly
        if isinstance(contact_data_value, list):
            contact = contact_data_value[0]
        elif isinstance(contact_data_value, dict):
            contact = contact_data_value
        else:
            return 'John Doe'
        
        # Get the contact's name and surname, defaulting to 'John' and 'Doe' if missing
        name = contact.get('contact_name')
        surname = contact.get('contact_surname')
        
        return f"{name} {surname}"
    
    except Exception as e:
        # If any error occurs, return the default name
        return 'John Doe'
    
def create_contact_fullname(orders):
    # Apply the function to the 'contact_data' column to create full names
    orders['contact_fullname'] = orders['contact_data'].apply(extract_contact_data)
    return orders[['order_id', 'contact_fullname']]

# Create a DataFrame with contact full names
df_1 = create_contact_fullname(orders)
print(df_1)

###### Extract contact address information #########

def extract_contact_address(contact_data):
    try:
        # If the contact data is null or NaN, return a default address
        if pd.isnull(contact_data):
            return 'Unknown, UNK00'

        # Evaluate the string into a Python structure (list or dict)
        contact_data_value = ast.literal_eval(contact_data)
        
        # If it's a list, take the first element; if it's a dict, use it directly
        if isinstance(contact_data_value, list):
            contact = contact_data_value[0]
        elif isinstance(contact_data_value, dict):
            contact = contact_data_value
        else:
            return 'Unknown, UNK00'
        
        # Get the city and postal code, defaulting to 'Unknown' and 'UNK00' if missing
        city = contact.get('city', 'Unknown')
        cp = contact.get('cp', 'UNK00')
        
        return f"{city}, {cp}"
    
    except Exception as e:
        # If any error occurs, return the default address
        return 'Unknown, UNK00'
    
def create_contact_address(orders):
    # Apply the function to the 'contact_data' column to create addresses
    orders['contact_address'] = orders['contact_data'].apply(extract_contact_address)
    return orders[['order_id', 'contact_address']]

# Create a DataFrame with contact addresses
df_2 = create_contact_address(orders)
print(df_2)

####### Calculate commission amounts #######

def calculate_commissions(orders, invoices):
    # Convert invoice values to numeric types
    invoices['grossValue'] = pd.to_numeric(invoices['grossValue'])
    invoices['vat'] = pd.to_numeric(invoices['vat'])

    # Calculate net value in euros
    invoices['net_value_euros'] = (invoices['grossValue'] - invoices['vat']) / 100

    # Merge orders with invoices to include sales owners and net value
    orders_with_invoices = pd.merge(orders, invoices, left_on='order_id', right_on='orderId')

    # Prepare a list to store commission data
    commission_data = []

    # Calculate commissions for each sales owner
    for id, row in orders_with_invoices.iterrows():
        salesowners = row['salesowners'].split(', ')
        net_value = row['net_value_euros']
        
        # Assign commissions based on the order of ownership
        if len(salesowners) > 0:
            commission_data.append((salesowners[0], net_value * 0.06))  # Main Owner
        if len(salesowners) > 1:
            commission_data.append((salesowners[1], net_value * 0.025))  # Co-owner 1
        if len(salesowners) > 2:
            commission_data.append((salesowners[2], net_value * 0.0095))  # Co-owner 2

    # Create a DataFrame from the commission data
    commission_df = pd.DataFrame(commission_data, columns=['salesowner', 'commission'])
    total_commissions = commission_df.groupby('salesowner').sum().reset_index()
    
    # Round commissions to 2 decimal places
    total_commissions['commission'] = total_commissions['commission'].round(2)
    
    # Sort commissions in descending order
    sorted_commissions = total_commissions.sort_values(by='commission', ascending=False)
    return sorted_commissions

# Execute the commission calculation function
commissions_df = calculate_commissions(orders, invoicing_df)
print(commissions_df)

########## Function to format and deduplicate sales owners #####

def format_salesowners(salesowners):
    # Flatten the list of sales owners, split by commas, and create a sorted unique list
    unique_salesowners = sorted(set(','.join(salesowners).split(',')))
    return ', '.join(unique_salesowners)

# Function to create a DataFrame of companies with their sales owners

def create_company_salesowners_df(orders_df):
    # Group by 'company_id' and apply the formatting function to create a list of sales owners
    company_salesowners = orders_df.groupby('company_id')['salesowners'].apply(format_salesowners).reset_index()
    
    # Rename columns for clarity
    company_salesowners.columns = ['company_id', 'list_salesowners']
    
    return company_salesowners

# Create a DataFrame with company sales owners
create_company_salesowners = create_company_salesowners_df(orders)
print(create_company_salesowners)
