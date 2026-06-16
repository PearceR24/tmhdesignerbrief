# TMH Designer Brief Automation — Setup Guide

## What This Does
When you add a HubSpot note containing the phrase **"design brief"**, this automation:
1. Reads the note + the client's contact details from HubSpot
2. Sends everything to Claude, which structures it into a Designer Briefing Document
3. Generates a professional PDF matching the TMH format
4. Emails it to Matthew Purves (matthew@spectura.com.au) from your Outlook

---

## Step 1 — Fill In Your Secrets

1. In the `TMH Designer Brief Automation` folder, find the file called `.env.example`
2. Duplicate it and rename the copy to `.env`
3. Open `.env` and fill in:

```
HUBSPOT_TOKEN=           ← your HubSpot Private App token
ANTHROPIC_API_KEY=       ← your Claude API key from console.anthropic.com
OUTLOOK_EMAIL=           pearce@tasmanufacturedhousing.com.au
OUTLOOK_PASSWORD=        ← your Microsoft 365 password
DESIGNER_EMAIL=          matthew@spectura.com.au
WEBHOOK_SECRET=          ← make up any word, e.g. tmhsecret2026
```

---

## Step 2 — Deploy to Railway (Free Hosting)

Railway hosts the script 24/7 so it's always listening for HubSpot.

1. Go to **railway.app** and sign up with your GitHub account
2. Click **New Project → Deploy from GitHub repo**
3. Upload this folder (or push it to a GitHub repo first — Railway can guide you)
4. Once deployed, Railway gives you a public URL like:
   `https://tmh-brief.up.railway.app`
5. In Railway's dashboard, go to **Variables** and add all the keys from your `.env` file

---

## Step 3 — Set Up the HubSpot Webhook

1. In HubSpot, go to **Settings → Integrations → Private Apps**
2. Open your "TMH Designer Brief Automation" app
3. Go to the **Webhooks** tab
4. Click **Create Subscription**
5. Choose:
   - **Object type:** Notes (Engagements)
   - **Event:** Note created
   - **Target URL:** `https://your-railway-url.up.railway.app/webhook/hubspot`
6. Save

---

## Step 4 — Enable SMTP in Microsoft 365

Microsoft 365 blocks SMTP by default. Enable it once:

1. Go to **admin.microsoft.com**
2. Go to **Users → Active users → pearce@tasmanufacturedhousing.com.au**
3. Click **Mail** tab → **Manage email apps**
4. Tick **Authenticated SMTP** → Save

---

## Step 5 — Test It

1. In HubSpot, open any contact
2. Add a note that includes the phrase **design brief** somewhere in it
3. Write your meeting notes as normal
4. Save the note
5. Within ~60 seconds, Matthew should receive an email with the PDF attached

---

## How to Write Notes for Best Results

Include as much detail as you can. Claude will extract it all. Example:

> design brief — met with John and Sarah Smith today at the warehouse then drove to 45 Binalong Bay Road, St Helens. They want to put two Atlas 2-bedroom dwellings on the property as permanent residence. Stage is Initial Consultation, invoice is outstanding. Main issues are slope on the northern end and a right of way along the eastern boundary. They want a deck facing the bay view. Action: Matthew to review site plan, Pearce to send contract.

Claude reads that and builds the full 7-section document automatically.

---

## Files in This Folder

| File | Purpose |
|---|---|
| `app.py` | The web server — receives HubSpot webhooks |
| `extract_brief.py` | Sends notes to Claude, gets structured data back |
| `generate_pdf.py` | Builds the PDF in TMH format |
| `send_email.py` | Sends the email via Microsoft Outlook |
| `requirements.txt` | Python packages needed |
| `.env` | Your secret keys (never share this file) |
