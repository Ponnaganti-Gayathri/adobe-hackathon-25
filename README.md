# Persona-Driven Document Intelligence

A Submission for the **Adobe India Hackathon 2025 (Round 1B)**. This project is an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of PDFs based on a specific user persona and their job-to-be-done, truly embodying the theme: _“Connect What Matters — For the User Who Matters”_.

## ✨ Key Features

-   **🧠 Semantic Analysis:** Moves beyond simple keyword matching by using a state-of-the-art Sentence Transformer model (`all-MiniLM-L6-v2`) to understand the contextual meaning of the user's request and the document text.
-   **📄 Intelligent Sectioning:** Instead of just extracting raw text, the system uses `PyMuPDF` to analyze font sizes, heuristically identifying section titles to parse documents into logically coherent chunks.
-   **🏆 Dual-Level Relevance Ranking:** Ranks both high-level sections and granular, sentence-level sub-sections, providing both a birds-eye view and a detailed analysis of the most important content.
-   **⚡ Fast & Lightweight:** The entire pipeline is optimized to run on a CPU, adhering to the **< 60-second** processing time and **< 1GB** model size constraints.
-   **📦 Fully Containerized:** Comes with a multi-stage `Dockerfile` for one-command, reproducible execution, ensuring it runs perfectly in any environment.

## 🛠️ Technology Stack

-   **Core Logic:** Python 3.9
-   **PDF Parsing:** PyMuPDF
-   **AI / Semantic Search:** Sentence-Transformers (PyTorch)
-   **Text Processing:** spaCy
-   **Containerization:** Docker

---

## 🚀 Getting Started

You can run this project in two ways: locally with a Python environment or via Docker.

### 1. Local Execution (Recommended for Development)

**Prerequisites:** Python 3.9+

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<YourUsername>/<your-repo-name>.git
    cd <your-repo-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate it (use the command for your OS)
    # On Windows:
    .\venv\Scripts\Activate.ps1
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Add your data:**
    -   Place your PDF files (3-10) inside the `input/documents/` directory.
    -   Edit the `input/persona.json` file to define the persona and job-to-be-done for your test case.

5.  **Run the analysis:**
    ```bash
    python main.py
    ```
    The script will print its progress to the console. The final JSON output will be saved in `output/challenge1b_output.json`.

### 2. Docker Execution (For Reproducibility)

**Prerequisites:** Docker Desktop must be running.

1.  **Build the Docker image:**
    From the root of the project directory, run:
    ```bash
    docker build -t adobe-hackathon-r1b .
    ```

2.  **Run the container:**
    This command will run the analysis inside the container and automatically save the results to your local `output` folder.

    *   **On macOS or Linux:**
        ```bash
        docker run --rm -v "$(pwd)/output":/app/output adobe-hackathon-r1b
        ```
    *   **On Windows (PowerShell):**
        ```powershell
        docker run --rm -v "${pwd}/output":/app/output adobe-hackathon-r1b
        ```
    The output file `challenge1b_output.json` will appear in your project's `output` folder.

---

## 📁 Project Structure

The repository is organized to be clean and intuitive.



## 🧠 Methodology Overview

Our system uses a multi-stage semantic pipeline to deliver highly relevant results:

1.  **Parse:** Extracts text and identifies sections from PDFs using layout cues.
2.  **Embed:** Converts the user query and all document sections into numerical vectors (embeddings) using the `all-MiniLM-L6-v2` model.
3.  **Rank:** Calculates the cosine similarity between the query vector and all document vectors to score and rank them by semantic relevance.
4.  **Refine:** Breaks down top sections into sentences and re-ranks them to find the most potent, granular insights.

For a detailed breakdown, please see the [**approach_explanation.md**](approach_explanation.md) file.

---

## 🔮 Vision for Round 2: The Web Application

This project's output is perfectly designed to power the Round 2 web application. The generated `challenge1b_output.json` can be used as an API response to create a beautiful, intuitive reading experience with **Adobe's PDF Embed API**.

**How it will work:**
1.  The frontend will display the ranked list of "Extracted Sections".
2.  When a user clicks on a section (e.g., "Methodology, Rank 1"), the web app will use the `document` and `page_number` from the JSON to command the PDF Embed API to instantly navigate to that exact page.
3.  Furthermore, the `sub_section_analysis` text can be used with the PDF Embed API's annotation and search tools to automatically highlight the most critical sentences on that page for the user.