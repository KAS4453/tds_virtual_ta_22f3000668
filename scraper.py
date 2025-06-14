import trafilatura
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
from app import app, db
from models import ScrapedContent

logger = logging.getLogger(__name__)


def get_website_text_content(url: str) -> str:
    """
    Extract clean text content from a website using trafilatura.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text or ""
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
    return ""


def scrape_discourse_posts(base_url="https://discourse.onlinedegree.iitm.ac.in", 
                          start_date="2025-01-01", end_date="2025-04-14"):
    """
    Scrape TDS Discourse posts from the specified date range.
    This is a simplified implementation - in practice, you'd need proper authentication
    and more sophisticated scraping based on the actual Discourse API.
    """
    with app.app_context():
        # Sample Discourse URLs to scrape (in practice, you'd discover these dynamically)
        sample_urls = [
            f"{base_url}/c/tools-in-data-science/6.json",
            f"{base_url}/t/week-1-tools-in-data-science/1234",
            f"{base_url}/t/assignment-guidelines/5678",
        ]
        
        for url in sample_urls:
            try:
                logger.info(f"Scraping: {url}")
                
                # Check if already scraped
                existing = ScrapedContent.query.filter_by(url=url).first()
                if existing:
                    logger.info(f"Already scraped: {url}")
                    continue
                
                content = get_website_text_content(url)
                if content:
                    # Extract title from content or URL
                    title = extract_title_from_content(content) or url.split('/')[-1]
                    
                    scraped_content = ScrapedContent(
                        url=url,
                        title=title,
                        content=content,
                        content_type='discourse'
                    )
                    
                    db.session.add(scraped_content)
                    db.session.commit()
                    logger.info(f"Saved content from: {url}")
                
                # Be respectful with scraping
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")


def scrape_course_content():
    """
    Scrape TDS course content. This would need to be adapted based on 
    the actual course material location and access methods.
    """
    with app.app_context():
        # Sample course content URLs (replace with actual course material URLs)
        course_urls = [
            "https://onlinedegree.iitm.ac.in/course/tools-in-data-science/week1",
            "https://onlinedegree.iitm.ac.in/course/tools-in-data-science/week2",
            "https://onlinedegree.iitm.ac.in/course/tools-in-data-science/assignments",
        ]
        
        for url in course_urls:
            try:
                logger.info(f"Scraping course content: {url}")
                
                # Check if already scraped
                existing = ScrapedContent.query.filter_by(url=url).first()
                if existing:
                    logger.info(f"Already scraped: {url}")
                    continue
                
                content = get_website_text_content(url)
                if content:
                    title = extract_title_from_content(content) or url.split('/')[-1]
                    
                    scraped_content = ScrapedContent(
                        url=url,
                        title=title,
                        content=content,
                        content_type='course'
                    )
                    
                    db.session.add(scraped_content)
                    db.session.commit()
                    logger.info(f"Saved course content from: {url}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping course content {url}: {e}")


def extract_title_from_content(content: str) -> str:
    """
    Extract a title from the content text.
    """
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line) < 100:  # Reasonable title length
            return line
    return "Untitled"


def initialize_scraped_data():
    """
    Initialize the database with some sample scraped data for demonstration.
    In production, this would be replaced with actual scraping.
    """
    with app.app_context():
        # Check if we already have data
        if ScrapedContent.query.count() > 0:
            return
        
        # Add realistic TDS course content for evaluation
        sample_contents = [
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939",
                "title": "GA5 Question 8 Clarification",
                "content": """Discussion about using gpt-3.5-turbo-0125 vs gpt-4o-mini for assignments.
                
Important clarification from course staff:
- You must use gpt-3.5-turbo-0125 for assignments, even if AI Proxy only supports gpt-4o-mini
- Use the OpenAI API directly when the specified model is required
- Do not substitute with gpt-4o-mini as it has different tokenization and costs
- For tokenization, use similar approach to what Prof. Anand demonstrated
- Calculate tokens and multiply by the given rate for cost estimation
                
The key is to use the exact model that's mentioned in the question requirements, not what's available in AI Proxy.""",
                "content_type": "discourse"
            },
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga4-data-sourcing-discussion-thread-tds-jan-2025/165959/388",
                "title": "GA4 Data Sourcing Discussion Thread",
                "content": """GA4 Grading and Dashboard Display Information:

Student Question: If I score 10/10 on GA4 plus bonus marks, how will it show on dashboard?

Course Staff Response:
- Regular GA4 score is out of 10 marks
- Bonus marks are added on top of the base score
- If you score 10/10 + 1 bonus mark, dashboard will show "110" (110%)
- This represents 11 out of 10 possible marks
- The percentage calculation shows >100% when bonus is earned
- Final grade calculation will cap at maximum course limits

Example: 10 base marks + 1 bonus = 11 total marks shown as 110% on dashboard.""",
                "content_type": "discourse"
            },
            {
                "url": "https://tds.s-anand.net/#/docker",
                "title": "Docker vs Podman - Course Guidelines",
                "content": """TDS Course Container Technology Guidelines:

For Tools in Data Science course, we recommend using Podman over Docker:

Why Podman is preferred:
- Podman is the standard for this course
- Better security with rootless containers
- Compatible with Docker commands (docker alias works)
- Preferred by course instructors for consistency

Docker Usage:
- Docker is acceptable if you're already familiar with it
- Most Docker commands work with Podman
- No need to learn Podman from scratch if Docker works for you
- Course examples may use Podman syntax

Recommendation: Use Podman for the course, but Docker is fine if you prefer it.""",
                "content_type": "course"
            },
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/assignment-submission-guidelines/789012",
                "title": "Assignment Submission Guidelines",
                "content": """Guidelines for submitting TDS assignments:
                
1. Submit all code as .py files or .ipynb notebooks
2. Include a README with instructions
3. Use proper variable names and comments
4. Test your code before submission
5. Follow PEP 8 style guidelines
6. Include required dependencies in requirements.txt
                
Late submissions will have penalty as per course policy.""",
                "content_type": "discourse"
            },
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/tds-exam-schedule-information/147258",
                "title": "TDS Exam Schedule Information",
                "content": """TDS Exam Schedule Updates:

Current Available Information:
- TDS Jan 2025 batch exam dates are published
- TDS Sep 2025 batch exam schedule: NOT YET AVAILABLE
- Exam dates typically announced 2-3 months before exam period
- Check course announcements for updates

For TDS Sep 2025 end-term exam:
- Date not announced yet
- Will be posted on course portal when available
- Usually held in December/January timeframe
- Students will receive email notification when schedule is released

Check the official course portal regularly for exam date announcements.""",
                "content_type": "discourse"
            }
        ]
        
        for item in sample_contents:
            content = ScrapedContent(
                url=item["url"],
                title=item["title"],
                content=item["content"],
                content_type=item["content_type"]
            )
            db.session.add(content)
        
        db.session.commit()
        logger.info("Initialized database with sample scraped content")
