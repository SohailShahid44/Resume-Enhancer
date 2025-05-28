import streamlit as st
from utils.extractors import extract_text_from_pdf
from utils.langchain_engine import (
    analyze_resume,
    ask_gemini,
    detect_experience_level,
    get_prebuilt_resume_content,
    update_resume_continuously,
    get_prebuilt_resumes,
    generate_resume_html,
    generate_tailored_resume,
    text_to_pdf,
    calculate_ats_score,
    generate_visual_editor,
    scrape_linkedin_jobs,
    extract_skills_from_resume,
    parse_html_resume,
    update_html_resume,
    get_public_templates,
    save_custom_template,
    get_custom_templates,
    get_template_preview,
    generate_resume_from_form,
    edit_template_content,
    apply_resume_template,
    generate_sample_resume,
    html_to_pdf,
    get_template_content
)

# Page configuration
st.set_page_config(
    page_title="Resume Enhancer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0f2f6;
    }
    .template-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        transition: all 0.2s;
    }
    .template-card:hover {
        border-color: #4a8bfc;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .template-selected {
        border: 2px solid #4a8bfc;
        background-color: #f8faff;
    }
    .template-category {
        font-size: 0.8em;
        color: #666;
        margin-top: 5px;
    }
    .template-edit-container {
        display: flex;
        gap: 20px;
    }
    .template-preview {
        flex: 1;
        border: 1px solid #eee;
        padding: 15px;
        border-radius: 8px;
        height: 500px;
        overflow-y: auto;
    }
    .template-editor {
        flex: 1;
    }
    .CodeMirror {
        height: 500px !important;
        border-radius: 8px;
        border: 1px solid #eee;
    }
    .resume-section {
        margin-bottom: 20px;
        padding: 15px;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    .hidden-button {
        display: none;
    }
    .add-experience-btn {
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .experience-level-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-left: 10px;
    }
    .fresher-badge {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    .mid-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .senior-badge {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Resume Enhancer Pro")
st.caption("AI-powered resume optimization with Gemini and LangChain")

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'visual_editor_html' not in st.session_state:
    st.session_state.visual_editor_html = ""
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": "",
        "projects": ""
    }
if 'edited_resume_html' not in st.session_state:
    st.session_state.edited_resume_html = ""
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = "professional"
if 'editing_template' not in st.session_state:
    st.session_state.editing_template = None
if 'template_content' not in st.session_state:
    st.session_state.template_content = ""
if 'experience_level' not in st.session_state:
    st.session_state.experience_level = ""

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    st.markdown("""
    - Upload your resume (PDF)
    - Paste the job description
    - Click Analyze to get started
    """)
    
    st.divider()
    st.markdown("### Features:")
    st.markdown("""
    - ATS Score Analysis
    - Resume Optimization
    - Cover Letter Generator
    - Interview Questions
    - LinkedIn Job Matching
    - Visual Resume Editor
    """)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Your Resume")
    uploaded_file = st.file_uploader("Choose PDF", type="pdf", key="resume_uploader")
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        st.session_state.resume_text = resume_text
        st.success("Resume uploaded and processed.")
        with st.expander("View Resume Text"):
            st.text(resume_text[:2000] + "..." if len(resume_text) > 2000 else resume_text)
    else:
        if st.button("Start with Sample Resume", key="sample_resume_button"):
            with st.spinner("Loading sample resume..."):
                st.session_state.resume_text = "SAMPLE RESUME CONTENT"
                st.session_state.sample_mode = True
                st.session_state.edited_resume_html = generate_sample_resume(st.session_state.selected_template)
                st.toast("Sample resume loaded!", icon="📄")

with col2:
    st.subheader("Paste Job Description")
    job_description = st.text_area("Job Description", height=300, key="job_desc_textarea")
    if job_description:
        st.session_state.job_description = job_description
        st.success("Job description received.")

# Analysis button
if st.button("✨ Analyze Resume & JD", use_container_width=True, type="primary", key="analyze_button"):
    if "resume_text" in st.session_state and "job_description" in st.session_state:
        with st.spinner("Analyzing with Gemini AI..."):
            try:
                # Run all analyses
                analysis, cover_letter, questions = analyze_resume(
                    st.session_state.resume_text,
                    st.session_state.job_description
                )

                # Calculate ATS score
                ats_score, ats_feedback = calculate_ats_score(
                    st.session_state.resume_text,
                    st.session_state.job_descriptionf
                )
                
                # Parse resume for visual editor
                tailored_resume = generate_tailored_resume(
                    st.session_state.resume_text,
                    st.session_state.job_description,
                    st.session_state.selected_template
                )
                st.session_state.resume_data = parse_html_resume(tailored_resume)
                
                # Apply selected template
                st.session_state.edited_resume_html = apply_resume_template(
                    tailored_resume,
                    st.session_state.selected_template
                )
                
                # Generate visual editor
                st.session_state.visual_editor_html = generate_visual_editor(st.session_state.resume_data)
                
                # Store all results
                st.session_state.analysis = analysis
                st.session_state.cover_letter = cover_letter
                st.session_state.questions = questions
                st.session_state.ats_score = ats_score
                st.session_state.ats_feedback = ats_feedback
                st.session_state.analysis_done = True
                
                # Detect experience level
                exp_level = detect_experience_level(st.session_state.resume_text)
                st.session_state.experience_level = exp_level
                
                st.toast("Analysis complete!", icon="✅")
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
               
    else:
        st.warning("Please upload resume and job description first")

# Display results if analysis is done
if st.session_state.get('analysis_done', False) or 'sample_mode' in st.session_state:
    st.divider()

    # ATS Score Summary (only show if not in sample mode)
    if 'analysis_done' in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.subheader("ATS Score Summary", anchor=False)
            score = st.session_state.ats_score
            if score >= 80:
                st.success(f"### {score}/100 - Excellent ATS Match")
            elif score >= 60:
                st.warning(f"### {score}/100 - Good ATS Match")
            else:
                st.error(f"### {score}/100 - Poor ATS Match")
            
            # Show experience level badge
            if st.session_state.experience_level:
                badge_class = ""
                badge_text = ""
                if st.session_state.experience_level == "fresher":
                    badge_class = "fresher-badge"
                    badge_text = "ENTRY-LEVEL"
                elif st.session_state.experience_level == "mid":
                    badge_class = "mid-badge"
                    badge_text = "MID-LEVEL"
                else:
                    badge_class = "senior-badge"
                    badge_text = "SENIOR"
                
                st.markdown(f"""
                <div style="text-align: center; margin-top: -10px;">
                    <span class="experience-level-badge {badge_class}">{badge_text}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander("Detailed ATS Feedback"):
                st.markdown(st.session_state.ats_feedback)

    # Tabs for different features
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Analysis", 
        "✉️ Cover Letter", 
        "❓ Interview Prep", 
        "🛠 Resume Builder",
        "🔍 Job Matches",
        "🎨 Visual Editor"
    ])

    with tab1:
        if 'analysis_done' in st.session_state:
            st.markdown("### Resume Analysis Report")
            st.markdown(st.session_state.analysis)
            
            st.download_button(
                "Download Analysis PDF", 
                data=text_to_pdf(st.session_state.analysis),
                file_name="resume_analysis.pdf",
                mime="application/pdf",
                key="download_analysis_pdf"
            )
        else:
            st.info("Analysis features available after analyzing a real resume")

    with tab2:
        if 'analysis_done' in st.session_state:
            st.markdown("### Generated Cover Letter")
            st.markdown(st.session_state.cover_letter)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "Download Cover Letter", 
                    data=text_to_pdf(st.session_state.cover_letter),
                    file_name="cover_letter.pdf",
                    mime="application/pdf",
                    key="download_cover_letter_pdf"
                )
            with col2:
                if st.button("Regenerate Cover Letter", key="regenerate_cover_btn"):
                    with st.spinner("Generating improved cover letter..."):
                        new_cover = ask_gemini(
                            "Improve this cover letter with more specific achievements and metrics",
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )
                        st.session_state.cover_letter = new_cover
                        st.rerun()
        else:
            st.info("Cover letter generation available after analyzing a real resume")

    with tab3:
        if 'analysis_done' in st.session_state:
            st.markdown("### Interview Preparation Questions")
            for i, q in enumerate(st.session_state.questions, 1):
                question_key = q[:20].replace(" ", "_").lower()
                st.markdown(f"{i}. **{q}**")
                
                if st.button(f"Get sample answer for question {i}", key=f"answer_{i}_{question_key}"):
                    with st.spinner("Generating sample answer..."):
                        answer = ask_gemini(
                            f"Provide a strong answer to this interview question: {q}",
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )
                        st.markdown(f"**Sample Answer:**\n\n{answer}")
            
            st.download_button(
                "Download Questions", 
                data=text_to_pdf("\n".join(st.session_state.questions)),
                file_name="interview_questions.pdf",
                mime="application/pdf",
                key="download_questions_pdf"
            )
            
            st.markdown("---")
            st.markdown("### Ask Your Own Question")
            user_question = st.text_input("Enter your question for the AI assistant", key="user_question_input")
            if st.button("Ask AI", key="ask_ai_button"):
                if user_question:
                    with st.spinner("Generating response..."):
                        answer = ask_gemini(
                            user_question,
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )
                        st.markdown(f"**AI Response:**\n\n{answer}")
        else:
            st.info("Interview preparation available after analyzing a real resume")

    with tab4:
        st.markdown("### AI-Optimized Resume Builder")
        
        # Template selection
        st.markdown("#### Select Template")
        
        # Get available templates (system + user's custom)
        system_templates = get_public_templates()
        user_id = "user_" + str(hash(st.experimental_user.email)) if st.experimental_user.email else "anonymous"
        custom_templates = get_custom_templates(user_id)
        all_templates = system_templates + custom_templates
        
        # Display as cards in 3 columns
       # In your tab4 (Resume Builder) section, modify the template selection code:

# Display as cards in 3 columns
        cols = st.columns(3)
        for idx, template in enumerate(all_templates):
            with cols[idx % 3]:
                is_selected = st.session_state.get('selected_template', '') == template['id']
                st.markdown(f"""
                <div class="template-card {'template-selected' if is_selected else ''}" 
                    onclick="window.parent.document.getElementById('select_template_{template['id']}_{idx}').click()">
                    <h4>{template['name']}</h4>
                    <p style="font-size:0.8em">{template['description']}</p>
                    <p class="template-category">{template.get('category', 'system').capitalize()}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create hidden button container
                if st.button(f"Select {template['name']}", 
                            key=f"select_template_{template['id']}_{idx}",
                            # Add this to hide the button visually but keep it functional
                            help=f"Select {template['name']} template",
                            type="primary" if is_selected else "secondary"):
                    st.session_state.selected_template = template['id']
                    # Immediately generate resume with new template
                    if "resume_text" in st.session_state and "job_description" in st.session_state:
                        with st.spinner(f"Generating resume with {template['name']} template..."):
                            try:
                                tailored_resume = generate_tailored_resume(
                                    st.session_state.resume_text,
                                    st.session_state.job_description,
                                    template['id']
                                )
                                st.session_state.edited_resume_html = tailored_resume
                                st.session_state.resume_data = parse_html_resume(tailored_resume)
                                st.toast(f"Resume generated with {template['name']} template!", icon="✅")
                            except Exception as e:
                                st.error(f"Error generating resume: {str(e)}")
                    st.rerun()
                    
            
        # Generate tailored resume button
        if st.button("✨ Generate Tailored Resume", use_container_width=True, type="primary", key="generate_resume_button"):
            if "resume_text" in st.session_state and "job_description" in st.session_state:
                with st.spinner("Creating ATS-optimized resume..."):
                    try:
                        # Generate with the selected template
                        tailored_resume = generate_tailored_resume(
                            st.session_state.resume_text,
                            st.session_state.job_description,
                            st.session_state.get('selected_template', 'professional')  # Default to professional if none selected
                        )
                        
                        # Store the generated resume
                        st.session_state.tailored_resume = tailored_resume
                        st.session_state.edited_resume_html = tailored_resume
                        st.session_state.resume_data = parse_html_resume(tailored_resume)
                        
                        st.toast("Resume generated successfully!", icon="✅")
                    except Exception as e:
                        st.error(f"Error generating resume: {str(e)}")
            else:
                st.warning("Please upload resume and job description first")
        
        # Display the generated resume
        if "edited_resume_html" in st.session_state:
            st.markdown("#### Preview:")
            st.components.v1.html(st.session_state.edited_resume_html, height=600, scrolling=True)
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                pdf_bytes = html_to_pdf(st.session_state.edited_resume_html)
                st.download_button(
                    "Download Resume (PDF)", 
                    data=pdf_bytes,
                    file_name=f"optimized_resume_{st.session_state.get('selected_template', '')}.pdf",
                    mime="application/pdf",
                    key="download_resume_pdf"
                )
            with col2:
                st.download_button(
                    "Download Resume (HTML)", 
                    data=st.session_state.edited_resume_html,
                    file_name=f"resume_{st.session_state.get('selected_template', '')}.html",
                    mime="text/html",
                    key="download_resume_html"
                )

    with tab5:
        if 'analysis_done' in st.session_state:
            st.markdown("### LinkedIn Job Matches")
            location = st.text_input("Preferred Location (optional)", key="job_location_input")
            
            if st.button("Find Matching Jobs", key="find_jobs_button"):
                with st.spinner("Searching LinkedIn for matching jobs..."):
                    try:
                        skills = extract_skills_from_resume(st.session_state.resume_text)
                        if skills:
                            jobs = scrape_linkedin_jobs(skills, location)
                            st.session_state.linkedin_jobs = jobs
                            st.toast(f"Found {len(jobs)} matching jobs!", icon="🔍")
                        else:
                            st.warning("No skills found in resume")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            if "linkedin_jobs" in st.session_state:
                st.markdown(f"#### Found {len(st.session_state.linkedin_jobs)} Matching Jobs")
                
                for i, job in enumerate(st.session_state.linkedin_jobs, 1):
                    company_key = job['company'][:10].replace(" ", "_").lower()
                    with st.expander(f"{i}. {job['title']} at {job['company']} ({job['match_percentage']}% match)"):
                        st.markdown(f"""
                        **Company:** {job['company']}  
                        **Location:** {job['location']}  
                        **Match Score:** {job['match_percentage']}%  
                        **Skills Matched:** {job['skill_matches']}  
                        **Apply:** [LinkedIn Job Page]({job['url']})
                        """)
                        
                        if st.button(f"Generate Cover Letter for {job['company']}", key=f"job_cover_{i}_{company_key}"):
                            with st.spinner("Creating tailored cover letter..."):
                                prompt = f"""
                                Write a compelling cover letter for the {job['title']} position at {job['company']}.
                                Highlight my relevant skills and experience for this role.
                                """
                                cover_letter = ask_gemini(
                                    prompt,
                                    st.session_state.resume_text,
                                    ""
                                )
                                st.session_state[f"job_cover_{i}"] = cover_letter
                        
                        if f"job_cover_{i}" in st.session_state:
                            st.markdown(st.session_state[f"job_cover_{i}"])
                            st.download_button(
                                f"Download Cover Letter for {job['company']}",
                                data=text_to_pdf(st.session_state[f"job_cover_{i}"]),
                                file_name=f"cover_letter_{job['company']}.pdf",
                                mime="application/pdf",
                                key=f"download_cover_{i}_{company_key}"
                            )
        else:
            st.info("Job matching available after analyzing a real resume")

    with tab6:
        st.markdown("### Visual Resume Editor")
        st.markdown("Edit your resume using the interactive form below:")

        # Initialize session state if not exists
        if 'visual_editor_html' not in st.session_state:
            st.session_state.visual_editor_html = ""
        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = {
                "name": "",
                "email": "",
                "phone": "",
                "linkedin": "",
                "summary": "",
                "skills": [],
                "experience": [],
                "education": "",
                "projects": ""
            }

        if st.session_state.visual_editor_html or 'sample_mode' in st.session_state:
            # Display the visual editor
            visual_editor = st.components.v1.html(
                st.session_state.visual_editor_html if 'visual_editor_html' in st.session_state else "",
                height=1000,
                scrolling=True
            )

            # JavaScript to handle messages from the iframe
            js_code = """
            <script>
            // Listen for messages from the iframe
            window.addEventListener('message', function(event) {
                // Only accept messages from our iframe
                if (event.origin !== window.location.origin) return;
                
                if (event.data.type === 'UPDATE_RESUME') {
                    // Store the data in session storage
                    sessionStorage.setItem('resumeData', JSON.stringify(event.data.data));
                    
                    // Send the data to Streamlit
                    const data = JSON.stringify(event.data.data);
                    const command = `st.session_state.new_resume_data = ${data}`;
                    const script = document.createElement('script');
                    script.innerHTML = command;
                    document.head.appendChild(script);
                    script.remove();
                    
                    // Trigger a rerun
                    const iframes = document.getElementsByTagName('iframe');
                    if (iframes.length > 0) {
                        iframes[0].contentWindow.postMessage({
                            type: 'RESUME_DATA_UPDATED'
                        }, '*');
                    }
                }
            });

            // Initialize with any existing data
            window.addEventListener('load', function() {
                const resumeData = sessionStorage.getItem('resumeData');
                if (resumeData) {
                    const iframes = document.getElementsByTagName('iframe');
                    if (iframes.length > 0) {
                        iframes[0].contentWindow.postMessage({
                            type: 'INIT_RESUME_DATA',
                            data: JSON.parse(resumeData)
                        }, '*');
                    }
                }
            });
            </script>
            """
            st.components.v1.html(js_code, height=0)

            # Listen for updates from the visual editor
            if 'resume_data' in st.session_state:
                try:
                    # Check for updated data from the visual editor
                    if 'new_resume_data' in st.session_state:
                        st.session_state.resume_data = st.session_state.new_resume_data
                        del st.session_state.new_resume_data
                    
                    # Generate updated HTML with the current template
                    updated_html = update_resume_continuously(
                        st.session_state.resume_data,
                        st.session_state.selected_template
                    )
                    st.session_state.edited_resume_html = updated_html
                    
                    # Show live preview
                    st.markdown("### Live Resume Preview")
                    st.components.v1.html(
                        st.session_state.edited_resume_html,
                        height=600,
                        scrolling=True
                    )
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        pdf_bytes = html_to_pdf(st.session_state.edited_resume_html)
                        st.download_button(
                            "Download Edited Resume (PDF)",
                            data=pdf_bytes,
                            file_name="edited_resume.pdf",
                            mime="application/pdf",
                            key="download_edited_pdf"
                        )
                    with col2:
                        st.download_button(
                            "Download Edited Resume (HTML)",
                            data=st.session_state.edited_resume_html,
                            file_name="resume.html",
                            mime="text/html",
                            key="download_edited_html"
                        )
                    
                except Exception as e:
                    st.error(f"Error updating resume: {str(e)}")
                    st.error("Please try analyzing your resume again or contact support.")
        else:
            st.warning("Please analyze your resume first to enable the visual editor")
            
            if st.button("Generate Sample Editor", key="sample_editor_button"):
                with st.spinner("Creating sample editor..."):
                    st.session_state.visual_editor_html = generate_visual_editor({
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "(123) 456-7890",
                        "linkedin": "linkedin.com/in/johndoe",
                        "summary": "Experienced software engineer with 5+ years in web development",
                        "skills": ["Python", "JavaScript", "React", "Node.js"],
                        "experience": [{
                            "title": "Senior Developer",
                            "company": "Tech Corp",
                            "duration": "2020-Present",
                            "description": "Led team of 5 developers\nImproved performance by 40%"
                        }],
                        "education": "BS in Computer Science, University of Tech",
                        "projects": "Built resume builder app\nCreated AI chatbot"
                    })
                    st.session_state.sample_mode = True
                    st.rerun()
                    
   
st.divider()
st.caption("""
🚀 Powered by Gemini AI and LangChain |
[Report Issues](https://github.com/your-repo/issues) |
[How It Works](https://github.com/your-repo/wiki)
""")