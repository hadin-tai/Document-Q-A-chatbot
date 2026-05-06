import streamlit as st
import requests

# ==================================
# CONFIG
# ==================================
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Vector RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ==================================
# SESSION STATE
# ==================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""

# ==================================
# API FUNCTIONS
# ==================================
def upload_file(file):
    files = {
        "file": (
            file.name,
            file.getvalue(),
            file.type
        )
    }

    res = requests.post(
        f"{BACKEND_URL}/api/upload",
        files=files,
        timeout=300
    )

    return res.status_code == 200


def ask_question(question):
    res = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={"question": question},
        timeout=300
    )

    if res.status_code == 200:
        data = res.json()
        return data.get("answer", "No answer found.")

    return "Backend error."


# ==================================
# SIDEBAR (SAME LAYOUT STYLE)
# ==================================
with st.sidebar:
    st.title("📂 Documents")

    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=5)

        if r.status_code == 200:
            st.success("Backend Connected")
        else:
            st.error("Backend Error")

    except:
        st.error("Backend Offline")

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "txt", "doc", "docx"]
    )

    if st.button("Upload"):
        if uploaded_file:
            with st.spinner("Uploading..."):
                try:
                    ok = upload_file(uploaded_file)

                    if ok:
                        st.session_state.uploaded = True
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.success("Uploaded Successfully")
                    else:
                        st.error("Upload failed")

                except Exception as e:
                    st.error(str(e))

    st.divider()

    st.subheader("Your File")

    if st.session_state.uploaded:
        st.write(st.session_state.uploaded_file_name)
        st.caption("✅ Ready")
    else:
        st.caption("No file uploaded")

# ==================================
# MAIN AREA
# ==================================
st.title("💬 Chat with Documents")

if st.session_state.uploaded:
    st.success("Document ready for chat")
else:
    st.info("Upload a document first.")

st.divider()

# ==================================
# CHAT HISTORY
# ==================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==================================
# CHAT INPUT
# ==================================
if prompt := st.chat_input("Ask something..."):

    if not st.session_state.uploaded:
        st.warning("Please upload a document first.")

    else:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_question(prompt)
                except Exception as e:
                    answer = str(e)

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )























# import streamlit as st
# import requests
# import time

# # ==================================
# # CONFIG
# # ==================================
# BACKEND_URL = "http://127.0.0.1:8000"

# st.set_page_config(
#     page_title="Vector RAG Chatbot",
#     page_icon="🤖",
#     layout="wide"
# )

# # ==================================
# # SESSION STATE
# # ==================================
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "uploaded" not in st.session_state:
#     st.session_state.uploaded = False

# # ==================================
# # CSS
# # ==================================
# st.markdown("""
# <style>
# html, body, [class*="css"] {
#     font-family: 'Segoe UI', sans-serif;
# }

# .main {
#     background-color: #0b0f19;
# }

# .block-container {
#     padding-top: 1rem;
#     max-width: 1100px;
# }

# /* Header */
# .title-box {
#     text-align:center;
#     padding:10px;
#     margin-bottom:15px;
# }

# .title-box h1 {
#     color:white;
#     margin-bottom:0px;
# }

# .title-box p {
#     color:#94a3b8;
#     font-size:14px;
# }

# /* Chat bubble */
# .user-msg {
#     background:#2563eb;
#     color:white;
#     padding:14px 18px;
#     border-radius:18px 18px 4px 18px;
#     max-width:75%;
#     margin-left:auto;
#     margin-bottom:12px;
#     font-size:15px;
# }

# .bot-msg {
#     background:#1e293b;
#     color:white;
#     padding:14px 18px;
#     border-radius:18px 18px 18px 4px;
#     max-width:75%;
#     margin-right:auto;
#     margin-bottom:12px;
#     font-size:15px;
#     border:1px solid #334155;
# }

# /* Sidebar */
# section[data-testid="stSidebar"] {
#     background:#111827;
# }

# section[data-testid="stSidebar"] * {
#     color:white;
# }

# /* Upload success */
# .success-box {
#     background:#14532d;
#     color:white;
#     padding:10px;
#     border-radius:10px;
# }

