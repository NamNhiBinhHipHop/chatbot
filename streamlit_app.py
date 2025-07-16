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

from core.rag_chain import deep_search_pipeline, debug_log
from core.milvus_utilis import save_to_milvus, search_similar_chunks, delete_file, delete_all, collection
from core.embedding import split_into_chunks
import fitz  # PyMuPDF

# Set Streamlit to run on port 8686
st.set_page_config(
    page_title="AI Immigration Lawyer Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

os.environ["STREAMLIT_SERVER_PORT"] = "8686"

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
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []  # List of dicts: {"role": "user"/"assistant", "content": ...}
    
    st.title("🤖 AI Immigration Lawyer Assistant")
    st.markdown("**US Immigration & Citizenship Document Analysis, AI to help you with your immigration questions**")
    
    # Sidebar: Only conversation management
    with st.sidebar:
        st.subheader("💬 Conversation")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content area: Live chat interface
    st.header("💬 Chat Interface")
    
    # Display chat history (top to bottom)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div style='text-align: right; font-size: 1.2em;'><b>🧑‍💼 You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: left;'><b>🤖 Assistant:</b> {msg['content']}</div>", unsafe_allow_html=True)
    
    # Chat input at the bottom
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message...", placeholder="e.g., What are the requirements for naturalization?", key="chat_input")
        submit = st.form_submit_button("Send")
    
    if submit and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("🤔 Thinking..."):
            # Build full cleaned Q&A chat history
            chat_history = []
            q_num = 1
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    chat_history.append(f"Q{q_num}: {msg['content']}")
                else:
                    # Clean answer of <think> tags
                    import re
                    cleaned = re.sub(r'<think>.*?</think>', '', msg['content'], flags=re.DOTALL)
                    cleaned = re.sub(r'<THINK>.*?</THINK>', '', cleaned, flags=re.DOTALL)
                    cleaned = cleaned.strip()
                    chat_history.append(f"A{q_num}: {cleaned}")
                    q_num += 1
            context = "\n".join(chat_history)
            answer = deep_search_pipeline(user_input, chat_history=context)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        # Show debug log in an expander
        with st.expander("🧠 Show LLM Thinking / Debug Output"):
            st.code(debug_log)
        st.rerun()

if __name__ == "__main__":
    main() 
