import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import docx  # python-docx
import openai

# ✅ OpenAI client using new SDK
client = openai.OpenAI(api_key="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")  # Replace with your real key

st.title("Talk to Your Data – Demo")
st.write("📂 Upload a file and ask questions about its content!")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt", "csv", "xlsx"])

if uploaded_file is not None:
    file_name = uploaded_file.name.lower()
    pdf_text = ""
    full_text = ""

    # Handle CSV or Excel
    if file_name.endswith(".csv") or file_name.endswith(".xlsx"):
        try:
            df = pd.read_csv(uploaded_file) if file_name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.success(f"✅ {uploaded_file.name} uploaded and processed successfully.")
            st.write("📊 Here's a preview of your data:")
            st.dataframe(df.head())
        except Exception as e:
            st.error("❌ Error reading the file.")

    # Handle Word (.docx)
    elif file_name.endswith(".docx"):
        try:
            doc = docx.Document(uploaded_file)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            st.success(f"✅ {uploaded_file.name} uploaded and processed successfully.")
        except Exception as e:
            st.error("❌ Could not read DOCX file.")

    # Handle PDF
    elif file_name.endswith(".pdf"):
        try:
            pdf_reader = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in pdf_reader:
                pdf_text += page.get_text()
            st.success(f"✅ {uploaded_file.name} uploaded and processed successfully.")
        except Exception as e:
            st.error("❌ Could not read PDF file.")

    # Q&A Section
    if file_name.endswith(('.pdf', '.docx', '.txt')):
        user_question = st.text_input("💬 Ask a question about this file:")

        if user_question and (pdf_text or full_text):
            with st.spinner("🤖 Thinking..."):
                content_to_send = pdf_text if file_name.endswith('.pdf') else full_text

                # ✂️ Limit to 3000 characters for token safety
                shortened_text = content_to_send[:3000]

                prompt = f"You are a helpful research assistant. Based on this document:\n\n{shortened_text}\n\nAnswer this question:\n{user_question}"

                try:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2
                    )
                    st.markdown("### 🧠 Answer:")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"⚠️ OpenAI Error: {e}")
