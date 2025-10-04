import streamlit as st
import os
import tempfile
import sys
from io import StringIO

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

# --- Streamlit UI (Front-End) ---
st.set_page_config(page_title="Legal Document Summarizer", layout="wide")

st.title("⚖ Legal Document Summarization")
st.write("Upload a document and our AI, powered by LangChain and Gemini, will provide a professional summary.")

# --- API Key Input ---
# Use a session state variable to store the key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.subheader("1. Enter Your Google Gemini API Key")
api_key = st.text_input(
    "API Key:",
    type="password",
    help="You can get your API key from https://aistudio.google.com/app/apikey"
)

# Update the session state and environment variable
if api_key:
    st.session_state.api_key = api_key
    os.environ["GOOGLE_API_KEY"] = st.session_state.api_key

# --- LangChain Setup ---
@st.cache_resource
def get_llm():
    """Initializes and returns the Gemini LLM model."""
    if not st.session_state.api_key:
        st.error("Please enter a valid API key to proceed.")
        return None
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.0,
            convert_system_message_to_human=True
        )
        return llm
    except Exception as e:
        st.error(f"Error initializing LLM. Please check your API key. Details: {e}")
        return None

# The prompt template that guides the LLM.
template = """
You are an expert legal assistant. Summarize the following document concisely and professionally. 
Identify the key parties, main legal issues, and any important clauses or deadlines.
The document content is as follows:
"{document_content}"
"""
prompt = PromptTemplate(template=template, input_variables=["document_content"])

# --- The Main Application Logic ---
st.subheader("2. Upload Your Document")
uploaded_file = st.file_uploader("Choose a legal document", type=['txt', 'docx', 'pdf'])

# The main logic is now wrapped in a button press
if st.button("Generate Summary"):
    if not uploaded_file:
        st.warning("Please upload a file first.")
        st.stop()
    if not st.session_state.api_key:
        st.warning("Please enter your API key first.")
        st.stop()

    document_content = ""
    temp_file_path = None

    try:
        with st.spinner('Loading and extracting text...'):
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            # Save the uploaded file to a temporary location for the loaders
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_file_path = temp_file.name
            
            if file_extension == ".pdf":
                loader = PyPDFLoader(temp_file_path)
                docs = loader.load()
                document_content = "\n\n".join([doc.page_content for doc in docs])
            elif file_extension == ".docx":
                loader = Docx2txtLoader(temp_file_path)
                docs = loader.load()
                document_content = "\n\n".join([doc.page_content for doc in docs])
            elif file_extension == ".txt":
                # For plain text, we read it directly.
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                document_content = stringio.read()
            else:
                st.warning("Unsupported file type. Please upload a .txt, .docx, or .pdf file.")
                st.stop()

        st.text_area("Original Text", document_content, height=300, disabled=True)
        
        st.markdown("---")
        st.subheader("AI-Generated Summary")
        
        llm_instance = get_llm()
        if llm_instance:
            llm_chain = LLMChain(llm=llm_instance, prompt=prompt)
            with st.spinner('Generating summary with Gemini...'):
                summary = llm_chain.invoke({"document_content": document_content})
                st.write(summary['text'])
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please ensure you have entered a valid API key and that the file is not corrupted.")
        
    finally:
        # Clean up the temporary file, if it was created
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)