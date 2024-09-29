import unittest
import pandas as pd

from main import crate_type, create_contact_fullname , create_contact_address, calculate_commissions, create_company_salesowners_df


class TestCrateTypeFunction(unittest.TestCase):
    
    #Unit Test # 1 
    def test_crate_type(self):
        # DataFrame de ejemplo que simula 'orders'
        data = {
            'crate_type': ['Metal', 'Metal', 'Metal', 'Plastic', 'Plastic', 'Plastic', 'Plastic', 'Plastic', 'Wood', 'Wood'],
            'company_id': [
                'A1', 'A2', 
                'A3', 'A4',
                'A5', 'A6', 
                'A7', 'A8', 
                'A9', 'A10'
            ],
            'order_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        }
        
        orders = pd.DataFrame(data)
        #expecter output
        expected_output = pd.DataFrame({
            'crate_type': ['Metal', 'Metal', 'Metal', 'Plastic', 'Plastic', 'Plastic', 'Plastic', 'Plastic', 'Wood', 'Wood'],
            'company_id': [
                'A1', 'A2', 
                'A3', 'A4',
                'A5', 'A6', 
                'A7', 'A8', 
                'A9', 'A10'
            ],
            'order_id': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # countof order ids 
        })
        
        results = crate_type(orders)
        
        results_sorted = results.sort_values(by=['crate_type', 'company_id']).reset_index(drop=True)
        expected_output_sorted = expected_output.sort_values(by=['crate_type', 'company_id']).reset_index(drop=True)
        
        pd.testing.assert_frame_equal(results_sorted, expected_output_sorted)
        
    #unit Test # 2 
    def test_create_contact_fullname_df(self):
        sample_data = {
            'order_id': [1, 2, 3],
            'contact_data': [
                '[{"contact_name": "John", "contact_surname": "Smith", "city": "New York", "cp": "10001"}]',  # Correct format
                '[]',  # Empty list, should default to "John Doe"
                None  # Null value, should default to "John Doe"
            ]
        }
        df = pd.DataFrame(sample_data)
        result = create_contact_fullname(df)
        self.assertEqual(result.loc[0, 'contact_fullname'], 'John Smith')
        self.assertEqual(result.loc[1, 'contact_fullname'], 'John Doe')
        self.assertEqual(result.loc[2, 'contact_fullname'], 'John Doe')

    #unit test # 3 
    
    def test_create_contact_address(self):
        # Datos de ejemplo simulando la estructura de la columna 'contact_data'
        sample_data = {
            'order_id': [1, 2, 3],
            'contact_data': [
                '[{"contact_name": "John", "contact_surname": "Doe", "city": "New York", "cp": "10001"}]',  # Datos completos
                '[{"contact_name": "Jane", "contact_surname": "Doe"}]',  # Sin ciudad ni código postal
                None  # Valor nulo, debe devolver "Unknown, UNK00"
            ]
        }
    
        df = pd.DataFrame(sample_data)
    
        # Llamar a la función que queremos probar
        result = create_contact_address(df)
    
        # Pruebas unitarias para verificar el comportamiento esperado
        self.assertEqual(result.loc[0, 'contact_address'], 'New York, 10001')  # Caso con dirección completa
        self.assertEqual(result.loc[1, 'contact_address'], 'Unknown, UNK00')   # Caso sin ciudad ni código postal
        self.assertEqual(result.loc[2, 'contact_address'], 'Unknown, UNK00')   # Caso con valor nulo
        
    # Unit Test # 4 
    def test_commission_calculation(self):
        
        orders_data = {
            'order_id': ['order_1'],
            'salesowners': ['Alice, Bob, Charlie']  # Tres salesowners: main owner y dos co-owners
        }

        invoices_data = {
            'orderId': ['order_1'],
            'grossValue': ['100000'],  # en centavos (equivale a 1000 euros)
            'vat': ['20000']  # en centavos (equivale a 200 euros)
        }

        # DataFrames de ejemplo
        orders_df = pd.DataFrame(orders_data)
        invoices_df = pd.DataFrame(invoices_data)
        # Caso de prueba para verificar cálculo de comisiones
        expected_data = {
            'salesowner': ['Alice', 'Bob', 'Charlie'],
            'commission': [48.0, 20.0, 7.6]  # Calculados como: 6%, 2.5%, y 0.95% de 800 euros (net_value)
        }
        expected_df = pd.DataFrame(expected_data)

        result_df = calculate_commissions(orders_df, invoices_df)
        
        # Verificar si las comisiones calculadas coinciden con las esperadas
        pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected_df.reset_index(drop=True))
        
    #unit test # 5
    
    def test_create_company_salesowners_df(self):
        # Sample data for testing
        orders_data = {
            'company_id': ['c1', 'c1', 'c2', 'c2', 'c3'],
            'salesowners': ['Alice,Bob', 'Alice,Charlie', 'David', 'Eve,David', 'Frank']
        }
        orders_df = pd.DataFrame(orders_data)
        
        # Expected output DataFrame
        expected_data = {
            'company_id': ['c1', 'c2', 'c3'],
            'list_salesowners': ['Alice, Bob, Charlie', 'David, Eve', 'Frank']
        }
        expected_df = pd.DataFrame(expected_data)

        # Get the result from the function
        result_df = create_company_salesowners_df(orders_df)
        
        # Test if the result matches the expected output
        pd.testing.assert_frame_equal(result_df, expected_df)
    
# Ejecutamos los tests
if __name__ == '__main__':
    unittest.main()
    
    
