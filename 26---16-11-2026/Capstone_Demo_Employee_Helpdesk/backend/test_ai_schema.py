
from app.schemas.ai_suggestion import AIAnalysisResponse


result = AIAnalysisResponse(
    suggested_category="HARDWARE",
    suggested_priority="HIGH",
    troubleshooting_steps="Check the keyboard connection and try another USB port.",
    explanation="The employee reported that the keyboard is not responding."
)

print(result.model_dump())
