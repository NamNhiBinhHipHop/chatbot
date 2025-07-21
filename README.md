# AI Document Assistant

A powerful document processing and question-answering system built with Python. The system uses Milvus vector database for efficient semantic search and custom LLM models for intelligent responses. Features a command-line interface (for developers) and a Streamlit web app (for end users) for USCIS documents.

## 🛠️ Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Custom LLM API endpoint and key
- 8GB+ RAM (for Milvus and ML models)

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/NamNhiBinhHipHop/chatbot.git
cd chatbot
```

### 2. Create Virtual Environment
```bash
python3.11 -m venv env311
source env311/bin/activate  # On Windows: env311\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure LLM Settings
Update `config/config.py` with your LLM settings:
```python
LLM_API_URL = "https://your-llm-endpoint.com/v1/chat/completions"
LLM_API_KEY = "your_llm_api_key_here"
```

### 5. Start Milvus Database
```bash
docker-compose up -d
```

Wait for all containers to be healthy (check with `docker-compose ps`).

## 🎯 Usage

### Streamlit Web App (Recommended for End Users)

Run the following to launch the user-friendly web interface:
```bash
streamlit run streamlit_app.py
```
- Open your browser to http://localhost:8501
- Upload, search, and interact with your documents easily

### Command Line Interface (For Developers)

#### Interactive Mode
```bash
python cli_app.py --interactive
```

#### Single Commands
```bash
# Ask a question
python cli_app.py --ask "What are the requirements for naturalization?"

# Upload a document
python cli_app.py --upload "path/to/document.pdf"

# Search for content
python cli_app.py --search "immigration law"

# List all documents
python cli_app.py --list

# Delete a document
python cli_app.py --delete "filename.pdf"

# Delete all documents
python cli_app.py --delete-all
```

### Interactive Commands
Once in interactive mode, you can use:
- `ask <question>` - Ask questions about your documents
- `upload <file>` - Upload and process a document
- `search <query>` - Search for similar content
- `delete <filename>` - Delete a document from the database
- `delete all` - Delete all documents from the database
- `list` - List all documents in the database
- `help` - Show available commands
- `quit` - Exit the application

### Web Crawler

#### Crawl USCIS Documents
```bash
python web_crawler.py --max-pages 50 --delay 1.5
```

#### Custom Crawling
```bash
# Crawl specific websites
python web_crawler.py --urls "https://example.com" "https://another.com" --names "site1" "site2"

# Custom settings
python web_crawler.py --max-pages 30 --delay 2.0 --output "my_data"
```

## 🏗️ Project Structure

```
chatbot/
├── core/                    # Core functionality
│   ├── rag_chain.py        # RAG implementation with smart routing
│   ├── embedding.py        # Text embedding utilities
│   └── milvus_utilis.py    # Milvus database operations
├── config/                 # Configuration files
│   └── config.py          # LLM API settings
├── testing files/          # Test documents
├── cli_app.py             # Command-line interface
├── web_crawler.py         # Web crawler for USCIS and other sites
├── docker-compose.yml     # Milvus database setup
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

### LLM Settings
Update `config/config.py`:
```python
LLM_API_URL = "https://your-llm-endpoint.com/v1/chat/completions"
LLM_API_KEY = "your_llm_api_key_here"
```

### Milvus Settings
The system uses Milvus 2.5.11 with:
- Vector dimension: 384 (all-MiniLM-L6-v2 model)
- Index type: IVF_SQ8
- Metric type: Inner Product

### Content Processing
- Chunk size: 300 characters
- Chunk overlap: 50 characters
- Batch size: 32 chunks
- Context limit: 8000 characters (prevents API errors)

## 🎨 Features in Detail

### Smart Routing System

The system intelligently routes questions to the most appropriate processing method:

#### 1. Semantic Search Mode
- Uses semantic search to find relevant chunks
- Faster responses with focused answers
- Best for specific, factual questions
- Limited context to prevent API errors

#### 2. Specific Question Mode
- Handles vague or overly broad questions
- Guides users to ask more specific questions
- Prevents processing of huge contexts
- Improves response quality and speed

### Web Crawler Capabilities
- **USCIS Integration**: Specialized crawler for USCIS.gov
- **AI-Powered Filtering**: Intelligent content relevance detection
- **Content Extraction**: Smart text extraction from various page structures
- **Rate Limiting**: Respectful crawling with configurable delays
- **Content Cleaning**: Automatic removal of navigation and non-content elements
- **Multi-format Output**: Saves to structured text files

### Document Processing
- **PDF Support**: Full text extraction from PDF files
- **Text Files**: Support for .txt and .md files
- **Chunking**: Intelligent text chunking with overlap
- **Embedding**: Fast vector embeddings using sentence-transformers

## 🐛 Troubleshooting

### Common Issues

#### Milvus Connection Error
```bash
# Check if Milvus is running
docker-compose ps

# Restart if needed
docker-compose down
docker-compose up -d
```

#### LLM API Error
```bash
# Check config/config.py contains correct settings:
LLM_API_URL = "https://your-llm-endpoint.com/v1/chat/completions"
LLM_API_KEY = "your_llm_api_key_here"
```

#### Memory Issues
- Reduce `max_pages` in web crawler
- Lower chunk limits in RAG functions
- Increase system RAM

#### Large File Warnings
- The system automatically excludes large files
- Use `.gitignore` to prevent tracking large data

## 🔒 Security

- API keys are stored in configuration files
- No sensitive data is committed to the repository
- Large files and virtual environments are excluded
- Rate limiting prevents server overload

## 📊 Performance

- **Embedding Speed**: ~0.1 seconds per chunk
- **Search Speed**: ~0.5 seconds for semantic search
- **Response Time**: 2-5 seconds for AI responses
- **Memory Usage**: ~2GB for typical document sets
- **Context Limit**: 8000 characters to prevent API errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Milvus](https://milvus.io/) for vector database
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [USCIS](https://www.uscis.gov/) for immigration information

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Open an issue on GitHub

---
