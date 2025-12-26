
import smtplib
import re
import subprocess
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from config import EMAIL, EMAIL_PASSWORD     # credentials.json
import config.settings as cfg               # ollama config
from config.contacts import CONTACTS        # your saved contacts

# -----------------------------
# Email Validation
# -----------------------------
def is_valid_email(address: str) -> bool:
    if not address or "@" not in address:
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, address) is not None

# -----------------------------
# Fallback deterministic subject
# -----------------------------
def deterministic_subject(body: str) -> str:
    body = body.strip()
    if not body:
        return f"Message from {EMAIL} - {datetime.now().strftime('%b %d, %Y')}"

    # Use first 7 words of body
    words = body.split()
    if len(words) <= 7:
        s = " ".join(words)
    else:
        s = " ".join(words[:3]) + "..."

    return s.capitalize()

# -----------------------------
# LLM subject generation
# -----------------------------
def generate_subject_with_llm(body: str) -> str:
    print("Generating subject with LLM...")
    if not body or not cfg.OLLAMA_MODEL:
        return None

    prompt = f"""
Generate a short, clean email subject by your own(3–8 words) for the following message.
Return ONLY the subject text. No quotes.

Message:
{body}

Subject:
"""

    try:
        p = subprocess.run(
            [cfg.OLLAMA_BIN, "run", cfg.OLLAMA_MODEL],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            
        )

        out = p.stdout.decode().strip()
        if not out:
            return None

        # Use first non-empty line as subject
        for line in out.splitlines():
            line = line.strip()
            if line:
                return line[:120]  # safety trim

        return None
    except Exception:
        return None


def send_email(slots: dict):
    try:
        to_field = (slots.get("to") or "").strip()
        body = (slots.get("body") or "").strip()
        user_subject = slots.get("subject", "").strip()

        if not to_field:
            return "No recipient name or email provided."

        # Resolve name -> email
        recipient = CONTACTS.get(to_field.lower(), to_field)

        if not is_valid_email(recipient):
            return f"❌ Invalid recipient email: {recipient}"

        # SUBJECT decision
        if user_subject:
            subject = user_subject
        else:
            # Try LLM
            subject = generate_subject_with_llm(body)
            if not subject:
                subject = deterministic_subject(body)

        # Compose email
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body if body else "No message content.", "plain"))

        # SEND
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)

        return f"Email sent to {recipient} with subject: {subject}"

    except Exception as e:
        return f"Failed to send email: {e}"

