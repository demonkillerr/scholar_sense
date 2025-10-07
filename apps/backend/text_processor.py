#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text Processing Module
Provides text extraction, cleaning, and processing functions
"""

import os
import re
import logging
import json
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Get logger for this module
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    logger.info("Downloading NLTK resources...")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class TextProcessor:
    """Text processing class for cleaning and analyzing text"""
    
    def __init__(self, language='english'):
        """
        Initialize text processor
        
        Parameters:
            language: Language for stopwords and processing (default: english)
        """
        self.language = language
        try:
            self.stop_words = set(stopwords.words(language))
        except:
            logger.warning(f"Stopwords not available for language: {language}. Using English.")
            self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text):
        """
        Clean text by removing special characters, extra spaces, etc.
        
        Parameters:
            text: Text to clean
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', ' ', text)
        
        # Remove special characters but keep punctuation for sentence splitting
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text):
        """
        Remove stopwords from text
        
        Parameters:
            text: Text to process
        
        Returns:
            Text with stopwords removed
        """
        if not text:
            return ""
        
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)
    
    def extract_keywords(self, text, top_n=10):
        """
        Extract keywords from text
        
        Parameters:
            text: Input text
            top_n: Number of top keywords to return
        
        Returns:
            List of (word, frequency) tuples
        """
        # Preprocess text
        cleaned_text = self.clean_text(text)
        
        # Tokenize
        words = word_tokenize(cleaned_text)
        
        # Remove stopwords
        stop_words = set(stopwords.words(self.language))
        filtered_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
        
        # Count word frequencies
        word_freq = Counter(filtered_words)
        
        # Return top N keywords
        return word_freq.most_common(top_n)
    
    def extract_sentences(self, text):
        """
        Extract sentences from text
        
        Parameters:
            text: Text to process
        
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        # Split text into sentences
        sentences = sent_tokenize(text)
        
        # Clean sentences
        cleaned_sentences = [s.strip() for s in sentences if s.strip()]
        
        return cleaned_sentences
    
    def summarize_text(self, text, num_sentences=3):
        """
        Create a simple extractive summary of text
        
        Parameters:
            text: Text to summarize
            num_sentences: Number of sentences to include in summary
        
        Returns:
            Summary text
        """
        if not text:
            return ""
        
        # Extract sentences
        sentences = self.extract_sentences(text)
        
        # If text is too short, return original
        if len(sentences) <= num_sentences:
            return text
        
        # Calculate word frequency
        cleaned_text = self.clean_text(text)
        word_freq = Counter(word_tokenize(cleaned_text))
        
        # Score sentences based on word frequency
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            for word in word_tokenize(sentence.lower()):
                if word in word_freq:
                    if i not in sentence_scores:
                        sentence_scores[i] = 0
                    sentence_scores[i] += word_freq[word]
        
        # Get top N sentences
        top_sentence_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        top_sentence_indices = sorted(top_sentence_indices)  # Sort by position in text
        
        # Create summary
        summary = ' '.join([sentences[i] for i in top_sentence_indices])
        
        return summary
    
    def analyze_text_structure(self, text):
        """
        Analyze text structure
        
        Parameters:
            text: Text to analyze
        
        Returns:
            Dictionary with text structure analysis
        """
        if not text:
            return {
                'sentence_count': 0,
                'word_count': 0,
                'avg_sentence_length': 0,
                'avg_word_length': 0
            }
        
        # Extract sentences and words
        sentences = self.extract_sentences(text)
        words = word_tokenize(text)
        
        # Filter out punctuation
        words = [word for word in words if word.isalpha()]
        
        # Calculate metrics
        sentence_count = len(sentences)
        word_count = len(words)
        
        # Average sentence length (in words)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        return {
            'sentence_count': sentence_count,
            'word_count': word_count,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length
        }
    
    def process_text_file(self, file_path):
        """
        Process plain text file
        
        Parameters:
            file_path: Path to the text file
        
        Returns:
            Processed text content dictionary
        """
        logger.info(f"Processing text file: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return None
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Use filename as title
            title = Path(file_path).stem
            
            # Split content into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            # If there are paragraphs, the first one might be an abstract
            abstract = paragraphs[0] if paragraphs else ""
            
            # The rest of the paragraphs as body text
            body_text = '\n\n'.join(paragraphs[1:]) if len(paragraphs) > 1 else ""
            
            # If there's no clear abstract, then the body text is the entire content
            if not body_text:
                body_text = abstract
                abstract = ""
            
            return {
                'title': title,
                'abstract': abstract,
                'body_text': body_text,
                'full_text': content,
                'references': []
            }
            
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            return None
    
    def process_json_file(self, file_path):
        """
        Process JSON file (such as social media data)
        
        Parameters:
            file_path: Path to the JSON file
        
        Returns:
            Processed text content dictionary
        """
        logger.info(f"Processing JSON file: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return None
            
            # Read JSON content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            
            # Process different types of JSON structures
            if isinstance(data, list):
                # If it's a list, it might be multiple social media posts
                return self._process_social_media_posts(data)
            elif isinstance(data, dict):
                # If it's a dictionary, it might be a single document or specific format
                return self._process_json_document(data)
            else:
                logger.error(f"Unsupported JSON format: {type(data)}")
                return None
            
        except Exception as e:
            logger.error(f"Error processing JSON file: {e}")
            return None
    
    def _process_social_media_posts(self, posts):
        """
        Process a list of social media posts
        
        Parameters:
            posts: List of posts
        
        Returns:
            Processed text content dictionary
        """
        if not posts:
            return {
                'title': "Social Media Posts",
                'abstract': "",
                'body_text': "",
                'full_text': "",
                'references': []
            }
        
        # Extract text content from all posts
        post_texts = []
        for post in posts:
            # Try to extract text from different fields
            text = ""
            if isinstance(post, dict):
                # Common social media fields
                for field in ['text', 'content', 'message', 'caption', 'body', 'tweet']:
                    if field in post and post[field]:
                        text = post[field]
                        break
                
                # If no text found, try using the entire post
                if not text:
                    text = json.dumps(post, ensure_ascii=False)
            elif isinstance(post, str):
                text = post
            
            if text:
                post_texts.append(text)
        
        # Combine all post texts
        combined_text = '\n\n'.join(post_texts)
        
        # Create title
        title = f"Social Media Posts ({len(posts)} items)"
        
        # Use first post as abstract
        abstract = post_texts[0] if post_texts else ""
        
        # Rest of posts as body text
        body_text = '\n\n'.join(post_texts[1:]) if len(post_texts) > 1 else ""
        
        return {
            'title': title,
            'abstract': abstract,
            'body_text': body_text,
            'full_text': combined_text,
            'references': []
        }
    
    def _process_json_document(self, document):
        """
        Process a JSON document
        
        Parameters:
            document: JSON document
        
        Returns:
            Processed text content dictionary
        """
        # Try to extract information from common fields
        title = ""
        abstract = ""
        body_text = ""
        references = []
        
        # Extract title
        for field in ['title', 'headline', 'subject', 'name']:
            if field in document and document[field]:
                title = document[field]
                break
        
        # Extract abstract
        for field in ['abstract', 'summary', 'description', 'snippet']:
            if field in document and document[field]:
                abstract = document[field]
                break
        
        # Extract body text
        for field in ['body', 'text', 'content', 'article', 'message']:
            if field in document and document[field]:
                body_text = document[field]
                break
        
        # Extract references
        for field in ['references', 'citations', 'sources']:
            if field in document and document[field]:
                if isinstance(document[field], list):
                    references = document[field]
                break
        
        # If no content found, use the entire document
        if not (title or abstract or body_text):
            full_text = json.dumps(document, ensure_ascii=False)
            return {
                'title': "JSON Document",
                'abstract': "",
                'body_text': full_text,
                'full_text': full_text,
                'references': references
            }
        
        # Combine full text
        full_text = ' '.join(filter(None, [title, abstract, body_text]))
        
        return {
            'title': title,
            'abstract': abstract,
            'body_text': body_text,
            'full_text': full_text,
            'references': references
        }
    
    def process_csv_file(self, file_path, text_column=None, title_column=None):
        """
        Process CSV file
        
        Parameters:
            file_path: Path to the CSV file
            text_column: Text column name or index
            title_column: Title column name or index
        
        Returns:
            Processed text content dictionary
        """
        logger.info(f"Processing CSV file: {file_path}")
        
        try:
            import pandas as pd
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return None
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # If text column not specified, try to guess
            if text_column is None:
                # Common text column names
                text_columns = ['text', 'content', 'message', 'body', 'description']
                for col in text_columns:
                    if col in df.columns:
                        text_column = col
                        break
                
                # If still not found, use the longest string column
                if text_column is None:
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            text_column = col
                            break
            
            # If title column not specified, try to guess
            if title_column is None:
                # Common title column names
                title_columns = ['title', 'headline', 'subject', 'name']
                for col in title_columns:
                    if col in df.columns:
                        title_column = col
                        break
            
            # Extract text content
            if text_column is not None and text_column in df.columns:
                texts = df[text_column].dropna().astype(str).tolist()
            else:
                # If no text column found, use all columns
                texts = df.apply(lambda row: ' '.join(row.astype(str)), axis=1).tolist()
            
            # Extract title
            if title_column is not None and title_column in df.columns:
                titles = df[title_column].dropna().astype(str).tolist()
                title = titles[0] if titles else Path(file_path).stem
            else:
                title = Path(file_path).stem
            
            # Combine text
            combined_text = '\n\n'.join(texts)
            
            # Use first row as abstract
            abstract = texts[0] if texts else ""
            
            # Rest of rows as body text
            body_text = '\n\n'.join(texts[1:]) if len(texts) > 1 else ""
            
            return {
                'title': title,
                'abstract': abstract,
                'body_text': body_text,
                'full_text': combined_text,
                'references': []
            }
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            return None
    
    def process_file(self, file_path):
        """
        Process file, automatically detecting file type
        
        Parameters:
            file_path: Path to the file
        
        Returns:
            Processed text content dictionary
        """
        # Get file extension
        ext = Path(file_path).suffix.lower()
        
        # Choose processing method based on extension
        if ext in ['.txt', '.md', '.rst']:
            return self.process_text_file(file_path)
        elif ext in ['.json']:
            return self.process_json_file(file_path)
        elif ext in ['.csv']:
            return self.process_csv_file(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            # Try processing as text file
            return self.process_text_file(file_path)
    
    def generate_topic_text(self, topic):
        """
        Generate text content related to a specific topic
        
        Parameters:
            topic: The topic to generate content for
        
        Returns:
            Text content related to the topic
        """
        logger.info(f"Generating text for topic: {topic}")
        
        # Convert topic to lowercase for case-insensitive matching
        topic_lower = topic.lower()
        
        # Dictionary of predefined topic texts
        topic_texts = {
            'ai': """
                Artificial Intelligence (AI) is revolutionizing industries across the globe. 
                Machine learning algorithms are becoming increasingly sophisticated, enabling computers to perform tasks 
                that once required human intelligence. Deep learning, a subset of AI, has made significant breakthroughs 
                in image recognition, natural language processing, and autonomous vehicles. However, concerns about AI ethics, 
                job displacement, and privacy issues have also emerged. Some experts worry about the potential for AI to 
                surpass human intelligence, while others see it as a tool that will enhance human capabilities. 
                Companies like Google, Microsoft, and OpenAI are investing billions in AI research and development. 
                The future of AI looks promising but requires careful consideration of its societal impacts.
            """,
            
            'climate change': """
                Climate change represents one of the most pressing challenges of our time. Rising global temperatures 
                have led to melting ice caps, rising sea levels, and increasingly severe weather events. Many scientists 
                warn that without immediate action, we face catastrophic consequences. Efforts to combat climate change 
                include renewable energy adoption, carbon capture technologies, and international agreements like the 
                Paris Accord. However, progress has been slow, and some countries continue to prioritize economic growth 
                over environmental concerns. Activists like Greta Thunberg have brought global attention to the urgency 
                of the situation, while some politicians and industry leaders remain skeptical about the severity of the 
                problem or the need for dramatic action.
            """,
            
            'healthcare': """
                The healthcare industry is undergoing rapid transformation due to technological advancements and changing 
                patient expectations. Telemedicine has expanded access to care, particularly in rural areas and during the 
                COVID-19 pandemic. Electronic health records have improved information sharing among providers but have 
                also raised concerns about data security. Precision medicine is enabling more personalized treatment plans 
                based on genetic factors. However, healthcare costs continue to rise in many countries, creating barriers 
                to access for vulnerable populations. The debate over universal healthcare remains contentious, with 
                proponents citing improved outcomes and equity, while critics worry about quality of care and economic impacts. 
                Mental health services have gained increased attention but still face stigma and funding challenges.
            """,
            
            'education': """
                Education systems worldwide are evolving to meet the demands of the 21st century. Digital learning tools 
                and online courses have expanded access to education beyond traditional classrooms. The COVID-19 pandemic 
                accelerated this trend, forcing schools and universities to adopt remote learning models. However, this 
                transition highlighted the digital divide, as students without reliable internet access or appropriate 
                devices fell behind. STEM education has received increased emphasis, reflecting the growing importance of 
                technical skills in the job market. At the same time, there's recognition of the continued value of liberal 
                arts education in developing critical thinking and communication skills. Issues of educational equity persist, 
                with significant disparities in resources and outcomes based on socioeconomic status, race, and geography.
            """,
            
            'cryptocurrency': """
                Cryptocurrency has emerged as a disruptive force in the financial world. Bitcoin, the first and most 
                well-known cryptocurrency, has experienced dramatic price fluctuations since its creation in 2009. 
                Blockchain technology, which underlies most cryptocurrencies, offers potential benefits beyond digital 
                currencies, including secure supply chain management and voting systems. Some countries have embraced 
                cryptocurrency, with El Salvador even adopting Bitcoin as legal tender. Others have imposed strict 
                regulations or outright bans, citing concerns about financial stability, criminal activity, and environmental 
                impact due to energy-intensive mining operations. The rise of decentralized finance (DeFi) platforms 
                promises to democratize access to financial services but also introduces new risks and regulatory challenges.
            """
        }
        
        # Check if we have predefined text for this topic
        for key, text in topic_texts.items():
            if topic_lower in key or key in topic_lower:
                # Clean up the text (remove extra whitespace)
                return re.sub(r'\s+', ' ', text).strip()
        
        # If no predefined text is found, generate a generic response
        return f"""
            The topic of {topic} encompasses various perspectives and developments. 
            Some view {topic} positively, citing benefits such as improved efficiency and innovation.
            Others express concerns about potential drawbacks and unintended consequences.
            Research on {topic} continues to evolve, with new findings regularly emerging.
            Experts in the field of {topic} often debate the best approaches and future directions.
            Public opinion on {topic} varies widely, influenced by media coverage and personal experiences.
        """
    
    def extract_topic_sentences(self, text, topic):
        """
        Extract sentences that are relevant to the given topic
        
        Parameters:
            text: Text to analyze
            topic: Topic to search for
        
        Returns:
            List of topic-relevant sentences
        """
        if not text or not topic:
            return []
        
        # Clean and tokenize topic
        topic_words = set(word_tokenize(self.clean_text(topic)))
        
        # Extract sentences
        sentences = self.extract_sentences(text)
        
        # Score sentences based on topic relevance
        topic_sentences = []
        for sentence in sentences:
            # Clean and tokenize sentence
            sentence_words = set(word_tokenize(self.clean_text(sentence)))
            
            # Calculate overlap with topic words
            overlap = len(sentence_words.intersection(topic_words))
            
            # If there's significant overlap, include the sentence
            if overlap > 0:
                topic_sentences.append(sentence)
        
        return topic_sentences
    
    def calculate_topic_relevance(self, text, topic):
        """
        Calculate how relevant the text is to the given topic
        
        Parameters:
            text: Text to analyze
            topic: Topic to check relevance against
        
        Returns:
            Relevance score between 0 and 1
        """
        if not text or not topic:
            return 0.0
        
        # Clean and tokenize text and topic
        text_words = set(word_tokenize(self.clean_text(text)))
        topic_words = set(word_tokenize(self.clean_text(topic)))
        
        # Calculate word overlap
        overlap = len(text_words.intersection(topic_words))
        
        # Calculate relevance score
        # Normalize by the number of topic words to get a score between 0 and 1
        relevance_score = overlap / len(topic_words) if topic_words else 0
        
        return min(1.0, relevance_score)  # Cap at 1.0
    
    def extract_topic_keywords(self, text, topic, top_n=10):
        """
        Extract keywords that are relevant to the given topic
        
        Parameters:
            text: Text to analyze
            topic: Topic to focus on
            top_n: Number of top keywords to return
        
        Returns:
            List of (word, frequency) tuples for topic-relevant keywords
        """
        if not text or not topic:
            return []
        
        # Clean and tokenize topic
        topic_words = set(word_tokenize(self.clean_text(topic)))
        
        # Extract topic-relevant sentences
        topic_sentences = self.extract_topic_sentences(text, topic)
        
        # If no topic-relevant sentences found, use the whole text
        if not topic_sentences:
            logger.info(f"No sentences related to topic '{topic}' found for keyword extraction. Using full text.")
            # Extract general keywords but prioritize those related to the topic
            all_keywords = self.extract_keywords(text, top_n * 2)
            
            # Filter keywords to prioritize those related to the topic
            topic_related = []
            other_keywords = []
            
            for word, count in all_keywords:
                if word.lower() in topic_words or any(topic_word in word.lower() for topic_word in topic_words):
                    topic_related.append((word, count))
                else:
                    other_keywords.append((word, count))
            
            # Combine lists, prioritizing topic-related keywords
            return topic_related + other_keywords[:max(0, top_n - len(topic_related))]
        
        # Combine topic-relevant sentences
        topic_text = ' '.join(topic_sentences)
        
        # Extract keywords from topic-relevant text
        return self.extract_keywords(topic_text, top_n)

# Test code
if __name__ == "__main__":
    processor = TextProcessor()
    test_text = """
    Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence 
    concerned with the interactions between computers and human language, in particular how to program computers 
    to process and analyze large amounts of natural language data. The goal is a computer capable of "understanding" 
    the contents of documents, including the contextual nuances of the language within them.
    """
    
    print("Cleaned text:")
    cleaned = processor.clean_text(test_text)
    print(cleaned)
    
    print("\nKeywords:")
    keywords = processor.extract_keywords(test_text, top_n=5)
    for word, count in keywords:
        print(f"{word}: {count}")
    
    print("\nSummary:")
    summary = processor.summarize_text(test_text, num_sentences=1)
    print(summary)
    
    print("\nText structure:")
    structure = processor.analyze_text_structure(test_text)
    for key, value in structure.items():
        print(f"{key}: {value}") 