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
            with open(message["pdf_path"], "rb") as pdf_file:
                st.download_button(
                    label="Download Report PDF",
                    data=pdf_file,
                    file_name=os.path.basename(message["pdf_path"]),
                    mime="application/pdf",
                    key=f"download_{message['pdf_path']}" # Unique key
                )
        if "documents" in message and message["documents"]:
            with st.expander("Relevant Documents Found"):
                for doc in message["documents"]:
                    st.markdown(f"- [{doc['title']}]({doc['url']}) ({doc['type']})")
        if "sources" in message and message["sources"]:
            with st.expander("Sources"):
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

                st.markdown(answer)
                st.audio(audio, format="audio/mp3")
                
                if pdf_path:
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="Download Report PDF",
                            data=pdf_file,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )

                if documents:
                    with st.expander("Relevant Documents Found"):
                        for doc in documents:
                            st.markdown(f"- [{doc['title']}]({doc['url']}) ({doc['type']})")

                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            st.markdown(f"- [{source['title']}]({source['url']})")

                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "audio": audio,
                    "sources": sources,
                    "documents": documents,
                    "pdf_path": pdf_path
                })
            except Exception as e:
                st.error(f"An error occurred: {e}")
