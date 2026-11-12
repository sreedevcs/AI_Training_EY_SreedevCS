
import re


# 1. PII Detection
def contains_pii(text):
    email = r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"
    phone = r"\b[6-9]\d{9}\b"

    return bool(
        re.search(email, text)
        or re.search(phone, text)
    )


# 2. Output Redaction
def clean_output(answer):

    answer = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL REDACTED]",
        answer
    )

    answer = re.sub(
        r"\b[6-9]\d{9}\b",
        "[PHONE REDACTED]",
        answer
    )

    return answer


# 3. Input Validation
def validate_input(text):

    if not text or not text.strip():
        return False, "Input cannot be empty."

    if len(text) > 1000:
        return False, "Input is too long. Maximum 1000 characters allowed."

    if contains_pii(text):
        return False, "Personal information detected. Please avoid sharing email addresses or phone numbers."

    return True, "Input accepted."


# 4. Domain Restriction
def is_restaurant_query(text):

    keywords = [
        "restaurant", "restaurants", "food",
        "dining", "cuisine", "indian",
        "chinese", "italian", "japanese",
        "kerala", "malabar", "price",
        "cost", "bill", "guest", "guests",
        "people", "seats", "seating",
        "available", "reservation", "booking",
        "menu", "lunch", "dinner",
        "hyderabad", "bangalore", "kochi",
        "chennai", "spice garden", "bistro",
        "sushi", "palace", "kitchen"
    ]

    text = text.lower()

    return any(
        keyword in text
        for keyword in keywords
    )


# 5. Contextual Follow-up Handling
def is_follow_up(text):

    follow_ups = [
        "yes", "no", "ok", "okay",
        "sure", "thanks", "thank you"
    ]

    text = text.lower().strip()

    if text in follow_ups:
        return True

    if re.search(
        r"\b\d+\s*(people|guests|persons)\b",
        text
    ):
        return True

    if any(
        phrase in text
        for phrase in [
            "make that",
            "change it",
            "increase it",
            "decrease it",
            "what about",
            "same restaurant"
        ]
    ):
        return True

    return False


# 6. Main Input Guardrail
def check_input(text, has_context=False):

    valid, message = validate_input(text)

    if not valid:
        return False, message

    if is_restaurant_query(text):
        return True, "Restaurant query accepted."

    if has_context and is_follow_up(text):
        return True, "Contextual follow-up accepted."

    return False, (
        "I can only assist with restaurant-related queries."
    )


# 7. Guest Count Validation
def validate_guest_count(guests):

    if guests < 1:
        return False, "At least 1 guest is required."

    if guests > 20:
        return False, "Maximum 20 guests are allowed."

    return True, "Guest count accepted."
