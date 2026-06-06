import streamlit as st
import docx
import PyPDF2
import io
import sys
import os

# Add the src directory to the path so we can import your algorithms
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from preprocessor import get_sentences
from algorithms import kmp_search

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Plagiarism Detector", page_icon="🔍", layout="wide")

st.title("🔍 Plagiarism Detector (String Matching)")
st.markdown("Upload documents or paste text to detect copied content using the **Knuth-Morris-Pratt (KMP)** algorithm.")

# --- HELPER FUNCTION: EXTRACT TEXT ---
def extract_text(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    extracted_text = ""
    
    try:
        if file_extension == 'txt':
            extracted_text = uploaded_file.getvalue().decode("utf-8")
        elif file_extension == 'docx':
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            extracted_text = "\n".join([para.text for para in doc.paragraphs])
        elif file_extension == 'pdf':
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        st.error(f"Error reading file: {e}")
        
    return extracted_text

# --- UI LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Original Source")
    orig_file = st.file_uploader("Upload Original (.txt, .pdf, .docx)", type=['txt', 'pdf', 'docx'], key="orig")
    orig_raw_text = extract_text(orig_file)
    orig_text = st.text_area("Or paste original text here:", value=orig_raw_text, height=250)

with col2:
    st.subheader("📝 Submitted Document")
    sub_file = st.file_uploader("Upload Submission (.txt, .pdf, .docx)", type=['txt', 'pdf', 'docx'], key="sub")
    sub_raw_text = extract_text(sub_file)
    sub_text = st.text_area("Or paste submitted text here:", value=sub_raw_text, height=250)

# --- DETECTION LOGIC ---
if st.button("🚀 Run KMP Algorithm", type="primary", use_container_width=True):
    if not orig_text.strip() or not sub_text.strip():
        st.warning("Please provide text for both the Original and Submitted documents.")
    else:
        with st.spinner("Analyzing documents..."):
            orig_sentences = get_sentences(orig_text)
            sub_sentences = get_sentences(sub_text)

            if not sub_sentences:
                st.error("Not enough valid text to analyze.")
            else:
                orig_clean_full = " ".join(orig_sentences)
                matched_sentences = []

                # KMP Execution
                for sentence in sub_sentences:
                    if kmp_search(orig_clean_full, sentence):
                        matched_sentences.append(sentence)

                # Results Calculation
                total_sentences = len(sub_sentences)
                plagiarized_count = len(matched_sentences)
                score = (plagiarized_count / total_sentences) * 100

                # --- DISPLAY RESULTS ---
                st.divider()
                st.subheader("📊 Analysis Report")
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Sentences", total_sentences)
                m2.metric("Plagiarized Sentences", plagiarized_count)
                
                # Color code the score
                if score == 0:
                    m3.metric("Plagiarism Score", f"{score:.2f}%", "Clean", delta_color="normal")
                    st.success("✅ No plagiarism detected. 100% Original!")
                elif score < 40:
                    m3.metric("Plagiarism Score", f"{score:.2f}%", "-Warning", delta_color="inverse")
                    st.warning("⚠️ Some similarities found. Review matched content.")
                else:
                    m3.metric("Plagiarism Score", f"{score:.2f}%", "-Critical", delta_color="inverse")
                    st.error("🚨 High level of plagiarism detected!")

                # Matched Content
                if matched_sentences:
                    st.markdown("### 🔴 Matched Content")
                    for i, match in enumerate(matched_sentences, 1):
                        st.error(f"**{i}.** {match}")