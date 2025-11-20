# 🔫 Gun Pointer Pro

**Gun Pointer Pro** is a forensic text analysis tool currently in open beta. It detects AI-generated writing patterns and identifies potential plagiarism in academic and technical documents.

Unlike commercial black-box detectors, Gun Pointer Pro is fully transparent — every statistical step is visible to the user. This open, educational approach makes it ideal for researchers, students, and developers.

---

## 🚀 Key Features

### **🖥️ Modern User Interface**

* Built with **CustomTkinter**
* Sleek dark-mode GUI
* Real-time logging and animated visualizations

### **🧠 Dual-Engine Detection**

1. **AI Probability (Stylometric Analysis):**

   * **Burstiness** (variance in sentence lengths)
   * **Lexical Diversity** (range of vocabulary)
   * Detects robotic or statistically uniform writing patterns

2. **Plagiarism Hunting:**

   * Live N-gram chunking via **SerpApi**
   * Queries Google for matching text
   * Includes fuzzy matching using `difflib`

### **⚡ Asynchronous Core**

* Multi-threaded scanning
* UI remains fully responsive

### **📄 Robust File Parsing**

* PDF support via **PyMuPDF (Fitz)**
* Also supports `.docx` and `.txt`
* Handles complex textbook formatting

### **🧹 Smart Sanitization**

* Automatically removes academic artifacts such as:

  * "(2 marks)"
  * "Q1"
  * numbering and structural clutter

---

## ⚠️ Current Status: **v1.0b (Beta)**

* **Accuracy:** Solid but can produce false positives or negatives
* **Performance:** Large document optimization in progress
* **Stability:** Occasional encoding-related edge cases

---

## ⚙️ Installation

### **Portable Executable Available (No Installation Needed)**

A standalone **Windows .exe** version of Gun Pointer Pro is available.

* No Python required
* No dependency installation
* Just download and double‑click to run

👉 *(https://github.com/nimo94/Gun-Pointer-Pro/releases/tag/Releases)*

---

### **Prerequisites**

* Python **3.10+**
* A **SerpApi API Key** (required for plagiarism detection)

---

### **1. Clone the Repository**

```bash
git clone https://github.com/yourusername/gun-pointer-pro.git
cd gun-pointer-pro
```

### **2. Install Dependencies**

```bash
pip install customtkinter packaging google-search-results python-docx pymupdf
```

### **3. Configure API Key**

Open **`modern_detector.py`** and find:

```python
SERP_API_KEY = "YOUR_API_KEY_HERE"
```

Replace the value with your SerpApi key.

---

### **4. Launch the Application**

```bash
python modern_detector.py
```

---

## 🧠 How It Works

Gun Pointer Pro uses **deterministic logic**, not neural networks.

### **1. AI Detector (Stylometry)**

Large Language Models tend to produce statistically average text. We analyze:

* **Burstiness:** Humans naturally vary sentence lengths more.
* **Lexical Diversity:** AI tends to repeat common words and phrases.

The combination yields a probability score indicating whether text may be AI-generated.

---

### **2. Plagiarism Hunter (N-Gram Shingling)**

#### **Process Overview:**

* Clean text and remove formatting artifacts
* Slice into overlapping **10–12 word shingles**
* Sample chunks from:

  * Start
  * Middle
  * End
  * Random intervals
* Search chunks using **SerpApi** → Google results
* Compare results with fuzzy matching to compute similarity

This allows detection even when text has been paraphrased.

---

## 🗺️ Roadmap (v1.1)

* [ ] **PDF/HTML Report Export**
* [ ] **Batch Processing** (scan multiple documents at once)
* [ ] **Custom Sensitivity Settings**
* [ ] **Offline Mode** for AI detection

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch:

   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit changes:

   ```bash
   git commit -m "Add AmazingFeature"
   ```
4. Push the branch:

   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request

---

## 📄 Disclaimer

Gun Pointer Pro assists with verification but does **not** provide absolute judgments. Always apply human review, especially for academic or professional decisions.

---

## 📄 License

Distributed under the **MIT License**. See the `LICENSE` file for details.
