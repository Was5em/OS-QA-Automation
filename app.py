import streamlit as st
import google.generativeai as genai
import json
import os
import tempfile
import time


genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(
    page_title="Outsourcing Skill AI QA Automation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎧 QA Automation")
st.markdown("**Powered by Outsourcing Skill - Automated Quality Assurance**")
st.markdown("---")

def process_audio_file(file_path):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    audio_file = genai.upload_file(path=file_path)
    
    while audio_file.state.name == "PROCESSING":
        time.sleep(2)
        audio_file = genai.get_file(audio_file.name)
    
    prompt = """
    Listen to this customer service call and act as a strict Senior QA Auditor and Medical Data Extraction Specialist.
    
    Task 1: Data Extraction
    Extract the following details exactly as mentioned in the call. If a detail is missing, write "Not Mentioned":
    - Agent_Name
    - Patient_Name
    - DOB
    - Address
    - Phone_Number
    - Medicare_ID
    - Brace_Size
    - Height
    - Weight
    - Pain_Level
    - Doctor_Name
    - Last_Visit_Date
    - Previous_Treatments
    
    Task 2: QA Evaluation
    Calculate the overall QA Score out of 100 based on standard call center metrics.
    List the agent's Strengths.
    List the agent's Weaknesses. CRITICAL: If the agent was pushy, ignored the customer saying they are not interested, or used coercive tactics, write a highly detailed analysis here with EXACT timestamps and quotes.
    
    CRITICAL JSON FORMATTING RULES:
    1. The output MUST be a single, valid JSON object.
    2. Escape all double quotes inside strings (use \\" instead of ").
    3. Use \\n for line breaks.
    
    Output exactly this JSON structure with NO extra text:
    {
      "Agent_Name": "", "Patient_Name": "", "DOB": "", "Address": "",
      "Phone_Number": "", "Medicare_ID": "", "Brace_Size": "", "Height": "",
      "Weight": "", "Pain_Level": "", "Doctor_Name": "", "Last_Visit_Date": "",
      "Previous_Treatments": "", "Score": "", "Strengths": "", "Weaknesses": ""
    }
    """
    
    response = model.generate_content(
        [prompt, audio_file],
        generation_config={"response_mime_type": "application/json"}
    )
    
    return json.loads(response.text.strip())


st.sidebar.header("📂 Upload Call Record")
uploaded_file = st.sidebar.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])

if uploaded_file is not None:
    st.sidebar.audio(uploaded_file, format='audio/mp3')
    
    if st.sidebar.button("🚀 Analyze Call Now"):
        with st.spinner('🤖 AI is listening and analyzing the call... Please wait.'):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio.write(uploaded_file.read())
                temp_audio_path = temp_audio.name

            try:
                result = process_audio_file(temp_audio_path)
                
                st.success("✅ Analysis Complete!")
                st.markdown("---")
                
                
                with st.container(border=True):
                    st.subheader("📊 QA Score")
                    score = result.get("Score", "N/A")
                    st.metric(label="Overall Performance", value=f"{score}/100")
                    st.info(f"**Agent Name:** {result.get('Agent_Name', 'N/A')}")
                
                st.markdown("<br>", unsafe_allow_html=True) 
                
                with st.container(border=True):
                    st.subheader("🏥 Extracted Medical Data")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Patient Name:** {result.get('Patient_Name', 'N/A')}")
                        st.markdown(f"**DOB:** {result.get('DOB', 'N/A')}")
                        st.markdown(f"**Phone Number:** {result.get('Phone_Number', 'N/A')}")
                        st.markdown(f"**Address:** {result.get('Address', 'N/A')}")
                        st.markdown(f"**Medicare ID:** {result.get('Medicare_ID', 'N/A')}")
                    with col_b:
                        st.markdown(f"**Doctor Name:** {result.get('Doctor_Name', 'N/A')}")
                        st.markdown(f"**Last Visit Date:** {result.get('Last_Visit_Date', 'N/A')}")
                        st.markdown(f"**Pain Level:** {result.get('Pain_Level', 'N/A')}")
                        st.markdown(f"**Brace Size:** {result.get('Brace_Size', 'N/A')}")
                        st.markdown(f"**Height/Weight:** {result.get('Height', 'N/A')} / {result.get('Weight', 'N/A')}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                with st.container(border=True):
                    st.subheader("💡 QA Feedback")
                    st.markdown("### 🌟 Strengths")
                    st.success(result.get("Strengths", "None listed."))
                    
                    st.markdown("### ⚠️ Weaknesses & Compliance")
                    st.error(result.get("Weaknesses", "None listed."))
                        
                st.markdown("---")
                st.subheader("📋 Full Extracted Record (JSON)")
                st.json(result)

            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {e}")
            
            finally:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
else:
    st.info("👈 Please upload an audio file from the sidebar to begin the AI Quality Assurance analysis.")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", width=250)
