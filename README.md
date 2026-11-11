<div align="center">

# SmartPDF

<p>Convert your PDF documents into an eye-friendly Dark Mode format.</p>

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![UI Framework](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

---

## Overview

**SmartPDF** is a simple and fast python application designed to convert standard PDF documents into custom Dark Mode PDFs.

Unlike traditional color invert tools, Smart PDF uses a smart color mapping engine. It changes white backgrounds and neutral text into dark palettes while preserving original images, formulas, photos, and visual diagrams.

## Examples

Here is a side-by-side comparison showing how Smart PDF inverts text and background while maintaining original image colors:

| Original Light PDF | Smart Dark Mode Output |
|:---:|:---:|
| <img src="samples/Screenshot 2026-11-11 065122.jpg" width="400" alt="Original Light PDF"/> | <img src="samples/Screenshot 2026-11-11 065106.jpg" width="400" alt="Dark Mode Output"/> |


## Features

* **Smart Dark Themes:** Choose between different color presets like *Classic Dark*, *Ocean Blue*, *Forest Green*, *Deep Purple*, and *Warm Sepia*.
* **Image Preservation:** Automatically detects and keeps original diagrams, charts, and illustrations intact.
* **Custom Resolution:** Adjust DPI settings (from 96 to 400 DPI) to match your quality needs.
* **Format Control:** Export pages as high-quality lossless PNG or compressed JPEG.
* **Safe & Non-Destructive:** Your original PDF file is never modified or overwritten.
* **User-Friendly GUI:** Simple desktop interface powered by `CustomTkinter` with smooth progress tracking.

## How It Works

Please keep the following technical details in mind when using SmartPDF:

1. **Rasterized Output (Image-Based Pages):**
   * Smart PDF processes each page by rendering it as a high-resolution image, applying dark mode filters, and building a new PDF.
   * **Text Selection & Copying:** Because pages become images, native text copying (selectable text) is not available inside basic PDF readers. However, modern browsers (like Google Chrome or Microsoft Edge) or readers with built-in **OCR (Optical Character Recognition)** will still allow you to select and copy text easily.

2. **Quality vs. File Size:**
   * Higher DPI values (e.g., 300 or 400 DPI) produce crisp text and sharp images matching the original file quality, but will result in a **larger output file size**.
   * Selecting **PNG** provides maximum sharpness (lossless), while **JPEG** significantly reduces file size with adjustable quality settings.

## Project Structure

```
SmartPDF/
├── Samples/
│   ├── Screenshot 2026-11-11 065106.jpg
│   ├── Screenshot 2026-11-11 065018.jpg
│   └── ....
├── main.py              # Application entry point
├── gui.py               # Desktop GUI interface & user event handling
├── pdf_converter.py     # Main PDF processing pipeline & file validation
├── image_processor.py   # Dark mode color mapping & image restoration logic
├── utils.py             # Path validation and logging utilities
├── .gitignore           # Git ignore file
├── LICENSE              # Project license
├── README.md            # Project documentation
└── requirements.txt     # Required Python packages
```

## Getting Started

### Prerequisites

* Python 3.13 or higher installed on your computer.

### Installation

1. **Clone or download this repository:**

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.