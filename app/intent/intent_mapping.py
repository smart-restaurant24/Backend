class IntentMapping:
    """Class to handle intent mapping and conversions"""

    INTENT_MAP = {
        0: "ENQUIRY_MENU",
        1: "ENQUIRY_CUISINE",
        2: "ENQUIRY_DISH",
        3: "ENQUIRY_RESTAURANT",
        4: "ORDER_RELATED",
        5: "RESERVATION_RELATED",
        6: "PAYMENT_RELATED",
        7: "GENERAL",
        8: "SERVICE_RELATED",
        9: "NON_RELATED",
        10: "RECOMMENDATION"
    }

    @classmethod
    def get_intent_name(cls, index: int) -> str:
        """
        Convert intent index to intent name
        Args:
            index: Integer index of the intent
        Returns:
            String name of the intent, or "UNKNOWN" if index not found
        """
        return cls.INTENT_MAP.get(index, "UNKNOWN")

    @classmethod
    def get_intent_index(cls, name: str) -> int:
        """
        Convert intent name to intent index
        Args:
            name: String name of the intent
        Returns:
            Integer index of the intent, or -1 if name not found
        """
        return {v: k for k, v in cls.INTENT_MAP.items()}.get(name, -1)