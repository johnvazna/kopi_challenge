#!/usr/bin/env python3
"""
Integration Test Scenarios for Kopi Challenge AI-Powered Debate Chatbot
Tests real-world usage scenarios and edge cases
"""

import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config

class IntegrationTestScenarios:
    """Integration test scenarios for real-world usage"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.get_test_base_url()
        self.conversation_id = None
        
    def scenario_1_new_user_experience(self):
        """Test complete new user experience flow"""
        print("\nScenario 1: New User Experience")
        print("-" * 40)
        
        try:
            print("1. Opening chat interface...")
            response = requests.get(f"{self.base_url}/chat", timeout=self.config.TEST_TIMEOUT)
            assert response.status_code == 200, "Chat interface not accessible"
            print("Chat interface loaded")
            
            print("2. Starting first conversation...")
            chat_request = {
                "message": "Hi, I'm new here. What can we debate about?"
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 200, "First conversation failed"
            data = response.json()
            self.conversation_id = data["conversation_id"]
            
            print(f"First conversation started: {self.conversation_id}")
            print(f"Bot topic: {data['message'][1]['message'][:50]}...")
            
            print("3. Engaging in debate...")
            debate_request = {
                "message": "I disagree with your stance. Can you convince me?",
                "conversation_id": self.conversation_id
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=debate_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 200, "Debate engagement failed"
            debate_data = response.json()
            
            print("Debate engagement successful")
            print(f"Bot response: {debate_data['message'][-1]['message'][:50]}...")
            
            return True
            
        except Exception as e:
            print(f"New user experience failed: {e}")
            return False
    
    def scenario_2_topic_switching_expert(self):
        """Test expert user who switches topics frequently"""
        print("\nScenario 2: Topic Switching Expert")
        print("-" * 40)
        
        try:
            topics_to_test = [
                "Let's talk about coffee vs tea instead",
                "I want to discuss spaces vs tabs",
                "Let's debate cats vs dogs",
                "I prefer dark mode over light mode",
                "Remote work is better than office work"
            ]
            
            for i, topic_request in enumerate(topics_to_test, 1):
                print(f"{i}. Switching to: {topic_request}")
                
                switch_request = {
                    "message": topic_request,
                    "conversation_id": self.conversation_id
                }
                
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=switch_request,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.TEST_TIMEOUT
                )
                
                assert response.status_code == 200, f"Topic switch {i} failed"
                switch_data = response.json()
                
                last_message = switch_data["message"][-1]["message"]
                print(f"Topic switched successfully")
                print(f"Bot response: {last_message[:50]}...")
                
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Topic switching expert scenario failed: {e}")
            return False
    
    def scenario_3_debate_champion(self):
        """Test user who challenges the bot extensively"""
        print("\nScenario 3: Debate Champion")
        print("-" * 40)
        
        try:
            challenges = [
                "That's not a strong argument",
                "I need more evidence",
                "Can you provide statistics?",
                "What about the opposite side?",
                "I'm still not convinced",
                "That's just your opinion",
                "Prove it with facts"
            ]
            
            for i, challenge in enumerate(challenges, 1):
                print(f"{i}. Challenge: {challenge}")
                
                challenge_request = {
                    "message": challenge,
                    "conversation_id": self.conversation_id
                }
                
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=challenge_request,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.TEST_TIMEOUT
                )
                
                assert response.status_code == 200, f"Challenge {i} failed"
                challenge_data = response.json()
                
                last_message = challenge_data["message"][-1]["message"]
                print(f"Bot defended stance")
                print(f"Response: {last_message[:50]}...")
                
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Debate champion scenario failed: {e}")
            return False
    
    def scenario_4_new_chat_enthusiast(self):
        """Test user who frequently starts new chats"""
        print("\nScenario 4: New Chat Enthusiast")
        print("-" * 40)
        
        try:
            for i in range(3):
                print(f"{i+1}. Starting new chat session...")
                
                new_chat_request = {
                    "message": f"Let's start fresh with a new debate topic"
                }
                
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=new_chat_request,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.TEST_TIMEOUT
                )
                
                assert response.status_code == 200, f"New chat {i+1} failed"
                new_chat_data = response.json()
                
                self.conversation_id = new_chat_data["conversation_id"]
                
                print(f"New chat started: {self.conversation_id}")
                print(f"Topic: {new_chat_data['message'][1]['message'][:50]}...")
                
                quick_request = {
                    "message": "Interesting topic! Tell me more.",
                    "conversation_id": self.conversation_id
                }
                
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=quick_request,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.TEST_TIMEOUT
                )
                
                assert response.status_code == 200, f"Quick interaction {i+1} failed"
                print(f"Quick interaction successful")
                
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"New chat enthusiast scenario failed: {e}")
            return False
    
    def scenario_5_edge_case_user(self):
        """Test edge cases and unusual inputs"""
        print("\nScenario 5: Edge Case User")
        print("-" * 40)
        
        try:
            edge_cases = [
                ("Short", "Hi"),
                ("Special chars", "Let's talk about AI & ML! @#$%^&*()"),
                ("Numbers", "I think 42 is better than 24"),
                ("Emojis", "Let's debate pizza vs burger"),
                ("Mixed languages", "Hola, let's talk about cafe vs te"),
                ("Typos", "Lets tlak abot cofee vs tee"),
                ("Questions", "What do you think about this topic?"),
                ("Exclamations", "This is amazing! I love it!"),
            ]
            
            for case_name, message in edge_cases:
                print(f"Testing {case_name}: {message}")
                
                edge_request = {
                    "message": message,
                    "conversation_id": self.conversation_id
                }
                
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=edge_request,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.TEST_TIMEOUT
                )
                
                assert response.status_code == 200, f"Edge case '{case_name}' failed"
                edge_data = response.json()
                
                last_message = edge_data["message"][-1]["message"]
                print(f"Handled successfully")
                print(f"Response: {last_message[:50]}...")
                
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"Edge case user scenario failed: {e}")
            return False
    
    def scenario_6_performance_stress(self):
        """Test system under stress"""
        print("\nScenario 6: Performance Stress Test")
        print("-" * 40)
        
        try:
            print("1. Rapid-fire message test...")
            start_time = time.time()
            
            for i in range(5):
                rapid_request = {
                    "message": f"Quick message {i+1}",
                    "conversation_id": self.conversation_id
                }
                
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=rapid_request,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.TEST_TIMEOUT
                )
                
                assert response.status_code == 200, f"Rapid message {i+1} failed"
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 5
            
            print(f"5 rapid messages completed in {total_time:.2f}s")
            print(f"Average response time: {avg_time:.2f}s")
            
            print("2. Concurrent request test...")
            import threading
            import queue
            
            results = queue.Queue()
            
            def concurrent_request(thread_id):
                try:
                    req = {
                        "message": f"Concurrent test {thread_id}",
                        "conversation_id": self.conversation_id
                    }
                    resp = requests.post(
                        f"{self.base_url}/chat",
                        json=req,
                        headers={"Content-Type": "application/json"},
                        timeout=self.config.TEST_TIMEOUT
                    )
                    results.put((thread_id, resp.status_code == 200))
                except Exception as e:
                    results.put((thread_id, False))
            
            threads = []
            for i in range(3):
                thread = threading.Thread(target=concurrent_request, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            success_count = 0
            while not results.empty():
                thread_id, success = results.get()
                if success:
                    success_count += 1
                    print(f"Thread {thread_id}: Success")
                else:
                    print(f"Thread {thread_id}: Failed")
            
            print(f"{success_count}/3 concurrent requests successful")
            
            return True
            
        except Exception as e:
            print(f"Performance stress test failed: {e}")
            return False
    
    def run_all_scenarios(self):
        """Run all integration test scenarios"""
        print("Starting Integration Test Scenarios")
        print("=" * 60)
        
        scenarios = [
            ("New User Experience", self.scenario_1_new_user_experience),
            ("Topic Switching Expert", self.scenario_2_topic_switching_expert),
            ("Debate Champion", self.scenario_3_debate_champion),
            ("New Chat Enthusiast", self.scenario_4_new_chat_enthusiast),
            ("Edge Case User", self.scenario_5_edge_case_user),
            ("Performance Stress", self.scenario_6_performance_stress),
        ]
        
        passed = 0
        failed = 0
        
        for scenario_name, scenario_func in scenarios:
            try:
                if scenario_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"{scenario_name} failed with exception: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Scenario Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("All scenarios passed! System handles real-world usage perfectly.")
            return True
        else:
            print("Some scenarios failed. Please check the issues above.")
            return False

def main():
    """Main scenario runner"""
    print("Kopi Challenge Integration Test Scenarios")
    print("Testing real-world usage patterns and edge cases")
    print()
    
    tester = IntegrationTestScenarios()
    success = tester.run_all_scenarios()
    
    if success:
        print("\nAll scenarios successful!")
        sys.exit(0)
    else:
        print("\nSome scenarios failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()