# TDS Virtual Teaching Assistant

## Overview

This is a virtual Teaching Assistant application designed to automatically answer student questions for the IIT Madras Online Degree Tools in Data Science (TDS) course. The system provides an API that processes student questions (with optional image attachments) and returns AI-generated answers with relevant source links from course content and Discourse posts.

## System Architecture

The application follows a Flask-based web architecture with the following key components:

- **Flask Web Framework**: Serves as the main application framework with Gunicorn as the WSGI server
- **SQLite Database**: Stores scraped content, question-answer pairs, and application data using SQLAlchemy ORM
- **Vector Store with FAISS**: Implements semantic search using sentence transformers for content retrieval
- **OpenAI GPT-4o Integration**: Provides AI-powered question answering capabilities
- **Web Scraping Pipeline**: Extracts content from course materials and Discourse forums

## Key Components

### Frontend Layer
- **Web Interface** (`templates/index.html`): Bootstrap-based dark theme interface for testing the API
- **JavaScript Client** (`static/script.js`): Handles form submissions, file uploads, and API interactions

### API Layer
- **Main API Endpoint** (`api.py`): Handles POST requests to `/api/` with question and optional image processing
- **Request Processing**: Validates input, converts images to base64, and manages response formatting
- **Error Handling**: Comprehensive error management with proper HTTP status codes

### Data Processing Layer
- **Web Scraper** (`scraper.py`): Extracts content from TDS course materials and Discourse posts using trafilatura
- **Vector Store** (`vector_store.py`): FAISS-based similarity search with SentenceTransformer embeddings
- **Content Storage**: Structured storage of scraped content with metadata and timestamps

### AI Integration Layer
- **AI Assistant** (`ai_assistant.py`): OpenAI GPT-4o integration for generating contextual answers
- **Context Assembly**: Combines relevant search results into prompts for the AI model
- **Response Processing**: Formats AI responses with relevant source links

### Database Layer
- **Models** (`models.py`): SQLAlchemy models for ScrapedContent and QuestionAnswer entities
- **Data Persistence**: Tracks scraped content, user interactions, and response metrics

## Data Flow

1. **Content Ingestion**: Scraper extracts text from course materials and Discourse posts
2. **Vector Indexing**: Content is embedded using SentenceTransformer and indexed in FAISS
3. **Question Processing**: User questions trigger similarity search across indexed content
4. **Context Assembly**: Relevant content pieces are assembled into context for AI processing
5. **AI Generation**: OpenAI GPT-4o generates answers using the assembled context
6. **Response Delivery**: Formatted JSON response with answer and source links

## External Dependencies

### AI Services
- **OpenAI API**: GPT-4o model for question answering (requires OPENAI_API_KEY)

### Machine Learning Libraries
- **SentenceTransformers**: all-MiniLM-L6-v2 model for text embeddings
- **FAISS**: Facebook AI Similarity Search for vector operations

### Web Scraping
- **Trafilatura**: Content extraction from web pages
- **BeautifulSoup**: HTML parsing and navigation
- **Requests**: HTTP client for web scraping

### Database and Web Framework
- **Flask + SQLAlchemy**: Web framework with ORM for SQLite
- **Gunicorn**: Production WSGI server

## Deployment Strategy

### Replit Configuration
- **Environment**: Python 3.11 with Nix package management
- **Database**: PostgreSQL package included for potential migration from SQLite
- **Server**: Gunicorn with auto-scaling deployment target
- **Port Configuration**: Runs on port 5000 with proper binding

### Environment Variables
- `OPENAI_API_KEY`: Required for AI functionality
- `DATABASE_URL`: Defaults to SQLite, supports PostgreSQL migration
- `SESSION_SECRET`: Flask session security (defaults to dev key)

### Production Considerations
- **Auto-scaling**: Configured for Replit's autoscale deployment
- **Process Management**: Gunicorn with reload capability for development
- **Proxy Handling**: ProxyFix middleware for proper header handling
- **Database Connection**: Pool management with ping and recycle settings

## Changelog

Changelog:
- June 13, 2025: Initial setup
- June 13, 2025: Completed TDS Virtual TA with working API, fallback mechanism, and web interface deployed
- June 14, 2025: Enhanced for evaluation criteria - added promptfoo config, improved search, discourse scraper, GitHub-ready structure

## User Preferences

Preferred communication style: Simple, everyday language.