#!/usr/bin/env python3
"""
Manual API test script for AI integration.
This script tests the API endpoints with AI integration.
"""

import requests
import time
from typing import Dict

class APITester:
    """API tester for the Kopi Challenge chatbot"""
    
    def __init__(self, base_url: str = None):
        from config import get_config
        self.base_url = base_url or get_config().get_test_base_url()
        self.session = requests.Session()
        self.conversation_id = None
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint"""
        print("Testing health endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Health check passed: {data['status']}")
                return True
            else:
                print(f"  Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Health check error: {str(e)}")
            return False
    
    def test_personality_endpoint(self) -> bool:
        """Test personality endpoint"""
        print("\nTesting personality endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/personality")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Personality: {data['personality']}")
                print(f"  Topic: {data['current_topic']}")
                print(f"  Stance: {data['position']}")
                return True
            else:
                print(f"  Personality check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Personality check error: {str(e)}")
            return False
    
    def test_new_conversation(self) -> bool:
        """Test new conversation creation"""
        print("\nTesting new conversation...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json={"message": "Hello! Let's start a debate about pineapple on pizza!"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data["conversation_id"]
                
                print(f"  Conversation created: {self.conversation_id}")
                print(f"  Messages: {len(data['message'])}")
                
                if data['message']:
                    bot_message = data['message'][-1]['message']
                    print(f"  Bot response: {bot_message[:100]}...")
                
                return True
            else:
                print(f"  New conversation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  New conversation error: {str(e)}")
            return False
    
    def test_continued_conversation(self) -> bool:
        """Test continued conversation"""
        if not self.conversation_id:
            print("\nNo conversation ID available for continued conversation test")
            return False
        
        print("\nTesting continued conversation...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json={
                    "message": "I disagree! Pineapple doesn't belong on pizza!",
                    "conversation_id": self.conversation_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"  Conversation continued: {data['conversation_id']}")
                print(f"  Total messages: {len(data['message'])}")
                
                if data['message']:
                    bot_message = data['message'][-1]['message']
                    print(f"  Bot response: {bot_message[:100]}...")
                
                return True
            else:
                print(f"  Continued conversation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Continued conversation error: {str(e)}")
            return False
    
    def test_conversation_history(self) -> bool:
        """Test conversation history retrieval"""
        if not self.conversation_id:
            print("\nNo conversation ID available for history test")
            return False
        
        print("\nTesting conversation history...")
        
        try:
            response = self.session.get(f"{self.base_url}/chat/{self.conversation_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"  Conversation ID: {data['conversation_id']}")
                print(f"  Topic: {data['topic']}")
                print(f"  Stance: {data['stance']}")
                print(f"  Total messages: {data['total_messages']}")
                print(f"  Created: {data['created_at']}")
                
                return True
            else:
                print(f"  History retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  History retrieval error: {str(e)}")
            return False
    
    def test_stats_endpoint(self) -> bool:
        """Test stats endpoint"""
        print("\nTesting stats endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"  API Version: {data['api_version']}")
                print(f"  Storage Type: {data['storage']['type']}")
                print(f"  Active Conversations: {data['storage']['active_conversations']}")
                print(f"  Total Messages: {data['storage']['total_messages']}")
                
                return True
            else:
                print(f"  Stats check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Stats check error: {str(e)}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test root endpoint"""
        print("\nTesting root endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"  Message: {data['message']}")
                print(f"  Version: {data['version']}")
                print(f"  Available endpoints: {len(data['endpoints'])}")
                
                return True
            else:
                print(f"  Root check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Root check error: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\nTesting error handling...")
        
        try:
            response = self.session.get(f"{self.base_url}/chat/invalid-id")
            
            if response.status_code == 404:
                print("  Invalid conversation ID handled correctly (404)")
                return True
            else:
                print(f"  Unexpected response for invalid ID: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Error handling test error: {str(e)}")
            return False
    
    def test_performance(self) -> bool:
        """Test API performance"""
        print("\nTesting API performance...")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json={"message": "Quick performance test message"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"  Response time: {response_time:.2f} seconds")
                
                if response_time < 10:
                    print("  Performance: Good")
                    return True
                else:
                    print("  Performance: Slow")
                    return False
            else:
                print(f"  Performance test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Performance test error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all API tests"""
        print("Starting API Tests")
        print("==================")
        
        tests = [
            ("Health", self.test_health_endpoint),
            ("Personality", self.test_personality_endpoint),
            ("New Conversation", self.test_new_conversation),
            ("Continued Conversation", self.test_continued_conversation),
            ("Conversation History", self.test_conversation_history),
            ("Stats", self.test_stats_endpoint),
            ("Root", self.test_root_endpoint),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                time.sleep(0.5)
            except Exception as e:
                print(f"  Test {test_name} failed with exception: {str(e)}")
                results[test_name] = False
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("Test Results Summary")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "PASSED" if result else "FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("All tests passed! API is working correctly.")
        else:
            print("Some tests failed. Check the API configuration.")
        
        return passed == total


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Tester for Kopi Challenge")
    parser.add_argument("--url", help="API base URL (defaults to config)")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    
    if args.quick:
        print("Running Quick API Tests")
        print("======================")
        
        results = {
            "Health": tester.test_health_endpoint(),
            "Personality": tester.test_personality_endpoint(),
            "New Conversation": tester.test_new_conversation()
        }
        
        tester.print_summary(results)
    else:
        results = tester.run_all_tests()
        tester.print_summary(results)


if __name__ == "__main__":
    main()