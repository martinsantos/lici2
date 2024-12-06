import unittest
from datetime import datetime
import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from licitaciones.templates.base_template import BaseLicitacionTemplate

# Create a concrete implementation for testing
class TestLicitacionTemplate(BaseLicitacionTemplate):
    def extract_licitaciones(self):
        # Dummy implementation for abstract method
        return []

class TestLicitacionesTemplate(unittest.TestCase):
    def setUp(self):
        # Create an instance of TestLicitacionTemplate for testing
        self.template = TestLicitacionTemplate('https://test.com')

    def test_two_digit_year_adjustment(self):
        """Test intelligent two-digit year adjustment"""
        test_cases = [
            ('23', '2023'),   # Recent year in 2000s
            ('75', '1975'),   # Older year in 1900s
            ('99', '1999'),   # Boundary case
            ('01', '2001'),   # Early 2000s
            ('50', '1950'),   # Boundary between decades
        ]
        
        for input_year, expected_year in test_cases:
            adjusted_year = self.template._adjust_two_digit_year(input_year)
            self.assertEqual(adjusted_year, expected_year, 
                             f"Failed to adjust year {input_year}")

    def test_date_parsing(self):
        """Test parsing of various problematic date formats"""
        test_cases = [
            # Problematic formats from logs
            ('75-08-01', '1975-08-01'),    # Two-digit year
            ('1-14-05', None),             # Invalid month
            ('2-14-25', None),             # Invalid month/year
            
            # Various valid formats
            ('31/12/2023', '2023-12-31'),
            ('12/31/2023', '2023-12-31'),  # US format
            ('2023-12-31', '2023-12-31'),
            ('31-12-23', '2023-12-31'),    # Two-digit year
            
            # Edge cases
            ('54-08-01', '1954-08-01'),    # Another two-digit year
            ('1/14/05', None),             # Invalid month
        ]
        
        for input_date, expected_date in test_cases:
            parsed_date = self.template.parse_date(input_date)
            
            if expected_date is None:
                self.assertIsNone(parsed_date, f"Expected None for {input_date}")
            else:
                self.assertIsNotNone(parsed_date, f"Failed to parse {input_date}")
                if parsed_date:
                    self.assertEqual(parsed_date.strftime('%Y-%m-%d'), expected_date, 
                                     f"Incorrect parsing for {input_date}")

    def test_licitacion_validation(self):
        """Test validation of licitaciones with various incomplete data"""
        test_cases = [
            # Minimal valid licitacion
            ({
                'titulo': 'Test Licitación',
                'organismo': 'Test Organismo',
                'fecha_apertura': '29/11/2024'
            }, True),
            
            # Missing critical fields
            ({
                'descripcion': 'Some description'
            }, False),
            
            # Invalid date formats
            ({
                'titulo': 'Test Licitación',
                'organismo': 'Test Organismo',
                'fecha_apertura': '1-14-05'
            }, True),  # Now uses current date if parsing fails
            
            # Licitacion with fallback date
            ({
                'titulo': 'Test Licitación',
                'organismo': 'Test Organismo',
                'fecha_apertura': '29/11/2024',
                'fecha_publicacion': '1-14-05'
            }, True)
        ]
        
        for licitacion, expected_validity in test_cases:
            is_valid = self.template.validate_licitacion(licitacion)
            self.assertEqual(is_valid, expected_validity, 
                             f"Validation failed for {licitacion}")

    def test_standardization(self):
        """Test standardization of licitaciones with incomplete data"""
        test_cases = [
            # Minimal licitacion
            {
                'titulo': 'Test Licitación',
                'url_fuente': 'https://test.com'
            },
            
            # Licitacion with partial data
            {
                'titulo': 'Servicio de Mantenimiento',
                'fecha_apertura': '29/11/2024'
            },
            
            # Licitacion with problematic date
            {
                'titulo': 'Adquisición de Equipos',
                'fecha_apertura': '75-08-01',
                'monto': '42,000'
            }
        ]
        
        for licitacion in test_cases:
            # Standardize the licitacion
            standardized = self.template.standardize_licitacion(licitacion)
            
            # Assertions for standardized licitacion
            self.assertIn('titulo', standardized)
            self.assertIn('estado', standardized)
            self.assertIn('organismo', standardized)
            self.assertIn('id', standardized)
            
            # Check date parsing
            if 'fecha_apertura' in licitacion:
                self.assertIn('fecha_apertura', standardized)
            
            # Check monetary fields
            if 'monto' in licitacion:
                self.assertIsInstance(standardized.get('monto'), float)

def run_tests():
    """Run the tests and print results"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLicitacionesTemplate)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return True if all tests pass, False otherwise
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
