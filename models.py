from app import db
from datetime import datetime


class ScrapedContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'course' or 'discourse'
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    embedding_id = db.Column(db.Integer)  # Reference to vector store index

    def __repr__(self):
        return f'<ScrapedContent {self.title}>'


class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    links = db.Column(db.Text)  # JSON string of links
    has_image = db.Column(db.Boolean, default=False)
    response_time = db.Column(db.Float)  # Response time in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<QuestionAnswer {self.id}>'
