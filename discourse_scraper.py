#!/usr/bin/env python3
"""
Discourse Scraper for TDS Course Posts
Bonus feature: Scrapes Discourse posts across a date range from TDS course pages.

Usage:
    python discourse_scraper.py --start-date 2025-01-01 --end-date 2025-04-14
    python discourse_scraper.py --category-url https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34
"""

import argparse
import requests
from datetime import datetime, timedelta
import time
import logging
from urllib.parse import urljoin, urlparse
import json
from bs4 import BeautifulSoup
from app import app, db
from models import ScrapedContent
import trafilatura

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscourseScrapperTDS:
    def __init__(self, base_url="https://discourse.onlinedegree.iitm.ac.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TDS-Virtual-TA-Bot/1.0 (Educational Purpose)'
        })
        
    def get_category_topics(self, category_id, start_date=None, end_date=None):
        """
        Fetch topics from a specific category within date range.
        """
        topics = []
        page = 0
        
        while True:
            try:
                # Discourse API endpoint for category topics
                url = f"{self.base_url}/c/{category_id}.json"
                params = {"page": page}
                
                logger.info(f"Fetching category {category_id}, page {page}")
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch page {page}: {response.status_code}")
                    break
                
                data = response.json()
                topic_list = data.get('topic_list', {})
                page_topics = topic_list.get('topics', [])
                
                if not page_topics:
                    break
                
                # Filter by date if specified
                for topic in page_topics:
                    created_at = datetime.fromisoformat(topic['created_at'].replace('Z', '+00:00'))
                    
                    if start_date and created_at < start_date:
                        continue
                    if end_date and created_at > end_date:
                        continue
                    
                    topics.append(topic)
                
                page += 1
                time.sleep(1)  # Be respectful with rate limiting
                
                # Stop if we've gone beyond date range
                if page_topics and start_date:
                    last_topic_date = datetime.fromisoformat(page_topics[-1]['created_at'].replace('Z', '+00:00'))
                    if last_topic_date < start_date:
                        break
                        
            except Exception as e:
                logger.error(f"Error fetching category topics: {e}")
                break
                
        return topics
    
    def get_topic_content(self, topic_id):
        """
        Fetch full content of a topic/post.
        """
        try:
            url = f"{self.base_url}/t/{topic_id}.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            posts = data.get('post_stream', {}).get('posts', [])
            
            # Combine all posts in the topic
            content_parts = []
            topic_title = data.get('title', 'Untitled')
            
            for post in posts:
                if post.get('cooked'):  # HTML content
                    # Convert HTML to clean text
                    soup = BeautifulSoup(post['cooked'], 'html.parser')
                    text_content = soup.get_text(separator='\n', strip=True)
                    content_parts.append(text_content)
            
            return {
                'title': topic_title,
                'content': '\n\n---\n\n'.join(content_parts),
                'url': f"{self.base_url}/t/{topic_id}"
            }
            
        except Exception as e:
            logger.error(f"Error fetching topic {topic_id}: {e}")
            return None
    
    def scrape_tds_course_posts(self, category_url=None, start_date=None, end_date=None):
        """
        Main scraping function for TDS course posts.
        """
        with app.app_context():
            # Extract category ID from URL
            if category_url:
                category_id = category_url.split('/')[-1]
            else:
                category_id = "34"  # Default TDS KB category
            
            logger.info(f"Scraping TDS Discourse category {category_id}")
            
            # Get topics from category
            topics = self.get_category_topics(category_id, start_date, end_date)
            logger.info(f"Found {len(topics)} topics to scrape")
            
            scraped_count = 0
            for topic in topics:
                try:
                    topic_id = topic['id']
                    topic_url = f"{self.base_url}/t/{topic_id}"
                    
                    # Check if already scraped
                    existing = ScrapedContent.query.filter_by(url=topic_url).first()
                    if existing:
                        logger.info(f"Topic {topic_id} already scraped, skipping")
                        continue
                    
                    # Get full topic content
                    topic_data = self.get_topic_content(topic_id)
                    
                    if topic_data:
                        # Save to database
                        scraped_content = ScrapedContent(
                            url=topic_data['url'],
                            title=topic_data['title'],
                            content=topic_data['content'],
                            content_type='discourse'
                        )
                        
                        db.session.add(scraped_content)
                        db.session.commit()
                        
                        scraped_count += 1
                        logger.info(f"Scraped topic: {topic_data['title']}")
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error processing topic {topic.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Scraping completed. {scraped_count} new topics added to database.")
            return scraped_count


def parse_date(date_string):
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


def main():
    parser = argparse.ArgumentParser(description='Scrape TDS Discourse posts within date range')
    parser.add_argument('--start-date', type=parse_date, 
                       help='Start date for scraping (YYYY-MM-DD)', default="2025-01-01")
    parser.add_argument('--end-date', type=parse_date,
                       help='End date for scraping (YYYY-MM-DD)', default="2025-04-14")
    parser.add_argument('--category-url', type=str,
                       help='Discourse category URL to scrape',
                       default="https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34")
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize scraper
    scraper = DiscourseScrapperTDS()
    
    logger.info(f"Starting TDS Discourse scraping:")
    logger.info(f"  Category URL: {args.category_url}")
    logger.info(f"  Date range: {args.start_date.strftime('%Y-%m-%d')} to {args.end_date.strftime('%Y-%m-%d')}")
    
    # Run scraping
    count = scraper.scrape_tds_course_posts(
        category_url=args.category_url,
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    print(f"✅ Scraping completed! {count} new posts added to database.")


if __name__ == "__main__":
    main()