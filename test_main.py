import unittest
import pandas as pd

# Import functions to be tested from the main module
from main import crate_type, create_contact_fullname, create_contact_address, calculate_commissions, create_company_salesowners_df

class TestCrateTypeFunction(unittest.TestCase):
    
    # Unit Test #1: Testing the crate_type function
    def test_crate_type(self):
        # Example DataFrame simulating 'orders'
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
        # Expected output DataFrame
        expected_output = pd.DataFrame({
            'crate_type': ['Metal', 'Metal', 'Metal', 'Plastic', 'Plastic', 'Plastic', 'Plastic', 'Plastic', 'Wood', 'Wood'],
            'company_id': [
                'A1', 'A2', 
                'A3', 'A4',
                'A5', 'A6', 
                'A7', 'A8', 
                'A9', 'A10'
            ],
            'order_id': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # Count of order IDs
        })
        
        results = crate_type(orders)
        
        # Sort results for comparison
        results_sorted = results.sort_values(by=['crate_type', 'company_id']).reset_index(drop=True)
        expected_output_sorted = expected_output.sort_values(by=['crate_type', 'company_id']).reset_index(drop=True)
        
        # Assert that the resulting DataFrame matches the expected output
        pd.testing.assert_frame_equal(results_sorted, expected_output_sorted)
        
    # Unit Test #2: Testing the create_contact_fullname function
    def test_create_contact_fullname_df(self):
        # Sample data for testing
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
        
        # Assertions to verify expected outcomes
        self.assertEqual(result.loc[0, 'contact_fullname'], 'John Smith')
        self.assertEqual(result.loc[1, 'contact_fullname'], 'John Doe')
        self.assertEqual(result.loc[2, 'contact_fullname'], 'John Doe')

    # Unit Test #3: Testing the create_contact_address function
    def test_create_contact_address(self):
        # Sample data simulating the structure of 'contact_data'
        sample_data = {
            'order_id': [1, 2, 3],
            'contact_data': [
                '[{"contact_name": "John", "contact_surname": "Doe", "city": "New York", "cp": "10001"}]',  # Complete data
                '[{"contact_name": "Jane", "contact_surname": "Doe"}]',  # Missing city and postal code
                None  # Null value, should return "Unknown, UNK00"
            ]
        }
    
        df = pd.DataFrame(sample_data)
    
        # Call the function to test
        result = create_contact_address(df)
    
        # Assertions to verify expected outcomes
        self.assertEqual(result.loc[0, 'contact_address'], 'New York, 10001')  # Case with full address
        self.assertEqual(result.loc[1, 'contact_address'], 'Unknown, UNK00')   # Case without city and postal code
        self.assertEqual(result.loc[2, 'contact_address'], 'Unknown, UNK00')   # Case with null value
        
    # Unit Test #4: Testing the commission calculation
    def test_commission_calculation(self):
        # Sample data for orders and invoices
        orders_data = {
            'order_id': ['order_1'],
            'salesowners': ['Alice, Bob, Charlie']  # Three sales owners: main owner and two co-owners
        }

        invoices_data = {
            'orderId': ['order_1'],
            'grossValue': ['100000'],  # In cents (equivalent to 1000 euros)
            'vat': ['20000']  # In cents (equivalent to 200 euros)
        }

        # Example DataFrames for orders and invoices
        orders_df = pd.DataFrame(orders_data)
        invoices_df = pd.DataFrame(invoices_data)

        # Expected output for commission calculations
        expected_data = {
            'salesowner': ['Alice', 'Bob', 'Charlie'],
            'commission': [48.0, 20.0, 7.6]  # Calculated as: 6%, 2.5%, and 0.95% of 800 euros (net_value)
        }
        expected_df = pd.DataFrame(expected_data)

        result_df = calculate_commissions(orders_df, invoices_df)
        
        # Verify if the calculated commissions match the expected output
        pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected_df.reset_index(drop=True))
        
    # Unit Test #5: Testing the create_company_salesowners_df function
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
    
# Execute the tests
if __name__ == '__main__':
    unittest.main()
