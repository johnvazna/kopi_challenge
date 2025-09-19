#!/usr/bin/env python3
"""
Demo script for AI integration capabilities.
This script demonstrates the key features of the AI-powered debate chatbot.
"""

import requests
import time

class DebateDemo:
    """Demo class for showcasing AI integration features"""
    
    def __init__(self, api_url: str = None):
        from config import get_config
        self.api_url = api_url or get_config().get_test_base_url()
        self.conversation_id = None
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f"{title}")
        print("=" * 60)
    
    def print_message(self, role: str, message: str, delay: float = 0.5):
        """Print a formatted message with delay"""
        if role == "user":
            print(f"\nUser: {message}")
        else:
            print(f"\nBot: {message}")
        
        if delay > 0:
            time.sleep(delay)
    
    def demo_ai_connection(self):
        """Demo 1: AI Service Connection"""
        self.print_header("Demo 1: AI Service Connection")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                print("AI connection successful")
                print("Model: Llama 3.1 via Ollama")
                print("Status: Connected and running")
                return True
            else:
                print("Connection error")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return False
    
    def demo_personality(self):
        """Demo 2: AI Personality"""
        self.print_header("Demo 2: AI Personality")
        
        try:
            response = requests.get(f"{self.api_url}/personality", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Personality: {data['personality']}")
                print(f"Description: {data['description']}")
                print(f"Topic: {data['current_topic']}")
                print(f"Position: {data['position']}")
                return True
            else:
                print("Error getting personality")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False
    
    def demo_new_conversation(self):
        """Demo 3: New AI Conversation"""
        self.print_header("Demo 3: New AI Conversation")
        
        user_message = "Hello! Let's debate about pineapple on pizza!"
        self.print_message("user", user_message)
        
        print("\nGenerating AI response...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": user_message},
                timeout=self.config.TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data["conversation_id"]
                
                end_time = time.time()
                response_time = end_time - start_time
                
                bot_message = data["message"][-1]["message"]
                self.print_message("bot", bot_message)
                
                print(f"\nResponse time: {response_time:.2f} seconds")
                print(f"Conversation ID: {self.conversation_id}")
                
                return True
            else:
                print(f"Conversation error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False
    
    def demo_continued_conversation(self):
        """Demo 4: Continued AI Conversation"""
        if not self.conversation_id:
            print("No active conversation")
            return False
        
        self.print_header("Demo 4: Continued AI Conversation")
        
        user_message = "But pineapple shouldn't be on pizza, it's too sweet!"
        self.print_message("user", user_message)
        
        print("\nGenerating AI response...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "message": user_message,
                    "conversation_id": self.conversation_id
                },
                timeout=self.config.TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                end_time = time.time()
                response_time = end_time - start_time
                
                bot_message = data["message"][-1]["message"]
                self.print_message("bot", bot_message)
                
                print(f"\nResponse time: {response_time:.2f} seconds")
                
                return True
            else:
                print(f"Conversation error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False
    
    def demo_conversation_history(self):
        """Demo 5: Conversation History"""
        if not self.conversation_id:
            print("No active conversation")
            return False
        
        self.print_header("Demo 5: Conversation History")
        
        try:
            response = requests.get(
                f"{self.api_url}/chat/{self.conversation_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Conversation ID: {data['conversation_id']}")
                print(f"Topic: {data['topic']}")
                print(f"Stance: {data['stance']}")
                print(f"Total messages: {data['total_messages']}")
                print(f"Created: {data['created_at']}")
                print(f"Updated: {data['updated_at']}")
                
                print("\nComplete history:")
                for i, msg in enumerate(data['messages'], 1):
                    role = "User" if msg['role'] == 'user' else "Bot"
                    print(f"  {i}. {role}: {msg['message'][:100]}...")
                
                return True
            else:
                print(f"Error getting history: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False
    
    def demo_stats(self):
        """Demo 6: System Stats"""
        self.print_header("Demo 6: System Statistics")
        
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"API Version: {data['api_version']}")
                print(f"Storage Type: {data['storage']['type']}")
                print(f"Active Conversations: {data['storage']['active_conversations']}")
                print(f"Total Messages: {data['storage']['total_messages']}")
                
                config = data['config']
                print(f"Max Exchanges: {config['max_history_exchanges']}")
                print(f"Max Tokens: {config['max_response_tokens']}")
                
                return True
            else:
                print(f"Error getting statistics: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False
    
    def run_full_demo(self):
        """Run the complete demo"""
        print("AI Integration Demo - Debate Chatbot")
        print("====================================")
        
        demos = [
            self.demo_ai_connection,
            self.demo_personality,
            self.demo_new_conversation,
            self.demo_continued_conversation,
            self.demo_conversation_history,
            self.demo_stats
        ]
        
        results = []
        for demo in demos:
            try:
                result = demo()
                results.append(result)
                time.sleep(1)
            except Exception as e:
                print(f"Demo error: {e}")
                results.append(False)
        
        print("\n" + "=" * 60)
        print("Demo Summary")
        print("=" * 60)
        
        demo_names = [
            "AI Connection",
            "Personality",
            "New Conversation",
            "Continued Conversation",
            "History",
            "Statistics"
        ]
        
        for i, (name, result) in enumerate(zip(demo_names, results)):
            status = "SUCCESS" if result else "FAILED"
            print(f"{i+1}. {name}: {status}")
        
        successful = sum(results)
        total = len(results)
        print(f"\nTotal: {successful}/{total} demos successful")
        
        if successful == total:
            print("All demos were successful!")
        else:
            print("Some demos failed. Check the configuration.")
    
    def run_quick_demo(self):
        """Run a quick demo with essential features"""
        print("Quick Demo - AI Integration")
        print("===========================")
        
        if not self.demo_ai_connection():
            print("Could not connect to AI service")
            return
        
        if not self.demo_personality():
            print("Could not get personality")
            return
        
        if not self.demo_new_conversation():
            print("Could not create new conversation")
            return
        
        print("\nQuick demo completed successfully!")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Integration Demo")
    parser.add_argument("--url", help="API URL (defaults to config)")
    parser.add_argument("--quick", action="store_true", help="Run quick demo")
    
    args = parser.parse_args()
    
    demo = DebateDemo(args.url)
    
    if args.quick:
        demo.run_quick_demo()
    else:
        demo.run_full_demo()

if __name__ == "__main__":
    main()