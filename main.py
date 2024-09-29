import pandas as pd
import numpy as np
import json
import ast

#Explore data

orders = pd.read_csv('orders.csv', sep = ';')
print(orders)

with open('invoicing_data.json', 'r') as i:
    invoicing = json.load(i)
print(invoicing)

invoicing_df = pd.json_normalize(invoicing['data']['invoices'])
print(invoicing_df)

print(invoicing_df.columns)
print(orders.columns)

print(invoicing_df.info())
print(orders.info())

# No of orders by crate type by company

def crate_type (orders):
    crate_type_company = orders.groupby(['crate_type','company_id'], dropna=False)[['order_id']].count().reset_index()
    return crate_type_company
results = crate_type(orders) 

print(results)

# contact information

def extract_contact_data(contact_data):
    try:
        # Si el valor es nulo o NaN, devolvemos 'John Doe'
        if pd.isnull(contact_data):
            return 'John Doe'

        # Intenta evaluar el string en una estructura de Python (lista o dict)
        contact_data_value = ast.literal_eval(contact_data)
        
        # Si es una lista, tomamos el primer elemento
        if isinstance(contact_data_value, list):
            contact = contact_data_value[0]
        elif isinstance(contact_data_value, dict):
            contact = contact_data_value
        else:
            return 'John Doe'
        
        # Obtener el nombre y apellido, por defecto 'John' y 'Doe' si faltan
        name = contact.get('contact_name')
        surname = contact.get('contact_surname')
        
        return f"{name} {surname}"
    
    except Exception as e:
        return 'John Doe'
    
def create_contact_fullname (orders):
    # Aplicar la función a la columna contact_data
    orders['contact_fullname'] = orders['contact_data'].apply(extract_contact_data)
    return orders[['order_id','contact_fullname']]

df_1 = create_contact_fullname(orders)

print(df_1)

# contact_address

def extract_contact_address(contact_data):
    try:
        # Si el valor es nulo o NaN, devolvemos 'John Doe'
        if pd.isnull(contact_data):
            return 'Unknown, UNK00'

        # Intenta evaluar el string en una estructura de Python (lista o dict)
        contact_data_value = ast.literal_eval(contact_data)
        
        # Si es una lista, tomamos el primer elemento
        if isinstance(contact_data_value, list):
            contact = contact_data_value[0]
        elif isinstance(contact_data_value, dict):
            contact = contact_data_value
        else:
            return 'Unknown, UNK00'
        
        # Obtener el nombre y apellido, por defecto 'John' y 'Doe' si faltan
        city = contact.get('city', 'Unknown')
        cp = contact.get('cp', 'UNK00')
        
        return f"{city}, {cp}"
    
    except Exception as e:
        return 'Unknown, UNK00'
    
def create_contact_address (orders):
    # Aplicar la función a la columna contact_data
    orders['contact_address'] = orders['contact_data'].apply(extract_contact_address)
    return orders[['order_id','contact_address']]

df_2 = create_contact_address(orders)

print(df_2)


# Commission

def calculate_commissions(orders, invoices):
    # Convertir a numérico
    invoices['grossValue'] = pd.to_numeric(invoices['grossValue'])
    invoices['vat'] = pd.to_numeric(invoices['vat'])

    # Calcular el valor neto como grossValue - vat (convertido a euros)
    invoices['net_value_euros'] = (invoices['grossValue'] - invoices['vat']) / 100

    # Merge con las órdenes para obtener salesowners y net_value
    orders_with_invoices = pd.merge(orders, invoices, left_on='order_id', right_on='orderId')

    # Calcular comisiones para cada dueño de ventas
    commission_data = []

    for id, row in orders_with_invoices.iterrows():
        salesowners = row['salesowners'].split(', ')
        net_value = row['net_value_euros']
        
        # Asignar comisiones según el orden de ownership
        if len(salesowners) > 0:
            commission_data.append((salesowners[0], net_value * 0.06))  # Main Owner
        if len(salesowners) > 1:
            commission_data.append((salesowners[1], net_value * 0.025))  # Co-owner 1
        if len(salesowners) > 2:
            commission_data.append((salesowners[2], net_value * 0.0095))  # Co-owner 2

    commission_df = pd.DataFrame(commission_data, columns=['salesowner', 'commission'])
    total_commissions = commission_df.groupby('salesowner').sum().reset_index()
    
    # Redondear a 2 decimales
    total_commissions['commission'] = total_commissions['commission'].round(2)
    
    sorted_commissions = total_commissions.sort_values(by='commission', ascending=False)
    return sorted_commissions

# Ejecución de la función
commissions_df = calculate_commissions(orders, invoicing_df)
print(commissions_df)


# Function to sort and deduplicate salesowners
def format_salesowners(salesowners):
    # Flatten the list of salesowners, split by commas, and create a sorted unique list
    unique_salesowners = sorted(set(','.join(salesowners).split(',')))
    return ', '.join(unique_salesowners)

# Function to create the DataFrame of companies with sales owners
def create_company_salesowners_df(orders_df):
    # Group by 'company_id' and apply the formatting function
    company_salesowners = orders_df.groupby('company_id')['salesowners'].apply(format_salesowners).reset_index()
    
    # Rename columns for clarity
    company_salesowners.columns = ['company_id', 'list_salesowners']
    
    return company_salesowners

create_company_salesowners = create_company_salesowners_df(orders)
print(create_company_salesowners)