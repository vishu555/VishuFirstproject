#!/usr/bin/env python3

import requests
import json
import sys
import time
from datetime import datetime, timedelta

# Backend URL from frontend/.env
BACKEND_URL = "https://spend-smart-575.preview.emergentagent.com/api"

class ExpenseManagerTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.access_token = None
        self.user_data = None
        self.created_items = {
            'income': [],
            'expenses': [],
            'budgets': []
        }
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'failures': []
        }

    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition and track results"""
        self.test_results['total'] += 1
        if condition:
            self.test_results['passed'] += 1
            self.log(f"✅ {test_name}", "PASS")
            return True
        else:
            self.test_results['failed'] += 1
            self.test_results['failures'].append(f"{test_name}: {error_msg}")
            self.log(f"❌ {test_name} - {error_msg}", "FAIL")
            return False

    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if we have token
        if self.access_token and headers:
            headers['Authorization'] = f"Bearer {self.access_token}"
        elif self.access_token:
            headers = {'Authorization': f"Bearer {self.access_token}"}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            self.log(f"Request error for {method} {url}: {str(e)}", "ERROR")
            return None

    def test_user_registration(self):
        """Test user registration"""
        self.log("=== Testing User Registration ===")
        
        # Generate unique email for testing
        timestamp = int(time.time())
        test_user = {
            "name": "John Doe",
            "email": f"john.doe.{timestamp}@example.com",
            "password": "securePassword123"
        }
        
        response = self.make_request('POST', '/auth/register', test_user)
        
        if not response:
            self.assert_test(False, "User Registration - Request Failed", "No response received")
            return
            
        success = response.status_code == 200
        self.assert_test(success, f"User Registration - Status Code ({response.status_code})", 
                        f"Expected 200, got {response.status_code}")
        
        if success:
            try:
                data = response.json()
                self.assert_test('access_token' in data, "User Registration - Access Token Present")
                self.assert_test('user' in data, "User Registration - User Object Present")
                self.assert_test(data.get('token_type') == 'bearer', "User Registration - Token Type")
                
                if 'access_token' in data:
                    self.access_token = data['access_token']
                if 'user' in data:
                    self.user_data = data['user']
                    
                self.log(f"User registered successfully: {self.user_data.get('email')}")
                
            except json.JSONDecodeError:
                self.assert_test(False, "User Registration - JSON Response", "Invalid JSON response")
        else:
            self.log(f"Registration failed: {response.text}")

    def test_user_login(self):
        """Test user login with registered credentials"""
        self.log("=== Testing User Login ===")
        
        if not self.user_data:
            self.log("Skipping login test - no user data from registration", "WARN")
            return
            
        login_data = {
            "email": self.user_data['email'],
            "password": "securePassword123"
        }
        
        response = self.make_request('POST', '/auth/login', login_data)
        
        if not response:
            self.assert_test(False, "User Login - Request Failed", "No response received")
            return
            
        success = response.status_code == 200
        self.assert_test(success, f"User Login - Status Code ({response.status_code})",
                        f"Expected 200, got {response.status_code}")
        
        if success:
            try:
                data = response.json()
                self.assert_test('access_token' in data, "User Login - Access Token Present")
                self.assert_test('user' in data, "User Login - User Object Present")
                self.assert_test(data.get('token_type') == 'bearer', "User Login - Token Type")
                
                # Update token from login (should be same as registration)
                if 'access_token' in data:
                    self.access_token = data['access_token']
                    
            except json.JSONDecodeError:
                self.assert_test(False, "User Login - JSON Response", "Invalid JSON response")
        else:
            self.log(f"Login failed: {response.text}")

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        self.log("=== Testing Invalid Login ===")
        
        invalid_login = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = self.make_request('POST', '/auth/login', invalid_login)
        
        if response:
            # Should return 401 for invalid credentials
            self.assert_test(response.status_code == 401, 
                           f"Invalid Login - Status Code ({response.status_code})",
                           f"Expected 401, got {response.status_code}")

    def test_income_management(self):
        """Test income CRUD operations"""
        self.log("=== Testing Income Management ===")
        
        if not self.access_token:
            self.log("Skipping income test - no access token", "WARN")
            return
            
        # Test creating income
        income_data = {
            "source": "Salary",
            "amount": 5000.00,
            "date": "2024-01-15",
            "notes": "Monthly salary"
        }
        
        response = self.make_request('POST', '/income', income_data)
        
        if not response:
            self.assert_test(False, "Create Income - Request Failed", "No response received")
            return
            
        success = response.status_code == 200
        self.assert_test(success, f"Create Income - Status Code ({response.status_code})",
                        f"Expected 200, got {response.status_code}")
        
        income_id = None
        if success:
            try:
                data = response.json()
                self.assert_test('id' in data, "Create Income - ID Present")
                self.assert_test(data.get('source') == income_data['source'], "Create Income - Source Match")
                self.assert_test(data.get('amount') == income_data['amount'], "Create Income - Amount Match")
                income_id = data.get('id')
                if income_id:
                    self.created_items['income'].append(income_id)
                    
            except json.JSONDecodeError:
                self.assert_test(False, "Create Income - JSON Response", "Invalid JSON response")
        
        # Test getting income list
        response = self.make_request('GET', '/income')
        
        if response:
            success = response.status_code == 200
            self.assert_test(success, f"Get Income List - Status Code ({response.status_code})")
            
            if success:
                try:
                    data = response.json()
                    self.assert_test(isinstance(data, list), "Get Income List - Returns Array")
                    if isinstance(data, list) and len(data) > 0:
                        self.assert_test('id' in data[0], "Get Income List - Items Have ID")
                        self.assert_test('source' in data[0], "Get Income List - Items Have Source")
                        self.assert_test('amount' in data[0], "Get Income List - Items Have Amount")
                except json.JSONDecodeError:
                    self.assert_test(False, "Get Income List - JSON Response", "Invalid JSON response")
        
        # Test creating another income with different source
        business_income = {
            "source": "Business",
            "amount": 2500.00,
            "date": "2024-01-10", 
            "notes": "Consulting work"
        }
        
        response = self.make_request('POST', '/income', business_income)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get('id'):
                    self.created_items['income'].append(data['id'])
            except:
                pass
                
        # Test deleting income
        if income_id:
            response = self.make_request('DELETE', f'/income/{income_id}')
            if response:
                success = response.status_code == 200
                self.assert_test(success, f"Delete Income - Status Code ({response.status_code})")
                if success:
                    self.created_items['income'].remove(income_id)

    def test_expense_management(self):
        """Test expense CRUD operations"""
        self.log("=== Testing Expense Management ===")
        
        if not self.access_token:
            self.log("Skipping expense test - no access token", "WARN")
            return
            
        # Test creating expense
        expense_data = {
            "amount": 150.00,
            "category": "Food",
            "date": "2024-01-15",
            "notes": "Grocery shopping"
        }
        
        response = self.make_request('POST', '/expenses', expense_data)
        
        if not response:
            self.assert_test(False, "Create Expense - Request Failed", "No response received")
            return
            
        success = response.status_code == 200
        self.assert_test(success, f"Create Expense - Status Code ({response.status_code})")
        
        expense_id = None
        if success:
            try:
                data = response.json()
                self.assert_test('id' in data, "Create Expense - ID Present")
                self.assert_test(data.get('category') == expense_data['category'], "Create Expense - Category Match")
                self.assert_test(data.get('amount') == expense_data['amount'], "Create Expense - Amount Match")
                expense_id = data.get('id')
                if expense_id:
                    self.created_items['expenses'].append(expense_id)
                    
            except json.JSONDecodeError:
                self.assert_test(False, "Create Expense - JSON Response", "Invalid JSON response")
        
        # Test creating more expenses for different categories
        test_expenses = [
            {"amount": 50.0, "category": "Transport", "date": "2024-01-14", "notes": "Gas"},
            {"amount": 1200.0, "category": "Rent", "date": "2024-01-01", "notes": "Monthly rent"}
        ]
        
        for expense in test_expenses:
            response = self.make_request('POST', '/expenses', expense)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('id'):
                        self.created_items['expenses'].append(data['id'])
                except:
                    pass
        
        # Test getting expenses list
        response = self.make_request('GET', '/expenses')
        
        if response:
            success = response.status_code == 200
            self.assert_test(success, f"Get Expenses List - Status Code ({response.status_code})")
            
            if success:
                try:
                    data = response.json()
                    self.assert_test(isinstance(data, list), "Get Expenses List - Returns Array")
                    if isinstance(data, list) and len(data) > 0:
                        self.assert_test('id' in data[0], "Get Expenses List - Items Have ID")
                        self.assert_test('category' in data[0], "Get Expenses List - Items Have Category")
                        self.assert_test('amount' in data[0], "Get Expenses List - Items Have Amount")
                except json.JSONDecodeError:
                    self.assert_test(False, "Get Expenses List - JSON Response", "Invalid JSON response")
        
        # Test deleting expense
        if expense_id:
            response = self.make_request('DELETE', f'/expenses/{expense_id}')
            if response:
                success = response.status_code == 200
                self.assert_test(success, f"Delete Expense - Status Code ({response.status_code})")
                if success and expense_id in self.created_items['expenses']:
                    self.created_items['expenses'].remove(expense_id)

    def test_budget_management(self):
        """Test budget CRUD operations"""
        self.log("=== Testing Budget Management ===")
        
        if not self.access_token:
            self.log("Skipping budget test - no access token", "WARN")
            return
            
        # Test creating budget
        budget_data = {
            "category": "Food",
            "limit": 500.00,
            "period": "monthly"
        }
        
        response = self.make_request('POST', '/budget', budget_data)
        
        if not response:
            self.assert_test(False, "Create Budget - Request Failed", "No response received")
            return
            
        success = response.status_code == 200
        self.assert_test(success, f"Create Budget - Status Code ({response.status_code})")
        
        budget_id = None
        if success:
            try:
                data = response.json()
                self.assert_test('id' in data, "Create Budget - ID Present")
                self.assert_test(data.get('category') == budget_data['category'], "Create Budget - Category Match")
                self.assert_test(data.get('limit') == budget_data['limit'], "Create Budget - Limit Match")
                budget_id = data.get('id')
                if budget_id:
                    self.created_items['budgets'].append(budget_id)
                    
            except json.JSONDecodeError:
                self.assert_test(False, "Create Budget - JSON Response", "Invalid JSON response")
        
        # Test creating budgets for other categories
        other_budgets = [
            {"category": "Transport", "limit": 200.00, "period": "monthly"},
            {"category": "Rent", "limit": 1300.00, "period": "monthly"}
        ]
        
        for budget in other_budgets:
            response = self.make_request('POST', '/budget', budget)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('id'):
                        self.created_items['budgets'].append(data['id'])
                except:
                    pass
        
        # Test getting budgets list
        response = self.make_request('GET', '/budget')
        
        if response:
            success = response.status_code == 200
            self.assert_test(success, f"Get Budget List - Status Code ({response.status_code})")
            
            if success:
                try:
                    data = response.json()
                    self.assert_test(isinstance(data, list), "Get Budget List - Returns Array")
                    if isinstance(data, list) and len(data) > 0:
                        self.assert_test('id' in data[0], "Get Budget List - Items Have ID")
                        self.assert_test('category' in data[0], "Get Budget List - Items Have Category")
                        self.assert_test('limit' in data[0], "Get Budget List - Items Have Limit")
                        self.assert_test('spent' in data[0], "Get Budget List - Items Have Spent Amount")
                        
                        # Check if spent calculation is working
                        food_budget = next((b for b in data if b['category'] == 'Food'), None)
                        if food_budget:
                            spent_amount = food_budget.get('spent', 0)
                            self.assert_test(isinstance(spent_amount, (int, float)), 
                                           "Budget Spent Calculation - Is Numeric")
                            
                except json.JSONDecodeError:
                    self.assert_test(False, "Get Budget List - JSON Response", "Invalid JSON response")
        
        # Test updating existing budget (same category)
        update_budget = {
            "category": "Food", 
            "limit": 600.00,
            "period": "monthly"
        }
        
        response = self.make_request('POST', '/budget', update_budget)
        if response:
            success = response.status_code == 200
            self.assert_test(success, f"Update Budget - Status Code ({response.status_code})")
        
        # Test deleting budget
        if budget_id:
            response = self.make_request('DELETE', f'/budget/{budget_id}')
            if response:
                success = response.status_code == 200
                self.assert_test(success, f"Delete Budget - Status Code ({response.status_code})")
                if success and budget_id in self.created_items['budgets']:
                    self.created_items['budgets'].remove(budget_id)

    def test_analytics(self):
        """Test analytics endpoints"""
        self.log("=== Testing Analytics ===")
        
        if not self.access_token:
            self.log("Skipping analytics test - no access token", "WARN")
            return
            
        # Test analytics summary
        response = self.make_request('GET', '/analytics/summary')
        
        if response:
            success = response.status_code == 200
            self.assert_test(success, f"Analytics Summary - Status Code ({response.status_code})")
            
            if success:
                try:
                    data = response.json()
                    required_fields = ['total_income', 'total_expenses', 'remaining_balance', 
                                     'monthly_income', 'monthly_expenses', 'savings_rate']
                    
                    for field in required_fields:
                        self.assert_test(field in data, f"Analytics Summary - {field} Present")
                        if field in data:
                            self.assert_test(isinstance(data[field], (int, float)), 
                                           f"Analytics Summary - {field} Is Numeric")
                    
                    # Validate calculations
                    if all(field in data for field in ['total_income', 'total_expenses', 'remaining_balance']):
                        expected_balance = data['total_income'] - data['total_expenses']
                        actual_balance = data['remaining_balance']
                        self.assert_test(abs(expected_balance - actual_balance) < 0.01,
                                       "Analytics Summary - Balance Calculation Correct")
                        
                except json.JSONDecodeError:
                    self.assert_test(False, "Analytics Summary - JSON Response", "Invalid JSON response")
        
        # Test category breakdown
        response = self.make_request('GET', '/analytics/category-breakdown')
        
        if response:
            success = response.status_code == 200
            self.assert_test(success, f"Category Breakdown - Status Code ({response.status_code})")
            
            if success:
                try:
                    data = response.json()
                    self.assert_test(isinstance(data, list), "Category Breakdown - Returns Array")
                    
                    if isinstance(data, list) and len(data) > 0:
                        category = data[0]
                        required_fields = ['category', 'amount', 'percentage', 'budget_limit', 'over_budget']
                        
                        for field in required_fields:
                            self.assert_test(field in category, f"Category Breakdown - {field} Present")
                        
                        # Validate percentage calculation
                        if 'percentage' in category:
                            self.assert_test(isinstance(category['percentage'], (int, float)),
                                           "Category Breakdown - Percentage Is Numeric")
                            self.assert_test(0 <= category['percentage'] <= 100,
                                           "Category Breakdown - Percentage In Valid Range")
                        
                except json.JSONDecodeError:
                    self.assert_test(False, "Category Breakdown - JSON Response", "Invalid JSON response")
        
        # Test monthly trend
        response = self.make_request('GET', '/analytics/monthly-trend')
        
        if response:
            success = response.status_code == 200
            self.assert_test(success, f"Monthly Trend - Status Code ({response.status_code})")
            
            if success:
                try:
                    data = response.json()
                    self.assert_test(isinstance(data, list), "Monthly Trend - Returns Array")
                    
                    if isinstance(data, list) and len(data) > 0:
                        month_data = data[0]
                        required_fields = ['month', 'income', 'expenses']
                        
                        for field in required_fields:
                            self.assert_test(field in month_data, f"Monthly Trend - {field} Present")
                            
                except json.JSONDecodeError:
                    self.assert_test(False, "Monthly Trend - JSON Response", "Invalid JSON response")

    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        self.log("=== Testing Authentication Requirements ===")
        
        # Temporarily remove token
        original_token = self.access_token
        self.access_token = None
        
        protected_endpoints = [
            ('GET', '/income'),
            ('POST', '/income'),
            ('GET', '/expenses'),
            ('POST', '/expenses'),
            ('GET', '/budget'),
            ('POST', '/budget'),
            ('GET', '/analytics/summary'),
            ('GET', '/analytics/category-breakdown'),
            ('GET', '/analytics/monthly-trend')
        ]
        
        for method, endpoint in protected_endpoints:
            response = self.make_request(method, endpoint, {})
            if response:
                # Accept both 401 and 403 as valid authentication error responses
                auth_error = response.status_code in [401, 403]
                self.assert_test(auth_error,
                               f"Auth Required {method} {endpoint} - Status Code ({response.status_code})",
                               f"Expected 401 or 403, got {response.status_code}")
        
        # Test with invalid token
        self.access_token = "invalid_token_12345"
        
        response = self.make_request('GET', '/income')
        if response:
            # Accept both 401 and 403 as valid authentication error responses
            auth_error = response.status_code in [401, 403]
            self.assert_test(auth_error,
                           f"Invalid Token - Status Code ({response.status_code})",
                           f"Expected 401 or 403, got {response.status_code}")
        
        # Restore original token
        self.access_token = original_token

    def test_data_isolation(self):
        """Test that users only see their own data"""
        self.log("=== Testing Data Isolation ===")
        
        if not self.access_token:
            self.log("Skipping data isolation test - no access token", "WARN")
            return
        
        # Create a test expense for current user
        expense_data = {
            "amount": 25.00,
            "category": "Test",
            "date": "2024-01-16",
            "notes": "Data isolation test"
        }
        
        response = self.make_request('POST', '/expenses', expense_data)
        current_user_expense_id = None
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                current_user_expense_id = data.get('id')
                if current_user_expense_id:
                    self.created_items['expenses'].append(current_user_expense_id)
            except:
                pass
        
        # Get expenses list - should only contain current user's expenses
        response = self.make_request('GET', '/expenses')
        
        if response and response.status_code == 200:
            try:
                expenses = response.json()
                self.assert_test(isinstance(expenses, list), "Data Isolation - Expenses List Type")
                
                # All expenses should belong to current user (no user_id field should be exposed)
                for expense in expenses:
                    self.assert_test('user_id' not in expense, 
                                   "Data Isolation - User ID Not Exposed in Response")
                    
            except json.JSONDecodeError:
                self.assert_test(False, "Data Isolation - JSON Response", "Invalid JSON response")

    def cleanup_test_data(self):
        """Clean up created test data"""
        self.log("=== Cleaning Up Test Data ===")
        
        if not self.access_token:
            self.log("Skipping cleanup - no access token", "WARN")
            return
        
        # Delete created income entries
        for income_id in self.created_items['income']:
            response = self.make_request('DELETE', f'/income/{income_id}')
            if response and response.status_code == 200:
                self.log(f"Deleted income {income_id}")
        
        # Delete created expense entries
        for expense_id in self.created_items['expenses']:
            response = self.make_request('DELETE', f'/expenses/{expense_id}')
            if response and response.status_code == 200:
                self.log(f"Deleted expense {expense_id}")
        
        # Delete created budgets
        for budget_id in self.created_items['budgets']:
            response = self.make_request('DELETE', f'/budget/{budget_id}')
            if response and response.status_code == 200:
                self.log(f"Deleted budget {budget_id}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("=" * 60)
        self.log("STARTING SMART EXPENSE MANAGER BACKEND API TESTS")
        self.log(f"Backend URL: {self.base_url}")
        self.log("=" * 60)
        
        try:
            # Authentication tests
            self.test_user_registration()
            self.test_user_login()
            self.test_invalid_login()
            
            # Main functionality tests
            self.test_income_management()
            self.test_expense_management() 
            self.test_budget_management()
            self.test_analytics()
            
            # Security tests
            self.test_authentication_required()
            self.test_data_isolation()
            
            # Cleanup
            self.cleanup_test_data()
            
        except Exception as e:
            self.log(f"Unexpected error during testing: {str(e)}", "ERROR")
            
        finally:
            self.print_test_summary()

    def print_test_summary(self):
        """Print final test results"""
        self.log("=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)
        
        total = self.test_results['total']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        
        if failed > 0:
            self.log("\nFAILURES:")
            for failure in self.test_results['failures']:
                self.log(f"  - {failure}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        self.log(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED!")
            return True
        else:
            self.log(f"💥 {failed} TESTS FAILED")
            return False

if __name__ == "__main__":
    tester = ExpenseManagerTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)