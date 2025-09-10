#!/usr/bin/env python3
"""
Simple demonstration of the AtomBot Product Agent system.

This creates a working product agent network and shows how it transforms
static product entities into distributed cognitive agents.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# Simple AtomBot implementation for demo
class SimpleAtomBot:
    """Simplified AtomBot for demonstration."""
    
    def __init__(self, name: str, product_info: Dict[str, Any]):
        self.name = name
        self.product_info = product_info
        self.category = product_info.get('category', 'general')
        self.functions = product_info.get('functions', [])
        self.properties = product_info.get('properties', [])
        self.persona = product_info.get('persona', {})
        self.conversation_history = []
        self.connections = []
        
    async def chat(self, message: str) -> str:
        """Handle chat messages with product-specific responses."""
        message_lower = message.lower()
        
        # Store conversation
        self.conversation_history.append({
            'user': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate response based on message type
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            response = await self._greeting_response()
        elif any(word in message_lower for word in ['benefits', 'help', 'good for']):
            response = await self._benefits_response()
        elif any(word in message_lower for word in ['how', 'use', 'apply']):
            response = await self._usage_response()
        elif any(word in message_lower for word in ['recommend', 'suggest', 'other']):
            response = await self._recommendation_response()
        else:
            response = await self._general_response()
            
        # Store response
        self.conversation_history.append({
            'agent': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return response
        
    async def _greeting_response(self) -> str:
        """Personalized greeting based on persona."""
        traits = self.persona.get('personality_traits', [])
        
        if 'sophisticated' in traits:
            return f"Good day! I'm {self.name}, your sophisticated skincare companion. How may I assist you today?"
        elif 'caring' in traits:
            return f"Hello! I'm {self.name}, and I'm here to care for your skin. What can I help you with?"
        elif 'solution-focused' in traits:
            return f"Hi! I'm {self.name}. I'm ready to help solve your skincare concerns. What would you like to know?"
        else:
            return f"Hello! I'm {self.name}. I'm excited to help with your skincare journey!"
            
    async def _benefits_response(self) -> str:
        """Explain product benefits."""
        response = f"As {self.name}, I offer these key benefits:\n\n"
        
        for i, function in enumerate(self.functions, 1):
            formatted_function = function.replace('-', ' ').title()
            response += f"{i}. {formatted_function}\n"
            
        if self.properties:
            response += f"\nWhat makes me special: I'm {', '.join(self.properties)}."
            
        return response
        
    async def _usage_response(self) -> str:
        """Provide usage instructions."""
        category_instructions = {
            'acne': "Apply to clean skin, focusing on problem areas. Start with 2-3 times per week.",
            'defence': "Apply generously 15 minutes before sun exposure. Reapply every 2 hours.",
            'anti-ageing': "Apply to clean skin morning and/or evening. Gently pat until absorbed.",
            'eye-care': "Gently pat around eye area with ring finger. Avoid direct contact with eyes.",
            'oil': "Warm a few drops between palms and gently press into skin.",
            'cleansing': "Apply to damp skin, massage gently, then rinse thoroughly."
        }
        
        instruction = category_instructions.get(self.category, 
            "Apply to clean skin as directed. Start slowly and adjust based on your skin's response.")
            
        return f"Here's how to use me effectively:\n\n{instruction}\n\nAlways patch test new products first!"
        
    async def _recommendation_response(self) -> str:
        """Suggest complementary products."""
        if not self.connections:
            return "I'd love to recommend complementary products, but I need to build more network connections first!"
            
        response = f"Based on my network knowledge, here are some recommendations:\n\n"
        for connection in self.connections[:3]:
            response += f"• {connection.name} - Great for {connection.category} concerns\n"
            
        return response
        
    async def _general_response(self) -> str:
        """General helpful response."""
        return f"I'm {self.name}, specializing in {', '.join(self.functions[:2])}. I'm here to help with your skincare needs. What specific questions do you have about my benefits or how to use me?"


class ProductAgentDemo:
    """Demonstration of the product agent system."""
    
    def __init__(self):
        self.agents = {}
        self.setup_sample_agents()
        
    def setup_sample_agents(self):
        """Create sample product agents."""
        
        sample_products = [
            {
                'name': 'Acne Attack Pro-Masque',
                'category': 'acne',
                'functions': ['acne-treatment', 'controls-oil', 'deep-cleansing'],
                'properties': ['professional-grade', 'intensive'],
                'persona': {
                    'personality_traits': ['solution-focused', 'encouraging', 'understanding'],
                    'communication_style': 'direct and supportive',
                    'description': 'I am a powerful acne-fighting specialist focused on clear, healthy skin.'
                }
            },
            {
                'name': 'Daily Ultra Defence',
                'category': 'defence',
                'functions': ['environmental-protection', 'barrier-protection'],
                'properties': ['daily-use', 'gentle'],
                'persona': {
                    'personality_traits': ['protective', 'reliable', 'caring'],
                    'communication_style': 'reassuring and informative',
                    'description': 'I am your daily guardian against environmental damage.'
                }
            },
            {
                'name': 'Active Facial Oil',
                'category': 'oil',
                'functions': ['hydrates-skin', 'nourishes-skin'],
                'properties': ['natural', 'nourishing'],
                'persona': {
                    'personality_traits': ['nurturing', 'holistic', 'natural'],
                    'communication_style': 'warm and educational',
                    'description': 'I am a natural nourishment specialist for glowing skin.'
                }
            },
            {
                'name': 'Anti-Inflamm-Ageing Complex',
                'category': 'anti-ageing',
                'functions': ['anti-aging', 'reduces-fine-lines', 'firms-skin'],
                'properties': ['premium', 'concentrated'],
                'persona': {
                    'personality_traits': ['sophisticated', 'confidence-building', 'experienced'],
                    'communication_style': 'elegant and knowledgeable',
                    'description': 'I am a sophisticated anti-aging specialist for mature, confident skin.'
                }
            }
        ]
        
        # Create agents
        for product_data in sample_products:
            agent = SimpleAtomBot(product_data['name'], product_data)
            self.agents[product_data['name']] = agent
            
        # Create network connections
        agent_list = list(self.agents.values())
        for i, agent in enumerate(agent_list):
            # Connect each agent to 1-2 others
            for j in range(i+1, min(i+3, len(agent_list))):
                agent.connections.append(agent_list[j])
                agent_list[j].connections.append(agent)
                
    async def demonstrate_conversations(self):
        """Demonstrate conversations with each agent."""
        
        print("🧠 ATOMBOT PRODUCT AGENT CONVERSATIONS")
        print("=" * 60)
        print("Demonstrating how static products become cognitive agents...")
        print()
        
        test_questions = [
            "Hello! What can you tell me about yourself?",
            "What benefits do you provide?",
            "How should I use you?",
            "Can you recommend other products?"
        ]
        
        for agent_name, agent in self.agents.items():
            print(f"💬 CHATTING WITH: {agent_name}")
            print("-" * 40)
            print(f"Category: {agent.category}")
            print(f"Personality: {', '.join(agent.persona.get('personality_traits', []))}")
            print()
            
            for question in test_questions[:2]:  # Demo first 2 questions
                print(f"👤 USER: {question}")
                response = await agent.chat(question)
                print(f"🤖 {agent.name}: {response}")
                print()
                
            print(f"📊 Agent has {len(agent.connections)} network connections")
            print("=" * 60)
            print()
            
    async def demonstrate_personas(self):
        """Show how different products have different personas."""
        
        print("🎭 AGENT PERSONAS DEMONSTRATION")
        print("=" * 60)
        print("Each product inherits a unique persona from its functions and properties...")
        print()
        
        for agent_name, agent in self.agents.items():
            print(f"🤖 {agent_name}")
            print(f"   Category: {agent.category}")
            print(f"   Functions: {', '.join(agent.functions)}")
            print(f"   Properties: {', '.join(agent.properties)}")
            print(f"   Personality: {', '.join(agent.persona.get('personality_traits', []))}")
            print(f"   Style: {agent.persona.get('communication_style', 'helpful')}")
            print(f"   Description: {agent.persona.get('description', 'A helpful product agent')}")
            print()
            
    def demonstrate_network(self):
        """Show the distributed cognitive network."""
        
        print("🌐 DISTRIBUTED COGNITIVE NETWORK")
        print("=" * 60)
        print("Products are connected in a knowledge network for collaboration...")
        print()
        
        for agent_name, agent in self.agents.items():
            connections = [conn.name for conn in agent.connections]
            print(f"🔗 {agent_name}")
            print(f"   Connected to: {', '.join(connections) if connections else 'Building connections...'}")
            print(f"   Network size: {len(agent.connections)} direct connections")
            print()
            
    async def interactive_demo(self):
        """Run an interactive demo with one agent."""
        
        print("🎮 INTERACTIVE DEMO")
        print("=" * 60)
        print("Try chatting with one of our product agents!")
        print()
        
        # List available agents
        print("Available agents:")
        for i, name in enumerate(self.agents.keys(), 1):
            print(f"{i}. {name}")
        print()
        
        # For demo, let's simulate choosing the first agent
        selected_agent = list(self.agents.values())[0]
        print(f"🤖 Selected: {selected_agent.name}")
        print(f"Type 'quit' to exit the demo")
        print()
        
        # Demo conversation
        demo_messages = [
            "Hello! What makes you special?",
            "What skin concerns do you help with?",
            "How often should I use you?",
            "quit"
        ]
        
        for message in demo_messages:
            if message == "quit":
                print("👤 USER: quit")
                print("Demo ended. Thanks for trying the AtomBot system!")
                break
                
            print(f"👤 USER: {message}")
            response = await selected_agent.chat(message)
            print(f"🤖 {selected_agent.name}: {response}")
            print()


async def main():
    """Run the complete demonstration."""
    
    print("🚀 ATOMBOT PRODUCT AGENT DEMONSTRATION")
    print("Transforming static beauty products into distributed cognitive agents")
    print("=" * 70)
    print()
    
    demo = ProductAgentDemo()
    
    # Run all demonstrations
    demo.demonstrate_personas()
    demo.demonstrate_network()
    await demo.demonstrate_conversations()
    await demo.interactive_demo()
    
    print("\n✅ DEMONSTRATION COMPLETE!")
    print("\nThe AtomBot system successfully transformed static product entities into:")
    print("• Intelligent conversational agents with unique personas")
    print("• Distributed cognitive network for collaboration")
    print("• Natural language interfaces for product interaction")
    print("• Analogous personalities based on product functions")
    print("\nThis shows how products can become cognitive agents that inherit")
    print("their personas from their functions and properties! 🧠✨")


if __name__ == "__main__":
    asyncio.run(main())