# AtomBot Integration for AF Beauty Products

This project transforms static beauty product entities into distributed cognitive agents using the atomlbot framework. Each product becomes an intelligent conversational agent that can discuss its properties, benefits, and collaborate with other products in the network.

## 🧠 What is AtomBot?

AtomBot combines:
- **Knowledge Representation**: Each product is represented as an atom in a semantic knowledge graph
- **Conversational AI**: Every product can engage in natural conversations about its benefits and usage
- **Distributed Cognition**: Products can collaborate and share knowledge across the network
- **Analogous Personas**: Each agent inherits personality traits based on its functions and properties

## 🚀 Features

- **Specialized Product Agents**: Each beauty product becomes a unique AI agent with its own personality
- **Natural Conversations**: Ask products about benefits, usage instructions, and recommendations
- **Network Collaboration**: Agents can work together to provide comprehensive skincare advice
- **Persona-Based Responses**: Each agent responds according to its product characteristics
- **Web Interface**: Interactive chat interface to communicate with product agents

## 📋 Requirements

- Python 3.7+
- BeautifulSoup4 for HTML parsing
- Basic web browser for the interface

## 🛠️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the System**:
   ```bash
   python test_atombot_system.py
   ```

3. **Run the Web Interface**:
   ```bash
   python run_server.py
   ```

4. **Open Your Browser**:
   Navigate to `http://localhost:8000` to access the product agent interface

## 🎯 How It Works

### Product Entity Extraction
The system analyzes existing HTML product pages and extracts:
- Product names and categories
- Functions (e.g., "acne-treatment", "anti-aging", "hydrates-skin")
- Properties (e.g., "professional-grade", "gentle", "daily-use")
- Automatically generated personas based on these characteristics

### Agent Creation
Each product becomes a specialized AtomBot with:
- **Unique Personality**: Based on product functions (e.g., acne products are "solution-focused")
- **Expertise Areas**: Deep knowledge about specific skincare concerns
- **Communication Style**: Tailored to the product's characteristics
- **Network Connections**: Links to related products for recommendations

### Distributed Cognition
Agents can:
- **Collaborate** on complex skincare routines
- **Share Knowledge** across the network
- **Make Recommendations** based on product relationships
- **Learn** from interactions and user feedback

## 💬 Example Conversations

### With "Acne Attack Pro-Masque":
**User**: "What benefits do you provide?"
**Agent**: "As Acne Attack Pro-Masque, I offer several key benefits:
• Acne Treatment
• Controls Oil
• Deep Cleansing

I'm particularly effective because I am professional-grade, intensive."

### With "Daily Ultra Defence":
**User**: "How should I use you?"
**Agent**: "Apply generously to clean skin 15 minutes before sun exposure. Reapply every 2 hours. I'm gentle enough for daily use as your protective barrier against environmental damage."

## 🏗️ Architecture

### Core Components

1. **atombot_core.py**: Core AtomBot framework implementation
   - AtomSpace for knowledge representation
   - Atom and Link classes for semantic relationships
   - ChatAgent base class for conversational capabilities

2. **product_agents.py**: Specialized ProductAgent class
   - Inherits from AtomBot
   - Product-specific conversation handling
   - Effectiveness scoring for different skin concerns

3. **atombot_integration.py**: Integration layer
   - ProductExtractor for HTML parsing
   - ProductAgentNetwork for managing agent relationships
   - Automatic persona generation

4. **product_agent_interface.html**: Web interface
   - Interactive chat with product agents
   - Agent selection and status display
   - Real-time conversation handling

### Data Flow

```
HTML Product Pages → ProductExtractor → Product Information
                                      ↓
Product Information → ProductAgent → AtomBot Instance
                                      ↓
AtomBot Instances → ProductAgentNetwork → Cognitive Network
                                      ↓
Web Interface ← API Server ← Agent Conversations
```

## 🧪 Testing

Run the test script to see the system in action:

```bash
python test_atombot_system.py
```

This demonstrates:
- Agent creation with specialized personas
- Natural language conversations
- Network collaboration capabilities
- Distributed cognitive reasoning

## 🌐 Web Interface Features

- **Agent Selection**: Choose from available product agents
- **Real-time Chat**: Natural conversations with each agent
- **Network Status**: View active agents and connections
- **Responsive Design**: Works on desktop and mobile devices
- **Conversation History**: Maintains chat history per agent

## 📊 Agent Personas

Each agent develops a unique persona based on its product characteristics:

### Acne Products
- **Personality**: Solution-focused, understanding, encouraging
- **Communication**: Direct and supportive
- **Expertise**: Acne control, oil management

### Anti-Aging Products
- **Personality**: Sophisticated, confidence-building, experienced
- **Communication**: Elegant and knowledgeable
- **Expertise**: Anti-aging, skin maturity

### Gentle/Daily Products
- **Personality**: Caring, reliable, protective
- **Communication**: Reassuring and informative
- **Expertise**: Daily care, skin protection

### Natural/Oil Products
- **Personality**: Nurturing, holistic, natural
- **Communication**: Warm and educational
- **Expertise**: Natural skincare, deep nourishment

## 🔗 Network Relationships

Agents form relationships based on:
- **Category Similarity**: Products in the same category (high similarity)
- **Function Overlap**: Shared skincare functions (medium similarity)
- **Complementary Use**: Products that work well together (contextual similarity)

## 🚀 Future Enhancements

- **LLM Integration**: Connect to GPT-4 or Claude for more sophisticated responses
- **Voice Interface**: Add speech-to-text and text-to-speech capabilities
- **Product Recommendations**: Enhanced recommendation engine based on skin analysis
- **Learning Capabilities**: Agents learn from user interactions and feedback
- **Mobile App**: Native mobile application for on-the-go consultations
- **Integration APIs**: Connect with e-commerce platforms and inventory systems

## 🤝 Contributing

This project demonstrates the concept of distributed cognitive agents for product entities. To extend it:

1. Add more sophisticated natural language processing
2. Integrate with real LLM APIs for enhanced conversations
3. Expand the knowledge graph with ingredient information
4. Add user profiling and personalized recommendations
5. Implement real-time learning from user interactions

## 📝 License

This project is part of the af.github.io repository and follows the same licensing terms.

## 🙏 Acknowledgments

- Built using concepts from the atomlbot framework
- Inspired by OpenCog AtomSpace architecture
- Product data extracted from existing RégimA website content