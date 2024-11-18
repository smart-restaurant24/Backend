import re
from typing import Dict, List, Tuple
from collections import defaultdict
import spacy


class RuleBasedIntentClassifier:
    def __init__(self):
        # Load spaCy model for linguistic analysis
        self.nlp = spacy.load('en_core_web_sm')

        # Define weighted patterns with scores and contextual variations
        self.intent_patterns = {
            'ENQUIRY_MENU': {
                'high_confidence': [
                    (r'\b(show|see|view|check|get)\s+(?:the|your)?\s*menu\b', 1.0),
                    (r'\bwhat(?:\s*\'s|\s+is)\s+on\s+(?:the\s+)?menu\b', 1.0),
                    (r'\bmenu\s+(?:options|items|dishes)\b', 0.9)
                ],
                'medium_confidence': [
                    (r'\b(?:food|dish(?:es)?|item(?:s)?)\s+(?:available|offer(?:ed)?|serve(?:d)?)\b', 0.7),
                    (r'\bprice(?:s)?\s+(?:list|range|of)\b', 0.7),
                    (r'\bspecials?\s+(?:today|tonight|this\s+evening)\b', 0.8)
                ],
                'context_terms': [
                    'menu', 'dish', 'food', 'price', 'cost', 'special', 'appetizer', 'main course',
                    'dessert', 'beverage', 'dinner', 'lunch', 'breakfast'
                ]
            },
            'ENQUIRY_CUISINE': {
                'high_confidence': [
                    (r'\bwhat\s+(?:type|kind)\s+of\s+cuisine\b', 1.0),
                    (r'\b(?:serve|offer)\s+(?:what|which)\s+cuisine\b', 1.0),
                    (r'\b(?:indian|chinese|italian|mexican|thai|japanese)\s+(?:food|cuisine|dishes)\b', 0.9)
                ],
                'medium_confidence': [
                    (r'\b(?:food|dishes)\s+(?:style|type)\b', 0.7),
                    (r'\b(?:traditional|authentic|fusion)\s+(?:food|cuisine|dishes)\b', 0.7)
                ],
                'context_terms': [
                    'cuisine', 'style', 'food type', 'traditional', 'authentic', 'spicy', 'flavor'
                ]
            },
            'ORDER_RELATED': {
                'high_confidence': [
                    (r'\b(?:want|like|place)\s+(?:to\s+)?order\b', 1.0),
                    (r'\bcan\s+(?:i|we)\s+(?:get|have|order)\b', 0.9),
                    (r'\border\s+(?:food|takeout|delivery)\b', 0.9)
                ],
                'medium_confidence': [
                    (r'\btake\s+(?:my|our)\s+order\b', 0.8),
                    (r'\b(?:ready|like)\s+to\s+(?:order|eat)\b', 0.7)
                ],
                'context_terms': [
                    'order', 'take', 'get', 'have', 'food', 'meal', 'dish', 'deliver', 'takeout'
                ],
                'negative_patterns': [
                    r'\b(?:not|don\'t)\s+want\s+to\s+order\b'
                ]
            },
            'RESERVATION_RELATED': {
                'high_confidence': [
                    (r'\b(?:make|place|book)\s+(?:a\s+)?reservation\b', 1.0),
                    (r'\breserve\s+(?:a\s+)?table\b', 1.0),
                    (r'\btable\s+for\s+\d+\s+(?:people|persons)?\b', 0.9)
                ],
                'medium_confidence': [
                    (r'\b(?:available|free)\s+table(?:s)?\b', 0.8),
                    (r'\b(?:tonight|today|tomorrow)\s+(?:at|for)\s+\d+(?::\d+)?\s*(?:pm|am)?\b', 0.7)
                ],
                'time_patterns': [
                    (r'\b(?:tonight|this\s+evening)\b', 0.3),
                    (r'\b(?:tomorrow|next\s+week)\b', 0.3),
                    (r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b', 0.3)
                ],
                'context_terms': [
                    'reservation', 'book', 'table', 'seat', 'dining', 'party', 'group'
                ]
            },
            'PAYMENT_RELATED': {
                'high_confidence': [
                    (r'\b(?:accept|take)\s+(?:credit\s+cards?|debit\s+cards?|cash|payment)\b', 1.0),
                    (r'\bhow\s+(?:can|do)\s+(?:i|we)\s+pay\b', 1.0),
                    (r'\b(?:bill|check|payment)\s+(?:please|options)\b', 0.9)
                ],
                'medium_confidence': [
                    (r'\b(?:split|divide)\s+(?:the\s+)?bill\b', 0.8),
                    (r'\b(?:payment|billing)\s+(?:method|option)s?\b', 0.7)
                ],
                'context_terms': [
                    'pay', 'payment', 'bill', 'check', 'card', 'cash', 'credit', 'debit', 'split'
                ]
            }
        }

        # Initialize contextual memory
        self.conversation_context = []

    def _check_time_relevance(self, text: str) -> float:
        """Check for time-related patterns and return relevance score"""
        time_indicators = {
            'lunch': (11, 14),  # 11 AM - 2 PM
            'dinner': (17, 22),  # 5 PM - 10 PM
            'breakfast': (6, 11)  # 6 AM - 11 AM
        }

        score = 0.0
        for indicator, (start, end) in time_indicators.items():
            if indicator in text.lower():
                score += 0.2
        return min(score, 0.5)

    def _check_negation(self, text: str) -> bool:
        """Check for negation in the text using spaCy"""
        doc = self.nlp(text)
        for token in doc:
            if token.dep_ == 'neg':
                return True
        return False

    def _get_context_score(self, text: str, context_terms: List[str]) -> float:
        """Calculate context relevance score"""
        words = set(text.lower().split())
        context_matches = sum(term in text.lower() for term in context_terms)
        return min(context_matches * 0.15, 0.5)

    def classify(self, text: str) -> Dict[str, float]:
        """
        Enhanced classification with contextual awareness and sophisticated pattern matching
        """
        results = defaultdict(float)
        doc = self.nlp(text.lower())

        # Store conversation context
        self.conversation_context.append(text)
        if len(self.conversation_context) > 3:
            self.conversation_context.pop(0)

        # Check each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0.0

            # Check high confidence patterns
            for pattern, weight in patterns['high_confidence']:
                matches = len(re.findall(pattern, text.lower()))
                if matches > 0:
                    score = max(score, weight * matches)

            # Check medium confidence patterns
            for pattern, weight in patterns['medium_confidence']:
                matches = len(re.findall(pattern, text.lower()))
                if matches > 0:
                    score = max(score, weight * matches)

            # Add context score
            context_score = self._get_context_score(text, patterns['context_terms'])
            score += context_score

            # Check time relevance if applicable
            if 'time_patterns' in patterns:
                time_score = self._check_time_relevance(text)
                score += time_score

            # Check negation
            if self._check_negation(text):
                score *= 0.3  # Reduce score if negation is present

            # Consider conversation context
            if len(self.conversation_context) > 1:
                prev_text = self.conversation_context[-2]
                context_score = self._get_context_score(prev_text, patterns['context_terms'])
                score += context_score * 0.2  # Add reduced weight for previous context

            # Check for negative patterns if they exist
            if 'negative_patterns' in patterns:
                for neg_pattern in patterns['negative_patterns']:
                    if re.search(neg_pattern, text.lower()):
                        score *= 0.2  # Significantly reduce score if negative pattern matches

            # Normalize final score
            results[intent] = min(score, 1.0)

        return dict(results)

    def get_top_intents(self, text: str, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Get top intents above threshold, sorted by confidence
        """
        predictions = self.classify(text)
        top_intents = [(intent, score) for intent, score in predictions.items()
                       if score >= threshold]
        return sorted(top_intents, key=lambda x: x[1], reverse=True)