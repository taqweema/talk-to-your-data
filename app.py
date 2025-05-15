import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import docx
import openai

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="Talk to Your Data – Demo", layout="centered")
st.title("Talk to Your Data – Demo")
st.write("📂 Upload a file and ask questions about its content!")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt", "csv", "xlsx"])

file_text = ""

if uploaded_file is not None:
    file_name = uploaded_file.name.lower()
    st.success(f"✅ {uploaded_file.name} uploaded and processed successfully.")

    try:
        if file_name.endswith(".csv") or file_name.endswith(".xlsx"):
            df = pd.read_csv(uploaded_file) if file_name.endswith(".csv") else pd.read_excel(uploaded_file)
            file_text = df.to_string()
            st.write("📊 Here's a preview of your data:")
            st.dataframe(df.head())

        elif file_name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            file_text = "\n".join([para.text for para in doc.paragraphs])

        elif file_name.endswith(".txt"):
            file_text = uploaded_file.read().decode("utf-8")

        elif file_name.endswith(".pdf"):
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_doc:
                for page in pdf_doc:
                    file_text += page.get_text()

    except Exception as e:
        st.error(f"❌ Error processing the file: {e}")
        file_text = ""

if file_text:
    question = st.text_input("💬 Ask a question about this file:")
    if question:
        try:
            with st.spinner("🤖 Thinking..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant who answers questions about uploaded documents."},
                        {"role": "user", "content": f"The document content is:\n{file_text}\n\nNow answer this question: {question}"}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )
                st.markdown("### 🧠 Answer:")
                st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"⚠️ OpenAI Error: {e}")
