import json
import os
import base64
import logging
from typing import List, Dict, Any
from openai import OpenAI
from vector_store import vector_store

logger = logging.getLogger(__name__)

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def answer_question(question: str, image_base64: str = None) -> Dict[str, Any]:
    """
    Answer a student question using the vector store and OpenAI.
    """
    if not openai_client:
        return {
            "answer": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
            "links": []
        }
    
    try:
        # Search for relevant content
        search_results = vector_store.search(question, top_k=5)
        
        # Prepare context from search results
        context_parts = []
        relevant_links = []
        
        for doc, score in search_results:
            if score > 0.3:  # Threshold for relevance
                context_parts.append(f"Title: {doc['title']}\nURL: {doc['url']}\nContent: {doc['content'][:500]}...")
                relevant_links.append({
                    "url": doc['url'],
                    "text": doc['title']
                })
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": """You are a helpful Teaching Assistant for the Tools in Data Science course at IIT Madras. 
                
Your task is to answer student questions based on the provided course content and discourse discussions.

Guidelines:
1. Provide accurate, helpful answers based on the context provided
2. If the question involves choosing between models (like GPT versions), refer to the specific requirements mentioned in the course materials
3. Be concise but comprehensive
4. If you cannot find relevant information in the context, say so clearly
5. Focus on practical, actionable advice for students

Respond with a clear, helpful answer that addresses the student's question directly."""
            }
        ]
        
        # Prepare user message
        user_content = [
            {
                "type": "text",
                "text": f"""Student Question: {question}

Relevant Course Content and Discussions:
{context}

Please provide a helpful answer to the student's question based on the above context."""
            }
        ]
        
        # Add image if provided
        if image_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })
            user_content[0]["text"] += "\n\nNote: The student has also provided an image/screenshot. Please analyze it in context of their question."
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Get response from OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o"
            messages=messages,
            max_tokens=1000,
            temperature=0.1
        )
        
        answer = response.choices[0].message.content
        
        # Filter and rank links based on relevance
        final_links = rank_and_filter_links(relevant_links, question, answer)
        
        return {
            "answer": answer,
            "links": final_links[:3]  # Return top 3 most relevant links
        }
        
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return {
            "answer": f"Sorry, I encountered an error while processing your question: {str(e)}",
            "links": []
        }


def rank_and_filter_links(links: List[Dict], question: str, answer: str) -> List[Dict]:
    """
    Rank and filter links based on relevance to the question and answer.
    """
    if not links:
        return []
    
    # Simple ranking based on keyword matching
    question_lower = question.lower()
    answer_lower = answer.lower()
    
    scored_links = []
    for link in links:
        score = 0
        title_lower = link['text'].lower()
        
        # Score based on title relevance
        question_words = question_lower.split()
        for word in question_words:
            if len(word) > 3 and word in title_lower:
                score += 1
        
        # Check if link is mentioned in answer
        if link['url'] in answer or link['text'].lower() in answer_lower:
            score += 2
        
        scored_links.append((link, score))
    
    # Sort by score and return
    scored_links.sort(key=lambda x: x[1], reverse=True)
    return [link for link, score in scored_links if score > 0]


def initialize_vector_store():
    """
    Initialize the vector store with scraped content.
    """
    try:
        vector_store.load_or_create_index()
        logger.info("Vector store initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
