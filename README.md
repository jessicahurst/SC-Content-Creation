# SC Content Creation Toolkit

Tools for Sales Consultants to produce compliant, on-brand social content.

## Features
- Markdown templates for LinkedIn, Facebook, Instagram, and Builder to Realtor posts, each following the required voice, structure, and compliance guidance.
- Automated branded image generation with validated uploads, brand color overlays, and logo placement.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
Generate the Markdown templates:
```bash
python -m src templates --output pulte_social_templates.md
```

Create a branded image:
```bash
python -m src image path/to/photo.jpg --message "Your tailored message here" --output pulte_branded.jpg
```

> **Tip:** Keep overlay messages concise and professional. Use the brackets in the templates to personalize community details while staying compliant.
