# SmartPDF - PDF Dark Mode Converter 🌙📄

A python-based application designed to convert bright, white-background PDF documents (lectures, slides, research papers, and books) into an eye-friendly **Dark Mode** without ruining diagrams, technical figures, or original images.

---

## 📸 Demo & Screenshots

| Original (Light Mode) | SmartPDF (Dark Mode) |
| :---: | :---: |
| ![Light Mode Sample](docs/images/light_mode_sample.png) | ![Dark Mode Sample](docs/images/dark_mode_sample.png) |

> **Note:** Notice how text, tables, and logic gate symbols are inverted for low-light reading while embedded hardware and server images retain their original clear colors.

---

## ⚡ The Problem

Studying slides or reading PDFs late at night with traditional white backgrounds causes severe eye strain. Built-in inverted/dark extensions often mess up color palettes in embedded images, making medical diagrams, technical circuits, and hardware figures unreadable or distorted.

## 💡 The Solution

**SmartPDF** intelligently maps light and neutral colors into a deep, comfortable dark palette while detecting and isolating embedded photos/diagrams to preserve their natural colors and fidelity.

---

## ✨ Features

* **Smart Color Inversion:** Maps background and neutral page elements to dark themes while leaving colored images untouched.
* **Preserve Original Imagery:** Dedicated logic isolates and restores original image regions (diagrams, logic gates, photos).
* **Color Presets:** Choose from predefined themes such as *Classic Dark*, *Ocean Blue*, *Forest Green*, *Deep Purple*, and *Warm Sepia*.
* **High Quality Output:** Supports high DPI scaling (up to 400 DPI) and lossless PNG or compressed JPEG encoding.
* **Modern GUI:** Built with `customtkinter` for a clean, user-friendly desktop experience.
* **Safe Processing:** Performs conversion using temporary files to ensure your original PDF is never modified or overwritten unexpectedly.

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mordekai66/SmartPDF.git
   cd SmartPDF
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Quick Start

Run the graphical interface using Python:

```bash
python main.py
```

### Steps:
1. Select your **Source PDF**.
2. Pick an **Output destination**.
3. Choose your preferred **Resolution (DPI)** and **Color Preset**.
4. Keep **"Preserve original images and illustrations"** checked for technical slides.
5. Click **Convert PDF**.

---

## 🛠️ Tech Stack & Requirements

* **Python 3.8+**
* **PyMuPDF (`fitz`):** For fast PDF rendering and image rectangle extraction.
* **Pillow (`PIL`) & NumPy:** For image processing and dark mode color transformation algorithms.
* **CustomTkinter:** For the modern dark-themed user interface.

---

## 📂 Project Structure

```text
SmartPDF/
├── main.py              # Application entry point
├── gui.py               # CustomTkinter GUI implementation
├── pdf_converter.py     # Main PDF processing logic & safety wrappers
├── image_processor.py   # Smart color mapping & image restoration algorithms
├── utils.py             # Path validation & PDF output verification
└── requirements.txt     # Dependency list
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check out the [issues page](https://github.com/Mordekai66/SmartPDF/issues).

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.