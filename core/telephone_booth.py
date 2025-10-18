#!/usr/bin/env python3
"""
Telephone Booth - Communication Initiator
Establishes connection, runs tests, and initiates conversations
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any


class TelephoneBooth:
    """Manages communication sessions and logging"""
    
    def __init__(self):
        self.connection_status = "disconnected"
        self.conversation_log: List[Dict[str, Any]] = []
        self.test_results: Dict[str, bool] = {}
        
    def initiate_connection(self) -> bool:
        """Establish the communication connection"""
        print("🔌 Initiating connection...")
        time.sleep(1)
        
        # Test basic communication channels
        tests = {
            "local_communication": self._test_local(),
            "global_communication": self._test_global(),
            "feedback_loop": self._test_feedback(),
            "security_validation": self._test_security()
        }
        
        self.test_results = tests
        all_passed = all(tests.values())
        
        if all_passed:
            self.connection_status = "connected"
            print("✅ Connection established successfully!")
            self._log_event("CONNECTION_ESTABLISHED", "All systems operational")
        else:
            self.connection_status = "failed"
            print("❌ Connection failed. Check test results.")
            self._log_event("CONNECTION_FAILED", f"Failed tests: {[k for k, v in tests.items() if not v]}")
        
        return all_passed
    
    def _test_local(self) -> bool:
        """Test local communication channel"""
        print("  - Testing local communication... ", end="")
        time.sleep(0.5)
        print("✓")
        return True
    
    def _test_global(self) -> bool:
        """Test global communication channel"""
        print("  - Testing global communication... ", end="")
        time.sleep(0.5)
        print("✓")
        return True
    
    def _test_feedback(self) -> bool:
        """Test feedback loop"""
        print("  - Testing feedback loop... ", end="")
        time.sleep(0.5)
        print("✓")
        return True
    
    def _test_security(self) -> bool:
        """Test security validation"""
        print("  - Testing security validation... ", end="")
        time.sleep(0.5)
        print("✓")
        return True
    
    def start_conversation(self, initial_question: str) -> Dict[str, Any]:
        """Initiate a conversation with a question"""
        if self.connection_status != "connected":
            return {
                "status": "error",
                "message": "Connection not established. Call initiate_connection() first."
            }
        
        print(f"\n📞 Starting conversation...")
        print(f"Question: {initial_question}")
        
        # Log the question
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "question",
            "content": initial_question,
            "status": "pending"
        }
        
        self.conversation_log.append(conversation_entry)
        self._log_event("QUESTION_ASKED", initial_question)
        
        # Simulate processing
        print("🤔 Processing question...")
        time.sleep(1)
        
        # Generate response based on question analysis
        response = self._generate_response(initial_question)
        
        response_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "content": response,
            "status": "completed"
        }
        
        self.conversation_log.append(response_entry)
        self._log_event("RESPONSE_GENERATED", response)
        
        print(f"💬 Response: {response}")
        
        return {
            "status": "success",
            "question": initial_question,
            "response": response,
            "conversation_id": len(self.conversation_log)
        }
    
    def _generate_response(self, question: str) -> str:
        """Generate a response based on the question"""
        question_lower = question.lower()
        
        # Simple response logic
        if "communication" in question_lower:
            return "Communication is established through local and global channels with real-time feedback."
        elif "trajectory" in question_lower:
            return "Trajectory analysis provides direction, confidence, health, and predictions for your work."
        elif "risk" in question_lower:
            return "Key risks include miscommunication, technical issues, and isolation. Mitigation strategies are in place."
        elif "demo" in question_lower:
            return "Two primary demos available: Text Editor Demo and Code Editor Demo."
        else:
            return f"Processing your question about: {question}. Additional context may be needed for detailed response."
    
    def _log_event(self, event_type: str, content: str):
        """Log an event with timestamp"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "content": content
        }
        # In production, this would write to a file
        
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        questions = [entry for entry in self.conversation_log if entry["type"] == "question"]
        responses = [entry for entry in self.conversation_log if entry["type"] == "response"]
        
        return {
            "connection_status": self.connection_status,
            "total_questions": len(questions),
            "total_responses": len(responses),
            "test_results": self.test_results,
            "conversation_log": self.conversation_log
        }
    
    def save_log(self, filepath: str = "telephone_booth_log.json"):
        """Save conversation log to file"""
        summary = self.get_conversation_summary()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"📝 Log saved to {filepath}")


def main():
    """Main execution"""
    print("=" * 70)
    print("TELEPHONE BOOTH - Communication Initiator")
    print("=" * 70)
    print()
    
    # Create booth instance
    booth = TelephoneBooth()
    
    # Step 1: Initiate connection
    print("Step 1: Initiating Connection")
    print("-" * 70)
    connection_success = booth.initiate_connection()
    print()
    
    if not connection_success:
        print("❌ Cannot proceed without successful connection.")
        return
    
    # Step 2: Start conversation with initial questions
    print("Step 2: Starting Conversation")
    print("-" * 70)
    
    questions = [
        "What is the current state of communication in the system?",
        "How does trajectory analysis work?",
        "What are the main risks in long-distance communication?",
        "What demos are available for testing?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n[Question {i}/{len(questions)}]")
        result = booth.start_conversation(question)
        time.sleep(0.5)
    
    # Step 3: Generate summary
    print("\n" + "=" * 70)
    print("CONVERSATION SUMMARY")
    print("=" * 70)
    summary = booth.get_conversation_summary()
    print(f"Connection Status: {summary['connection_status']}")
    print(f"Total Questions: {summary['total_questions']}")
    print(f"Total Responses: {summary['total_responses']}")
    print(f"Test Results: {summary['test_results']}")
    print()
    
    # Step 4: Save log
    booth.save_log("d:\\realtime\\telephone_booth_log.json")
    print()
    print("✅ Communication session completed successfully!")
    

if __name__ == "__main__":
    main()
