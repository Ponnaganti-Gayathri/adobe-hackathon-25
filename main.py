import os
import json
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import numpy as np
import spacy
import time
import argparse

# --- Configuration ---
MODEL_NAME = 'all-MiniLM-L6-v2'
SPACY_MODEL_NAME = "en_core_web_sm"

# --- Helper Functions ---

def load_models():
    """Loads the sentence transformer and spacy models."""
    print("Loading models...")
    model = SentenceTransformer(MODEL_NAME)
    try:
        nlp = spacy.load(SPACY_MODEL_NAME)
    except OSError:
        print(f"Downloading spacy model {SPACY_MODEL_NAME}...")
        spacy.cli.download(SPACY_MODEL_NAME)
        nlp = spacy.load(SPACY_MODEL_NAME)
    print("Models loaded successfully.")
    return model, nlp

def parse_documents(doc_paths):
    """
    Parses PDF documents to extract text, trying to identify sections based on font size.
    Returns a list of dictionaries, each representing a potential section.
    """
    print(f"Parsing {len(doc_paths)} documents...")
    all_sections = []
    for doc_path in doc_paths:
        doc_name = os.path.basename(doc_path)
        try:
            document = fitz.open(doc_path)
            current_title = "Introduction" # Default title for text before the first heading
            current_text_block = ""
            # Heuristic: Identify titles by looking for text with a larger font size.
            for page_num, page in enumerate(document):
                blocks = page.get_text("dict", flags=11)["blocks"]
                for b in blocks:
                    if 'lines' in b:
                        for l in b['lines']:
                            for s in l['spans']:
                                # Heuristic: If font size is > 14 (common for headings) and text is short.
                                if s['size'] > 14 and len(s['text'].split()) < 10:
                                    if current_text_block.strip(): # Save the previous section if it has content
                                        all_sections.append({
                                            "document": doc_name,
                                            "page_number": page_num + 1, # Use current page for previous block
                                            "section_title": current_title.strip(),
                                            "text": current_text_block.strip()
                                        })
                                    current_title = s['text']
                                    current_text_block = ""
                                else:
                                    current_text_block += s['text'] + " "
            # Add the last collected section
            if current_text_block.strip():
                all_sections.append({
                    "document": doc_name,
                    "page_number": document.page_count,
                    "section_title": current_title.strip(),
                    "text": current_text_block.strip()
                })
        except Exception as e:
            print(f"Error processing {doc_name}: {e}")
    print(f"Extracted {len(all_sections)} potential sections.")
    return all_sections


def refine_and_split_sections(sections, nlp, min_length=20):
    """Splits large sections into smaller, meaningful sub-sections (sentences)."""
    print("Refining and splitting sections into sub-sections...")
    sub_sections = []
    for section in sections:
        if len(section['text']) > min_length:
            doc = nlp(section['text'])
            for sentence in doc.sents:
                if len(sentence.text.strip()) > min_length:
                    sub_sections.append({
                        "document": section['document'],
                        "page_number": section['page_number'],
                        "section_title": section['section_title'],
                        "refined_text": sentence.text.strip()
                    })
    print(f"Created {len(sub_sections)} sub-sections.")
    return sub_sections


def analyze_and_rank(persona, job, sections, sub_sections, model):
    """Analyzes content against the persona and job, then ranks them."""
    print("Analyzing and ranking sections and sub-sections...")
    query = f"As a {persona['role']} with expertise in {persona['focus_areas']}, I need to {job}."
    
    print("Generating embeddings for query and documents...")
    query_embedding = model.encode(query, convert_to_tensor=True)
    section_texts = [s['text'] for s in sections]
    section_embeddings = model.encode(section_texts, convert_to_tensor=True, show_progress_bar=True)
    sub_section_texts = [s['refined_text'] for s in sub_sections]
    sub_section_embeddings = model.encode(sub_section_texts, convert_to_tensor=True, show_progress_bar=True)

    print("Calculating relevance scores...")
    section_scores = util.pytorch_cos_sim(query_embedding, section_embeddings)[0]
    sub_section_scores = util.pytorch_cos_sim(query_embedding, sub_section_embeddings)[0]

    for i, section in enumerate(sections):
        section['score'] = section_scores[i].item()
    ranked_sections = sorted(sections, key=lambda x: x['score'], reverse=True)
    final_ranked_sections = []
    for i, section in enumerate(ranked_sections):
        if section['score'] > 0.15: # Confidence threshold
            final_ranked_sections.append({
                "document": section['document'],
                "page_number": section['page_number'],
                "section_title": section['section_title'],
                "importance_rank": i + 1
            })

    for i, sub_section in enumerate(sub_sections):
        sub_section['score'] = sub_section_scores[i].item()
    ranked_sub_sections = sorted(sub_sections, key=lambda x: x['score'], reverse=True)
    final_ranked_sub_sections = []
    seen_texts = set()
    for sub_section in ranked_sub_sections:
        if sub_section['score'] > 0.2 and sub_section['refined_text'] not in seen_texts: # Higher threshold
            final_ranked_sub_sections.append({
                "document": sub_section['document'],
                "page_number": sub_section['page_number'],
                "refined_text": sub_section['refined_text']
            })
            seen_texts.add(sub_section['refined_text'])
            if len(final_ranked_sub_sections) >= 50: # Limit output size
                break
    print("Ranking complete.")
    return final_ranked_sections, final_ranked_sub_sections


def main(input_dir, output_dir):
    start_time = time.time()
    persona_path = os.path.join(input_dir, 'persona.json')
    with open(persona_path, 'r') as f:
        input_data = json.load(f)
    persona = input_data['persona']
    job = input_data['job_to_be_done']
    doc_dir = os.path.join(input_dir, 'documents')
    doc_paths = [os.path.join(doc_dir, f) for f in os.listdir(doc_dir) if f.lower().endswith('.pdf')]
    
    model, nlp = load_models()
    sections = parse_documents(doc_paths)
    sub_sections = refine_and_split_sections(sections, nlp)
    ranked_sections, ranked_sub_sections = analyze_and_rank(persona, job, sections, sub_sections, model)

    output_data = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in doc_paths],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        },
        "extracted_sections": ranked_sections,
        "sub_section_analysis": ranked_sub_sections
    }
    
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"\nTotal processing time: {processing_time:.2f} seconds.")
    if processing_time > 60:
        print("WARNING: Processing time exceeded the 60-second constraint.")

    output_path = os.path.join(output_dir, 'challenge1b_output.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"\nOutput successfully saved to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Persona-Driven Document Intelligence System")
    parser.add_argument('--input_dir', type=str, default='input', help="Directory containing persona.json and documents/")
    parser.add_argument('--output_dir', type=str, default='output', help="Directory to save the output JSON file.")
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)