# Approach Explanation: Semantic Document Intelligence Engine

## Core Philosophy

Our solution is engineered to transcend traditional keyword-based analysis and achieve a deep, contextual understanding of user needs. The core philosophy is **"Relevance through Semantics."** Instead of just matching words, we analyze the underlying meaning of the persona's role, their task, and the content within the documents. This allows us to surface insights that would be missed by conventional methods, directly addressing the hackathon's primary scoring criteria: Section and Sub-Section Relevance.

## Methodology: A Multi-Stage Pipeline

Our system operates through a streamlined, multi-stage pipeline designed for accuracy, efficiency, and adherence to all technical constraints.

**1. Intelligent Document Parsing:**
We begin by using the `PyMuPDF` library to parse PDFs. Crucially, we don't just extract raw text. We employ a heuristic-based approach to identify document structure by analyzing font sizes. Text with significantly larger fonts is flagged as a potential section title, allowing us to break the document into logically coherent chunks rather than arbitrary paragraphs.

**2. Semantic Embedding with Sentence-Transformers:**
This is the heart of our engine. We use the `all-MiniLM-L6-v2` model from the `sentence-transformers` library. This model was chosen specifically for its exceptional balance:
*   **High Performance:** It provides state-of-the-art semantic search capabilities.
*   **Lightweight:** With a size of under 90MB, it comfortably fits within the 1GB model constraint.
*   **CPU-Optimized:** It runs efficiently on a CPU, meeting the processing time requirement of <60 seconds.

We create a rich "query vector" by combining the persona's role, focus areas, and job-to-be-done. Then, we generate embedding vectors for every extracted section and sub-section from the documents.

**3. Relevance Ranking via Cosine Similarity:**
With all text converted into a high-dimensional vector space, we calculate the cosine similarity between the user's query vector and every document chunk vector. This mathematical measure represents true semantic relevance. A higher score means the document chunk is more conceptually aligned with the user's need. The chunks are then ranked based on this score to produce the final `importance_rank`.

**4. Granular Sub-Section Analysis:**
To fulfill the sub-section requirement, we use the lightweight `spaCy` model (`en_core_web_sm`) to further break down the top-ranked sections into individual sentences. These sentences (sub-sections) are then also scored and ranked against the same query vector, ensuring that the most granular, relevant pieces of information are highlighted for the user.

## Why This Approach is a Winner

*   **Superior Relevance:** By understanding intent, not just keywords, we deliver results that are contextually rich and directly useful to the persona.
*   **Constraint Compliant:** Our choice of lightweight, powerful models ensures we meet all size, speed, and hardware constraints without sacrificing quality.
*   **Robust and Generalizable:** The approach is domain-agnostic. It works equally well for academic papers, financial reports, or textbooks because it relies on the universal structure of language, not on domain-specific rules.
*   **Future-Ready:** The output JSON and the modular code are designed for seamless integration into the Round 2 web application, where these ranked sections can be used to power an interactive reading experience.