#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sentiment Analysis Module
Using multiple methods to analyze text sentiment
"""

import logging
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from collections import Counter

# Get logger for this module
logger = logging.getLogger(__name__)

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    logger.info("Downloading NLTK resources...")
    nltk.download('vader_lexicon')
    nltk.download('punkt')

class SentimentAnalyzer:
    """Sentiment analysis class, providing multiple sentiment analysis methods"""

    def __init__(self):
        """Initialize sentiment analyzer"""
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text, method='combined'):
        """
        Analyze text sentiment
        
        Parameters:
            text: Text to analyze
            method: Analysis method, options: 'vader', 'textblob', 'combined'
        
        Returns:
            Sentiment analysis result dictionary
        """
        if not text or text.strip() == "":
            logger.warning("Input text is empty or contains only whitespace")
            return {
                'sentiment': 'neutral',
                'score': 0,
                'confidence': 0,
                'details': {'message': 'Empty text provided'}
            }
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        if not cleaned_text or cleaned_text.strip() == "":
            logger.warning("Cleaned text is empty")
            return {
                'sentiment': 'neutral',
                'score': 0,
                'confidence': 0,
                'details': {'message': 'Text contained only special characters or stopwords'}
            }
        
        # Choose analyzer based on method
        if method == 'vader':
            return self._analyze_with_vader(cleaned_text)
        elif method == 'textblob':
            return self._analyze_with_textblob(cleaned_text)
        else:  # Default to combined method
            return self._analyze_combined(cleaned_text)
    
    def _clean_text(self, text):
        """
        Clean text
        
        Parameters:
            text: Original text
        
        Returns:
            Cleaned text
        """
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _analyze_with_vader(self, text):
        """
        Use VADER for sentiment analysis
        
        Parameters:
            text: Text to analyze
        
        Returns:
            VADER sentiment analysis result
        """
        try:
            # Split long text into sentences
            sentences = nltk.sent_tokenize(text)
            
            # Analyze each sentence
            sentence_scores = []
            for sentence in sentences:
                if sentence:
                    score = self.vader.polarity_scores(sentence)
                    sentence_scores.append(score)
            
            # If no valid sentences, return neutral result
            if not sentence_scores:
                return {
                    'sentiment': 'neutral',
                    'score': 0,
                    'confidence': 0,
                    'details': {'pos': 0, 'neg': 0, 'neu': 1, 'compound': 0}
                }
            
            # Calculate average scores
            avg_scores = {
                'pos': sum(s['pos'] for s in sentence_scores) / len(sentence_scores),
                'neg': sum(s['neg'] for s in sentence_scores) / len(sentence_scores),
                'neu': sum(s['neu'] for s in sentence_scores) / len(sentence_scores),
                'compound': sum(s['compound'] for s in sentence_scores) / len(sentence_scores)
            }
            
            # Determine sentiment
            compound = avg_scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calculate confidence
            confidence = abs(compound)
            
            return {
                'sentiment': sentiment,
                'score': compound,
                'confidence': confidence,
                'details': avg_scores
            }
            
        except Exception as e:
            logger.error(f"VADER analysis error: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0,
                'confidence': 0,
                'details': {'error': str(e)}
            }
    
    def _analyze_with_textblob(self, text):
        """
        Use TextBlob for sentiment analysis
        
        Parameters:
            text: Text to analyze
        
        Returns:
            TextBlob sentiment analysis result
        """
        try:
            # Create TextBlob object
            blob = TextBlob(text)
            
            # Get polarity and subjectivity
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment
            if polarity > 0.05:
                sentiment = 'positive'
            elif polarity < -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calculate confidence
            confidence = abs(polarity) * subjectivity
            
            return {
                'sentiment': sentiment,
                'score': polarity,
                'confidence': confidence,
                'details': {
                    'polarity': polarity,
                    'subjectivity': subjectivity
                }
            }
            
        except Exception as e:
            logger.error(f"TextBlob analysis error: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0,
                'confidence': 0,
                'details': {'error': str(e)}
            }
    
    def _analyze_combined(self, text):
        """
        Use combined method for sentiment analysis
        
        Parameters:
            text: Text to analyze
        
        Returns:
            Combined sentiment analysis result
        """
        # Get VADER and TextBlob results
        vader_result = self._analyze_with_vader(text)
        textblob_result = self._analyze_with_textblob(text)
        
        # Combine results
        sentiments = [vader_result['sentiment'], textblob_result['sentiment']]
        sentiment_counter = Counter(sentiments)
        
        # If both methods agree, use that result
        if len(sentiment_counter) == 1:
            combined_sentiment = sentiments[0]
        else:
            # Otherwise, weight by confidence
            vader_weight = vader_result['confidence']
            textblob_weight = textblob_result['confidence']
            
            # If VADER has higher confidence
            if vader_weight > textblob_weight:
                combined_sentiment = vader_result['sentiment']
            else:
                combined_sentiment = textblob_result['sentiment']
        
        # Calculate combined score and confidence
        combined_score = (vader_result['score'] + textblob_result['score']) / 2
        combined_confidence = (vader_result['confidence'] + textblob_result['confidence']) / 2
        
        return {
            'sentiment': combined_sentiment,
            'score': combined_score,
            'confidence': combined_confidence,
            'details': {
                'vader': vader_result,
                'textblob': textblob_result
            }
        }
    
    def analyze_document(self, document_data):
        """
        Analyze document sentiment
        
        Parameters:
            document_data: Document data dictionary, including title, abstract, body text, etc.
        
        Returns:
            Document sentiment analysis result
        """
        results = {}
        
        # Analyze title
        if document_data.get('title'):
            results['title'] = self.analyze_text(document_data['title'])
        
        # Analyze abstract
        if document_data.get('abstract'):
            results['abstract'] = self.analyze_text(document_data['abstract'])
        
        # Analyze body text
        if document_data.get('body_text'):
            results['body_text'] = self.analyze_text(document_data['body_text'])
        
        # Analyze full text
        if document_data.get('full_text'):
            results['full_text'] = self.analyze_text(document_data['full_text'])
        else:
            # If full text not provided, combine title, abstract, and body text
            full_text = ' '.join([
                document_data.get('title', ''),
                document_data.get('abstract', ''),
                document_data.get('body_text', '')
            ])
            results['full_text'] = self.analyze_text(full_text)
        
        # Determine overall sentiment
        if results.get('full_text'):
            overall_sentiment = results['full_text']['sentiment']
            overall_score = results['full_text']['score']
        elif results.get('body_text'):
            overall_sentiment = results['body_text']['sentiment']
            overall_score = results['body_text']['score']
        elif results.get('abstract'):
            overall_sentiment = results['abstract']['sentiment']
            overall_score = results['abstract']['score']
        elif results.get('title'):
            overall_sentiment = results['title']['sentiment']
            overall_score = results['title']['score']
        else:
            overall_sentiment = 'neutral'
            overall_score = 0
        
        # Return result
        return {
            'overall_sentiment': overall_sentiment,
            'overall_score': overall_score,
            'detailed_results': results
        }

# Test code
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    test_text = "I love this product. It's amazing and works perfectly. However, the customer service was terrible."
    result = analyzer.analyze_text(test_text)
    print(f"Sentiment: {result['sentiment']}, Score: {result['score']:.2f}, Confidence: {result['confidence']:.2f}") 