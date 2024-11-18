from hybrid_classifier import HybridIntentClassifier


def main():
    # Example usage
    classifier = HybridIntentClassifier()

    # Test single query
    text = "Can I see the menu please?"
    result = classifier.get_top_intent(text)
    if result:
        intent, confidence = result
        print(f"\nQuery: {text}")
        print(f"Top Intent: {intent}")
        print(f"Confidence: {confidence:.4f}")

    # Test batch processing
    texts = [
        "Book table for tonight and check menu",
        "What cuisine do you serve?",
        "I'd like to make a reservation",
        "What cards do you accept?"
    ]

    batch_results = classifier.batch_classify(texts)
    print("\nBatch Results:")
    for text, predictions in zip(texts, batch_results):
        print(f"\nQuery: {text}")
        top_3 = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:3]
        for intent, confidence in top_3:
            print(f"{intent}: {confidence:.4f}")


if __name__ == "__main__":
    main()