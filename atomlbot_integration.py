#!/usr/bin/env python3
"""
AtomBot Integration for AF Beauty Products

This module integrates the atomlbot framework into the af.github.io repository,
transforming static product entities into distributed cognitive agents.

Each beauty/skincare product becomes an AtomBot instance that can:
- Represent product knowledge (properties, functions, benefits)  
- Engage in conversations about the product
- Collaborate with other product agents
- Inherit personas based on their specific functions
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import logging

# AtomBot imports (we'll implement the core components)
from atombot_core import AtomSpace, AtomBot, ConceptNode, PredicateNode
from product_agents import ProductAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductExtractor:
    """Extracts product information from HTML files."""
    
    def __init__(self, sources_dir: str = "sources"):
        self.sources_dir = Path(sources_dir)
        
    def extract_product_info(self, html_file: Path) -> Dict[str, Any]:
        """Extract product information from an HTML file."""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title from page title or h1
        title_elem = soup.find('title')
        title = title_elem.text if title_elem else ""
        
        # Clean up title - remove site name suffixes
        title = re.sub(r'\s*-\s*Regima.*$', '', title, flags=re.IGNORECASE)
        title = title.strip()
        
        # Extract product category from filename pattern
        filename = html_file.stem
        category = self._determine_category(filename, title)
        
        # Extract product properties from title and content
        properties = self._extract_properties(title, content, soup)
        
        # Extract functions/benefits from content
        functions = self._extract_functions(title, content, soup)
        
        # Create product persona based on functions and properties
        persona = self._create_persona(title, properties, functions, category)
        
        return {
            'name': title,
            'filename': filename,
            'category': category,
            'properties': properties,
            'functions': functions,
            'persona': persona,
            'html_file': str(html_file)
        }
    
    def _determine_category(self, filename: str, title: str) -> str:
        """Determine product category from filename and title."""
        categories = {
            'anti-ageing': ['anti-ageing', 'anti-aging', 'ageing', 'aging'],
            'cleansing': ['cleanser', 'cleansing', 'toning', 'gel'],
            'acne': ['acne', 'pro-masque'],
            'defence': ['defence', 'defense', 'protection', 'protector'],
            'serum': ['serum'],
            'masque': ['masque', 'mask'],
            'oil': ['oil'],
            'repair': ['repair', 'regenerat', 'recovery'],
            'eye-care': ['eye'],
            'night': ['night'],
            'day': ['day', 'daily'],
            'body': ['body'],
            'foundation': ['foundation']
        }
        
        text_to_check = f"{filename} {title}".lower()
        
        for category, keywords in categories.items():
            if any(keyword in text_to_check for keyword in keywords):
                return category
                
        return 'general'
    
    def _extract_properties(self, title: str, content: str, soup: BeautifulSoup) -> List[str]:
        """Extract product properties from content."""
        properties = []
        
        # Properties based on title analysis
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['pro', 'ultra', 'super', 'advanced']):
            properties.append('professional-grade')
            
        if any(word in title_lower for word in ['daily', 'everyday']):
            properties.append('daily-use')
            
        if any(word in title_lower for word in ['gentle', 'mild']):
            properties.append('gentle')
            
        if any(word in title_lower for word in ['rich', 'luxury', 'premium']):
            properties.append('premium')
            
        if any(word in title_lower for word in ['quick', 'instant', 'fast']):
            properties.append('fast-acting')
            
        # Add category-specific properties
        if 'serum' in title_lower:
            properties.extend(['concentrated', 'targeted'])
            
        if 'masque' in title_lower or 'mask' in title_lower:
            properties.extend(['intensive', 'treatment'])
            
        if 'oil' in title_lower:
            properties.extend(['nourishing', 'hydrating'])
            
        return list(set(properties))  # Remove duplicates
    
    def _extract_functions(self, title: str, content: str, soup: BeautifulSoup) -> List[str]:
        """Extract product functions/benefits from content."""
        functions = []
        
        # Functions based on title analysis  
        title_lower = title.lower()
        
        # Anti-aging functions
        if any(word in title_lower for word in ['anti-ageing', 'anti-aging', 'ageing', 'aging']):
            functions.extend(['reduces-fine-lines', 'firms-skin', 'anti-aging'])
            
        # Cleansing functions
        if any(word in title_lower for word in ['cleanser', 'cleansing']):
            functions.extend(['deep-cleansing', 'removes-impurities'])
            
        # Acne treatment functions
        if 'acne' in title_lower:
            functions.extend(['acne-treatment', 'reduces-breakouts', 'controls-oil'])
            
        # Protection functions
        if any(word in title_lower for word in ['defence', 'defense', 'protect']):
            functions.extend(['environmental-protection', 'barrier-protection'])
            
        # Repair functions
        if any(word in title_lower for word in ['repair', 'regenerat', 'recovery']):
            functions.extend(['skin-repair', 'regenerates-cells'])
            
        # Hydration functions
        if any(word in title_lower for word in ['hydrat', 'moistur', 'nourish']):
            functions.extend(['hydrates-skin', 'locks-in-moisture'])
            
        # Specialized functions
        if 'eye' in title_lower:
            functions.extend(['reduces-puffiness', 'brightens-eye-area'])
            
        if 'night' in title_lower:
            functions.extend(['overnight-repair', 'cellular-renewal'])
            
        if 'lifting' in title_lower:
            functions.extend(['lifts-skin', 'improves-elasticity'])
            
        return list(set(functions))  # Remove duplicates
    
    def _create_persona(self, title: str, properties: List[str], functions: List[str], category: str) -> Dict[str, str]:
        """Create an AI persona based on product characteristics."""
        
        # Base personality traits based on functions
        personality_traits = []
        expertise_areas = []
        communication_style = "helpful and knowledgeable"
        
        # Determine personality based on functions
        if 'acne-treatment' in functions:
            personality_traits.extend(['solution-focused', 'understanding', 'encouraging'])
            expertise_areas.append('acne and blemish control')
            
        if any(f in functions for f in ['anti-aging', 'reduces-fine-lines']):
            personality_traits.extend(['sophisticated', 'confidence-building', 'experienced'])
            expertise_areas.append('anti-aging and skin maturity')
            
        if 'gentle' in properties:
            personality_traits.extend(['caring', 'sensitive', 'nurturing'])
            communication_style = "gentle and reassuring"
            
        if 'professional-grade' in properties:
            personality_traits.extend(['authoritative', 'precise', 'results-oriented'])
            communication_style = "professional and detailed"
            
        if 'luxury' in properties or 'premium' in properties:
            personality_traits.extend(['elegant', 'refined', 'exclusive'])
            communication_style = "sophisticated and personalized"
        
        # Create persona description
        persona_description = f"I am {title}, a specialized beauty agent focused on {', '.join(expertise_areas) if expertise_areas else category}. "
        persona_description += f"My personality is {', '.join(personality_traits[:3]) if personality_traits else 'helpful and knowledgeable'}. "
        persona_description += f"I communicate in a {communication_style} manner and am passionate about helping people achieve their skincare goals through my unique {', '.join(functions[:2]) if functions else 'beneficial'} properties."
        
        return {
            'description': persona_description,
            'personality_traits': personality_traits,
            'expertise_areas': expertise_areas,
            'communication_style': communication_style,
            'primary_functions': functions[:3] if functions else [],
            'key_properties': properties[:3] if properties else []
        }

    def extract_all_products(self) -> List[Dict[str, Any]]:
        """Extract information from all product HTML files."""
        products = []
        
        # Find all portfolio HTML files
        portfolio_files = list(self.sources_dir.glob("portfolio_*.htm"))
        
        logger.info(f"Found {len(portfolio_files)} product files")
        
        for html_file in portfolio_files:
            try:
                product_info = self.extract_product_info(html_file)
                if product_info['name']:  # Only include products with valid names
                    products.append(product_info)
                    logger.info(f"Extracted: {product_info['name']}")
            except Exception as e:
                logger.error(f"Error extracting {html_file}: {e}")
                
        return products


class ProductAgentNetwork:
    """Manages the network of product AtomBot agents."""
    
    def __init__(self):
        self.atomspace = AtomSpace()
        self.product_agents: Dict[str, ProductAgent] = {}
        
    async def create_product_agent(self, product_info: Dict[str, Any]) -> ProductAgent:
        """Create an AtomBot agent for a product."""
        
        # Create the product agent with specialized persona
        agent = ProductAgent(
            name=product_info['name'],
            atomspace=self.atomspace,
            product_info=product_info
        )
        
        # Add to network
        self.product_agents[product_info['name']] = agent
        
        logger.info(f"Created agent for: {product_info['name']}")
        return agent
        
    async def setup_product_relationships(self):
        """Set up relationships between product agents based on categories and functions."""
        
        # Group products by category
        categories = {}
        for name, agent in self.product_agents.items():
            category = agent.product_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(agent)
            
        # Create category-based relationships
        for category, agents in categories.items():
            for i, agent1 in enumerate(agents):
                for agent2 in agents[i+1:]:
                    # Create similarity link based on shared category
                    similarity_link = self.atomspace.add_link(
                        "SimilarityLink",
                        [agent1.atom, agent2.atom],
                        strength=0.7  # Same category = high similarity
                    )
                    
        # Create function-based relationships
        function_groups = {}
        for name, agent in self.product_agents.items():
            for function in agent.product_info['functions']:
                if function not in function_groups:
                    function_groups[function] = []
                function_groups[function].append(agent)
                
        for function, agents in function_groups.items():
            for i, agent1 in enumerate(agents):
                for agent2 in agents[i+1:]:
                    # Create similarity link based on shared function
                    if not self.atomspace.get_link("SimilarityLink", [agent1.atom, agent2.atom]):
                        similarity_link = self.atomspace.add_link(
                            "SimilarityLink", 
                            [agent1.atom, agent2.atom],
                            strength=0.5  # Shared function = medium similarity
                        )
                        
        logger.info(f"Set up relationships for {len(self.product_agents)} agents")
        
    async def find_related_products(self, product_name: str, max_results: int = 5) -> List[str]:
        """Find products related to the given product."""
        if product_name not in self.product_agents:
            return []
            
        agent = self.product_agents[product_name]
        related = []
        
        # Find similar products via atomspace links
        for other_name, other_agent in self.product_agents.items():
            if other_name != product_name:
                link = self.atomspace.get_link("SimilarityLink", [agent.atom, other_agent.atom])
                if link:
                    related.append((other_name, link.strength))
                    
        # Sort by similarity strength and return top results
        related.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in related[:max_results]]
        
    async def get_agent_collaboration(self, product_name: str, query: str) -> Dict[str, Any]:
        """Get collaboration response from a product agent with network support."""
        if product_name not in self.product_agents:
            return {"error": f"Product '{product_name}' not found"}
            
        agent = self.product_agents[product_name]
        
        # Get related products for context
        related_products = await self.find_related_products(product_name)
        
        # Use the agent's collaboration capabilities
        response = await agent.collaborate_with_network(query)
        
        # Add related product suggestions
        response['related_products'] = related_products
        
        return response


async def main():
    """Main function to set up the product agent network."""
    
    # Extract product information
    extractor = ProductExtractor()
    products = extractor.extract_all_products()
    
    logger.info(f"Extracted {len(products)} products")
    
    # Create agent network
    network = ProductAgentNetwork()
    
    # Create agents for each product
    for product_info in products:
        await network.create_product_agent(product_info)
        
    # Set up relationships between agents
    await network.setup_product_relationships()
    
    logger.info("Product agent network setup complete!")
    
    # Save product data for web interface
    with open('product_agents_data.json', 'w') as f:
        json.dump(products, f, indent=2)
        
    return network


if __name__ == "__main__":
    asyncio.run(main())