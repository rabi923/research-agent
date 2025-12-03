import streamlit as st
import sys
import os

# Add project root to path so we can import modules
# We need to go up two levels: ui -> research_agent -> root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research_agent.agent.research_agent import ResearchAgent

st.set_page_config(page_title="Research AI Agent", page_icon="🤖")

st.title("🤖 Research AI Agent")
st.markdown("Ask me anything! I'll research it, analyze it, and generate a report.")

# Initialize Agent
if "agent" not in st.session_state:
    st.session_state.agent = ResearchAgent()

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")
        if "pdf_path" in message and message["pdf_path"]:
            col1, col2, col3 = st.columns(3)
            with open(message["pdf_path"], "rb") as pdf_file:
                col1.download_button(
                    label="📄 PDF",
                    data=pdf_file,
                    file_name=os.path.basename(message["pdf_path"]),
                    mime="application/pdf",
                    key=f"download_pdf_{message['pdf_path']}"
                )
            if "docx_path" in message and message.get("docx_path"):
                 with open(message["docx_path"], "rb") as docx_file:
                    col2.download_button(
                        label="📝 DOCX",
                        data=docx_file,
                        file_name=os.path.basename(message["docx_path"]),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_docx_{message['docx_path']}"
                    )
            if "excel_path" in message and message.get("excel_path"):
                 with open(message["excel_path"], "rb") as excel_file:
                    col3.download_button(
                        label="📊 Excel",
                        data=excel_file,
                        file_name=os.path.basename(message["excel_path"]),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_excel_{message['excel_path']}"
                    )
        if "documents" in message and message["documents"]:
            with st.expander("Relevant Documents Found"):
                for doc in message["documents"]:
                    st.markdown(f"- [{doc['title']}]({doc['url']}) ({doc['type']})")
        if "sources" in message and message["sources"]:
            with st.expander("Sources Analyzed"):
                for source in message["sources"]:
                    st.markdown(f"- [{source['title']}]({source['url']})")

# User Input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Researching and Analyzing..."):
            try:
                history = st.session_state.messages[:-1]
                
                response = st.session_state.agent.process_query(prompt, history=history)
                
                answer = response["answer"]
                audio = response["audio"]
                sources = response["sources"]
                documents = response.get("documents", [])
                pdf_path = response.get("pdf_path")
                docx_path = response.get("docx_path")
                excel_path = response.get("excel_path")

                st.markdown(answer)
                if audio:
                    st.audio(audio, format="audio/mp3")
                
                col1, col2, col3 = st.columns(3)
                
                if pdf_path:
                    with open(pdf_path, "rb") as pdf_file:
                        col1.download_button(
                            label="📄 Download PDF",
                            data=pdf_file,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )
                
                if docx_path:
                    with open(docx_path, "rb") as docx_file:
                        col2.download_button(
                            label="📝 Download DOCX",
                            data=docx_file,
                            file_name=os.path.basename(docx_path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        
                if excel_path:
                    with open(excel_path, "rb") as excel_file:
                        col3.download_button(
                            label="📊 Download Excel",
                            data=excel_file,
                            file_name=os.path.basename(excel_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                if documents:
                    with st.expander("Relevant Documents Found"):
                        for doc in documents:
                            st.markdown(f"- [{doc['title']}]({doc['url']}) ({doc['type']})")

                if sources:
                    with st.expander("Sources Analyzed"):
                        for source in sources:
                            st.markdown(f"- [{source['title']}]({source['url']})")

                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "audio": audio,
                    "sources": sources,
                    "documents": documents,
                    "pdf_path": pdf_path,
                    "docx_path": docx_path,
                    "excel_path": excel_path
                })
            except Exception as e:
                st.error(f"An error occurred: {e}")