# /* Input */
# .stTextInput input {
#     border-radius:12px;
#     height:48px;
#     font-size:15px;
# }

# /* Buttons */
# .stButton button {
#     width:100%;
#     border-radius:12px;
#     height:46px;
#     font-weight:600;
# }
# </style>
# """, unsafe_allow_html=True)

# # ==================================
# # SIDEBAR
# # ==================================
# with st.sidebar:
#     st.title("📄 Document Panel")

#     try:
#         r = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
#         if r.status_code == 200:
#             st.success("Backend Connected")
#         else:
#             st.error("Backend Error")
#     except:
#         st.error("Backend Offline")

#     st.markdown("---")

#     uploaded_file = st.file_uploader(
#         "Upload Document",
#         type=["pdf", "txt", "doc", "docx"]
#     )

#     if uploaded_file:
#         if st.button("📤 Upload File"):
#             files = {
#                 "file": (
#                     uploaded_file.name,
#                     uploaded_file.getvalue(),
#                     uploaded_file.type
#                 )
#             }

#             with st.spinner("Uploading document..."):
#                 try:
#                     res = requests.post(
#                         f"{BACKEND_URL}/api/upload",
#                         files=files,
#                         timeout=300
#                     )

#                     if res.status_code == 200:
#                         st.session_state.uploaded = True
#                         st.markdown(
#                             f"""
#                             <div class="success-box">
#                             ✅ Uploaded Successfully<br>
#                             {uploaded_file.name}
#                             </div>
#                             """,
#                             unsafe_allow_html=True
#                         )
#                     else:
#                         st.error("Upload failed")

#                 except Exception as e:
#                     st.error(str(e))

# # ==================================
# # HEADER
# # ==================================
# st.markdown("""
# <div class="title-box">
# <h1>🤖 Vector RAG Chatbot</h1>
# <p>Upload documents and chat with your data intelligently</p>
# </div>
# """, unsafe_allow_html=True)

# # ==================================
# # CHAT AREA
# # ==================================
# chat_container = st.container()

# with chat_container:
#     for msg in st.session_state.messages:
#         if msg["role"] == "user":
#             st.markdown(
#                 f'<div class="user-msg">{msg["content"]}</div>',
#                 unsafe_allow_html=True
#             )
#         else:
#             st.markdown(
#                 f'<div class="bot-msg">{msg["content"]}</div>',
#                 unsafe_allow_html=True
#             )

# # ==================================
# # INPUT AREA
# # ==================================
# st.markdown("---")

# col1, col2 = st.columns([5,1])

# with col1:
#     question = st.text_input(
#         "",
#         placeholder="Type your message here..."
#     )

# with col2:
#     send = st.button("Send")

# # ==================================
# # SEND MESSAGE
# # ==================================
# if send and question.strip():

#     st.session_state.messages.append(
#         {"role": "user", "content": question}
#     )

#     with st.spinner("Thinking..."):
#         try:
#             res = requests.post(
#                 f"{BACKEND_URL}/api/chat",
#                 json={"question": question},
#                 timeout=300
#             )

#             if res.status_code == 200:
#                 data = res.json()
#                 answer = data.get("answer", "No answer found.")
#             else:
#                 answer = "Backend error."

#         except Exception as e:
#             answer = str(e)

#     st.session_state.messages.append(
#         {"role": "assistant", "content": answer}
#     )

#     st.rerun()





    







# import streamlit as st
# import requests
# import time

# # ==========================================
# # CONFIG
# # ==========================================
# BACKEND_URL = "http://127.0.0.1:5000"

# st.set_page_config(
#     page_title="Vector RAG Assistant",
#     page_icon="📄",
#     layout="wide"
# )

