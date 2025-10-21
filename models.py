from pydantic import BaseModel, Field, EmailStr
from typing import List

# Data model for attachments (like the sample image)
class Attachment(BaseModel):
    name: str = Field(..., description="Name of the attached file (e.g., 'sample.png')")
    url: str = Field(..., description="The content encoded as a data URI (data:image/png;base64,...)")

# The main data model for the incoming task payload
class TaskRequest(BaseModel):
    # Student email ID
    email: EmailStr = Field(..., description="Student email ID")
    # Student-provided secret
    secret: str = Field(..., description="Student-provided secret")
    # A unique task ID.
    task: str = Field(..., description="A unique task ID (e.g., 'captcha-solver-...')")
    # There will be multiple rounds per task. This is the round index
    round: int = Field(..., description="The round index (e.g., 1)")
    # Pass this nonce back to the evaluation URL
    nonce: str = Field(..., description="Pass this nonce back to the evaluation URL below")
    # brief: mentions what the app needs to do
    brief: str = Field(..., description="Brief description of what the app needs to do")
    # checks: mention how it will be evaluated
    checks: List[str] = Field(..., description="Evaluation checks (e.g., license, readme quality)")
    # Send repo & commit details to the URL below
    evaluation_url: str = Field(..., description="URL to send repo & commit details")
    # Attachments will be encoded as data URIs
    attachments: List[Attachment] = Field(..., description="Attachments encoded as data URIs")

