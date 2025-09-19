#!/usr/bin/env python3
"""
Load and Performance Tests for Kopi Challenge AI-Powered Debate Chatbot
Tests system performance under various load conditions
"""

import sys
import time
import requests
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config

class LoadPerformanceTester:
    """Load and performance testing for the debate chatbot"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.get_test_base_url()
        self.results = []
        
    def single_request_test(self, message, conversation_id=None):
        """Test a single request and measure performance"""
        start_time = time.time()
        
        try:
            request_data = {
                "message": message,
            }
            
            if conversation_id:
                request_data["conversation_id"] = conversation_id
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": response.status_code == 200,
                "response_time": response_time,
                "status_code": response.status_code,
                "conversation_id": response.json().get("conversation_id") if response.status_code == 200 else None
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": end_time - start_time,
                "error": str(e),
                "conversation_id": None
            }
    
    def test_response_times(self):
        """Test response times for different types of requests"""
        print("\nTesting Response Times")
        print("-" * 30)
        
        test_cases = [
            ("New conversation", "Let's start a new debate"),
            ("Topic change", "Let's talk about coffee vs tea instead"),
            ("Debate continuation", "I disagree with your stance"),
            ("Question", "What evidence do you have?"),
            ("Challenge", "That's not convincing enough"),
        ]
        
        conversation_id = None
        results = []
        
        for test_name, message in test_cases:
            print(f"Testing: {test_name}")
            
            result = self.single_request_test(message, conversation_id)
            results.append((test_name, result))
            
            if result["success"]:
                conversation_id = result["conversation_id"]
                print(f"Success: {result['response_time']:.2f}s")
            else:
                print(f"Failed: {result.get('error', 'Unknown error')}")
        
        successful_times = [r[1]["response_time"] for r in results if r[1]["success"]]
        
        if successful_times:
            avg_time = statistics.mean(successful_times)
            min_time = min(successful_times)
            max_time = max(successful_times)
            
            print(f"\nResponse Time Statistics:")
            print(f"Average: {avg_time:.2f}s")
            print(f"Minimum: {min_time:.2f}s")
            print(f"Maximum: {max_time:.2f}s")
            
            return avg_time < 10
        
        return False
    
    def test_concurrent_users(self, num_users=5, requests_per_user=3):
        """Test system with multiple concurrent users"""
        print(f"\nTesting Concurrent Users ({num_users} users, {requests_per_user} requests each)")
        print("-" * 60)
        
        def user_simulation(user_id):
            """Simulate a single user's session"""
            user_results = []
            conversation_id = None
            
            messages = [
                f"User {user_id}: Let's start a debate",
                f"User {user_id}: I disagree with your stance",
                f"User {user_id}: Can you convince me otherwise?"
            ]
            
            for i, message in enumerate(messages[:requests_per_user]):
                result = self.single_request_test(message, conversation_id)
                result["user_id"] = user_id
                result["request_id"] = i
                user_results.append(result)
                
                if result["success"]:
                    conversation_id = result["conversation_id"]
            
            return user_results
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_simulation, i) for i in range(num_users)]
            all_results = []
            
            for future in as_completed(futures):
                user_results = future.result()
                all_results.extend(user_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]
        
        success_rate = len(successful_requests) / len(all_results) * 100
        
        print(f"Concurrent User Results:")
        print(f"Total requests: {len(all_results)}")
        print(f"Successful: {len(successful_requests)}")
        print(f"Failed: {len(failed_requests)}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Total time: {total_time:.2f}s")
        print(f"Requests/second: {len(all_results)/total_time:.2f}")
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            print(f"Average response time: {avg_response_time:.2f}s")
        
        return success_rate >= 80
    
    def test_sustained_load(self, duration_seconds=60, requests_per_second=1):
        """Test system under sustained load"""
        print(f"\nTesting Sustained Load ({duration_seconds}s, {requests_per_second} req/s)")
        print("-" * 50)
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        results = []
        request_count = 0
        
        print("Starting sustained load test...")
        
        while time.time() < end_time:
            batch_start = time.time()
            
            for _ in range(requests_per_second):
                message = f"Sustained load test request {request_count}"
                result = self.single_request_test(message)
                result["request_id"] = request_count
                results.append(result)
                request_count += 1
            
            batch_time = time.time() - batch_start
            if batch_time < 1.0:
                time.sleep(1.0 - batch_time)
        
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = len(successful_requests) / len(results) * 100
        actual_duration = time.time() - start_time
        actual_rps = len(results) / actual_duration
        
        print(f"Sustained Load Results:")
        print(f"Duration: {actual_duration:.2f}s")
        print(f"Total requests: {len(results)}")
        print(f"Target RPS: {requests_per_second}")
        print(f"Actual RPS: {actual_rps:.2f}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            
            print(f"Average response time: {avg_response_time:.2f}s")
            print(f"95th percentile: {p95_response_time:.2f}s")
        
        return success_rate >= 90
    
    def test_memory_usage(self):
        """Test memory usage and cleanup"""
        print("\nTesting Memory Usage")
        print("-" * 25)
        
        conversation_ids = []
        
        print("Creating multiple conversations...")
        for i in range(10):
            result = self.single_request_test(f"Memory test conversation {i}")
            if result["success"]:
                conversation_ids.append(result["conversation_id"])
        
        print(f"Created {len(conversation_ids)} conversations")
        
        print("Testing conversation retrieval...")
        retrieval_success = 0
        
        for conv_id in conversation_ids[:5]:
            try:
                response = requests.get(f"{self.base_url}/chat/{conv_id}", timeout=self.config.TEST_TIMEOUT)
                if response.status_code == 200:
                    retrieval_success += 1
            except:
                pass
        
        print(f"Retrieved {retrieval_success}/5 conversations")
        
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=self.config.TEST_TIMEOUT)
            if response.status_code == 200:
                stats = response.json()
                print(f"Stats endpoint working: {stats}")
            else:
                print("Stats endpoint failed")
        except Exception as e:
            print(f"Stats endpoint error: {e}")
        
        return retrieval_success >= 4
    
    def test_error_recovery(self):
        """Test system error recovery"""
        print("\nTesting Error Recovery")
        print("-" * 30)
        
        error_tests = [
            ("Invalid JSON", {"invalid": "json"}),
            ("Empty message", {"message": ""}),
            ("Very long message", {"message": "A" * 2000}),
            ("Special characters", {"message": "Special chars test"}),
            ("SQL injection attempt", {"message": "'; DROP TABLE users; --"}),
        ]
        
        recovery_success = 0
        
        for test_name, request_data in error_tests:
            print(f"Testing: {test_name}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.TEST_TIMEOUT
                )
                
                if response.status_code in [200, 400, 422]:
                    print(f"Handled gracefully: {response.status_code}")
                    recovery_success += 1
                else:
                    print(f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                print(f"Request failed: {e}")
        
        print("Testing normal operation after errors...")
        normal_result = self.single_request_test("Normal message after errors")
        
        if normal_result["success"]:
            print("Normal operation restored")
            recovery_success += 1
        else:
            print("Normal operation failed")
        
        return recovery_success >= 5
    
    def run_all_tests(self):
        """Run all load and performance tests"""
        print("Starting Load and Performance Tests")
        print("=" * 50)
        
        tests = [
            ("Response Times", self.test_response_times),
            ("Concurrent Users", self.test_concurrent_users),
            ("Sustained Load", self.test_sustained_load),
            ("Memory Usage", self.test_memory_usage),
            ("Error Recovery", self.test_error_recovery),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\nRunning: {test_name}")
                if test_func():
                    print(f"{test_name} PASSED")
                    passed += 1
                else:
                    print(f"{test_name} FAILED")
                    failed += 1
            except Exception as e:
                print(f"{test_name} FAILED with exception: {e}")
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"Load Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("All load tests passed! System is performant and robust.")
            return True
        else:
            print("Some load tests failed. System may need optimization.")
            return False

def main():
    """Main load test runner"""
    print("Kopi Challenge Load and Performance Tests")
    print("Testing system performance under various load conditions")
    print()
    
    tester = LoadPerformanceTester()
    success = tester.run_all_tests()
    
    if success:
        print("\nAll load tests successful!")
        sys.exit(0)
    else:
        print("\nSome load tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()