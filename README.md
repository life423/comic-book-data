🎨 Comic Book Data
A structured toolkit for importing, processing, and analyzing comic book datasets.

🔧 Features
Data ingestion: Load panels, pages, and metadata from various sources and formats.

Preprocessing pipeline: Automate image resizing, OCR text extraction, metadata normalization, and HDF5 dataset creation.

Query utilities: Functions to extract and filter pages or panels based on attributes (e.g., issue number, characters, dialogue).

Analysis-ready output: Structured data files compatible with ML workflows (e.g., panel image arrays, tokenized text).

Template modules: Easily extend for new data sources or output formats.

📦 Table of Contents
Installation

Usage

CLI

Python API

Data Formats

Pipeline Overview

Examples

Project Structure

Contributing & License

🛠 Installation
bash
Copy
Edit
# Clone the repository
git clone https://github.com/life423/comic-book-data.git
cd comic-book-data

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
🚀 Usage
CLI
Run the full preprocessing pipeline:

bash
Copy
Edit
python scripts/run_pipeline.py \
  --input ./raw_data \
  --output ./processed_data \
  --format hdf5
List available commands:

bash
Copy
Edit
python scripts/run_pipeline.py --help
📚 Python API
python
Copy
Edit
from comic_data.loader import ComicLoader
from comic_data.pipeline import preprocess

# Load raw comic metadata
loader = ComicLoader("path/to/data")
panels = loader.load_panels()

# Preprocess images and extract text
processed = preprocess(panels)

# Save output to HDF5
processed.save("output/comics.h5")
📁 Data Formats
Input:

Image files (e.g., PNG, JPEG)

OCR outputs (CSV/JSON)

Metadata (JSON or CSV)

Output:

HDF5 groups containing:

images: numpy arrays for panel visuals

text: cleaned, tokenized dialogue

metadata: structured fields (e.g. issue, panel index, characters)

🧭 Pipeline Overview
Load raw files → returns unified data objects.

Process images: resize, normalize.

Extract OCR text: clean and tokenize.

Assemble HDF5 datasets — ready for ML ingestion.

✍️ Examples
python
Copy
Edit
from comic_data.viewer import ComicViewer

viewer = ComicViewer("output/comics.h5")
viewer.sample_panels(count=5)
Drawn example notebooks: see /examples/analysis_panels.ipynb, /examples/text_stats.ipynb

🗂 Project Structure
bash
Copy
Edit
comic-book-data/
├── scripts/                # CLI utilities
├── comic_data/
│   ├── loader.py           # Data ingestion
│   ├── pipeline.py         # Preprocessing logic
│   ├── viewer.py           # Visualization tools
│   └── utils.py            # Helpers (OCR, tokenization)
├── tests/                  # Unit & integration tests
├── examples/               # Jupyter notebooks
├── requirements.txt        # Python dependencies
└── setup.py                # Package installer
🤝 Contributing & License
Contributions welcome! Please fork the repo, create a feature branch, and open a PR. Include unit tests and update docs.

This project is released under the [MIT License]—see the LICENSE file for full details.

🧭 Roadmap
Support multi-language OCR (e.g., Spanish, French)

Export to JSON‑lines for web visualizations

Integration with comic‑genre classification models