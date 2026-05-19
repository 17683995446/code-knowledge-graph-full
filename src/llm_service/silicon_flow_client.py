"""
LLM Service Module
Integration with Silicon Flow API for code analysis and Q&A
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import requests

from ..core.configuration import CONFIG, LOGGER


@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    error: Optional[str] = None


class SiliconFlowLLMService:
    """
    Silicon Flow API integration
    Uses free models for code analysis and knowledge graph queries
    """
    
    def __init__(
        self,
        api_key: str = CONFIG.api_key,
        base_url: str = CONFIG.api_base_url
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "Qwen/Qwen2.5-7B-Instruct"
        self.timeout = 60
        self.max_retries = 3
    
    def _make_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> LLMResponse:
        """Make request to Silicon Flow API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return LLMResponse(
                        content=data['choices'][0]['message']['content'],
                        model=data.get('model', self.model),
                        usage=data.get('usage', {}),
                        finish_reason=data['choices'][0].get('finish_reason', 'stop')
                    )
                elif response.status_code == 429:
                    LOGGER.warning("Rate limited, waiting...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return LLMResponse(
                        content="",
                        model=self.model,
                        usage={},
                        finish_reason="error",
                        error=f"API error: {response.status_code}"
                    )
                    
            except requests.exceptions.Timeout:
                LOGGER.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    return LLMResponse(
                        content="",
                        model=self.model,
                        usage={},
                        finish_reason="error",
                        error="Request timeout"
                    )
            except Exception as e:
                LOGGER.error(f"Request error: {e}")
                return LLMResponse(
                    content="",
                    model=self.model,
                    usage={},
                    finish_reason="error",
                    error=str(e)
                )
        
        return LLMResponse(
            content="",
            model=self.model,
            usage={},
            finish_reason="error",
            error="Max retries exceeded"
        )
    
    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Send chat request"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self._make_request(messages, temperature=temperature)
    
    def analyze_code(
        self,
        code: str,
        language: str,
        analysis_type: str = "general"
    ) -> LLMResponse:
        """Analyze code and provide insights"""
        prompts = {
            "general": f"Analyze this {language} code and provide a summary:\n\n```{language}\n{code}\n```",
            "complexity": f"Analyze the complexity of this {language} code:\n\n```{language}\n{code}\n```",
            "bugs": f"Find potential bugs in this {language} code:\n\n```{language}\n{code}\n```",
            "suggestions": f"Provide improvement suggestions for this {language} code:\n\n```{language}\n{code}\n```"
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        
        system_prompt = """You are an expert code analyst. Provide clear, concise analysis focusing on:
- Functionality and purpose
- Code quality and readability
- Potential improvements
- Relationships with other code elements"""
        
        return self.chat(prompt, system_prompt)
    
    def explain_relationship(
        self,
        caller: str,
        callee: str,
        context: str
    ) -> LLMResponse:
        """Explain relationship between code elements"""
        prompt = f"""Explain the relationship between these code elements:

Caller: {caller}
Callee: {callee}

Context:
{context}

Provide a clear explanation of how these elements interact."""
        
        system_prompt = """You are explaining code relationships in a knowledge graph. 
Be concise and focus on the functional relationship between elements."""
        
        return self.chat(prompt, system_prompt)
    
    def query_knowledge_graph(
        self,
        question: str,
        graph_context: str
    ) -> LLMResponse:
        """Answer questions about the code knowledge graph"""
        prompt = f"""Based on the following code knowledge graph information, answer the question:

Graph Information:
{graph_context}

Question: {question}

If the graph information doesn't contain enough context to answer, say so."""
        
        system_prompt = """You are a code knowledge graph assistant. Answer questions based on the provided graph data.
Always reference specific elements (files, types, functions) when available."""
        
        return self.chat(prompt, system_prompt)
    
    def generate_documentation(
        self,
        type_info: Dict[str, Any],
        function_info: List[Dict[str, Any]]
    ) -> LLMResponse:
        """Generate documentation for a type or module"""
        prompt = f"""Generate documentation for the following code elements:

Type/Module:
{json.dumps(type_info, indent=2)}

Functions/Methods:
{json.dumps(function_info, indent=2)}

Provide well-structured documentation including:
1. Overview
2. Key functionalities
3. Usage examples
4. Dependencies"""
        
        system_prompt = """You are a documentation generator. Create clear, comprehensive documentation.
Use markdown formatting for structure."""
        
        return self.chat(prompt, system_prompt, temperature=0.5)


class KnowledgeGraphRAGService:
    """
    RAG (Retrieval Augmented Generation) service for knowledge graph
    """
    
    def __init__(self, llm_service: SiliconFlowLLMService):
        self.llm_service = llm_service
        self._type_index: Dict[str, Dict[str, Any]] = {}
        self._function_index: Dict[str, Dict[str, Any]] = {}
        self._file_index: Dict[str, Dict[str, Any]] = {}
    
    def index_entity(
        self,
        entity_type: str,
        entity_id: int,
        name: str,
        data: Dict[str, Any]
    ) -> None:
        """Index an entity for retrieval"""
        key = f"{entity_type}:{entity_id}:{name}"
        
        if entity_type == "type":
            self._type_index[key] = data
        elif entity_type == "function":
            self._function_index[key] = data
        elif entity_type == "file":
            self._file_index[key] = data
    
    def retrieve_relevant_context(
        self,
        query: str,
        limit: int = 5
    ) -> str:
        """Retrieve relevant context for a query"""
        query_lower = query.lower()
        
        relevant_types = []
        for key, data in self._type_index.items():
            name = data.get('name', '').lower()
            if any(word in name for word in query_lower.split()):
                relevant_types.append(data)
                if len(relevant_types) >= limit:
                    break
        
        relevant_funcs = []
        for key, data in self._function_index.items():
            name = data.get('name', '').lower()
            if any(word in name for word in query_lower.split()):
                relevant_funcs.append(data)
                if len(relevant_funcs) >= limit:
                    break
        
        context_parts = ["## Relevant Types\n"]
        for t in relevant_types:
            context_parts.append(f"- {t.get('name')} ({t.get('kind')}) in {t.get('file_path', 'Unknown')}")
        
        context_parts.append("\n## Relevant Functions\n")
        for f in relevant_funcs:
            context_parts.append(f"- {f.get('name')} in {f.get('file_path', 'Unknown')}")
        
        return '\n'.join(context_parts)
    
    def answer_with_rag(
        self,
        question: str
    ) -> LLMResponse:
        """Answer question using RAG"""
        context = self.retrieve_relevant_context(question)
        
        return self.llm_service.query_knowledge_graph(question, context)


LLM_SERVICE: Optional[SiliconFlowLLMService] = None

def initialize_llm_service(api_key: Optional[str] = None) -> SiliconFlowLLMService:
    """Initialize global LLM service"""
    global LLM_SERVICE
    
    if api_key:
        CONFIG.api_key = api_key
    
    if not CONFIG.api_key:
        LOGGER.warning("No API key provided for LLM service")
        return None
    
    LLM_SERVICE = SiliconFlowLLMService()
    LOGGER.info(f"LLM service initialized with model: {LLM_SERVICE.model}")
    
    return LLM_SERVICE

def get_llm_service() -> Optional[SiliconFlowLLMService]:
    """Get global LLM service"""
    return LLM_SERVICE
