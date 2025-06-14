# TDS Virtual Teaching Assistant

A virtual Teaching Assistant API that automatically answers student questions for the IIT Madras Online Degree Tools in Data Science (TDS) course. The system processes student questions (with optional image attachments) and returns AI-generated answers with relevant source links from course content and Discourse posts.

## Features

- **REST API**: Accepts POST requests with questions and optional base64 images
- **Intelligent Answers**: Uses OpenAI GPT-4o with course content context
- **Fallback System**: Works without AI using keyword-based search
- **Source Links**: Returns relevant course material and Discourse post links
- **Web Interface**: Bootstrap-themed testing interface
- **Analytics**: Tracks question patterns and response times
- **PostgreSQL Database**: Stores course content and interaction history

## API Usage

### Endpoint
```
POST /api/
```

### Request Format
```json
{
  "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt-3.5-turbo?",
  "image": "base64_encoded_image_data"
}
```

### Response Format
```json
{
  "answer": "You must use gpt-3.5-turbo-0125, even if the AI Proxy only supports gpt-4o-mini...",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939",
      "text": "GA5 Question 8 Clarification"
    }
  ]
}
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- OpenAI API key (optional - works with fallback)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd tds-virtual-ta
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb tds_virtual_ta

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/tds_virtual_ta"
export OPENAI_API_KEY="your_openai_api_key"
export SESSION_SECRET="your_secret_key"
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:5000`

## Testing

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Test Question
```bash
curl -X POST http://localhost:5000/api/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the assignment submission guidelines?"}'
```

### Evaluation with Promptfoo
```bash
npx promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
```

## Bonus Features

### Discourse Scraper
Scrapes TDS course posts from Discourse within a date range:

```bash
python discourse_scraper.py --start-date 2025-01-01 --end-date 2025-04-14
python discourse_scraper.py --category-url https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34
```

## Project Structure

```
tds-virtual-ta/
├── main.py                 # Application entry point
├── app.py                  # Flask application setup
├── models.py               # Database models
├── api.py                  # API endpoints
├── ai_assistant_simple.py  # Question answering logic
├── scraper.py              # Content scraping utilities
├── discourse_scraper.py    # Bonus: Discourse scraper
├── routes.py               # Web interface routes
├── templates/
│   └── index.html          # Web interface
├── static/
│   └── script.js           # Frontend JavaScript
├── project-tds-virtual-ta-promptfoo.yaml  # Evaluation config
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI functionality
- `SESSION_SECRET`: Flask session secret key

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Evaluation Criteria

This project meets the following evaluation requirements:
- ✅ Publicly accessible GitHub repository
- ✅ MIT license in root folder
- ✅ Promptfoo evaluation configuration
- ✅ Handles realistic TDS course questions
- ✅ Returns proper JSON response format
- ✅ Bonus: Discourse scraper script

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For questions about the TDS course content, refer to the official course materials and Discourse forums. For technical issues with this virtual TA, please open an issue in the GitHub repository.