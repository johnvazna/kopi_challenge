#!/usr/bin/env python3
"""
Master Test Runner for Kopi Challenge AI-Powered Debate Chatbot
Runs all test suites: unit tests, integration tests, and load tests
"""

import sys
import time
import subprocess
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config

class MasterTestRunner:
    """Master test runner for all test suites"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.get_test_base_url()
        self.test_results = {}
        
    def check_server_availability(self):
        """Check if the server is running and accessible"""
        print("Checking server availability...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("Server is running and accessible")
                return True
            else:
                print(f"Server returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Server not accessible: {e}")
            print(f"Make sure the server is running on port {self.config.PORT}")
            return False
    
    def run_test_suite(self, test_name, test_file, description):
        """Run a specific test suite"""
        print(f"\nRunning {test_name}")
        print("=" * 60)
        print(f"{description}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, test_file
            ], capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.test_results[test_name] = {
                "success": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
            if result.returncode == 0:
                print(f"{test_name} PASSED ({duration:.2f}s)")
                if result.stdout:
                    print("Output:")
                    print(result.stdout)
            else:
                print(f"{test_name} FAILED ({duration:.2f}s)")
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
                if result.stdout:
                    print("Output:")
                    print(result.stdout)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"{test_name} TIMED OUT (5 minutes)")
            self.test_results[test_name] = {
                "success": False,
                "duration": 300,
                "error": "Test timed out after 5 minutes"
            }
            return False
            
        except Exception as e:
            print(f"{test_name} CRASHED: {e}")
            self.test_results[test_name] = {
                "success": False,
                "duration": 0,
                "error": str(e)
            }
            return False
    
    def run_quick_smoke_test(self):
        """Run a quick smoke test to verify basic functionality"""
        print("\nQuick Smoke Test")
        print("-" * 30)
        
        try:
            endpoints = [
                ("/health", "Health check"),
                ("/personality", "Personality info"),
                ("/stats", "Statistics"),
            ]
            
            for endpoint, description in endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=self.config.TEST_TIMEOUT)
                if response.status_code == 200:
                    print(f"{description}: OK")
                else:
                    print(f"{description}: Failed ({response.status_code})")
                    return False
            
            chat_request = {
                "message": "Quick smoke test message"
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                print("Chat functionality: OK")
                return True
            else:
                print(f"Chat functionality: Failed ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"Smoke test failed: {e}")
            return False
    
    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\nTest Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Test Suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 40)
        
        for test_name, result in self.test_results.items():
            status = "PASSED" if result["success"] else "FAILED"
            duration = result.get("duration", 0)
            print(f"{test_name}: {status} ({duration:.2f}s)")
            
            if not result["success"] and "error" in result:
                print(f"  Error: {result['error']}")
        
        print("\nOverall Assessment:")
        if failed_tests == 0:
            print("ALL TESTS PASSED! System is fully functional and robust.")
            print("Ready for production use!")
        elif failed_tests <= total_tests // 2:
            print("Most tests passed. System is mostly functional.")
            print("Some issues need attention before production.")
        else:
            print("Multiple test failures. System needs significant work.")
            print("Not ready for production use.")
        
        return failed_tests == 0
    
    def run_all_tests(self):
        """Run all test suites"""
        print("Kopi Challenge Master Test Runner")
        print("Running comprehensive test suite for AI-powered debate chatbot")
        print("=" * 70)
        
        if not self.check_server_availability():
            print("\nCannot run tests - server not available")
            print("Please start the server first:")
            print("   cd /Users/jonathanvazquez/Documents/Cuenca/kopi-challenge")
            print("   source venv/bin/activate")
            print(f"   PORT={self.config.PORT} python src/main.py")
            return False
        
        if not self.run_quick_smoke_test():
            print("\nSmoke test failed - skipping other tests")
            return False
        
        test_suites = [
            {
                "name": "Comprehensive System Tests",
                "file": "test_comprehensive_system.py",
                "description": "Tests all major functionality including AI integration, topic switching, and web interface"
            },
            {
                "name": "Integration Test Scenarios",
                "file": "test_integration_scenarios.py",
                "description": "Tests real-world usage scenarios and edge cases"
            },
            {
                "name": "Load and Performance Tests",
                "file": "test_load_performance.py",
                "description": "Tests system performance under various load conditions"
            }
        ]
        
        for suite in test_suites:
            test_file = Path(__file__).parent / suite["file"]
            if test_file.exists():
                self.run_test_suite(
                    suite["name"],
                    str(test_file),
                    suite["description"]
                )
            else:
                print(f"Test file not found: {test_file}")
                self.test_results[suite["name"]] = {
                    "success": False,
                    "duration": 0,
                    "error": "Test file not found"
                }
        
        return self.generate_test_report()

def main():
    """Main test runner"""
    runner = MasterTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\nAll tests completed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()