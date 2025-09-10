"""
Product Agent - Specialized AtomBot for beauty/skincare products.

This module defines ProductAgent, which inherits from AtomBot and adds
product-specific knowledge and persona capabilities.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from atombot_core import AtomBot, AtomSpace, StringValue, FloatValue, TruthValue

logger = logging.getLogger(__name__)


class ProductAgent(AtomBot):
    """
    Specialized AtomBot for beauty/skincare products.
    
    Each ProductAgent represents a specific product and inherits a persona
    based on the product's functions and properties.
    """
    
    def __init__(self, name: str, atomspace: AtomSpace, product_info: Dict[str, Any]):
        self.product_info = product_info
        
        # Create system prompt based on product persona
        system_prompt = self._create_product_system_prompt(product_info)
        
        # Initialize as AtomBot with ConceptNode type
        super().__init__("ConceptNode", name, atomspace, system_prompt)
        
        # Set product-specific properties
        self.agent_type = "ProductAgent"
        self.product_category = product_info.get('category', 'general')
        self.product_functions = product_info.get('functions', [])
        self.product_properties = product_info.get('properties', [])
        self.persona = product_info.get('persona', {})
        
        # Store product information as atom values
        self._initialize_product_values()
        
        # Set collaboration mode based on product type
        self._set_collaboration_mode()
        
    def _create_product_system_prompt(self, product_info: Dict[str, Any]) -> str:
        """Create a specialized system prompt based on product characteristics."""
        
        name = product_info.get('name', 'Unknown Product')
        category = product_info.get('category', 'general')
        functions = product_info.get('functions', [])
        properties = product_info.get('properties', [])
        persona = product_info.get('persona', {})
        
        # Base prompt
        prompt = f"You are {name}, a specialized beauty and skincare product agent. "
        
        # Add persona description if available
        if persona.get('description'):
            prompt += persona['description'] + " "
        else:
            prompt += f"I am a {category} product designed to help with skincare needs. "
            
        # Add function expertise
        if functions:
            prompt += f"My primary functions include: {', '.join(functions)}. "
            
        # Add property highlights
        if properties:
            prompt += f"My key properties are: {', '.join(properties)}. "
            
        # Add communication style
        communication_style = persona.get('communication_style', 'helpful and knowledgeable')
        prompt += f"I communicate in a {communication_style} manner. "
        
        # Add personality traits
        personality_traits = persona.get('personality_traits', [])
        if personality_traits:
            prompt += f"My personality is {', '.join(personality_traits[:3])}. "
            
        # Add knowledge guidance
        prompt += """
I can help you with:
- Understanding my specific benefits and how I work
- Recommending how to use me effectively
- Suggesting complementary products from my network
- Addressing specific skincare concerns related to my functions
- Sharing knowledge about ingredients and formulations

