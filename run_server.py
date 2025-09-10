#!/usr/bin/env python3
"""
Simple web server for the AtomBot Product Agent Interface.

This server provides the web interface and API endpoints for interacting
with the product agents.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    import socket
except ImportError:
    print("Warning: Some HTTP modules not available. Web server may have limited functionality.")

# Import local modules
import sys
sys.path.append('.')

from atomlbot_integration import ProductExtractor, ProductAgentNetwork

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductAgentServer:
    """Web server for the product agent interface."""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.network = None
        self.agents_data = {}
        
    async def initialize_agents(self):
        """Initialize the product agent network."""
        try:
            # Extract product information
            extractor = ProductExtractor("sources")
            products = extractor.extract_all_products()
            
            if not products:
                # Create sample agents if no products found
                products = self._create_sample_products()
                
            logger.info(f"Loaded {len(products)} products")
            
            # Create agent network
            self.network = ProductAgentNetwork()
            
            # Create agents
            for product_info in products:
                await self.network.create_product_agent(product_info)
                
            # Set up relationships
            await self.network.setup_product_relationships()
            
            # Store data for API
            self.agents_data = {
                'agents': {name: {
                    'name': agent.name,
                    'category': agent.product_category,
                    'functions': agent.product_functions,
                    'properties': agent.product_properties,
                    'persona': agent.persona,
                    'status': 'active'
                } for name, agent in self.network.product_agents.items()},
                'network_status': 'connected',
                'total_agents': len(self.network.product_agents)
            }
            
            logger.info(f"Agent network initialized with {len(self.network.product_agents)} agents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            return False
            
    def _create_sample_products(self):
        """Create sample products for demonstration."""
        return [
            {
                'name': 'Acne Attack Pro-Masque',
                'filename': 'acne-attack-pro-masque',
                'category': 'acne',
                'functions': ['acne-treatment', 'controls-oil', 'deep-cleansing'],
                'properties': ['professional-grade', 'intensive'],
                'persona': {
                    'description': 'I am a solution-focused acne treatment specialist passionate about clear skin.',
                    'personality_traits': ['solution-focused', 'understanding', 'encouraging'],
                    'communication_style': 'direct and supportive',
                    'expertise_areas': ['acne control', 'oil management']
                }
            },
            {
                'name': 'Daily Ultra Defence',
                'filename': 'daily-ultra-defence',
                'category': 'defence',
                'functions': ['environmental-protection', 'barrier-protection'],
                'properties': ['daily-use', 'gentle'],
                'persona': {
                    'description': 'I am your daily protection guardian for healthy, resilient skin.',
                    'personality_traits': ['protective', 'reliable', 'caring'],
                    'communication_style': 'reassuring and informative',
                    'expertise_areas': ['daily protection', 'skin barriers']
                }
            },
            {
                'name': 'Active Facial Oil',
                'filename': 'active-facial-oil',
                'category': 'oil',
                'functions': ['hydrates-skin', 'nourishes-skin'],
                'properties': ['natural', 'nourishing'],
                'persona': {
                    'description': 'I am a nurturing natural oil for deep skin nourishment and glow.',
                    'personality_traits': ['nurturing', 'natural', 'holistic'],
                    'communication_style': 'warm and educational',
                    'expertise_areas': ['natural skincare', 'deep hydration']
                }
            },
            {
                'name': 'Eye Opener Serum Revolution EYZ',
                'filename': 'eye-opener-serum',
                'category': 'eye-care',
                'functions': ['reduces-puffiness', 'brightens-eye-area'],
                'properties': ['concentrated', 'gentle'],
                'persona': {
                    'description': 'I am a precise eye care specialist focused on bright, youthful eyes.',
                    'personality_traits': ['precise', 'gentle', 'expert'],
                    'communication_style': 'careful and detailed',
                    'expertise_areas': ['eye care', 'anti-puffiness']
                }
            },
            {
                'name': 'Anti-Inflamm-Ageing Complex',
                'filename': 'anti-inflamm-ageing',
                'category': 'anti-ageing',
                'functions': ['anti-aging', 'reduces-fine-lines', 'firms-skin'],
                'properties': ['premium', 'concentrated'],
                'persona': {
                    'description': 'I am a sophisticated anti-aging specialist for mature, confident skin.',
                    'personality_traits': ['sophisticated', 'confidence-building', 'experienced'],
                    'communication_style': 'elegant and knowledgeable',
                    'expertise_areas': ['anti-aging', 'skin maturity']
                }
            }
        ]
        
    async def chat_with_agent(self, agent_name: str, message: str) -> Dict[str, Any]:
        """Chat with a specific agent."""
        if not self.network or agent_name not in self.network.product_agents:
            return {
                'error': f'Agent "{agent_name}" not found',
                'response': "I'm sorry, that agent is not available right now."
            }
            
        try:
            agent = self.network.product_agents[agent_name]
            response = await agent.enhanced_chat(message)
            
            return {
                'agent': agent_name,
                'message': message,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Chat error with {agent_name}: {e}")
            return {
                'error': str(e),
                'response': "I'm experiencing some technical difficulties. Please try again."
            }

    def get_agent_data(self) -> Dict[str, Any]:
        """Get data about available agents."""
        return self.agents_data
        
    def start_server(self):
        """Start the web server."""
        
        class RequestHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, server_instance=None, **kwargs):
                self.server_instance = server_instance
                super().__init__(*args, **kwargs)
                
            def do_GET(self):
                """Handle GET requests."""
                parsed_path = urlparse(self.path)
                
                if parsed_path.path == '/':
                    # Serve the main interface
                    self.serve_file('product_agent_interface.html')
                elif parsed_path.path == '/api/agents':
                    # Return agent data
                    self.serve_json(self.server_instance.get_agent_data())
                elif parsed_path.path.startswith('/api/'):
                    self.serve_json({'error': 'Endpoint not found'}, 404)
                else:
                    # Serve static files
                    super().do_GET()
                    
            def do_POST(self):
                """Handle POST requests."""
                parsed_path = urlparse(self.path)
                
                if parsed_path.path == '/api/chat':
                    asyncio.create_task(self.handle_chat_request())
                else:
                    self.serve_json({'error': 'Endpoint not found'}, 404)
                    
            async def handle_chat_request(self):
                """Handle chat API requests."""
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    agent_name = data.get('agent')
                    message = data.get('message', '')
                    
                    if not agent_name or not message:
                        self.serve_json({'error': 'Missing agent or message'}, 400)
                        return
                        
                    response = await self.server_instance.chat_with_agent(agent_name, message)
                    self.serve_json(response)
                    
                except Exception as e:
                    logger.error(f"Chat request error: {e}")
                    self.serve_json({'error': 'Internal server error'}, 500)
                    
            def serve_file(self, filename):
                """Serve a static file."""
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Content-length', len(content))
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                    
                except FileNotFoundError:
                    self.send_error(404, f"File {filename} not found")
                    
            def serve_json(self, data, status=200):
                """Serve JSON response."""
                content = json.dumps(data, indent=2)
                
                self.send_response(status)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-length', len(content))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                
            def log_message(self, format, *args):
                """Override to reduce log noise."""
                return
        
        # Create partial function to pass server instance
        def handler_factory(*args, **kwargs):
            return RequestHandler(*args, server_instance=self, **kwargs)
            
        try:
            server = HTTPServer(('localhost', self.port), handler_factory)
            print(f"🌐 Server running at http://localhost:{self.port}")
            print(f"💬 Product Agent Interface available at http://localhost:{self.port}")
            print("Press Ctrl+C to stop the server")
            
            server.serve_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")


async def main():
    """Main function to start the server."""
    
    print("🧠 ATOMBOT PRODUCT AGENT SERVER")
    print("="*50)
    
    server = ProductAgentServer()
    
    print("Initializing product agents...")
    success = await server.initialize_agents()
    
    if success:
        print("✅ Agent network ready!")
        server.start_server()
    else:
        print("❌ Failed to initialize agents")


if __name__ == "__main__":
    asyncio.run(main())