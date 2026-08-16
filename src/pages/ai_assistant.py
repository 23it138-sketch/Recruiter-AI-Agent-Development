import streamlit as st
from config import is_gemini_available, get_data_dir
from utils import load_json
from chat_agent import ChatAgent

def render_ai_assistant():
    st.markdown("<h1 class='gradient-text'>🤖 AI Recruiting Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Ask questions about candidates, jobs, and the hiring process.</p>", unsafe_allow_html=True)
    
    if not is_gemini_available():
        st.markdown('''
        <div class="card" style="border-left: 6px solid #E17055;">
            <h3 style="color: #E17055; margin-top: 0;">Gemini AI is Disconnected</h3>
            <p>The AI Assistant requires a valid Gemini API Key to function.</p>
            <p><strong>To set this up:</strong></p>
            <ol>
                <li>Create a <code>.env</code> file in the project root.</li>
                <li>Add your key: <code>GEMINI_API_KEY=your_key_here</code></li>
                <li>Restart the Streamlit server.</li>
            </ol>
            <hr>
            <p style="color: #64748B;"><em>Suggested prompts you could try once connected:</em></p>
            <ul>
                <li>"Summarize the current candidate's experience."</li>
                <li>"What are 3 behavioral questions for the Frontend Developer role?"</li>
                <li>"Why might this candidate struggle with the Backend Engineer position?"</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        return
        
    # AI IS AVAILABLE
    agent = ChatAgent()
    
    col_chat, col_context = st.columns([3, 1])
    
    with col_context:
        st.markdown("<div class='section-header'>📚 Context & Tools</div>", unsafe_allow_html=True)
        
        include_resume = False
        if st.session_state.get("parsed_resume"):
            include_resume = st.checkbox("Include Current Resume", value=True)
            st.caption(f"Candidate: {st.session_state.parsed_resume.name}")
            
        jobs_file = get_data_dir() / "sample_jobs.json"
        jobs = load_json(jobs_file) if jobs_file.exists() else []
        selected_job = None
        
        if jobs:
            job_titles = ["None"] + [j.get("title") for j in jobs]
            job_sel = st.selectbox("Include Job Context", options=job_titles)
            if job_sel != "None":
                selected_job = next((j for j in jobs if j.get("title") == job_sel), None)
                
        st.markdown("### Quick Prompts")
        
        prompts = [
            "Summarize this resume",
            "Generate interview questions",
            "Compare strengths & weaknesses",
            "Draft a rejection email",
            "Draft an interview invite"
        ]
        
        clicked_prompt = None
        for p in prompts:
            if st.button(p, use_container_width=True):
                clicked_prompt = p
                
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            agent.clear_history()
            st.rerun()

    with col_chat:
        # Display chat history
        st.markdown("<div class='card' style='min-height: 400px; padding: 20px;'>", unsafe_allow_html=True)
        
        if not st.session_state.chat_history:
            st.markdown('''
            <div style="text-align: center; color: #64748B; margin-top: 50px;">
                <div style="font-size: 3rem;">👋</div>
                <h3>How can I help you today?</h3>
                <p>Select context from the sidebar and ask me anything about the hiring process.</p>
            </div>
            ''', unsafe_allow_html=True)
            
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chat Input
        user_input = st.chat_input("Type your message here...")
        
        # Handle Input
        prompt_to_send = user_input or clicked_prompt
        
        if prompt_to_send:
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt_to_send)
                
            st.session_state.chat_history.append({"role": "user", "content": prompt_to_send})
            
            # Build Context
            context_data = {}
            if include_resume and st.session_state.get("parsed_resume"):
                context_data["resume"] = st.session_state.parsed_resume
            if selected_job:
                context_data["job"] = selected_job
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = agent.chat(prompt_to_send, context=context_data)
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error communicating with AI: {str(e)}")