# # ==========================================
# # CUSTOM CSS
# # ==========================================
# st.markdown("""
# <style>
# .main {
#     background-color: #0f172a;
# }
# .block-container {
#     padding-top: 2rem;
# }
# h1,h2,h3 {
#     color: white;
# }
# .stTextInput input {
#     border-radius: 10px;
# }
# .stButton button {
#     width: 100%;
#     border-radius: 10px;
#     height: 45px;
#     font-weight: bold;
# }
# .chat-user {
#     background:#1e293b;
#     padding:15px;
#     border-radius:12px;
#     color:white;
#     margin-bottom:10px;
# }
# .chat-bot {
#     background:#14532d;
#     padding:15px;
#     border-radius:12px;
#     color:white;
#     margin-bottom:20px;
# }
# .success-box {
#     background:#166534;
#     padding:12px;
#     border-radius:10px;
#     color:white;
# }
# </style>
# """, unsafe_allow_html=True)

# # ==========================================
# # SESSION STATE
# # ==========================================
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # ==========================================
# # HEADER
# # ==========================================
# st.title("📄 Vector RAG Assistant")
# st.caption("Upload documents and ask intelligent questions powered by Pinecone Assistant")

# # ==========================================
# # SIDEBAR
# # ==========================================
# with st.sidebar:
#     st.header("⚙️ System Status")

#     try:
#         r = requests.get(f"{BACKEND_URL}/api/health")
#         if r.status_code == 200:
#             st.success("Backend Connected")
#         else:
#             st.error("Backend Error")
#     except:
#         st.error("Backend Offline")

#     st.markdown("---")
#     st.info("Backend URL:")
#     st.code(BACKEND_URL)

# # ==========================================
# # MAIN LAYOUT
# # ==========================================
# col1, col2 = st.columns([1, 2])

# # ==========================================
# # LEFT SIDE - UPLOAD
# # ==========================================
# with col1:
#     st.subheader("📤 Upload Document")

#     uploaded_file = st.file_uploader(
#         "Choose file",
#         type=["pdf", "txt", "doc", "docx"]
#     )

#     if uploaded_file:
#         st.write("Selected:", uploaded_file.name)

#         if st.button("Upload File"):
#             files = {
#                 "file": (
#                     uploaded_file.name,
#                     uploaded_file.getvalue(),
#                     uploaded_file.type
#                 )
#             }

#             with st.spinner("Uploading file to server..."):
#                 try:
#                     response = requests.post(
#                         f"{BACKEND_URL}/api/upload",
#                         files=files,
#                         timeout=300
#                     )

#                     if response.status_code == 200:
#                         st.markdown(
#                             f"""
#                             <div class="success-box">
#                             ✅ Upload Completed Successfully
#                             <br>
#                             File: {uploaded_file.name}
#                             </div>
#                             """,
#                             unsafe_allow_html=True
#                         )
#                     else:
#                         st.error("Upload failed")

#                 except Exception as e:
#                     st.error(f"Error: {str(e)}")

# # ==========================================
# # RIGHT SIDE - CHAT
# # ==========================================
# with col2:
#     st.subheader("💬 Ask Questions")

#     question = st.text_input(
#         "Enter your question",
#         placeholder="What is this document about?"
#     )

#     if st.button("Ask Question"):
#         if question.strip():

#             st.session_state.chat_history.append(
#                 {"role": "user", "content": question}
#             )

#             with st.spinner("Thinking... getting answer from backend..."):
#                 try:
#                     response = requests.post(
#                         f"{BACKEND_URL}/api/chat",
#                         json={"question": question},
#                         timeout=300
#                     )

#                     if response.status_code == 200:
#                         data = response.json()

#                         answer = data.get("answer", "No response")

#                         st.session_state.chat_history.append(
#                             {"role": "bot", "content": answer}
#                         )

#                     else:
#                         st.error("Backend failed")

#                 except Exception as e:
#                     st.error(str(e))

# # ==========================================
# # CHAT HISTORY
# # ==========================================
# st.markdown("---")
# st.subheader("🧠 Conversation")

# for msg in st.session_state.chat_history:
#     if msg["role"] == "user":
#         st.markdown(
#             f'<div class="chat-user">🧑‍💼 {msg["content"]}</div>',
#             unsafe_allow_html=True
#         )
#     else:
#         st.markdown(
#             f'<div class="chat-bot">🤖 {msg["content"]}</div>',
#             unsafe_allow_html=True
#         )