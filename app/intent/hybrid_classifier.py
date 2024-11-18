from typing import Dict, List, Tuple, Optional
from text_preprocessor import TextPreprocessor
from rule_based_classifier import RuleBasedIntentClassifier
from bert_client import BERTIntentClient


class HybridIntentClassifier:
    def __init__(self, triton_url: str = "localhost:8000"):
        """
        Initialize hybrid classifier with all components
        Args:
            triton_url: URL of the Triton inference server
        """
        self.preprocessor = TextPreprocessor()
        self.rule_based = RuleBasedIntentClassifier()
        self.bert_client = BERTIntentClient(triton_url)

    def classify(self, text: str) -> Dict[str, float]:
        """
        Combine rule-based and BERT predictions for final intent classification
        Args:
            text: Input text to classify
        Returns:
            Dictionary mapping intents to confidence scores
        """
        processed_text = self.preprocessor.preprocess(text)

        rule_predictions = self.rule_based.classify(processed_text)
        bert_predictions = self.bert_client.get_intent(processed_text)

        final_predictions = {}
        all_intents = set(list(rule_predictions.keys()) + list(bert_predictions.keys()))
        print(text)
        for intent in all_intents:
            rule_score = rule_predictions.get(intent, 0.0)
            bert_score = bert_predictions.get(intent, 0.0)
            print("Scores for intent " + intent)
            print("rule : " + rule_score.__str__() + "| bert : " + bert_score.__str__())
            # Weight BERT predictions higher (0.7) than rule-based (0.3)
            final_predictions[intent] = (0.3 * rule_score + 0.7 * bert_score)

        return final_predictions

    def get_top_intent(self, text: str, threshold: float = 0.3) -> Optional[Tuple[str, float]]:
        """
        Get the most likely intent if it exceeds the confidence threshold
        Args:
            text: Input text to classify
            threshold: Minimum confidence threshold
        Returns:
            Tuple of (intent, confidence) or None if below threshold
        """
        predictions = self.classify(text)
        if not predictions:
            return None

        top_intent = max(predictions.items(), key=lambda x: x[1])
        if top_intent[1] >= threshold:
            return top_intent
        return None

    def batch_classify(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Process a batch of texts and return intent classifications
        Args:
            texts: List of input texts to classify
        Returns:
            List of dictionaries mapping intents to confidence scores
        """
        processed_texts = [self.preprocessor.preprocess(text) for text in texts]

        bert_predictions = self.bert_client.get_batch_intents(processed_texts)
        rule_predictions = [self.rule_based.classify(text) for text in processed_texts]

        final_predictions = []
        for bert_pred, rule_pred in zip(bert_predictions, rule_predictions):
            combined = {}
            all_intents = set(list(rule_pred.keys()) + list(bert_pred.keys()))

            for intent in all_intents:
                rule_score = rule_pred.get(intent, 0.0)
                bert_score = bert_pred.get(intent, 0.0)
                print("Scores for intent " + intent)
                print("rule : " + rule_score.__str__() + "| bert : " + bert_score.__str__())
                print(" ")
                combined[intent] = (0.3 * rule_score + 0.7 * bert_score)

            final_predictions.append(combined)

        return final_predictions