import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from extract_brief import extract_brief_from_notes
from generate_pdf import generate_brief_pdf
from send_email import send_designer_brief

load_dotenv()

app = Flask(__name__)

TRIGGER_PHRASE = "design brief"
HUBSPOT_TOKEN = os.environ.get("HUBSPOT_TOKEN", "")
HUBSPOT_HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}


def get_contact_for_note(note_id: str) -> dict:
    """Fetch the contact associated with a HubSpot note."""
    url = f"https://api.hubapi.com/crm/v3/objects/notes/{note_id}/associations/contacts"
    resp = requests.get(url, headers=HUBSPOT_HEADERS)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return {}

    contact_id = results[0]["id"]
    contact_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    params = {"properties": "firstname,lastname,phone,email,address,city"}
    resp = requests.get(contact_url, headers=HUBSPOT_HEADERS, params=params)
    resp.raise_for_status()
    props = resp.json().get("properties", {})

    first = props.get("firstname", "") or ""
    last = props.get("lastname", "") or ""
    return {
        "name": f"{first} {last}".strip(),
        "phone": props.get("phone", "") or "",
        "email": props.get("email", "") or "",
        "address": props.get("address", "") or "",
        "city": props.get("city", "") or "",
    }


@app.route("/webhook/hubspot", methods=["POST"])
def hubspot_webhook():
    try:
        payload = request.get_json(force=True)

        # HubSpot sends a list of subscription events
        if isinstance(payload, list):
            events = payload
        else:
            events = [payload]

        for event in events:
            event_type = event.get("subscriptionType", "")

            # Only process new notes
            if "note" not in event_type.lower() and "engagement" not in event_type.lower():
                continue

            object_id = str(event.get("objectId", ""))
            if not object_id:
                continue

            # Fetch the note body from HubSpot
            note_url = f"https://api.hubapi.com/crm/v3/objects/notes/{object_id}"
            note_resp = requests.get(
                note_url,
                headers=HUBSPOT_HEADERS,
                params={"properties": "hs_note_body,hs_timestamp"}
            )
            note_resp.raise_for_status()
            note_body = note_resp.json().get("properties", {}).get("hs_note_body", "") or ""

            # Check for trigger phrase (case-insensitive)
            if TRIGGER_PHRASE not in note_body.lower():
                continue

            print(f"Trigger found in note {object_id} — generating designer brief...")

            # Get associated contact details
            contact_data = get_contact_for_note(object_id)

            # Ask Claude to extract and structure the brief
            brief = extract_brief_from_notes(note_body, contact_data)

            # Generate the PDF
            pdf_bytes = generate_brief_pdf(brief)

            # Send the email to Matthew
            send_designer_brief(
                pdf_bytes,
                brief.get("client_names", contact_data.get("name", "Client")),
                brief.get("site_address", contact_data.get("address", ""))
            )

            print("Designer brief sent successfully.")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "TMH Designer Brief Automation is running"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
