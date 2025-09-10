"""
Core AtomBot components for the af.github.io integration.

This module provides simplified implementations of the core atomlbot components
needed for the product agent system.
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)


class Value:
    """Base class for values in the atomspace."""
    
    def __init__(self, value: Any):
        self.value = value
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def __str__(self):
        return str(self.value)
        
    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


class StringValue(Value):
    """String value type."""
    pass


class FloatValue(Value):
    """Float value type."""
    pass


class TruthValue(Value):
    """Truth value with strength and confidence."""
    
    def __init__(self, strength: float = 0.5, confidence: float = 0.5):
        self.strength = max(0.0, min(1.0, strength))
        self.confidence = max(0.0, min(1.0, confidence))
        super().__init__((self.strength, self.confidence))
        
    def __str__(self):
        return f"TruthValue({self.strength:.3f}, {self.confidence:.3f})"


class StreamValue(Value):
    """Stream value for time-series data."""
    
    def __init__(self, name: str):
        self.name = name
        self.stream = []
        super().__init__(self.stream)
        
    def push(self, item: Any):
        """Add item to stream."""
        self.stream.append({
            'data': item,
            'timestamp': datetime.now().isoformat()
        })
        self.updated_at = datetime.now()


class Atom:
    """Base atom class representing knowledge nodes."""
    
    def __init__(self, atom_type: str, name: str, atomspace: Optional['AtomSpace'] = None):
        self.id = str(uuid.uuid4())
        self.atom_type = atom_type
        self.name = name
        self.atomspace = atomspace
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Connections to other atoms
        self.incoming: Set['Link'] = set()
        self.outgoing: Set['Link'] = set()
        
        # Values attached to this atom
        self.values: Dict[str, Value] = {}
        
        # Register with atomspace if provided
        if atomspace:
            atomspace.add_atom(self)
            
    def set_value(self, key: str, value: Value):
        """Set a value on this atom."""
        self.values[key] = value
        self.updated_at = datetime.now()
        
    def get_value(self, key: str) -> Optional[Value]:
        """Get a value from this atom."""
        return self.values.get(key)
        
    def get_all_values(self) -> Dict[str, Value]:
        """Get all values attached to this atom."""
        return self.values.copy()
        
    def get_neighbors(self) -> List['Atom']:
        """Get all atoms connected to this one."""
        neighbors = []
        for link in self.incoming | self.outgoing:
            for atom in link.outgoing:
                if atom != self:
                    neighbors.append(atom)
        return neighbors
        
    def __str__(self):
        return f"{self.atom_type}:{self.name}"
        
    def __repr__(self):
        return f"Atom(type={self.atom_type}, name='{self.name}', id={self.id[:8]})"
        
    def __hash__(self):
        return hash(self.id)
        
    def __eq__(self, other):
        return isinstance(other, Atom) and self.id == other.id


class Link(Atom):
    """Link atom connecting multiple atoms."""
    
    def __init__(self, link_type: str, outgoing: List[Atom], atomspace: Optional['AtomSpace'] = None, strength: float = 0.5):
        name = f"{link_type}({', '.join(str(atom) for atom in outgoing)})"
        super().__init__(link_type, name, atomspace)
        
        self.outgoing = outgoing
        self.strength = strength
        
        # Add this link to incoming sets of target atoms
        for atom in outgoing:
            atom.incoming.add(self)


class ConceptNode(Atom):
    """Concept node representing a concept."""
    
    def __init__(self, name: str, atomspace: Optional['AtomSpace'] = None):
        super().__init__("ConceptNode", name, atomspace)


class PredicateNode(Atom):
    """Predicate node representing a predicate/relationship."""
    
    def __init__(self, name: str, atomspace: Optional['AtomSpace'] = None):
        super().__init__("PredicateNode", name, atomspace)


class AtomSpace:
    """AtomSpace containing atoms and managing the knowledge graph."""
    
    def __init__(self):
        self.atoms: Dict[str, Atom] = {}
        self.links: Dict[str, Link] = {}
        self.created_at = datetime.now()
        
    def add_atom(self, atom: Atom) -> Atom:
        """Add an atom to the atomspace."""
        self.atoms[atom.id] = atom
        if isinstance(atom, Link):
            self.links[atom.id] = atom
        return atom
        
    def get_atom(self, atom_id: str) -> Optional[Atom]:
        """Get an atom by ID."""
        return self.atoms.get(atom_id)
        
    def find_atoms_by_name(self, name: str) -> List[Atom]:
        """Find atoms by name."""
        return [atom for atom in self.atoms.values() if atom.name == name]
        
    def find_atoms_by_type(self, atom_type: str) -> List[Atom]:
        """Find atoms by type."""
        return [atom for atom in self.atoms.values() if atom.atom_type == atom_type]
        
    def add_link(self, link_type: str, outgoing: List[Atom], strength: float = 0.5) -> Link:
        """Add a link between atoms."""
        link = Link(link_type, outgoing, self, strength)
        return link
        
    def get_link(self, link_type: str, outgoing: List[Atom]) -> Optional[Link]:
        """Find an existing link of given type between atoms."""
        for link in self.links.values():
            if (link.atom_type == link_type and 
                len(link.outgoing) == len(outgoing) and
                all(a in link.outgoing for a in outgoing)):
                return link
        return None
        
    def get_all_atoms(self) -> List[Atom]:
        """Get all atoms in the atomspace."""
        return list(self.atoms.values())
        
    def find_similar_atoms(self, atom: Atom, threshold: float = 0.5) -> List[tuple]:
        """Find atoms similar to the given atom."""
        similar = []
        
        for other in self.atoms.values():
            if other != atom:
                # Simple similarity based on shared connections
                shared_neighbors = set(atom.get_neighbors()) & set(other.get_neighbors())
                total_neighbors = len(set(atom.get_neighbors()) | set(other.get_neighbors()))
                
                if total_neighbors > 0:
                    similarity = len(shared_neighbors) / total_neighbors
                    if similarity >= threshold:
                        similar.append((other, similarity))
                        
        return sorted(similar, key=lambda x: x[1], reverse=True)
        
    async def propagate_values(self, source_atom: Atom, value_key: str, max_hops: int = 3):
        """Propagate values through the network."""
        if value_key not in source_atom.values:
            return
            
        value = source_atom.values[value_key]
        visited = {source_atom}
        queue = [(source_atom, 0)]
        
        while queue:
            current_atom, hop_count = queue.pop(0)
            
            if hop_count >= max_hops:
                continue
                
            for neighbor in current_atom.get_neighbors():
                if neighbor not in visited:
                    # Propagate value with diminishing strength
                    propagated_value = Value(value.value)
                    neighbor.set_value(f"propagated_{value_key}", propagated_value)
                    
                    visited.add(neighbor)
                    queue.append((neighbor, hop_count + 1))
                    
        logger.info(f"Propagated {value_key} from {source_atom} to {len(visited)-1} atoms")
        
    def __str__(self):
        return f"AtomSpace(atoms={len(self.atoms)}, links={len(self.links)})"


class ChatAgent:
    """Base chat agent with conversational capabilities."""
    
    def __init__(self, agent_id: str, name: str, system_prompt: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.system_prompt = system_prompt
        self.interaction_count = 0
        self.last_interaction = None
        self.conversation_history = []
        
    async def chat(self, message: str) -> str:
        """Process a chat message and return response."""
        self.interaction_count += 1
        self.last_interaction = datetime.now()
        
        # Store conversation
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': 'user'
        })
        
        # Generate response based on system prompt and context
        response = await self._generate_response(message)
        
        # Store response
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'message': response,
            'type': 'agent'
        })
        
        return response
        
    async def _generate_response(self, message: str) -> str:
        """Generate a response to the user message."""
        # This is a simplified response generation
        # In a real implementation, this would use an LLM
        
        message_lower = message.lower()
        
        # Basic keyword-based responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return f"Hello! I'm {self.name}. How can I help you today?"
            
        elif any(word in message_lower for word in ['what', 'tell me', 'describe']):
            return self._describe_self()
            
        elif any(word in message_lower for word in ['help', 'assist', 'support']):
            return self._offer_help()
            
        elif any(word in message_lower for word in ['benefits', 'good for', 'does']):
            return self._explain_benefits()
            
        else:
            return f"I'm {self.name}. Could you tell me more about what you'd like to know? I'm here to help with any questions about my properties and benefits."
            
    def _describe_self(self) -> str:
        """Provide self-description."""
        return f"I am {self.name}, a specialized beauty agent. {self.system_prompt}"
        
    def _offer_help(self) -> str:
        """Offer help to the user."""
        return f"I'm here to help! As {self.name}, I can tell you about my properties, benefits, and how I can address your skincare needs. What would you like to know?"
        
    def _explain_benefits(self) -> str:
        """Explain benefits."""
        return f"As {self.name}, I offer various benefits for your skincare routine. Let me know your specific concerns and I'll explain how I can help!"


class AtomBot(Atom, ChatAgent):
    """Hybrid atom and chat agent - the core AtomBot class."""
    
    def __init__(self, atom_type: str, name: str, atomspace: Optional[AtomSpace] = None, system_prompt: str = ""):
        # Initialize both parent classes
        Atom.__init__(self, atom_type, name, atomspace)
        ChatAgent.__init__(self, self.id, name, system_prompt)
        
        self.agent_type = "AtomBot"
        self.knowledge_role = self._determine_knowledge_role()
        self.collaboration_mode = "active"
        
    def _determine_knowledge_role(self) -> str:
        """Determine knowledge role based on atom type."""
        if self.atom_type == "ConceptNode":
            return "concept_expert"
        elif self.atom_type == "PredicateNode":
            return "relationship_expert"
        else:
            return "knowledge_node"
            
    async def collaborate_with_network(self, task: str) -> Dict[str, Any]:
        """Collaborate with other AtomBots in the network."""
        if not self.atomspace:
            return {"error": "No atomspace available for collaboration"}
            
        collaboration_results = {
            "task": task,
            "initiator": self.name,
            "responses": [],
            "insights": []
        }
        
        # Find collaborators among connected atoms
        collaborators = []
        for neighbor in self.get_neighbors():
            if hasattr(neighbor, 'chat') and hasattr(neighbor, 'collaboration_mode'):
                if neighbor.collaboration_mode == "active":
                    collaborators.append(neighbor)
                    
        # Collaborate with up to 3 neighbors
        for collaborator in collaborators[:3]:
            try:
                response = await collaborator.chat(f"Collaboration request from {self.name}: {task}")
                collaboration_results["responses"].append({
                    "agent": collaborator.name,
                    "response": response
                })
            except Exception as e:
                collaboration_results["responses"].append({
                    "agent": collaborator.name,
                    "error": str(e)
                })
                
        collaboration_results["insights"].append(
            f"Collaborated with {len(collaboration_results['responses'])} network agents"
        )
        
        return collaboration_results
        
    async def enhanced_chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Enhanced chat with atom capabilities."""
        # Add atom context
        enhanced_context = f"""
Context about me:
- I am a {self.atom_type} representing '{self.name}'
- Knowledge role: {self.knowledge_role}
- Connected to {len(self.get_neighbors())} other agents
- Have {len(self.get_all_values())} values stored
"""
        
        if context:
            enhanced_context += f"\nAdditional context: {context}"
            
        # Add context to system prompt temporarily
        original_prompt = self.system_prompt
        self.system_prompt = f"{original_prompt}\n{enhanced_context}"
        
        try:
            response = await self.chat(message)
        finally:
            # Restore original prompt
            self.system_prompt = original_prompt
            
        return response
        
    def get_atombot_status(self) -> Dict[str, Any]:
        """Get comprehensive status of this AtomBot."""
        return {
            "atom_info": {
                "id": self.id,
                "type": self.atom_type,
                "name": self.name,
                "created": self.created_at.isoformat(),
                "updated": self.updated_at.isoformat()
            },
            "agent_info": {
                "interactions": self.interaction_count,
                "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
                "collaboration_mode": self.collaboration_mode,
                "knowledge_role": self.knowledge_role
            },
            "network_info": {
                "incoming_links": len(self.incoming),
                "outgoing_links": len(self.outgoing),
                "total_neighbors": len(self.get_neighbors()),
                "values_count": len(self.get_all_values())
            },
            "atomspace": str(self.atomspace) if self.atomspace else None
        }
        
    def __str__(self):
        return f"AtomBot({self.atom_type}:'{self.name}')"
        
    def __repr__(self):
        return f"AtomBot(type={self.atom_type}, name='{self.name}', role={self.knowledge_role})"