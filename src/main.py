import os
from preprocessor import get_sentences
from algorithms import kmp_search, rabin_karp_search

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None

def main():
    print("=== Plagiarism Detector ===")
    
    # Define file paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    orig_path = os.path.join(base_dir, "documents", "original.txt")
    sub_path = os.path.join(base_dir, "documents", "submitted.txt")

    original_text = read_file(orig_path)
    submitted_text = read_file(sub_path)

    if not original_text or not submitted_text:
        return

    # Preprocessing
    orig_sentences = get_sentences(original_text)
    sub_sentences = get_sentences(submitted_text)
    orig_clean_full = " ".join(orig_sentences)

    total_sentences = len(sub_sentences)
    if total_sentences == 0:
        print("Submitted document is empty or unreadable.")
        return

    print("\n[+] Processing Documents...")
    print(f"Algorithm Selected: Knuth-Morris-Pratt (KMP) & Rabin-Karp")
    
    matched_sentences = []
    
    # Detection Engine
    for sentence in sub_sentences:
        # Using KMP for demonstration; you could toggle to Rabin-Karp here
        if kmp_search(orig_clean_full, sentence):
            matched_sentences.append(sentence)

    # Report Generation
    plagiarism_score = (len(matched_sentences) / total_sentences) * 100

    print("\n=== Plagiarism Report ===")
    print(f"Total Sentences Analyzed: {total_sentences}")
    print(f"Plagiarized Sentences Found: {len(matched_sentences)}")
    print(f"Plagiarism Percentage: {plagiarism_score:.2f}%\n")
    
    if matched_sentences:
        print("--- Matched Content ---")
        for idx, match in enumerate(matched_sentences, 1):
            print(f"{idx}. {match}")
    else:
        print("No plagiarism detected. Great job!")

if __name__ == "__main__":
    main()