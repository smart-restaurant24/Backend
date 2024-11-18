import numpy as np
from typing import Dict, List
import tritonclient.http as httpclient
from intent_mapping import IntentMapping


class BERTIntentClient:
    def __init__(self, triton_url: str = "localhost:8000"):
        """
        Initialize BERT client with Triton server URL
        Args:
            triton_url: URL of the Triton inference server
        """
        self.client = httpclient.InferenceServerClient(url=triton_url)

    def _prepare_input(self, text: str) -> httpclient.InferInput:
        """
        Prepare input tensor for BERT model
        Args:
            text: Input text to prepare
        Returns:
            Triton input tensor
        """
        input_data = np.array([[text.encode('utf-8')]], dtype=np.object_)
        input_tensor = httpclient.InferInput(
            "text",
            [1, 1],
            "BYTES"
        )
        input_tensor.set_data_from_numpy(input_data)
        return input_tensor

    def get_intent(self, text: str) -> Dict[str, float]:
        """
        Get intent predictions from BERT model
        Args:
            text: Input text to classify
        Returns:
            Dictionary mapping intents to confidence scores
        """
        try:
            input_tensor = self._prepare_input(text)
            output_tensor_1 = httpclient.InferRequestedOutput("intents")
            output_tensor_2 = httpclient.InferRequestedOutput("probabilities")

            response = self.client.infer(
                "intent_classifier",
                model_version="1",
                inputs=[input_tensor],
                outputs=[output_tensor_1, output_tensor_2]
            )

            probabilities = response.as_numpy("probabilities")[0]

            results = {}
            for idx, prob in enumerate(probabilities):
                intent_name = IntentMapping.get_intent_name(idx)
                results[intent_name] = float(prob)

            return results

        except Exception as e:
            print(f"Error calling BERT service: {e}")
            return {}

    def get_batch_intents(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Get intent predictions for a batch of texts
        Args:
            texts: List of input texts to classify
        Returns:
            List of dictionaries mapping intents to confidence scores
        """
        try:
            batch_data = np.array([[text.encode('utf-8')] for text in texts], dtype=np.object_)
            batch_input_tensor = httpclient.InferInput(
                "text",
                [len(texts), 1],
                "BYTES"
            )
            batch_input_tensor.set_data_from_numpy(batch_data)

            output_tensor_1 = httpclient.InferRequestedOutput("intents")
            output_tensor_2 = httpclient.InferRequestedOutput("probabilities")

            batch_response = self.client.infer(
                "intent_classifier",
                model_version="1",
                inputs=[batch_input_tensor],
                outputs=[output_tensor_1, output_tensor_2]
            )

            batch_probabilities = batch_response.as_numpy("probabilities")

            results = []
            for probs in batch_probabilities:
                intent_dict = {}
                for idx, prob in enumerate(probs):
                    intent_name = IntentMapping.get_intent_name(idx)
                    intent_dict[intent_name] = float(prob)
                results.append(intent_dict)

            return results

        except Exception as e:
            print(f"Error in batch processing: {e}")
            return [{} for _ in texts]