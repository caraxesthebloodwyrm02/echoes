"""
User-defined tool: sentiment_analyzer
Description: Analyze text sentiment
Created: 2025-11-02T09:06:51.698109
"""


def sentiment_analyzer(text):
    positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
    negative_words = ["bad", "terrible", "awful", "horrible", "worse"]

    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Negative"
    else:
        return "Neutral"
