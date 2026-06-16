import json
import anthropic
from datetime import datetime

SYSTEM_PROMPT = """You are an assistant for Tasman Manufactured Housing (TMH), a construction company in Tasmania.
Your job is to read raw meeting notes written by Pearce (the owner) after client meetings and extract structured
information to populate a Designer Briefing Document for the company's designer, Matthew Purves.

You must return ONLY valid JSON — no markdown, no explanation, just the JSON object.

Extract the following fields:

{
  "client_names": "Full names of client(s)",
  "client_contact": "Phone number and/or email if mentioned",
  "site_address": "Full site address",
  "project_stage": "e.g. Complex Site Assessment (Paid), Initial Consultation, Design Stage etc — extract from notes",
  "invoice_status": "e.g. Complex Site Assessment paid, Invoice outstanding etc — extract from notes",
  "project_description": "2-3 paragraph professional narrative describing the project, what the clients want to achieve, the context of the meeting, and the intent of the briefing. Write in third person.",
  "design_summary": [
    ["TMH Design", "e.g. Atlas, Apex, etc"],
    ["Number of Dwellings", "e.g. 1 (one)"],
    ["Configuration", "e.g. 3 Bedroom"],
    ["Design Approach", "Brief description"],
    ["Intended Use", "e.g. Primary residence, Short-term accommodation"]
  ],
  "intended_use_notes": [
    "Bullet point 1 — a key design consideration from the meeting",
    "Bullet point 2",
    "..."
  ],
  "actions": [
    {"item": "Action description", "owner": "Pearce / Matthew / Client etc", "status": "Outstanding / In Progress / Complete"},
    ...
  ],
  "notes": "A 2-3 paragraph professional summary of the meeting — what was discussed, what was agreed, what happens next."
}

Rules:
- Write in professional, formal language suitable for a construction design brief
- If a field is not mentioned in the notes, use an empty string "" or empty list []
- For design_summary, only include rows where you have real information
- For actions, include any next steps, follow-ups, or tasks mentioned
- Always include today's date context: """ + datetime.today().strftime("%-d %B %Y") + """
- The TMH Contact is always: Pearce | admin@tasmanufacturedhousing.com.au
- The Designer is always: Matthew Purves
"""


def extract_brief_from_notes(raw_notes: str, contact_data: dict) -> dict:
    """
    raw_notes: the HubSpot note body text
    contact_data: dict with keys name, phone, email, address, city from HubSpot contact
    """
    client = anthropic.Anthropic()

    context = f"""
HUBSPOT CONTACT DATA:
Name: {contact_data.get('name', '')}
Phone: {contact_data.get('phone', '')}
Email: {contact_data.get('email', '')}
Address: {contact_data.get('address', '')} {contact_data.get('city', '')}

MEETING NOTES FROM PEARCE:
{raw_notes}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context}]
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    brief = json.loads(raw.strip())
    brief["document_date"] = datetime.today().strftime("%-d %B %Y")
    return brief