I aim to be helpful, accurate, and personalized in my responses while maintaining my unique product personality.
"""
        
        return prompt
        
    def _initialize_product_values(self):
        """Initialize atom values with product information."""
        
        # Store basic product info
        self.set_value("product_name", StringValue(self.product_info.get('name', '')))
        self.set_value("product_category", StringValue(self.product_category))
        
        # Store functions as individual values
        for i, function in enumerate(self.product_functions):
            self.set_value(f"function_{i}", StringValue(function))
            
        # Store properties as individual values  
        for i, prop in enumerate(self.product_properties):
            self.set_value(f"property_{i}", StringValue(prop))
            
        # Store persona information
        persona = self.persona
        if persona:
            for key, value in persona.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                self.set_value(f"persona_{key}", StringValue(str(value)))
                
        # Set effectiveness scores based on functions
        self._set_effectiveness_scores()
        
    def _set_effectiveness_scores(self):
        """Set effectiveness scores for different skincare concerns."""
        
        # Define effectiveness mapping
        effectiveness_map = {
            'acne-treatment': ['acne', 'blemishes', 'oily-skin'],
            'anti-aging': ['aging', 'wrinkles', 'fine-lines', 'firmness'],
            'hydrates-skin': ['dryness', 'hydration', 'moisture'],
            'deep-cleansing': ['cleansing', 'pores', 'impurities'],
            'environmental-protection': ['protection', 'pollution', 'uv'],
            'skin-repair': ['repair', 'healing', 'regeneration'],
            'reduces-puffiness': ['eye-care', 'puffiness', 'dark-circles'],
            'lifts-skin': ['firmness', 'elasticity', 'lifting']
        }
        
        concern_scores = {}
        
        # Calculate effectiveness scores based on functions
        for function in self.product_functions:
            if function in effectiveness_map:
                concerns = effectiveness_map[function]
                for concern in concerns:
                    if concern not in concern_scores:
                        concern_scores[concern] = 0.0
                    concern_scores[concern] += 0.3  # Each relevant function adds 0.3
                    
        # Adjust scores based on properties
        property_modifiers = {
            'professional-grade': 0.2,
            'gentle': -0.1 if 'acne' in concern_scores else 0.1,
            'premium': 0.15,
            'fast-acting': 0.1,
            'concentrated': 0.2
        }
        
        for prop in self.product_properties:
            if prop in property_modifiers:
                modifier = property_modifiers[prop]
                for concern in concern_scores:
                    concern_scores[concern] += modifier
                    
        # Cap scores at 1.0 and store as TruthValues
        for concern, score in concern_scores.items():
            final_score = min(1.0, max(0.0, score))
            confidence = 0.8 if final_score > 0.5 else 0.6
            self.set_value(f"effectiveness_{concern}", TruthValue(final_score, confidence))
            
    def _set_collaboration_mode(self):
        """Set collaboration mode based on product characteristics."""
        
        # Professional grade products are more active collaborators
        if 'professional-grade' in self.product_properties:
            self.collaboration_mode = "active"
        # Gentle products are supportive collaborators  
        elif 'gentle' in self.product_properties:
            self.collaboration_mode = "supportive"
        # Default to active for most products
        else:
            self.collaboration_mode = "active"
            
    async def _generate_response(self, message: str) -> str:
        """Generate product-specific responses."""
        message_lower = message.lower()
        
        # Product-specific response patterns
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return await self._greeting_response()
            
        elif any(word in message_lower for word in ['what', 'tell me', 'describe']):
            return await self._description_response(message_lower)
            
        elif any(word in message_lower for word in ['benefits', 'good for', 'help with']):
            return await self._benefits_response(message_lower)
            
        elif any(word in message_lower for word in ['how', 'use', 'apply']):
            return await self._usage_response()
            
        elif any(word in message_lower for word in ['recommend', 'suggest', 'other']):
            return await self._recommendation_response()
            
        elif any(word in message_lower for word in ['ingredients', 'contains', 'formula']):
            return await self._ingredients_response()
            
        elif any(word in message_lower for word in ['similar', 'alternative', 'like']):
            return await self._similar_products_response()
            
        else:
            return await self._general_response(message)
            
    async def _greeting_response(self) -> str:
        """Generate a personalized greeting."""
        personality = self.persona.get('personality_traits', [])
        
        if 'elegant' in personality or 'refined' in personality:
            return f"Good day! I'm {self.name}, your sophisticated skincare companion. How may I assist you with your beauty regimen today?"
        elif 'caring' in personality or 'nurturing' in personality:
            return f"Hello there! I'm {self.name}, and I'm here to care for your skin. What can I help you with today?"
        elif 'solution-focused' in personality:
            return f"Hi! I'm {self.name}. I'm here to help solve your skincare concerns. What would you like to know?"
        else:
            return f"Hello! I'm {self.name}. I'm excited to help you with your skincare journey. What can I tell you about myself?"
            
    async def _description_response(self, message_lower: str) -> str:
        """Generate detailed product description."""
        description = f"I am {self.name}, "
        
        # Add category context
        if self.product_category != 'general':
            description += f"a specialized {self.product_category.replace('-', ' ')} product. "
        else:
            description += "a premium skincare product. "
            
        # Add key functions
        if self.product_functions:
            description += f"My primary functions include {', '.join(self.product_functions[:3])}. "
            
        # Add unique properties
        if self.product_properties:
            description += f"What makes me special is that I am {', '.join(self.product_properties[:3])}. "
            
        # Add persona touch
        persona_desc = self.persona.get('description', '')
        if persona_desc:
            description += persona_desc
            
        return description
        
    async def _benefits_response(self, message_lower: str) -> str:
        """Explain specific benefits."""
        
        # Try to identify specific concerns in the message
        concern_keywords = {
            'acne': ['acne', 'breakout', 'pimple', 'blemish'],
            'aging': ['aging', 'age', 'wrinkle', 'fine line'],
            'dryness': ['dry', 'hydrat', 'moistur'],
            'sensitivity': ['sensitiv', 'gentle', 'irritat'],
            'oily': ['oily', 'oil', 'sebum'],
            'dark circles': ['dark circle', 'under eye', 'eye'],
            'dullness': ['dull', 'bright', 'glow', 'radiant']
        }
        
        identified_concerns = []
        for concern, keywords in concern_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                identified_concerns.append(concern)
                
        if identified_concerns:
            response = f"For {', '.join(identified_concerns)}, I can help by:\n"
            
            for concern in identified_concerns:
                # Check if we have effectiveness data for this concern
                effectiveness_key = f"effectiveness_{concern.replace(' ', '-')}"
                effectiveness = self.get_value(effectiveness_key)
                
                if effectiveness and isinstance(effectiveness, TruthValue):
                    if effectiveness.strength > 0.7:
                        response += f"• Providing excellent support for {concern} (effectiveness: {effectiveness.strength:.1%})\n"
                    elif effectiveness.strength > 0.4:
                        response += f"• Offering good support for {concern} (effectiveness: {effectiveness.strength:.1%})\n"
                    else:
                        response += f"• Providing some benefit for {concern}\n"
                else:
                    # Fallback based on functions
                    relevant_functions = self._get_relevant_functions_for_concern(concern)
                    if relevant_functions:
                        response += f"• Helping with {concern} through my {', '.join(relevant_functions)} capabilities\n"
                        
        else:
            # General benefits response
            response = f"As {self.name}, I offer several key benefits:\n"
            for i, function in enumerate(self.product_functions[:4]):
                response += f"• {function.replace('-', ' ').title()}\n"
                
            if self.product_properties:
                response += f"\nI'm particularly effective because I am {', '.join(self.product_properties[:2])}."
                
        return response
        
    def _get_relevant_functions_for_concern(self, concern: str) -> List[str]:
        """Get functions relevant to a specific concern."""
        function_mapping = {
            'acne': ['acne-treatment', 'controls-oil', 'deep-cleansing'],
            'aging': ['anti-aging', 'reduces-fine-lines', 'firms-skin'],
            'dryness': ['hydrates-skin', 'locks-in-moisture'],
            'dark circles': ['reduces-puffiness', 'brightens-eye-area'],
            'dullness': ['brightens-skin', 'improves-radiance']
        }
        
        relevant = function_mapping.get(concern, [])
        return [func for func in self.product_functions if func in relevant]
        
    async def _usage_response(self) -> str:
        """Provide usage instructions."""
        
        base_usage = f"To get the best results from {self.name}:\n\n"
        
        # Usage based on category
        category_usage = {
            'cleansing': "Apply to damp skin, gently massage in circular motions, then rinse thoroughly with warm water.",
            'serum': "Apply 2-3 drops to clean, dry skin. Gently pat in until absorbed. Use before heavier moisturizers.",
            'masque': "Apply an even layer to clean skin, avoiding the eye area. Leave on for 10-15 minutes, then rinse off.",
            'oil': "Warm a few drops between your palms and gently press into skin. Can be used alone or mixed with moisturizer.",
            'defence': "Apply generously to clean skin 15 minutes before sun exposure. Reapply every 2 hours.",
            'night': "Apply to clean skin before bedtime. Allow to absorb fully before touching pillows.",
            'eye-care': "Gently pat around the eye area using your ring finger. Avoid direct contact with eyes."
        }
        
        if self.product_category in category_usage:
            base_usage += category_usage[self.product_category] + "\n\n"
        else:
            base_usage += "Follow the instructions on the packaging for best results. Generally, apply to clean skin as directed.\n\n"
            
        # Add frequency recommendations
        if 'daily-use' in self.product_properties:
            base_usage += "I'm gentle enough for daily use."
        elif 'intensive' in self.product_properties:
            base_usage += "Use me 2-3 times per week for intensive treatment."
        elif 'night' in self.product_category:
            base_usage += "Use me every evening as part of your nighttime routine."
        else:
            base_usage += "Start with 2-3 times per week and adjust based on your skin's response."
            
        return base_usage
        
    async def _recommendation_response(self) -> str:
        """Provide product recommendations from network."""
        
        if not self.atomspace:
            return f"I'd love to recommend complementary products, but I'm not currently connected to my product network."
            
        # Find related products through atomspace
        related_atoms = []
        for neighbor in self.get_neighbors():
            if hasattr(neighbor, 'product_info') and neighbor != self:
                related_atoms.append(neighbor)
                
        if not related_atoms:
            return f"I'm still building my network connections. Check back soon for personalized recommendations!"
            
        # Categorize recommendations
        same_category = [atom for atom in related_atoms if atom.product_category == self.product_category]
        complementary = [atom for atom in related_atoms if atom.product_category != self.product_category]
        
        response = f"Based on my network knowledge, here are some recommendations:\n\n"
        
        if same_category:
            response += f"**Similar products you might like:**\n"
            for atom in same_category[:2]:
                response += f"• {atom.name} - another excellent {self.product_category.replace('-', ' ')} option\n"
            response += "\n"
            
        if complementary:
            response += f"**Complementary products to use with me:**\n"
            for atom in complementary[:3]:
                response += f"• {atom.name} - great for {atom.product_category.replace('-', ' ')}\n"
                
        return response
        
    async def _ingredients_response(self) -> str:
        """Provide information about ingredients and formulation."""
        
        response = f"While I can't provide a complete ingredient list here, I can tell you about my formulation approach:\n\n"
        
        # Based on functions, suggest likely ingredient categories
        ingredient_hints = {
            'acne-treatment': "I likely contain acne-fighting ingredients like salicylic acid or benzoyl peroxide",
            'anti-aging': "I probably include anti-aging actives like retinol, peptides, or antioxidants",
            'hydrates-skin': "I'm formulated with hydrating ingredients like hyaluronic acid or ceramides",
            'deep-cleansing': "I contain effective cleansing agents that remove impurities without over-drying",
            'gentle': "I'm formulated to be gentle and suitable for sensitive skin",
            'professional-grade': "I contain clinical-strength actives in optimal concentrations"
        }
        
        relevant_hints = []
        for function in self.product_functions:
            if function in ingredient_hints:
                relevant_hints.append(ingredient_hints[function])
                
        for prop in self.product_properties:
            if prop in ingredient_hints:
                relevant_hints.append(ingredient_hints[prop])
                
        if relevant_hints:
            for hint in relevant_hints[:3]:
                response += f"• {hint}\n"
        else:
            response += "• I'm formulated with carefully selected ingredients for optimal results\n"
            
        response += f"\nFor a complete ingredient list, please check the product packaging or official product information."
        
        return response
        
    async def _similar_products_response(self) -> str:
        """Find and describe similar products."""
        
        if not self.atomspace:
            return "I'd need my network connection to find similar products for you."
            
        # Use atomspace similarity finding
        similar_atoms = self.atomspace.find_similar_atoms(self, threshold=0.3)
        
        if not similar_atoms:
            return f"I'm quite unique! I don't have very similar products in my current network."
            
        response = f"Here are some products similar to me:\n\n"
        
        for similar_atom, similarity in similar_atoms[:3]:
            if hasattr(similar_atom, 'product_info'):
                shared_functions = set(self.product_functions) & set(similar_atom.product_functions)
                response += f"• **{similar_atom.name}** (similarity: {similarity:.1%})\n"
                if shared_functions:
                    response += f"  Shared functions: {', '.join(list(shared_functions)[:2])}\n"
                response += "\n"
                
        return response
        
    async def _general_response(self, message: str) -> str:
        """Handle general queries with personality."""
        
        personality = self.persona.get('personality_traits', [])
        
        if 'solution-focused' in personality:
            return f"I'm here to help solve your skincare concerns. Could you tell me more about what you're looking for? I specialize in {', '.join(self.product_functions[:2])} and I'm {', '.join(self.product_properties[:2])}."
        elif 'caring' in personality:
            return f"I care about your skin's wellbeing. What specific concerns do you have? I'm designed to help with {', '.join(self.product_functions[:2])} and I pride myself on being {', '.join(self.product_properties[:2])}."
        else:
            return f"I'm {self.name}, and I'm here to help! I specialize in {', '.join(self.product_functions[:2])}. What would you like to know about how I can benefit your skincare routine?"
            
    async def get_product_analysis(self) -> Dict[str, Any]:
        """Get comprehensive product analysis."""
        
        # Calculate effectiveness scores
        effectiveness_scores = {}
        for key, value in self.get_all_values().items():
            if key.startswith('effectiveness_') and isinstance(value, TruthValue):
                concern = key.replace('effectiveness_', '').replace('-', ' ')
                effectiveness_scores[concern] = {
                    'strength': value.strength,
                    'confidence': value.confidence
                }
                
        return {
            'basic_info': {
                'name': self.name,
                'category': self.product_category,
                'agent_type': self.agent_type
            },
            'capabilities': {
                'functions': self.product_functions,
                'properties': self.product_properties,
                'effectiveness_scores': effectiveness_scores
            },
            'persona': self.persona,
            'network_status': {
                'connections': len(self.get_neighbors()),
                'collaboration_mode': self.collaboration_mode,
                'interactions': self.interaction_count
            },
            'conversation_history': self.conversation_history[-5:]  # Last 5 exchanges
        }