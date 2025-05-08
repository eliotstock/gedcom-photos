# GEDCOM photo downloader

myheritage.com, piece of work that it is, makes it extremely difficult to export a family tree including the images. The GEDCOM file they give you contains photo URLs for a CDN server that are not persistent. You need to grab these images soon after you download your GEDCOM file, but they do not tell you this.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script on your GEDCOM file:
```bash
python3 ./src/main.py ./my_export.ged
```
