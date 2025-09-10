#!/usr/bin/env python3
"""
Test script to demonstrate the AtomBot product agent system.

This script creates a few sample product agents and demonstrates their
cognitive capabilities including conversation and collaboration.
"""

import asyncio
import json
from atombot_core import AtomSpace, ConceptNode
from product_agents import ProductAgent


async def create_sample_agents():
    """Create sample product agents for demonstration."""
    
    # Create atomspace
    atomspace = AtomSpace()
    
    # Sample product data
    sample_products = [
        {
            'name': 'Acne Attack Pro-Masque',
            'category': 'acne',
            'functions': ['acne-treatment', 'controls-oil', 'deep-cleansing'],
            'properties': ['professional-grade', 'intensive'],
            'persona': {
                'description': 'I am a solution-focused acne treatment specialist.',
                'personality_traits': ['solution-focused', 'understanding', 'encouraging'],
                'communication_style': 'direct and supportive',
                'expertise_areas': ['acne control', 'oil management']
            }
        },
        {
            'name': 'Daily Ultra Defence',
            'category': 'defence',
            'functions': ['environmental-protection', 'barrier-protection'],
            'properties': ['daily-use', 'gentle'],
            'persona': {
                'description': 'I am your daily protection guardian for healthy skin.',
                'personality_traits': ['protective', 'reliable', 'caring'],
                'communication_style': 'reassuring and informative',
                'expertise_areas': ['daily protection', 'skin barriers']
            }
        },
        {
            'name': 'Active Facial Oil',
            'category': 'oil',
            'functions': ['hydrates-skin', 'nourishes-skin'],
            'properties': ['natural', 'nourishing'],
            'persona': {
                'description': 'I am a nurturing natural oil for deep skin nourishment.',
                'personality_traits': ['nurturing', 'natural', 'holistic'],
                'communication_style': 'warm and educational',
                'expertise_areas': ['natural skincare', 'hydration']
            }
        }
    ]
    
    # Create agents
    agents = []
    for product_data in sample_products:
        agent = ProductAgent(
            name=product_data['name'],
            atomspace=atomspace,
            product_info=product_data
        )
        agents.append(agent)
        print(f"✓ Created agent: {agent.name}")
    
    # Create relationships between agents
    print("\nCreating agent relationships...")
    
    # Add similarity links
    acne_agent = agents[0]  # Acne Attack
    defence_agent = agents[1]  # Daily Ultra Defence  
    oil_agent = agents[2]  # Active Facial Oil
    
    # Link acne and defence (both daily skincare)
    atomspace.add_link("SimilarityLink", [acne_agent, defence_agent], strength=0.4)
    
    # Link defence and oil (both gentle daily care)
    atomspace.add_link("SimilarityLink", [defence_agent, oil_agent], strength=0.6)
    
    print(f"✓ Created {len(atomspace.links)} relationships in the network")
    
    return agents, atomspace


async def demonstrate_conversations():
    """Demonstrate conversations with product agents."""
    
    print("\n" + "="*60)
    print("DEMONSTRATING PRODUCT AGENT CONVERSATIONS")
    print("="*60)
    
    agents, atomspace = await create_sample_agents()
    
    # Test conversations with each agent
    test_messages = [
        "Hello, what can you tell me about yourself?",
        "What benefits do you provide?",
        "How should I use you?",
        "Can you recommend other products?"
    ]
    
    for agent in agents:
        print(f"\n🤖 AGENT: {agent.name}")
        print("-" * 40)
        
        for message in test_messages[:2]:  # Test first 2 messages
            print(f"👤 USER: {message}")
            response = await agent.chat(message)
            print(f"🤖 {agent.name}: {response}\n")
            
        # Show agent status
        status = agent.get_atombot_status()
        print(f"📊 Agent Status:")
        print(f"   - Interactions: {status['agent_info']['interactions']}")
        print(f"   - Network connections: {status['network_info']['total_neighbors']}")
        print(f"   - Knowledge role: {status['agent_info']['knowledge_role']}")


async def demonstrate_collaboration():
    """Demonstrate collaboration between agents."""
    
    print("\n" + "="*60)
    print("DEMONSTRATING AGENT COLLABORATION")
    print("="*60)
    
    agents, atomspace = await create_sample_agents()
    
    acne_agent = agents[0]
    
    # Test collaboration
    print(f"\n🤝 COLLABORATION TEST")
    print(f"Initiator: {acne_agent.name}")
    print("-" * 40)
    
    collaboration_task = "Help me create a complete skincare routine for someone with acne-prone skin"
    print(f"👤 USER ASKS: {collaboration_task}")
    
    # Get collaboration response
    collaboration_result = await acne_agent.collaborate_with_network(collaboration_task)
    
    print(f"\n🤖 {acne_agent.name} COLLABORATION RESPONSE:")
    print(f"Task: {collaboration_result['task']}")
    print(f"Collaborator responses: {len(collaboration_result['responses'])}")
    
    for response in collaboration_result['responses']:
        if 'response' in response:
            print(f"  • {response['agent']}: {response['response'][:100]}...")
        else:
            print(f"  • {response['agent']}: {response['error']}")
    
    print(f"Insights: {collaboration_result['insights']}")


async def demonstrate_network_analysis():
    """Demonstrate network analysis capabilities."""
    
    print("\n" + "="*60)
    print("DEMONSTRATING NETWORK ANALYSIS")
    print("="*60)
    
    agents, atomspace = await create_sample_agents()
    
    print(f"\n📊 ATOMSPACE NETWORK ANALYSIS")
    print("-" * 40)
    print(f"Total atoms: {len(atomspace.atoms)}")
    print(f"Total links: {len(atomspace.links)}")
    
    # Analyze each agent's connections
    for agent in agents:
        neighbors = agent.get_neighbors()
        print(f"\n🔗 {agent.name}:")
        print(f"   - Neighbors: {len(neighbors)}")
        for neighbor in neighbors:
            if hasattr(neighbor, 'name'):
                print(f"     • Connected to: {neighbor.name}")
                
        # Show effectiveness scores
        product_analysis = await agent.get_product_analysis()
        effectiveness = product_analysis['capabilities']['effectiveness_scores']
        if effectiveness:
            print(f"   - Top effectiveness areas:")
            for concern, scores in list(effectiveness.items())[:3]:
                print(f"     • {concern}: {scores['strength']:.1%}")


async def main():
    """Main demonstration function."""
    
    print("🧠 ATOMBOT PRODUCT AGENT DEMONSTRATION")
    print("Transforming beauty products into distributed cognitive agents")
    print("="*60)
    
    try:
        # Run demonstrations
        await demonstrate_conversations()
        await demonstrate_collaboration()
        await demonstrate_network_analysis()
        
        print("\n" + "="*60)
        print("✅ DEMONSTRATION COMPLETE!")
        print("The AtomBot system successfully:")
        print("• Created specialized product agents with unique personas")
        print("• Enabled natural conversations about product benefits")
        print("• Demonstrated network collaboration capabilities") 
        print("• Showed distributed cognitive reasoning")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())