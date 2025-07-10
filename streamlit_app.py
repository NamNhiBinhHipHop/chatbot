#!/usr/bin/env python3
"""
AI Document Assistant - Streamlit Web Interface
"""

import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
import json
import datetime
from typing import List, Dict, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.rag_chain import ask_question_smart_with_toolcall, ask_llm_with_context, ask_with_full_context
from core.milvus_utilis import save_to_milvus, search_similar_chunks, delete_file, delete_all, collection
from core.embedding import split_into_chunks
import fitz  # PyMuPDF

# Page configuration
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitConversationMemory:
    """Manages conversation history for the Streamlit app"""
    
    def __init__(self):
        self.history: List[Dict] = []
        
    def add_ask_query(self, question: str, answer: str):
        """Add an ask query with its answer"""
        # Clean the answer before storing
        cleaned_answer = self._clean_answer(answer)
        entry = {
            "question": question,
            "answer": cleaned_answer,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        self.history.append(entry)
        
    def _clean_answer(self, answer: str) -> str:
        """Remove thinking tags and clean up the answer"""
        import re
        # Remove thinking tags and content
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
        answer = re.sub(r'<THINK>.*?</THINK>', '', answer, flags=re.DOTALL)
        # Clean up extra whitespace
        answer = re.sub(r'\n\s*\n', '\n\n', answer)
        answer = answer.strip()
        return answer
        
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation for context"""
        if not self.history:
            return ""
            
        recent_queries = self.history[-3:]  # Last 3 Q&A pairs
        summary_parts = []
        
        for i, entry in enumerate(recent_queries, 1):
            summary_parts.append(f"Q{i}: {entry['question']}")
            summary_parts.append(f"A{i}: {entry['answer']}")
                
        return "\n".join(summary_parts)
        
    def clear_history(self):
        """Clear conversation history"""
        self.history = []

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        st.error(f"❌ Error reading PDF {pdf_path}: {e}")
        return ""

def extract_text_from_txt(txt_path: str) -> str:
    """Extract text from a text file."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        st.error(f"❌ Error reading text file {txt_path}: {e}")
        return ""

def process_document(file_path: str, filename: str) -> bool:
    """Process a document and add it to the vector database."""
    # Extract text based on file type
    if filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif filename.lower().endswith(('.txt', '.md')):
        text = extract_text_from_txt(file_path)
    else:
        st.error(f"❌ Unsupported file type: {filename}")
        return False
    
    if not text.strip():
        st.error(f"❌ No text extracted from {filename}")
        return False
    
    # Split into chunks
    chunks = split_into_chunks(text)
    st.success(f"📄 Extracted {len(chunks)} chunks from {filename}")
    
    # Save to Milvus
    try:
        save_to_milvus(chunks, filename)
        st.success(f"✅ Successfully processed {filename}")
        return True
    except Exception as e:
        st.error(f"❌ Error saving to database: {e}")
        return False

def get_document_list():
    """Get list of documents in the database"""
    try:
        collection.load()
        results = collection.query(
            expr="",
            output_fields=["filename"],
            limit=1000
        )
        filenames = list(set([r["filename"] for r in results]))
        return filenames
    except Exception as e:
        st.error(f"❌ Error listing documents: {e}")
        return []

def main():
    # Initialize session state
    if 'conversation_memory' not in st.session_state:
        st.session_state.conversation_memory = StreamlitConversationMemory()
    
    # Header
    st.title("🤖 AI Immigration Lawyer Assistant")
    st.markdown("**US Immigration & Citizenship Document Analysis, AI to help you with your immigration questions**")
    
    # Sidebar: Only conversation management
    with st.sidebar:
        st.subheader("💬 Conversation")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.conversation_memory.clear_history()
            st.rerun()
    
    # Main content area (single column, chat only)
    st.header("💬 Chat Interface")
    
    # Chat input
    st.subheader("Ask a Question")
    question = st.text_input(
        "Type your question here...",
        placeholder="e.g., What are the requirements for naturalization?",
        key="question_input"
    )
    
    # Ask button and answer display
    if st.button("🤖 Ask", type="primary"):
        if question:
            with st.spinner("🤔 Thinking..."):
                try:
                    # Get conversation context
                    context = st.session_state.conversation_memory.get_context_summary()
                    
                    # Pass the context directly to the function
                    answer = ask_question_smart_with_toolcall(question, context)
                    st.session_state.conversation_memory.add_ask_query(question, answer)
                    
                    # Display the answer immediately
                    st.success("💡 Answer:")
                    st.write(answer)
                    
                    # Clear the input
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter a question")
    
    # Show the most recent answer if available
    if st.session_state.conversation_memory.history:
        latest_entry = st.session_state.conversation_memory.history[-1]
        st.success("💡 Latest Answer:")
        st.write(latest_entry['answer'])
    
    # Chat history display (without timestamps) - right below the answer
    if st.session_state.conversation_memory.history:
        st.subheader("📝 Conversation History")
        for i, entry in enumerate(st.session_state.conversation_memory.history):
            with st.expander(f"Q{i+1}: {entry['question']}"):
                st.write(f"**Question:** {entry['question']}")
                st.write(f"**Answer:** {entry['answer']}")

if __name__ == "__main__":
    main() 