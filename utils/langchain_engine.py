import os
import time
from fpdf import FPDF
import io
import unicodedata
import requests
import json
from typing import Dict
from bs4 import BeautifulSoup
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from google.api_core.exceptions import ResourceExhausted
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Set API keys
os.environ["GOOGLE_API_KEY"] = "AIzaSyAJqExbErV1CGz9k5ySpmKkmiYz8sBP1dI"

# Models
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Template storage (in a real app, use a database)
TEMPLATE_STORAGE = {
    "fresher": {
        "name": "Fresher Template",
        "description": "Template for entry-level candidates (0-1 years experience)",
        "content": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resume</title>
            <style>
                body { 
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: white;
                    color: #333;
                }
                .header { 
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #3f51b5;
                    padding-bottom: 15px;
                }
                .name {
                    font-size: 28px;
                    font-weight: bold;
                    color: #3f51b5;
                    margin-bottom: 5px;
                }
                .contact-info {
                    font-size: 14px;
                    color: #666;
                }
                .section {
                    margin-bottom: 20px;
                }
                .section-title {
                    font-weight: bold;
                    font-size: 18px;
                    color: #3f51b5;
                    border-bottom: 1px solid #e0e0e0;
                    padding-bottom: 5px;
                    margin-bottom: 10px;
                }
                .skills {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 10px;
                }
                .skill-tag {
                    background: #e8eaf6;
                    padding: 4px 10px;
                    border-radius: 15px;
                    font-size: 14px;
                    color: #3f51b5;
                }
                ul {
                    padding-left: 20px;
                }
                li {
                    margin-bottom: 5px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">Your Name</div>
                <div class="contact-info">
                    your.email@example.com | (123) 456-7890 | linkedin.com/in/yourprofile
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Summary</h2>
                <p>Recent graduate with strong academic background in Computer Science seeking an entry-level software engineering position. Passionate about coding and eager to apply classroom knowledge to real-world projects.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p><strong>Bachelor of Science in Computer Science</strong></p>
                <p>University Name, Graduation Year</p>
                <p>GPA: 3.5/4.0</p>
                <p>Relevant Coursework: Data Structures, Algorithms, Database Systems, Web Development</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills">
                    <span class="skill-tag">Python</span>
                    <span class="skill-tag">Java</span>
                    <span class="skill-tag">JavaScript</span>
                    <span class="skill-tag">HTML/CSS</span>
                    <span class="skill-tag">SQL</span>
                    <span class="skill-tag">Git</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Projects</h2>
                <p><strong>E-commerce Website</strong></p>
                <ul>
                    <li>Developed a full-stack e-commerce platform using React and Node.js</li>
                    <li>Implemented user authentication and product search functionality</li>
                    <li>Deployed using AWS EC2 and S3</li>
                </ul>
                
                <p><strong>Student Management System</strong></p>
                <ul>
                    <li>Created a Java application to manage student records</li>
                    <li>Used MySQL for database storage</li>
                    <li>Implemented CRUD operations with a GUI interface</li>
                </ul>
            </div>
        </body>
        </html>
        """
    },
    "intermediate": {
        "name": "Intermediate Template",
        "description": "Template for mid-level candidates (1-3 years experience)",
        "content": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resume</title>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    background-color: white;
                    margin: 0 auto;
                    padding: 20px;
                    color: #444;
                }
                .header { 
                    background-color: #3498db;
                    color: white;
                    padding: 20px;
                    margin-bottom: 25px;
                    border-radius: 5px;
                }
                .name {
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .contact-info {
                    font-size: 15px;
                    opacity: 0.9;
                }
                .section { 
                    margin-bottom: 25px;
                    background-color: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .section-title { 
                    font-weight: bold;
                    font-size: 20px;
                    color: #3498db;
                    margin-bottom: 15px;
                    padding-bottom: 5px;
                    border-bottom: 2px solid #3498db;
                }
                .job-header { 
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }
                .job-title {
                    font-weight: bold;
                    font-size: 17px;
                    color: #2c3e50;
                }
                .company {
                    color: #3498db;
                }
                .job-duration {
                    color: #7f8c8d;
                }
                .skills { 
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-top: 15px;
                }
                .skill-tag { 
                    background: #3498db;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 14px;
                }
                ul {
                    padding-left: 25px;
                }
                li {
                    margin-bottom: 8px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">Your Name</div>
                <div class="contact-info">
                    your.email@example.com | (123) 456-7890 | linkedin.com/in/yourprofile
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Summary</h2>
                <p>Software Engineer with 2 years of experience developing web applications. Skilled in full-stack development with expertise in JavaScript frameworks. Passionate about creating efficient, scalable solutions and collaborating with cross-functional teams.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Experience</h2>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Software Engineer</span>
                            <span class="company">, Tech Company Inc.</span>
                        </div>
                        <span class="job-duration">Jan 2021 - Present</span>
                    </div>
                    <ul>
                        <li>Developed and maintained React front-end for customer portal</li>
                        <li>Created RESTful APIs using Node.js and Express</li>
                        <li>Improved application performance by 30% through code optimization</li>
                        <li>Collaborated with UX team to implement responsive designs</li>
                    </ul>
                </div>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Junior Developer</span>
                            <span class="company">, Startup Solutions</span>
                        </div>
                        <span class="job-duration">Jun 2020 - Dec 2020</span>
                    </div>
                    <ul>
                        <li>Assisted in development of internal tools using Python</li>
                        <li>Fixed bugs and implemented new features for legacy systems</li>
                        <li>Participated in code reviews and team meetings</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills">
                    <span class="skill-tag">JavaScript</span>
                    <span class="skill-tag">React</span>
                    <span class="skill-tag">Node.js</span>
                    <span class="skill-tag">Python</span>
                    <span class="skill-tag">SQL</span>
                    <span class="skill-tag">Git</span>
                    <span class="skill-tag">AWS</span>
                    <span class="skill-tag">Docker</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p><strong>Bachelor of Science in Computer Science</strong></p>
                <p>University Name, 2020</p>
            </div>
        </body>
        </html>
        """
    },
    "experienced": {
        "name": "Experienced Template",
        "description": "Template for senior candidates (4+ years experience)",
        "content": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resume</title>
            <style>
                body { 
                    font-family: 'Times New Roman', serif;
                    line-height: 1.7;
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    color: #000;
                }
                .header { 
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px double #000;
                }
                .name {
                    font-size: 32px;
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                    letter-spacing: 2px;
                }
                .contact-info {
                    font-size: 16px;
                    color: #555;
                    letter-spacing: 1px;
                }
                .section { 
                    margin-bottom: 30px;
                }
                .section-title { 
                    font-weight: bold;
                    font-size: 22px;
                    color: #000;
                    margin-bottom: 15px;
                    letter-spacing: 1px;
                    border-bottom: 1px solid #000;
                }
                .job-header { 
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                }
                .job-title {
                    font-weight: bold;
                    font-size: 18px;
                    color: #000;
                }
                .company {
                    font-style: italic;
                }
                .job-duration {
                    color: #666;
                    font-size: 15px;
                }
                .skills { 
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-top: 20px;
                }
                .skill-tag { 
                    background: #f5f5f5;
                    color: #000;
                    padding: 6px 15px;
                    border-radius: 25px;
                    font-size: 14px;
                    border: 1px solid #ddd;
                }
                ul {
                    padding-left: 30px;
                }
                li {
                    margin-bottom: 10px;
                    position: relative;
                }
                li:before {
                    content: "•";
                    color: #000;
                    font-size: 20px;
                    position: absolute;
                    left: -15px;
                    top: -2px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">Your Name</div>
                <div class="contact-info">
                    your.email@example.com | (123) 456-7890 | linkedin.com/in/yourprofile
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Professional Summary</h2>
                <p>Senior Software Engineer with 7+ years of experience leading development teams and architecting scalable systems. Proven track record of delivering complex projects on time while maintaining high code quality. Strong expertise in cloud technologies and microservices architecture.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Professional Experience</h2>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Senior Software Engineer</span>
                            <span class="company">, Enterprise Tech Solutions</span>
                        </div>
                        <span class="job-duration">Jan 2019 - Present</span>
                    </div>
                    <ul>
                        <li>Led a team of 5 developers in building a distributed microservices platform</li>
                        <li>Architected and implemented CI/CD pipeline reducing deployment time by 40%</li>
                        <li>Mentored junior developers and conducted code reviews</li>
                        <li>Collaborated with product managers to define technical requirements</li>
                    </ul>
                </div>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Software Engineer</span>
                            <span class="company">, Tech Innovations Inc.</span>
                        </div>
                        <span class="job-duration">Mar 2016 - Dec 2018</span>
                    </div>
                    <ul>
                        <li>Developed core features for flagship product using Java and Spring Boot</li>
                        <li>Optimized database queries improving performance by 25%</li>
                        <li>Implemented automated testing framework reducing bugs by 30%</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Technical Skills</h2>
                <div class="skills">
                    <span class="skill-tag">Java</span>
                    <span class="skill-tag">Spring Boot</span>
                    <span class="skill-tag">Microservices</span>
                    <span class="skill-tag">AWS</span>
                    <span class="skill-tag">Kubernetes</span>
                    <span class="skill-tag">Docker</span>
                    <span class="skill-tag">CI/CD</span>
                    <span class="skill-tag">SQL</span>
                    <span class="skill-tag">NoSQL</span>
                    <span class="skill-tag">Agile Methodologies</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p><strong>Master of Science in Computer Science</strong></p>
                <p>University Name, 2016</p>
            </div>
        </body>
        </html>
        """
    }
}

def get_template_content(template_id: str) -> str:
    """Get the HTML content of a specific template"""
    return TEMPLATE_STORAGE.get(template_id, {}).get("content", "")

def save_template_content(template_id: str, content: str) -> bool:
    """Save the modified template content"""
    if template_id in TEMPLATE_STORAGE:
        TEMPLATE_STORAGE[template_id]["content"] = content
        return True
    return False

def build_vector_store(text: str, index_name: str = "faiss_store"):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents([text])
    vectordb = FAISS.from_documents(docs, embedding_model)
    vectordb.save_local(index_name)
    return vectordb

def load_vector_store(index_name: str = "faiss_store"):
    return FAISS.load_local(index_name, embedding_model, allow_dangerous_deserialization=True)

def extract_skills_from_resume(resume_text: str) -> List[str]:
    try:
        skill_prompt = PromptTemplate.from_template("""
        Extract the top 10 most important technical skills from this resume.
        Focus on programming languages, frameworks, tools, and technologies.
        Return only a comma-separated list, no explanations.
        
        Resume:
        {resume}
        
        Skills:
        """)
        
        skill_chain = LLMChain(llm=llm, prompt=skill_prompt)
        skills = skill_chain.run(resume=resume_text)
        return [skill.strip().lower() for skill in skills.split(",") if skill.strip()][:10]
    except Exception as e:
        print(f"Error extracting skills: {str(e)}")
        return []

def scrape_linkedin_jobs(skills: List[str], location: str = "") -> List[Dict]:
    try:
        if not skills:
            return []

        primary_skills = skills[:3]
        skills_query = "%20".join(primary_skills)
        location_param = f"&location={location.replace(' ', '%20')}" if location else ""
        
        url = f"https://www.linkedin.com/jobs/search/?keywords={skills_query}{location_param}&position=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        for job in soup.find_all("div", class_="base-card")[:15]:
            try:
                title = job.find("h3", class_="base-search-card__title").text.strip()
                company = job.find("h4", class_="base-search-card__subtitle").text.strip()
                job_location = job.find("span", class_="job-search-card__location").text.strip()
                url = job.find("a", class_="base-card__full-link")["href"].split("?")[0]
                
                if location and location.lower() not in job_location.lower():
                    continue
                
                job_page = requests.get(url, headers=headers, timeout=5)
                job_soup = BeautifulSoup(job_page.text, 'html.parser')
                description = job_soup.find("div", class_="description__text").get_text().lower() if job_soup.find("div", class_="description__text") else ""
                
                skill_matches = sum(1 for skill in skills if skill.lower() in description)
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "url": url,
                    "skill_matches": skill_matches,
                    "match_percentage": int((skill_matches / len(skills)) * 100 ) if skills else 0
                })
            except Exception:
                continue
        
        return sorted(jobs, key=lambda x: (-x['skill_matches'], x['title']))[:10]
    except Exception as e:
        print(f"Error scraping LinkedIn: {str(e)}")
        return []

def ask_gemini(question: str, resume: str, job_description: str) -> str:
    qna_prompt = PromptTemplate.from_template("""
    You are an interview preparation assistant. Answer the following question from a candidate based on their resume and the job description.

    Resume:
    {resume}

    Job Description:
    {jd}

    Question:
    {question}

    Answer in a professional and helpful tone.
    """)

    qna_chain = LLMChain(llm=llm, prompt=qna_prompt)

    for _attempt in range(3):
        try:
            return qna_chain.run(resume=resume, jd=job_description, question=question)
        except ResourceExhausted:
            time.sleep(15)
        except Exception as e:
            return f"⚠️ Gemini API Error: {str(e)}"

    return "⚠️ Gemini API is currently rate-limited. Please try again later."

def analyze_resume(resume_text: str, job_description: str):
    try:
        build_vector_store(resume_text, "faiss_resume")
        build_vector_store(job_description, "faiss_jd")

        resume_db = load_vector_store("faiss_resume")
        jd_db = load_vector_store("faiss_jd")

        resume_summary = " ".join([doc.page_content for doc in resume_db.similarity_search("Summarize this resume", k=3)])
        jd_summary = " ".join([doc.page_content for doc in jd_db.similarity_search("Summarize this job description", k=3)])

        analysis_prompt = PromptTemplate.from_template("""
        ### Resume Analysis
        Compare the following resume and job description:

        Resume:
        {resume}

        Job Description:
        {jd}

        Provide insights:
        - Strengths
        - Weaknesses and improvements
        - Missing keywords
        - Top 5 recommendations
        """)

        cover_letter_prompt = PromptTemplate.from_template("""
        Write a professional cover letter for this resume and job description.

        Resume:
        {resume}

        Job Description:
        {jd}
        """)

        interview_prompt = PromptTemplate.from_template("""
        Generate 10 interview questions based on this resume and job description.

        Resume:
        {resume}

        Job Description:
        {jd}
        """)

        analysis = LLMChain(llm=llm, prompt=analysis_prompt).run(resume=resume_summary, jd=jd_summary)
        cover_letter = LLMChain(llm=llm, prompt=cover_letter_prompt).run(resume=resume_summary, jd=jd_summary)
        questions = [q.strip() for q in LLMChain(llm=llm, prompt=interview_prompt).run(resume=resume_summary, jd=jd_summary).split('\n') if q.strip()]
        
        return analysis, cover_letter, questions
    except Exception as e:
        raise Exception(f"Error in analyze_resume: {str(e)}")

def calculate_ats_score(resume_text: str, job_description: str) -> tuple[int, str]:
    try:
        ats_prompt = PromptTemplate.from_template("""
        Analyze this resume against the job description and calculate an ATS score (0-100).
        Consider keyword matching, skills alignment, experience relevance, education, format, and customization.

        Resume:
        {resume}

        Job Description:
        {jd}

        Return response in format:
        SCORE: [number]
        FEEDBACK: [multiline feedback]
        """)

        response = LLMChain(llm=llm, prompt=ats_prompt).run(resume=resume_text, jd=job_description)
        score = int(response.split("SCORE:")[1].split()[0].strip()) if "SCORE:" in response else 0
        feedback = response.split("FEEDBACK:")[1].strip() if "FEEDBACK:" in response else ""
        return score, feedback
    except Exception as e:
        print(f"Error calculating ATS score: {str(e)}")
        return 0, f"Could not calculate ATS score: {str(e)}"


import os
import time
from fpdf import FPDF
import io
import unicodedata
import requests
import json
from typing import Dict
from bs4 import BeautifulSoup
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from google.api_core.exceptions import ResourceExhausted
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Set API keys
os.environ["GOOGLE_API_KEY"] = "AIzaSyAJqExbErV1CGz9k5ySpmKkmiYz8sBP1dI"

# Models
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Template storage (in a real app, use a database)
TEMPLATE_STORAGE = {
    "fresher": {
        "name": "Fresher Template",
        "description": "Template for entry-level candidates (0-1 years experience)",
        "content": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resume</title>
            <style>
                body { 
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: white;
                    color: #333;
                }
                .header { 
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #3f51b5;
                    padding-bottom: 15px;
                }
                .name {
                    font-size: 28px;
                    font-weight: bold;
                    color: #3f51b5;
                    margin-bottom: 5px;
                }
                .contact-info {
                    font-size: 14px;
                    color: #666;
                }
                .section {
                    margin-bottom: 20px;
                }
                .section-title {
                    font-weight: bold;
                    font-size: 18px;
                    color: #3f51b5;
                    border-bottom: 1px solid #e0e0e0;
                    padding-bottom: 5px;
                    margin-bottom: 10px;
                }
                .skills {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 10px;
                }
                .skill-tag {
                    background: #e8eaf6;
                    padding: 4px 10px;
                    border-radius: 15px;
                    font-size: 14px;
                    color: #3f51b5;
                }
                ul {
                    padding-left: 20px;
                }
                li {
                    margin-bottom: 5px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">Your Name</div>
                <div class="contact-info">
                    your.email@example.com | (123) 456-7890 | linkedin.com/in/yourprofile
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Summary</h2>
                <p>Recent graduate with strong academic background in Computer Science seeking an entry-level software engineering position. Passionate about coding and eager to apply classroom knowledge to real-world projects.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p><strong>Bachelor of Science in Computer Science</strong></p>
                <p>University Name, Graduation Year</p>
                <p>GPA: 3.5/4.0</p>
                <p>Relevant Coursework: Data Structures, Algorithms, Database Systems, Web Development</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills">
                    <span class="skill-tag">Python</span>
                    <span class="skill-tag">Java</span>
                    <span class="skill-tag">JavaScript</span>
                    <span class="skill-tag">HTML/CSS</span>
                    <span class="skill-tag">SQL</span>
                    <span class="skill-tag">Git</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Projects</h2>
                <p><strong>E-commerce Website</strong></p>
                <ul>
                    <li>Developed a full-stack e-commerce platform using React and Node.js</li>
                    <li>Implemented user authentication and product search functionality</li>
                    <li>Deployed using AWS EC2 and S3</li>
                </ul>
                
                <p><strong>Student Management System</strong></p>
                <ul>
                    <li>Created a Java application to manage student records</li>
                    <li>Used MySQL for database storage</li>
                    <li>Implemented CRUD operations with a GUI interface</li>
                </ul>
            </div>
        </body>
        </html>
        """
    },
    "intermediate": {
        "name": "Intermediate Template",
        "description": "Template for mid-level candidates (1-3 years experience)",
        "content": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resume</title>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    background-color: white;
                    margin: 0 auto;
                    padding: 20px;
                    color: #444;
                }
                .header { 
                    background-color: #3498db;
                    color: white;
                    padding: 20px;
                    margin-bottom: 25px;
                    border-radius: 5px;
                }
                .name {
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .contact-info {
                    font-size: 15px;
                    opacity: 0.9;
                }
                .section { 
                    margin-bottom: 25px;
                    background-color: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .section-title { 
                    font-weight: bold;
                    font-size: 20px;
                    color: #3498db;
                    margin-bottom: 15px;
                    padding-bottom: 5px;
                    border-bottom: 2px solid #3498db;
                }
                .job-header { 
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }
                .job-title {
                    font-weight: bold;
                    font-size: 17px;
                    color: #2c3e50;
                }
                .company {
                    color: #3498db;
                }
                .job-duration {
                    color: #7f8c8d;
                }
                .skills { 
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-top: 15px;
                }
                .skill-tag { 
                    background: #3498db;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 14px;
                }
                ul {
                    padding-left: 25px;
                }
                li {
                    margin-bottom: 8px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">Your Name</div>
                <div class="contact-info">
                    your.email@example.com | (123) 456-7890 | linkedin.com/in/yourprofile
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Summary</h2>
                <p>Software Engineer with 2 years of experience developing web applications. Skilled in full-stack development with expertise in JavaScript frameworks. Passionate about creating efficient, scalable solutions and collaborating with cross-functional teams.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Experience</h2>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Software Engineer</span>
                            <span class="company">, Tech Company Inc.</span>
                        </div>
                        <span class="job-duration">Jan 2021 - Present</span>
                    </div>
                    <ul>
                        <li>Developed and maintained React front-end for customer portal</li>
                        <li>Created RESTful APIs using Node.js and Express</li>
                        <li>Improved application performance by 30% through code optimization</li>
                        <li>Collaborated with UX team to implement responsive designs</li>
                    </ul>
                </div>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Junior Developer</span>
                            <span class="company">, Startup Solutions</span>
                        </div>
                        <span class="job-duration">Jun 2020 - Dec 2020</span>
                    </div>
                    <ul>
                        <li>Assisted in development of internal tools using Python</li>
                        <li>Fixed bugs and implemented new features for legacy systems</li>
                        <li>Participated in code reviews and team meetings</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills">
                    <span class="skill-tag">JavaScript</span>
                    <span class="skill-tag">React</span>
                    <span class="skill-tag">Node.js</span>
                    <span class="skill-tag">Python</span>
                    <span class="skill-tag">SQL</span>
                    <span class="skill-tag">Git</span>
                    <span class="skill-tag">AWS</span>
                    <span class="skill-tag">Docker</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p><strong>Bachelor of Science in Computer Science</strong></p>
                <p>University Name, 2020</p>
            </div>
        </body>
        </html>
        """
    },
    "experienced": {
        "name": "Experienced Template",
        "description": "Template for senior candidates (4+ years experience)",
        "content": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resume</title>
            <style>
                body { 
                    font-family: 'Times New Roman', serif;
                    line-height: 1.7;
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    color: #000;
                }
                .header { 
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px double #000;
                }
                .name {
                    font-size: 32px;
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                    letter-spacing: 2px;
                }
                .contact-info {
                    font-size: 16px;
                    color: #555;
                    letter-spacing: 1px;
                }
                .section { 
                    margin-bottom: 30px;
                }
                .section-title { 
                    font-weight: bold;
                    font-size: 22px;
                    color: #000;
                    margin-bottom: 15px;
                    letter-spacing: 1px;
                    border-bottom: 1px solid #000;
                }
                .job-header { 
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                }
                .job-title {
                    font-weight: bold;
                    font-size: 18px;
                    color: #000;
                }
                .company {
                    font-style: italic;
                }
                .job-duration {
                    color: #666;
                    font-size: 15px;
                }
                .skills { 
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-top: 20px;
                }
                .skill-tag { 
                    background: #f5f5f5;
                    color: #000;
                    padding: 6px 15px;
                    border-radius: 25px;
                    font-size: 14px;
                    border: 1px solid #ddd;
                }
                ul {
                    padding-left: 30px;
                }
                li {
                    margin-bottom: 10px;
                    position: relative;
                }
                li:before {
                    content: "•";
                    color: #000;
                    font-size: 20px;
                    position: absolute;
                    left: -15px;
                    top: -2px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">Your Name</div>
                <div class="contact-info">
                    your.email@example.com | (123) 456-7890 | linkedin.com/in/yourprofile
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Professional Summary</h2>
                <p>Senior Software Engineer with 7+ years of experience leading development teams and architecting scalable systems. Proven track record of delivering complex projects on time while maintaining high code quality. Strong expertise in cloud technologies and microservices architecture.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Professional Experience</h2>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Senior Software Engineer</span>
                            <span class="company">, Enterprise Tech Solutions</span>
                        </div>
                        <span class="job-duration">Jan 2019 - Present</span>
                    </div>
                    <ul>
                        <li>Led a team of 5 developers in building a distributed microservices platform</li>
                        <li>Architected and implemented CI/CD pipeline reducing deployment time by 40%</li>
                        <li>Mentored junior developers and conducted code reviews</li>
                        <li>Collaborated with product managers to define technical requirements</li>
                    </ul>
                </div>
                
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">Software Engineer</span>
                            <span class="company">, Tech Innovations Inc.</span>
                        </div>
                        <span class="job-duration">Mar 2016 - Dec 2018</span>
                    </div>
                    <ul>
                        <li>Developed core features for flagship product using Java and Spring Boot</li>
                        <li>Optimized database queries improving performance by 25%</li>
                        <li>Implemented automated testing framework reducing bugs by 30%</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Technical Skills</h2>
                <div class="skills">
                    <span class="skill-tag">Java</span>
                    <span class="skill-tag">Spring Boot</span>
                    <span class="skill-tag">Microservices</span>
                    <span class="skill-tag">AWS</span>
                    <span class="skill-tag">Kubernetes</span>
                    <span class="skill-tag">Docker</span>
                    <span class="skill-tag">CI/CD</span>
                    <span class="skill-tag">SQL</span>
                    <span class="skill-tag">NoSQL</span>
                    <span class="skill-tag">Agile Methodologies</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p><strong>Master of Science in Computer Science</strong></p>
                <p>University Name, 2016</p>
            </div>
        </body>
        </html>
        """
    }
}

def get_template_content(template_id: str) -> str:
    """Get the HTML content of a specific template"""
    return TEMPLATE_STORAGE.get(template_id, {}).get("content", "")

def save_template_content(template_id: str, content: str) -> bool:
    """Save the modified template content"""
    if template_id in TEMPLATE_STORAGE:
        TEMPLATE_STORAGE[template_id]["content"] = content
        return True
    return False

def build_vector_store(text: str, index_name: str = "faiss_store"):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents([text])
    vectordb = FAISS.from_documents(docs, embedding_model)
    vectordb.save_local(index_name)
    return vectordb

def load_vector_store(index_name: str = "faiss_store"):
    return FAISS.load_local(index_name, embedding_model, allow_dangerous_deserialization=True)

def extract_skills_from_resume(resume_text: str) -> List[str]:
    try:
        skill_prompt = PromptTemplate.from_template("""
        Extract the top 10 most important technical skills from this resume.
        Focus on programming languages, frameworks, tools, and technologies.
        Return only a comma-separated list, no explanations.
        
        Resume:
        {resume}
        
        Skills:
        """)
        
        skill_chain = LLMChain(llm=llm, prompt=skill_prompt)
        skills = skill_chain.run(resume=resume_text)
        return [skill.strip().lower() for skill in skills.split(",") if skill.strip()][:10]
    except Exception as e:
        print(f"Error extracting skills: {str(e)}")
        return []

def scrape_linkedin_jobs(skills: List[str], location: str = "") -> List[Dict]:
    try:
        if not skills:
            return []

        primary_skills = skills[:3]
        skills_query = "%20".join(primary_skills)
        location_param = f"&location={location.replace(' ', '%20')}" if location else ""
        
        url = f"https://www.linkedin.com/jobs/search/?keywords={skills_query}{location_param}&position=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        for job in soup.find_all("div", class_="base-card")[:15]:
            try:
                title = job.find("h3", class_="base-search-card__title").text.strip()
                company = job.find("h4", class_="base-search-card__subtitle").text.strip()
                job_location = job.find("span", class_="job-search-card__location").text.strip()
                url = job.find("a", class_="base-card__full-link")["href"].split("?")[0]
                
                if location and location.lower() not in job_location.lower():
                    continue
                
                job_page = requests.get(url, headers=headers, timeout=5)
                job_soup = BeautifulSoup(job_page.text, 'html.parser')
                description = job_soup.find("div", class_="description__text").get_text().lower() if job_soup.find("div", class_="description__text") else ""
                
                skill_matches = sum(1 for skill in skills if skill.lower() in description)
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "url": url,
                    "skill_matches": skill_matches,
                    "match_percentage": int((skill_matches / len(skills)) * 100 ) if skills else 0
                })
            except Exception:
                continue
        
        return sorted(jobs, key=lambda x: (-x['skill_matches'], x['title']))[:10]
    except Exception as e:
        print(f"Error scraping LinkedIn: {str(e)}")
        return []

def ask_gemini(question: str, resume: str, job_description: str) -> str:
    qna_prompt = PromptTemplate.from_template("""
    You are an interview preparation assistant. Answer the following question from a candidate based on their resume and the job description.

    Resume:
    {resume}

    Job Description:
    {jd}

    Question:
    {question}

    Answer in a professional and helpful tone.
    """)

    qna_chain = LLMChain(llm=llm, prompt=qna_prompt)

    for _attempt in range(3):
        try:
            return qna_chain.run(resume=resume, jd=job_description, question=question)
        except ResourceExhausted:
            time.sleep(15)
        except Exception as e:
            return f"⚠️ Gemini API Error: {str(e)}"

    return "⚠️ Gemini API is currently rate-limited. Please try again later."

def analyze_resume(resume_text: str, job_description: str):
    try:
        build_vector_store(resume_text, "faiss_resume")
        build_vector_store(job_description, "faiss_jd")

        resume_db = load_vector_store("faiss_resume")
        jd_db = load_vector_store("faiss_jd")

        resume_summary = " ".join([doc.page_content for doc in resume_db.similarity_search("Summarize this resume", k=3)])
        jd_summary = " ".join([doc.page_content for doc in jd_db.similarity_search("Summarize this job description", k=3)])

        analysis_prompt = PromptTemplate.from_template("""
        ### Resume Analysis
        Compare the following resume and job description:

        Resume:
        {resume}

        Job Description:
        {jd}

        Provide insights:
        - Strengths
        - Weaknesses and improvements
        - Missing keywords
        - Top 5 recommendations
        """)

        cover_letter_prompt = PromptTemplate.from_template("""
        Write a professional cover letter for this resume and job description.

        Resume:
        {resume}

        Job Description:
        {jd}
        """)

        interview_prompt = PromptTemplate.from_template("""
        Generate 10 interview questions based on this resume and job description.

        Resume:
        {resume}

        Job Description:
        {jd}
        """)

        analysis = LLMChain(llm=llm, prompt=analysis_prompt).run(resume=resume_summary, jd=jd_summary)
        cover_letter = LLMChain(llm=llm, prompt=cover_letter_prompt).run(resume=resume_summary, jd=jd_summary)
        questions = [q.strip() for q in LLMChain(llm=llm, prompt=interview_prompt).run(resume=resume_summary, jd=jd_summary).split('\n') if q.strip()]
        
        return analysis, cover_letter, questions
    except Exception as e:
        raise Exception(f"Error in analyze_resume: {str(e)}")

def calculate_ats_score(resume_text: str, job_description: str) -> tuple[int, str]:
    try:
        ats_prompt = PromptTemplate.from_template("""
        Analyze this resume against the job description and calculate an ATS score (0-100).
        Consider keyword matching, skills alignment, experience relevance, education, format, and customization.

        Resume:
        {resume}

        Job Description:
        {jd}

        Return response in format:
        SCORE: [number]
        FEEDBACK: [multiline feedback]
        """)

        response = LLMChain(llm=llm, prompt=ats_prompt).run(resume=resume_text, jd=job_description)
        score = int(response.split("SCORE:")[1].split()[0].strip()) if "SCORE:" in response else 0
        feedback = response.split("FEEDBACK:")[1].strip() if "FEEDBACK:" in response else ""
        return score, feedback
    except Exception as e:
        print(f"Error calculating ATS score: {str(e)}")
        return 0, f"Could not calculate ATS score: {str(e)}"

def calculate_experience_years(experience: List[Dict]) -> float:
    total_days = 0
    for exp in experience:
        duration = exp.get('duration', '')
        if not duration:
            continue
            
        # Try to parse dates like "Jan 2020 - Present" or "2020 - 2022"
        date_parts = re.findall(r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b|\d{4})', duration)
        
        if len(date_parts) == 2:
            try:
                start_date = datetime.strptime(date_parts[0], '%b %Y') if ' ' in date_parts[0] else datetime.strptime(date_parts[0], '%Y')
                end_date = datetime.strptime(date_parts[1], '%b %Y') if ' ' in date_parts[1] else datetime.strptime(date_parts[1], '%Y')
                total_days += (end_date - start_date).days
            except ValueError:
                continue
        elif 'present' in duration.lower() and len(date_parts) == 1:
            try:
                start_date = datetime.strptime(date_parts[0], '%b %Y') if ' ' in date_parts[0] else datetime.strptime(date_parts[0], '%Y')
                total_days += (datetime.now() - start_date).days
            except ValueError:
                continue
    
    return round(total_days / 365, 1)

def get_resume_templates() -> List[Dict]:
    """Return available resume templates with previews"""
    return [
        {
            "id": "professional",
            "name": "Professional Blue",
            "description": "Clean, corporate design with blue accents",
            "category": "all",
            "preview": "professional_preview.html"
        },
        {
            "id": "modern",
            "name": "Modern Green",
            "description": "Contemporary design with green accents",
            "category": "all",
            "preview": "modern_preview.html"
        },
        {
            "id": "creative",
            "name": "Creative Orange",
            "description": "Bold design for creative fields",
            "category": "all",
            "preview": "creative_preview.html"
        },
        {
            "id": "executive",
            "name": "Executive Dark",
            "description": "Sophisticated design for senior professionals",
            "category": "experienced",
            "preview": "executive_preview.html"
        },
        {
            "id": "fresher",
            "name": "Fresher Light",
            "description": "Optimized for entry-level candidates",
            "category": "fresher",
            "preview": "fresher_preview.html"
        },
        {
            "id": "academic",
            "name": "Academic",
            "description": "Perfect for students and researchers",
            "category": "fresher",
            "preview": "academic_preview.html"
        },
        {
            "id": "technical",
            "name": "Technical",
            "description": "Optimized for technical roles",
            "category": "mid-level",
            "preview": "technical_preview.html"
        },
        {
            "id": "minimal",
            "name": "Minimal Black",
            "description": "Ultra-clean black and white design",
            "category": "all",
            "preview": "minimal_preview.html"
        }
    ]
    
def apply_resume_template(html_content: str, template_id: str) -> str:
    """
    Apply selected template styling to resume HTML
    """
    templates = {
        "professional": """
        <style>
            body { font-family: 'Calibri', sans-serif; background-color:white; }
            .name { color: #2a5f8a; font-size: 28px; }
            .section-title { color: #2a5f8a; border-bottom: 2px solid #2a5f8a; }
            .skill-tag { background: #e6f2ff; color: #2a5f8a; }
        </style>
        """,
        "modern": """
        <style>
            body { font-family: 'Segoe UI', sans-serif;  background-color:white;}
            .name { color: #4CAF50; font-size: 28px; }
            .section-title { color: #4CAF50; border-bottom: 2px solid #4CAF50; }
            .skill-tag { background: #e8f5e9; color: #2E7D32; }
        </style>
        """,
        "creative": """
        <style>
            body { font-family: 'Roboto', sans-serif;  background-color:white;}
            .name { color: #FF5722; font-size: 28px; }
            .section-title { color: #FF5722; border-bottom: 2px solid #FF5722; }
            .skill-tag { background: #FFF3E0; color: #E64A19; }
        </style>
        """,
        "executive": """
        <style>
            body { font-family: 'Times New Roman', serif; background-color:white; }
            .name { color: #000; font-size: 32px; text-transform: uppercase; }
            .section-title { color: #000; border-bottom: 1px solid #000; }
            .skill-tag { background: #f5f5f5; color: #000; border: 1px solid #ddd; }
        </style>
        """,
        "fresher": """
        <style>
            body { font-family: 'Arial', sans-serif;  background-color:white;}
            .name { color: #3f51b5; font-size: 24px; }
            .section-title { color: #3f51b5; border-bottom: 1px dashed #3f51b5; }
            .skill-tag { background: #e8eaf6; color: #3f51b5; }
        </style>
        """,
        "academic": """
        <style>
            body { font-family: 'Garamond', serif;background-color:white; }
            .name { color: #795548; font-size: 26px; }
            .section-title { color: #795548; border-bottom: 1px solid #795548; }
            .skill-tag { background: #efebe9; color: #795548; }
        </style>
        """,
        "technical": """
        <style>
            body { font-family: 'Courier New', monospace;background-color:white; }
            .name { color: #006064; font-size: 26px; }
            .section-title { color: #006064; border-bottom: 1px solid #006064; }
            .skill-tag { background: #e0f7fa; color: #006064; }
        </style>
        """,
        "minimal": """
        <style>
            body { font-family: 'Helvetica Neue', sans-serif; background-color:white;}
            .name { color: #000; font-size: 24px; }
            .section-title { color: #000; border-bottom: 1px solid #000; }
            .skill-tag { background: #f5f5f5; color: #000; border: 1px solid #ddd; }
        </style>
        """
    }
    
    # Insert template CSS into the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    head = soup.find('head')
    if head:
        style_tag = soup.new_tag('style')
        style_tag.string = templates.get(template_id, templates["professional"])
        head.append(style_tag)
    
    return str(soup)

def generate_html_resume(resume_data: dict, template_id: str = "professional") -> str:
    """Generate HTML resume with proper section ordering based on experience"""
    try:
        # Calculate experience years
        experience_years = calculate_experience_years(resume_data.get("experience", []))
        
        # Determine experience level and section order
        if experience_years >= 4:
            section_order = ["summary", "experience", "projects", "skills", "education"]
        elif experience_years >= 1:
            section_order = ["summary", "experience", "skills", "education"] 
        else:
            section_order = ["summary", "education", "skills", "projects"]
        
        # Get the template content
        template_content = get_template_content(template_id)
        if not template_content:
            template_content = get_template_content("professional")  # fallback
            
        # Create a BeautifulSoup object from the template
        soup = BeautifulSoup(template_content, 'html.parser')
        
        # Replace placeholder content with actual data
        if soup.find(class_='name'):
            soup.find(class_='name').string = resume_data.get('name', 'Your Name')
        
        # Update contact info
        contact_info = soup.find(class_='contact-info')
        if contact_info:
            contact_info.string = f"{resume_data.get('email', '')} | {resume_data.get('phone', '')} | {resume_data.get('linkedin', '')}"
        
        # Update summary
        summary_section = soup.find(class_='summary') or soup.find(string=re.compile('Summary'))
        if summary_section:
            summary_content = summary_section.find_next('p') if summary_section.name != 'p' else summary_section
            if summary_content:
                summary_content.string = resume_data.get('summary', '')
        
        # Update skills
        skills_container = soup.find(class_='skills')
        if skills_container:
            skills_container.clear()
            for skill in resume_data.get('skills', []):
                skill_tag = soup.new_tag('span', **{'class': 'skill-tag'})
                skill_tag.string = skill
                skills_container.append(skill_tag)
        
        # Update experience
        experience_container = soup.find(class_='experience-container') or soup.find(string=re.compile('Experience'))
        if experience_container:
            if experience_container.name != 'div':
                experience_container = experience_container.find_parent('div') or experience_container.find_next('div')
            
            experience_container.clear()
            for exp in resume_data.get('experience', []):
                job_div = soup.new_tag('div', **{'class': 'job'})
                
                header = soup.new_tag('div', **{'class': 'job-header'})
                title = soup.new_tag('span', **{'class': 'job-title'})
                title.string = exp.get('title', '')
                company = soup.new_tag('span', **{'class': 'company'})
                company.string = f", {exp.get('company', '')}"
                duration = soup.new_tag('span', **{'class': 'job-duration'})
                duration.string = exp.get('duration', '')
                
                header.append(title)
                header.append(company)
                header.append(duration)
                job_div.append(header)
                
                ul = soup.new_tag('ul')
                for bullet in exp.get('description', '').split('\n'):
                    if bullet.strip():
                        li = soup.new_tag('li')
                        li.string = bullet.strip()
                        ul.append(li)
                job_div.append(ul)
                
                experience_container.append(job_div)
        
        # Update education
        education_section = soup.find(class_='education') or soup.find(string=re.compile('Education'))
        if education_section:
            education_content = education_section.find_next('p') or education_section.find_next('ul') or education_section
            if education_content.name == 'ul':
                education_content.clear()
                for bullet in resume_data.get('education', '').split('\n'):
                    if bullet.strip():
                        li = soup.new_tag('li')
                        li.string = bullet.strip()
                        education_content.append(li)
            else:
                education_content.string = resume_data.get('education', '')
        
        # Update projects
        projects_section = soup.find(class_='projects') or soup.find(string=re.compile('Projects'))
        if projects_section:
            projects_content = projects_section.find_next('ul') or projects_section.find_next('div') or projects_section
            if projects_content.name == 'ul':
                projects_content.clear()
                for bullet in resume_data.get('projects', '').split('\n'):
                    if bullet.strip():
                        li = soup.new_tag('li')
                        li.string = bullet.strip()
                        projects_content.append(li)
            else:
                projects_content.string = resume_data.get('projects', '')
        return str(soup)
    except Exception as e:
        raise Exception(f"Error generating HTML resume: {str(e)}")




def generate_experience_based_resume(resume: str, job_description: str, experience_level: str) -> str:
    """
    Generate resume with different formats based on experience level
    """
    try:
        if experience_level == 'senior':
            template = """
            Create an ATS-optimized resume for a senior candidate (4+ years experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Work Experience (detailed with achievements and metrics)
            5. Key Projects (showcasing impact and leadership)
            6. Education (brief section at end)
            
            Return the resume in HTML format with professional styling. Focus on leadership, achievements, and impact.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        elif experience_level == 'mid':
            template = """
            Create an ATS-optimized resume for a mid-level candidate (1-3 years experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Work Experience (detailed with achievements)
            5. Skills (technical skills relevant to the job)
            6. Education (brief section at end)
            
            Return the resume in HTML format with clean styling. Focus on skills and contributions.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        elif experience_level == 'junior':
            template = """
            Create an ATS-optimized resume for a junior candidate (<1 year experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Education (detailed with relevant coursework)
            5. Skills (technical skills with proficiency levels)
            6. Work Experience (if any, otherwise academic projects)
            7. Projects (academic or personal projects)
            
            Return the resume in HTML format with modern styling. Focus on education and potential.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        else:  # fresher
            template = """
            Create an ATS-optimized resume for a fresher (no experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Education (detailed with relevant coursework)
            5. Skills (technical skills with proficiency levels)
            6. Projects (academic or personal projects)
            
            Return the resume in HTML format with modern styling. Focus on education and potential.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        
        resume_prompt = PromptTemplate.from_template(template)
        chain = LLMChain(llm=llm, prompt=resume_prompt)
        
        # Get the HTML content from the LLM
        html_content = chain.run(resume=resume, jd=job_description)
        
        # Parse the HTML to ensure it's valid and get structured data
        resume_data = parse_html_resume(html_content)
        
        # Generate the final HTML with proper template
        return generate_html_resume(resume_data)
    except Exception as e:
        raise Exception(f"Error in generate_experience_based_resume: {str(e)}")
def get_resume_template(template_name: str, experience_years: float) -> tuple[dict, str, list]:
    """Get template by name and determine experience level with section order and CSS"""
    templates = {
        "professional": {
            "css": """
                body { font-family: 'Calibri', sans-serif;background-color:white; }
                .name { color: #2a5f8a; font-size: 28px; }
                .section-title { color: #2a5f8a; border-bottom: 2px solid #2a5f8a; }
                .skill-tag { background: #e6f2ff; color: #2a5f8a; }
            """
        },
        "modern": {
            "css": """
                body { font-family: 'Segoe UI', sans-serif;background-color:white; }
                .name { color: #4CAF50; font-size: 28px; }
                .section-title { color: #4CAF50; border-bottom: 2px solid #4CAF50; }
                .skill-tag { background: #e8f5e9; color: #2E7D32; }
            """
        },
        # Add other templates with their CSS here
    }
    
    # Get the requested template or default to professional
    template = templates.get(template_name, templates["professional"])
    
    # Determine experience level and section order
    if experience_years >= 4:
        exp_level = "senior"
        section_order = ["summary", "experience", "projects", "skills", "education"]
    elif experience_years >= 1:
        exp_level = "mid"
        section_order = ["summary", "skills", "experience", "education"]
    else:
        exp_level = "fresher"
        section_order = ["summary", "education", "skills", "projects"]
    
    return template, exp_level, section_order


# Modify your generate_tailored_resume function to better handle templates:

def generate_tailored_resume(resume: str, job_description: str, template_id: str = "professional") -> str:
    """
    Generate a resume tailored to the candidate's experience level and job description
    while maintaining the selected template's formatting.
    """
    try:
        # First parse the resume text into structured data
        resume_data = parse_html_resume(resume) if '<html' in resume.lower() else {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "summary": resume[:500],  # Use first 500 chars as summary if plain text
            "skills": extract_skills_from_resume(resume),
            "experience": [],
            "education": "",
            "projects": ""
        }

        # Generate content using Gemini
        prompt = PromptTemplate.from_template("""
        Create an ATS-optimized resume based on the following resume content and job description.
        The candidate is a {experience_level} level professional.
        
        Structure the resume with these sections:
        - Professional summary tailored to the job
        - Work experience with achievements and metrics
        - Skills (technical and soft skills)
        - Education 
        - Projects (if applicable)
        
        Return ONLY the content (no HTML tags or styling) in this JSON format:
        {{
            "summary": "Tailored professional summary...",
            "skills": ["skill1", "skill2", ...],
            "experience": [
                {{
                    "title": "Job Title",
                    "company": "Company Name",
                    "duration": "Time Period",
                    "description": "Achievements and responsibilities"
                }}
            ],
            "education": "Education details",
            "projects": "Project details"
        }}
        
        Resume Content:
        {resume}
        
        Job Description:
        {jd}
        """)
        
        chain = LLMChain(llm=llm, prompt=prompt)
        experience_level = detect_experience_level(resume)
        generated_content = chain.run(
            resume=resume,
            jd=job_description,
            experience_level=experience_level
        )
        
        try:
            # Parse the generated JSON content
            content_data = json.loads(generated_content)
            # Merge with existing resume data
            resume_data.update({
                "summary": content_data.get("summary", resume_data["summary"]),
                "skills": list(set(resume_data["skills"] + content_data.get("skills", []))),
                "experience": resume_data["experience"] + content_data.get("experience", []),
                "education": content_data.get("education", resume_data["education"]),
                "projects": content_data.get("projects", resume_data["projects"])
            })
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            resume_data["summary"] = generated_content

        # Generate HTML using the selected template
        return generate_html_resume(resume_data, template_id)
        
    except Exception as e:
        raise Exception(f"Error generating tailored resume: {str(e)}")

def detect_experience_level(resume_text: str) -> str:
    """
    Detect experience level from resume text
    Returns: 'fresher', 'junior', 'mid', or 'senior'
    """
    try:
        exp_prompt = PromptTemplate.from_template("""
        Analyze this resume and determine the candidate's experience level:
        - 'fresher' if no experience
        - 'junior' if less than 1 year experience
        - 'mid' if 1-3 years experience
        - 'senior' if 4+ years experience
        
        Return only one of these four words in lowercase.
        
        Resume:
        {resume}
        """)
        
        exp_chain = LLMChain(llm=llm, prompt=exp_prompt)
        level = exp_chain.run(resume=resume_text).strip().lower()
        return level if level in ['fresher', 'junior', 'mid', 'senior'] else 'mid'
    except Exception:
        return 'mid'

def clean_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

def text_to_pdf(text: str) -> bytes:
    try:
        if isinstance(text, (bytes, bytearray)):
            return bytes(text)
        
        if "<html" in text.lower():
            return html_to_pdf(text)

        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)
        
        pdf.set_font("Arial", size=10)
        text = clean_text(text)
        lines = text.split('\n')
        
        for line in lines:
            pdf.multi_cell(0, 10, line)

        buffer = io.BytesIO()
        pdf.output(buffer)
        return buffer.getvalue()
    except Exception as e:
        print(f"Error converting text to PDF: {str(e)}")
        return b""

def html_to_pdf(html_content: str) -> bytes:
    """Convert HTML content to PDF bytes using pdfkit"""
    try:
        import pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': ''
        }
        
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        return pdf_bytes
        
    except ImportError:
        # Fallback to FPDF if pdfkit not available
        try:
            from xhtml2pdf import pisa
            from io import BytesIO
            
            pdf_bytes = BytesIO()
            pisa.CreatePDF(html_content, dest=pdf_bytes)
            return pdf_bytes.getvalue()
            
        except ImportError:
            # Final fallback - create simple text PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            
            # Clean HTML and convert to text
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text("\n")
            text = clean_text(text)
            
            # Add text to PDF
            for line in text.split('\n'):
                if line.strip():
                    pdf.multi_cell(0, 5, line)
            
            # Return PDF bytes
            return pdf.output(dest='S').encode('latin-1')
    
def parse_html_resume(html_content: str) -> dict:
    """Parse HTML resume into structured data for the visual editor"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        resume_data = {
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
        
        # Extract name (usually in h1 or .name class)
        name_tag = soup.find('h1') or soup.find(class_='name')
        if name_tag:
            resume_data['name'] = name_tag.get_text().strip()
        
        # Extract contact info (usually in the header)
        header = soup.find(class_='header') or soup.find('p')
        if header:
            contact_text = header.get_text()
            if "|" in contact_text:
                parts = [part.strip() for part in contact_text.split("|")]
                for part in parts:
                    if "@" in part and "." in part:
                        resume_data['email'] = part.strip()
                    elif part.startswith("http"):
                        resume_data['linkedin'] = part.strip()
                    elif any(c.isdigit() for c in part.replace(" ", "").replace("-", "")):
                        resume_data['phone'] = part.strip()
        
        # Extract summary
        for tag in soup.find_all(['h2', 'h3']):
            if 'summary' in tag.get_text().lower():
                next_tag = tag.find_next(['p', 'div'])
                if next_tag:
                    resume_data['summary'] = next_tag.get_text().strip()
                break
        
        # Extract skills
        for tag in soup.find_all(['h2', 'h3']):
            if 'skill' in tag.get_text().lower():
                skills_container = tag.find_next(['ul', 'div'])
                if skills_container:
                    if skills_container.name == 'ul':
                        resume_data['skills'] = [li.get_text().strip() for li in skills_container.find_all('li')]
                    elif skills_container.name == 'div' and 'skills' in skills_container.get('class', []):
                        resume_data['skills'] = [span.get_text().strip() for span in skills_container.find_all('span', class_='skill-tag')]
                break
        
        # Extract experience
        for tag in soup.find_all(['h2', 'h3']):
            if 'experience' in tag.get_text().lower():
                exp_items = []
                current_item = tag.find_next(['div', 'h4'])
                while current_item and 'experience' in current_item.find_previous(['h2', 'h3']).get_text().lower():
                    if current_item.name == 'h4':
                        exp_data = {
                            "title": current_item.get_text().strip(),
                            "company": "",
                            "duration": "",
                            "description": ""
                        }
                        
                        # Get company (usually next p or span)
                        company_tag = current_item.find_next(['p', 'span'])
                        if company_tag:
                            exp_data['company'] = company_tag.get_text().strip()
                        
                        # Get duration (often in same p as company or next p)
                        duration_tag = company_tag.find_next(['p', 'span']) if company_tag else None
                        if duration_tag and ("-" in duration_tag.get_text() or "present" in duration_tag.get_text().lower()):
                            exp_data['duration'] = duration_tag.get_text().strip()
                        
                        # Get description (usually ul or next p)
                        desc_tag = duration_tag.find_next(['ul', 'p']) if duration_tag else None
                        if desc_tag:
                            if desc_tag.name == 'ul':
                                exp_data['description'] = "\n".join([f"- {li.get_text().strip()}" for li in desc_tag.find_all('li')])
                            else:
                                exp_data['description'] = desc_tag.get_text().strip()
                        
                        exp_items.append(exp_data)
                    current_item = current_item.find_next(['div', 'h4'])
                resume_data['experience'] = exp_items
                break
        
        # Extract education
        for tag in soup.find_all(['h2', 'h3']):
            if 'education' in tag.get_text().lower():
                edu_tag = tag.find_next(['p', 'ul'])
                if edu_tag:
                    if edu_tag.name == 'ul':
                        resume_data['education'] = "\n".join([f"- {li.get_text().strip()}" for li in edu_tag.find_all('li')])
                    else:
                        resume_data['education'] = edu_tag.get_text().strip()
                break
        
        # Extract projects
        for tag in soup.find_all(['h2', 'h3']):
            if 'project' in tag.get_text().lower():
                projects_tag = tag.find_next(['ul', 'div'])
                if projects_tag:
                    if projects_tag.name == 'ul':
                        resume_data['projects'] = "\n".join([f"- {li.get_text().strip()}" for li in projects_tag.find_all('li')])
                    else:
                        resume_data['projects'] = projects_tag.get_text().strip()
                break
        
        return resume_data
    except Exception as e:
        print(f"Error parsing HTML resume: {str(e)}")
        return {
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

def update_html_resume(resume_data: dict, template_name: str = "professional") -> str:
    """Update HTML resume based on edited visual form data"""
    try:
        return generate_html_resume(resume_data, template_name)
    except Exception as e:
        print(f"Error updating HTML resume: {str(e)}")
        return ""
    
def update_resume_continuously(resume_data: dict, template_id: str = "professional") -> str:
    """Continuously update resume HTML based on changes"""
    try:
        # Generate the base HTML resume
        html_content = generate_html_resume(resume_data)
        
        # Apply the selected template styling
        styled_html = apply_resume_template(html_content, template_id)
        
        
        return styled_html
    except Exception as e:
        print(f"Error updating resume: {str(e)}")
        return ""
    
    
def generate_visual_editor(resume_data: dict) -> str:
    """Generate a visual form editor for the resume"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Resume Editor</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                line-height: 1.6; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 20px;
                background-color: white;
                color: black;
            }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ 
                display: block; 
                margin-bottom: 5px; 
                font-weight: bold;
                color: black;
            }}
            input[type="text"], textarea {{ 
                width: 100%; 
                padding: 8px; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                background-color: white;
                color: black;
            }}
            textarea {{ min-height: 100px; }}
            .section {{ 
                margin-bottom: 30px; 
                border: 1px solid #eee; 
                padding: 15px; 
                border-radius: 5px;
                background-color: white;
            }}
            .section-title {{ 
                font-size: 18px; 
                margin-top: 0; 
                color: black;
            }}
            .skill-tag {{ 
                background: #f0f0f0; 
                padding: 3px 8px; 
                border-radius: 3px; 
                display: inline-block; 
                margin-right: 5px; 
                margin-bottom: 5px;
                color: black;
            }}
            .add-btn {{ 
                background: #4CAF50; 
                color: white; 
                border: none; 
                padding: 5px 10px; 
                border-radius: 3px; 
                cursor: pointer; 
            }}
            .remove-btn {{ 
                background: #f44336; 
                color: white; 
                border: none; 
                padding: 2px 5px; 
                border-radius: 3px; 
                cursor: pointer; 
                margin-left: 5px; 
            }}
            .preview-btn {{ 
                background: #2196F3; 
                color: white; 
                padding: 10px 15px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 16px; 
            }}
        </style>
    </head>
    <body>
        <h1 style="color: black;">Resume Editor</h1>
        
        <div class="section">
            <h2 class="section-title">Personal Information</h2>
            <div class="form-group">
                <label for="name">Full Name</label>
                <input type="text" id="name" value="{resume_data.get('name', '')}">
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="text" id="email" value="{resume_data.get('email', '')}">
            </div>
            <div class="form-group">
                <label for="phone">Phone</label>
                <input type="text" id="phone" value="{resume_data.get('phone', '')}">
            </div>
            <div class="form-group">
                <label for="linkedin">LinkedIn URL</label>
                <input type="text" id="linkedin" value="{resume_data.get('linkedin', '')}">
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Summary</h2>
            <div class="form-group">
                <textarea id="summary">{resume_data.get('summary', '')}</textarea>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Skills</h2>
            <div id="skills-container">
                {"".join([f'<span class="skill-tag">{skill}<button class="remove-btn" onclick="removeSkill(this)">×</button></span>' for skill in resume_data.get('skills', [])])}
            </div>
            <div class="form-group" style="margin-top: 10px;">
                <input type="text" id="new-skill" placeholder="Add new skill">
                <button class="add-btn" onclick="addSkill()">Add Skill</button>
            </div>
        </div>fz

        <div class="section">
            <h2 class="section-title">Experience</h2>
            <div id="experience-container">
                {"".join([f"""
                <div class="experience-item" style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
                    <div class="form-group">
                        <label>Job Title</label>
                        <input type="text" class="exp-title" value="{exp.get('title', '')}">
                    </div>
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" class="exp-company" value="{exp.get('company', '')}">
                    </div>
                    <div class="form-group">
                        <label>Duration</label>
                        <input type="text" class="exp-duration" value="{exp.get('duration', '')}">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea class="exp-description">{exp.get('description', '')}</textarea>
                    </div>
                    <button class="remove-btn" onclick="this.parentElement.remove()">Remove Experience</button>
                </div>
                """ for exp in resume_data.get('experience', [])])}
            </div>
            <button class="add-btn" onclick="addExperience()">Add Experience</button>
        </div>

        <div class="section">
            <h2 class="section-title">Education</h2>
            <div class="form-group">
                <label for="education">Education Details</label>
                <textarea id="education">{resume_data.get('education', '')}</textarea>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Projects</h2>
            <div class="form-group">
                <label for="projects">Project Details</label>
                <textarea id="projects">{resume_data.get('projects', '')}</textarea>
            </div>
        </div>

        <button class="preview-btn" onclick="updateResume()">Update Resume</button>

        <script>
            function addSkill() {{
                const skillInput = document.getElementById('new-skill');
                if (skillInput.value.trim() === '') return;
                
                const skillTag = document.createElement('span');
                skillTag.className = 'skill-tag';
                skillTag.innerHTML = `${{skillInput.value.trim()}}<button class="remove-btn" onclick="removeSkill(this)">×</button>`; 
                
                document.getElementById('skills-container').appendChild(skillTag);
                skillInput.value = '';
                updateResume();
            }}

            function removeSkill(button) {{
                button.parentElement.remove();
                updateResume();
            }}

            function addExperience() {{
                const expHtml = ` 
                <div class="experience-item" style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
                    <div class="form-group">
                        <label>Job Title</label>
                        <input type="text" class="exp-title" placeholder="Software Developer">
                    </div>
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" class="exp-company" placeholder="ABC Corp">
                    </div>
                    <div class="form-group">
                        <label>Duration</label>
                        <input type="text" class="exp-duration" placeholder="Jan 2020 - Present">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea class="exp-description" placeholder="Your responsibilities and achievements"></textarea>
                    </div>
                    <button class="remove-btn" onclick="this.parentElement.remove()">Remove Experience</button>
                </div>`;
                
                document.getElementById('experience-container').insertAdjacentHTML('beforeend', expHtml);
                updateResume();
            }}

            function updateResume() {{
                const resumeData = {{
                    name: document.getElementById('name').value,
                    email: document.getElementById('email').value,
                    phone: document.getElementById('phone').value,
                    linkedin: document.getElementById('linkedin').value,
                    summary: document.getElementById('summary').value,
                    skills: Array.from(document.querySelectorAll('.skill-tag')).map(el => el.textContent.replace('×', '').trim()),
                    experience: Array.from(document.querySelectorAll('.experience-item')).map(item => ({{
                        title: item.querySelector('.exp-title').value,
                        company: item.querySelector('.exp-company').value,
                        duration: item.querySelector('.exp-duration').value,
                        description: item.querySelector('.exp-description').value
                    }})),
                    education: document.getElementById('education').value,
                    projects: document.getElementById('projects').value
                }};
                
                window.parent.postMessage({{
                    type: 'UPDATE_RESUME',
                    data: resumeData
                }}, '*');
            }}

            document.querySelectorAll('input, textarea').forEach(element => {{
                element.addEventListener('input', updateResume);
            }});

            const observer = new MutationObserver(updateResume);
            observer.observe(document.getElementById('skills-container'), {{ 
                childList: true, 
                subtree: true 
            }});
            observer.observe(document.getElementById('experience-container'), {{ 
                childList: true, 
                subtree: true 
            }});
        </script>
    </body>
    </html>
    """
    return html_template

# Add these new functions to your existing backend code

def get_public_templates() -> List[Dict]:
    """Return templates that users can select and customize"""
    return [
        {
            "id": "professional",
            "name": "Professional Blue",
            "description": "Clean, corporate design with blue accents",
            "category": "all",
            "preview": "professional_preview.html"
        },
        {
            "id": "modern",
            "name": "Modern Green",
            "description": "Contemporary design with green accents",
            "category": "all",
            "preview": "modern_preview.html"
        },
        {
            "id": "minimal",
            "name": "Minimal Black",
            "description": "Ultra-clean black and white design",
            "category": "all",
            "preview": "minimal_preview.html"
        }
    ]

def save_custom_template(user_id: str, template_name: str, template_content: str) -> bool:
    """Save a custom template for a user"""
    try:
        if not os.path.exists('user_templates'):
            os.makedirs('user_templates')
            
        file_path = f"user_templates/{user_id}_{template_name}.html"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        return True
    except Exception as e:
        print(f"Error saving template: {str(e)}")
        return False

def get_custom_templates(user_id: str) -> List[Dict]:
    """Get all custom templates for a user"""
    templates = []
    if os.path.exists('user_templates'):
        for filename in os.listdir('user_templates'):
            if filename.startswith(user_id + "_"):
                template_name = filename[len(user_id)+1:-5]  # Remove userid_ and .html
                templates.append({
                    "id": filename,
                    "name": template_name.replace('_', ' '),
                    "description": f"Custom template by {user_id}",
                    "category": "custom"
                })
    return templates

def get_template_preview(template_id: str) -> str:
    """Get HTML preview of a template"""
    if template_id in TEMPLATE_STORAGE:
        return TEMPLATE_STORAGE[template_id]["content"]
    
    # Check for custom templates
    if os.path.exists('user_templates'):
        file_path = f"user_templates/{template_id}"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    return ""
# Add this to your existing backend code
def get_prebuilt_resumes() -> List[Dict]:
    """Return simplified pre-built resume templates with text structure"""
    return [
        {
            "id": "professional",
            "name": "Professional Resume",
            "description": "Standard format for corporate jobs",
            "category": "all",
            "structure": {
                "sections": ["summary", "experience", "skills", "education"],
                "experience_format": "detailed"
            }
        },
        
        {
            "id": "modern",
            "name": "Modern Resume",
            "description": "Contemporary design with skills focus",
            "category": "all",
            "structure": {
                "sections": ["summary", "skills", "experience", "education"],
                "experience_format": "concise"
            }
        },
        {
            "id": "fresher",
            "name": "Fresher Resume",
            "description": "For students and entry-level candidates",
            "category": "fresher",
            "structure": {
                "sections": ["summary", "education", "skills", "projects"],
                "experience_format": "simple"
            }
        }
    ]

def get_prebuilt_resume_content(resume_id: str) -> Dict:
    """Get sample content structure for a pre-built resume"""
    samples = {
        "professional": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(123) 456-7890",
            "linkedin": "linkedin.com/in/johndoe",
            "summary": "Experienced software engineer with 5+ years in full-stack development...",
            "skills": ["Python", "JavaScript", "SQL", "AWS"],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2020-Present",
                    "description": "Lead development team...\nImproved system performance..."
                }
            ],
            "education": "BSc Computer Science, University X, 2019"
        },
        "modern": {
            "name": "Jane Smith",
            "summary": "Innovative designer with UX/UI expertise...",
            "skills": ["Figma", "Adobe XD", "HTML/CSS", "User Research"],
            "experience": [
                {
                    "title": "UX Designer",
                    "company": "Design Studio",
                    "duration": "2021-Present",
                    "description": "Redesigned mobile app interface..."
                }
            ],
            "education": "BA Design, Art College, 2020"
        },
        "fresher": {
            "name": "Alex Johnson",
            "summary": "Recent computer science graduate seeking entry-level position...",
            "skills": ["Java", "Python", "Data Structures"],
            "education": "BSc Computer Science, State University, 2023",
            "projects": [
                "E-commerce website - Full stack project with React and Node.js",
                "Library management system - Java application with MySQL"
            ]
        }
    }
    return samples.get(resume_id, {})

def generate_resume_html(resume_data: Dict, template_id: str) -> str:
    """Convert structured resume data to HTML based on template"""
    template = get_prebuilt_resumes()[0]  # Default to first template
    for t in get_prebuilt_resumes():
        if t["id"] == template_id:
            template = t
            break
    
    # Generate HTML based on template structure
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{resume_data.get('name', 'Resume')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background-color:white; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .name {{ font-size: 24px; font-weight: bold; }}
            .section {{ margin-bottom: 20px; }}
            .section-title {{ font-weight: bold; font-size: 18px; border-bottom: 1px solid #ddd; }}
            .job-header {{ display: flex; justify-content: space-between; }}
            .skills {{ display: flex; flex-wrap: wrap; gap: 8px; }}
            .skill-tag {{ background: #f0f0f0; padding: 4px 8px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="name">{resume_data.get('name', 'Your Name')}</div>
            <div class="contact-info">
                {resume_data.get('email', '')} | {resume_data.get('phone', '')} | {resume_data.get('linkedin', '')}
            </div>
        </div>
    """
    
    # Add sections based on template structure
    for section in template["structure"]["sections"]:
        if section == "summary" and resume_data.get("summary"):
            html += f"""
            <div class="section">
                <h2 class="section-title">Summary</h2>
                <p>{resume_data['summary']}</p>
            </div>
            """
        elif section == "skills" and resume_data.get("skills"):
            html += f"""
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills">
                    {"".join([f'<span class="skill-tag">{skill}</span>' for skill in resume_data['skills']])}
                </div>
            </div>
            """
        elif section == "experience" and resume_data.get("experience"):
            html += """
            <div class="section">
                <h2 class="section-title">Experience</h2>
            """
            for exp in resume_data["experience"]:
                html += f"""
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">{exp.get('title', '')}</span>
                            <span class="company">, {exp.get('company', '')}</span>
                        </div>
                        <span class="job-duration">{exp.get('duration', '')}</span>
                    </div>
                    <ul>
                        {"".join([f'<li>{bullet.strip()}</li>' for bullet in exp.get('description', '').split('\n') if bullet.strip()])}
                    </ul>
                </div>
                """
            html += "</div>"
        elif section == "education" and resume_data.get("education"):
            html += f"""
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p>{resume_data['education']}</p>
            </div>
            """
        elif section == "projects" and resume_data.get("projects"):
            html += """
            <div class="section">
                <h2 class="section-title">Projects</h2>
                <ul>
            """
            for project in resume_data["projects"]:
                html += f'<li>{project}</li>'
            html += """
                </ul>
            </div>
            """
    
    html += """
    </body>
    </html>
    """
    return html 



def generate_resume_from_form(form_data: dict, template_id: str = "professional") -> str:
    """Generate resume HTML from form data using specified template"""
    try:
        # Ensure all sections exist even if empty
        form_data.setdefault("name", "Your Name")
        form_data.setdefault("email", "")
        form_data.setdefault("phone", "")
        form_data.setdefault("linkedin", "")
        form_data.setdefault("summary", "")
        form_data.setdefault("skills", [])
        form_data.setdefault("experience", [])
        form_data.setdefault("education", "")
        form_data.setdefault("projects", "")

        # Generate base HTML
        html_content = generate_html_resume(form_data)
        
        # Apply template styling
        styled_html = apply_resume_template(html_content, template_id)
        
        return styled_html
    except Exception as e:
        raise Exception(f"Error generating resume from form: {str(e)}")

def edit_template_content(template_id: str, new_content: str) -> bool:
    """Update template content in storage"""
    if template_id in TEMPLATE_STORAGE:
        TEMPLATE_STORAGE[template_id]["content"] = new_content
        return True
    return False


{

}
def generate_sample_resume(template_id: str = "professional") -> str:
    """
    Generate a sample resume for users to edit
    """
    sample_content = """
    <div class="header">
        <div class="name">YOUR NAME HERE</div>
        <p>
            your.email@example.com | 
            (123) 456-7890 | 
            linkedin.com/in/yourprofile
        </p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Summary</h2>
        <p>Professional summary highlighting your key qualifications and career goals.</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Skills</h2>
        <div class="skills">
            <span class="skill-tag">Skill 1</span>
            <span class="skill-tag">Skill 2</span>
            <span class="skill-tag">Skill 3</span>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Experience</h2>
        <div class="job">
            <div class="job-header">
                <h3>Job Title</h3>
                <p>Company Name</p>
            </div>
            <p>Month Year - Present</p>
            <ul>
                <li>Responsibility or achievement 1</li>
                <li>Responsibility or achievement 2</li>
            </ul>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Education</h2>
        <p><strong>Degree Name</strong>, University Name, Graduation Year</p>
    </div>
    """
    
    html_template = generate_html_resume(sample_content)
    return apply_resume_template(html_template, template_id)

def get_section_order(experience_level: str) -> List[str]:
    """
    Return the appropriate section order based on experience level
    """
    if experience_level == 'senior':
        return ["summary", "experience", "projects", "skills", "education"]
    elif experience_level == 'mid':
        return ["summary", "experience", "skills", "education"]
    else:  # fresher
        return ["summary", "education", "skills", "projects"]

def calculate_experience_years(experience: List[Dict]) -> float:
    """
    Calculate total years of experience from resume data
    """
    total_days = 0
    for exp in experience:
        duration = exp.get('duration', '')
        if not duration:
            continue
            
        # Parse dates like "Jan 2020 - Present" or "2020 - 2022"
        date_parts = re.findall(r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b|\d{4})', duration)
        
        if len(date_parts) == 2:
            try:
                start_date = datetime.strptime(date_parts[0], '%b %Y') if ' ' in date_parts[0] else datetime.strptime(date_parts[0], '%Y')
                end_date = datetime.strptime(date_parts[1], '%b %Y') if ' ' in date_parts[1] else datetime.strptime(date_parts[1], '%Y')
                total_days += (end_date - start_date).days
            except ValueError:
                continue
        elif 'present' in duration.lower() and len(date_parts) == 1:
            try:
                start_date = datetime.strptime(date_parts[0], '%b %Y') if ' ' in date_parts[0] else datetime.strptime(date_parts[0], '%Y')
                total_days += (datetime.now() - start_date).days
            except ValueError:
                continue
    
    return round(total_days / 365, 1)


def get_resume_templates() -> List[Dict]:
    """Return available resume templates with previews"""
    return [
        {
            "id": "professional",
            "name": "Professional Blue",
            "description": "Clean, corporate design with blue accents",
            "category": "all",
            "preview": "professional_preview.html"
        },
        {
            "id": "modern",
            "name": "Modern Green",
            "description": "Contemporary design with green accents",
            "category": "all",
            "preview": "modern_preview.html"
        },
        {
            "id": "creative",
            "name": "Creative Orange",
            "description": "Bold design for creative fields",
            "category": "all",
            "preview": "creative_preview.html"
        },
        {
            "id": "executive",
            "name": "Executive Dark",
            "description": "Sophisticated design for senior professionals",
            "category": "experienced",
            "preview": "executive_preview.html"
        },
        {
            "id": "fresher",
            "name": "Fresher Light",
            "description": "Optimized for entry-level candidates",
            "category": "fresher",
            "preview": "fresher_preview.html"
        },
        {
            "id": "academic",
            "name": "Academic",
            "description": "Perfect for students and researchers",
            "category": "fresher",
            "preview": "academic_preview.html"
        },
        {
            "id": "technical",
            "name": "Technical",
            "description": "Optimized for technical roles",
            "category": "mid-level",
            "preview": "technical_preview.html"
        },
        {
            "id": "minimal",
            "name": "Minimal Black",
            "description": "Ultra-clean black and white design",
            "category": "all",
            "preview": "minimal_preview.html"
        }
    ]
    
def apply_resume_template(html_content: str, template_id: str) -> str:
    """
    Apply selected template styling to resume HTML while preserving content structure
    """
    try:
        # Get the template HTML
        template_html = get_template_content(template_id)
        if not template_html:
            return html_content
            
        # Parse both documents
        content_soup = BeautifulSoup(html_content, 'html.parser')
        template_soup = BeautifulSoup(template_html, 'html.parser')
        
        # Find the main content containers
        content_body = content_soup.find('body')
        template_body = template_soup.find('body')
        
        if not content_body or not template_body:
            return html_content
            
        # Replace template content with our generated content
        template_body.clear()
        for child in content_body.children:
            template_body.append(child)
            
        # Preserve the template's CSS
        template_style = template_soup.find('style')
        if template_style:
            # Remove any existing style tags
            for style in content_soup.find_all('style'):
                style.decompose()
            # Add the template style
            template_soup.head.append(template_style)
            
        return str(template_soup)
    except Exception as e:
        print(f"Error applying template: {str(e)}")
        return html_content

def generate_html_resume(resume_data: dict, template_name: str = "professional") -> str:
    """Generate HTML resume with proper section ordering based on experience"""
    try:
        # Calculate experience years
        experience_years = calculate_experience_years(resume_data.get("experience", []))
        
        # Determine experience level and section order
        if experience_years >= 4:
            section_order = ["summary", "experience", "projects", "skills", "education"]
        elif experience_years >= 1:
            section_order = ["summary", "experience", "skills", "education"] 
        else:
            section_order = ["summary", "education", "skills", "projects"]
        
        # Generate header
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{resume_data.get('name', 'Resume')}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    max-width: 800px; 
                    background-color:white;
                    margin: 0 auto; 
                    padding: 20px;
                    color: #333;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 20px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 15px;
                }}
                .name {{ 
                    font-size: 28px; 
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: #2a5f8a;
                }}
                .contact-info {{
                    font-size: 14px;
                    color: #666;
                }}
                .section {{ 
                    margin-bottom: 25px;
                }}
                .section-title {{ 
                    font-weight: bold;
                    font-size: 20px;
                    color: #2a5f8a;
                    border-bottom: 2px solid #2a5f8a;
                    padding-bottom: 5px;
                    margin-bottom: 15px;
                }}
                .job-header {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                }}
                .job-title {{
                    font-weight: bold;
                }}
                .job-company {{
                    font-style: italic;
                }}
                .job-duration {{
                    color: #666;
                }}
                .skills {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 10px;
                }}
                .skill-tag {{
                    background: #e6f2ff;
                    color: #2a5f8a;
                    padding: 4px 10px;
                    border-radius: 15px;
                    font-size: 14px;
                }}
                ul {{
                    padding-left: 20px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">{resume_data.get('name', 'Your Name')}</div>
                <div class="contact-info">
                    {resume_data.get('email', '')} | {resume_data.get('phone', '')} | {resume_data.get('linkedin', '')}
                </div>
            </div>
        """
        
        # Add sections in the determined order
        for section in section_order:
            if section == "summary" and resume_data.get("summary"):
                html += f"""
                <div class="section">
                    <h2 class="section-title">Professional Summary</h2>
                    <p>{resume_data['summary']}</p>
                </div>
                """
            elif section == "experience" and resume_data.get("experience"):
                html += """
                <div class="section">
                    <h2 class="section-title">Work Experience</h2>
                """
                for exp in resume_data["experience"]:
                    html += f"""
                    <div class="job">
                        <div class="job-header">
                            <div>
                                <span class="job-title">{exp.get('title', '')}</span>
                                <span class="job-company">, {exp.get('company', '')}</span>
                            </div>
                            <span class="job-duration">{exp.get('duration', '')}</span>
                        </div>
                        <ul>
                            {"".join([f'<li>{bullet.strip()}</li>' for bullet in exp.get('description', '').split('\n') if bullet.strip()])}
                        </ul>
                    </div>
                    """
                html += "</div>"
            elif section == "skills" and resume_data.get("skills"):
                html += f"""
                <div class="section">
                    <h2 class="section-title">Skills</h2>
                    <div class="skills">
                        {"".join([f'<span class="skill-tag">{skill}</span>' for skill in resume_data['skills']])}
                    </div>
                </div>
                """
            elif section == "education" and resume_data.get("education"):
                html += f"""
                <div class="section">
                    <h2 class="section-title">Education</h2>
                    <ul>
                        {"".join([f'<li>{bullet.strip()}</li>' for bullet in resume_data['education'].split('\n') if bullet.strip()])}
                    </ul>
                </div>
                """
            elif section == "projects" and resume_data.get("projects"):
                html += """
                <div class="section">
                    <h2 class="section-title">Projects</h2>
                    <ul>
                """
                for project in resume_data["projects"]:
                    html += f'<li>{project}</li>'
                html += """
                    </ul>
                </div>
                """
        
        html += """
        </body>
        </html>
        """
        return html
    except Exception as e:
        raise Exception(f"Error generating HTML resume: {str(e)}")

def generate_experience_based_resume(resume: str, job_description: str, experience_level: str) -> str:
    """
    Generate resume with different formats based on experience level
    """
    try:
        if experience_level == 'senior':
            template = """
            Create an ATS-optimized resume for a senior candidate (4+ years experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Work Experience (detailed with achievements and metrics)
            5. Key Projects (showcasing impact and leadership)
            6. Education (brief section at end)
            
            Return the resume in HTML format with professional styling. Focus on leadership, achievements, and impact.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        elif experience_level == 'mid':
            template = """
            Create an ATS-optimized resume for a mid-level candidate (1-3 years experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Work Experience (detailed with achievements)
            5. Skills (technical skills relevant to the job)
            6. Education (brief section at end)
            
            Return the resume in HTML format with clean styling. Focus on skills and contributions.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        elif experience_level == 'junior':
            template = """
            Create an ATS-optimized resume for a junior candidate (<1 year experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Education (detailed with relevant coursework)
            5. Skills (technical skills with proficiency levels)
            6. Work Experience (if any, otherwise academic projects)
            7. Projects (academic or personal projects)
            
            Return the resume in HTML format with modern styling. Focus on education and potential.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        else:  # fresher
            template = """
            Create an ATS-optimized resume for a fresher (no experience) with this structure:
            1. Name (large font, centered)
            2. Contact info (single line below name: email | phone | LinkedIn)
            3. Professional Summary (tailored to the job description)
            4. Education (detailed with relevant coursework)
            5. Skills (technical skills with proficiency levels)
            6. Projects (academic or personal projects)
            
            Return the resume in HTML format with modern styling. Focus on education and potential.
            Include all sections even if empty.
            
            Resume Content:
            {resume}
            
            Job Description:
            {jd}
            """
        
        resume_prompt = PromptTemplate.from_template(template)
        chain = LLMChain(llm=llm, prompt=resume_prompt)
        
        # Get the HTML content from the LLM
        html_content = chain.run(resume=resume, jd=job_description)
        
        # Parse the HTML to ensure it's valid and get structured data
        resume_data = parse_html_resume(html_content)
        
        # Generate the final HTML with proper template
        return generate_html_resume(resume_data)
    except Exception as e:
        raise Exception(f"Error in generate_experience_based_resume: {str(e)}")
def get_resume_template(template_name: str, experience_years: float) -> tuple[dict, str, list]:
    """Get template by name and determine experience level with section order and CSS"""
    templates = {
        "professional": {
            "css": """
                body { font-family: 'Calibri', sans-serif;background-color:white; }
                .name { color: #2a5f8a; font-size: 28px; }
                .section-title { color: #2a5f8a; border-bottom: 2px solid #2a5f8a; }
                .skill-tag { background: #e6f2ff; color: #2a5f8a; }
            """
        },
        "modern": {
            "css": """
                body { font-family: 'Segoe UI', sans-serif;background-color:white; }
                .name { color: #4CAF50; font-size: 28px; }
                .section-title { color: #4CAF50; border-bottom: 2px solid #4CAF50; }
                .skill-tag { background: #e8f5e9; color: #2E7D32; }
            """
        },
        # Add other templates with their CSS here
    }
    
    # Get the requested template or default to professional
    template = templates.get(template_name, templates["professional"])
    
    # Determine experience level and section order
    if experience_years >= 4:
        exp_level = "senior"
        section_order = ["summary", "experience", "projects", "skills", "education"]
    elif experience_years >= 1:
        exp_level = "mid"
        section_order = ["summary", "skills", "experience", "education"]
    else:
        exp_level = "fresher"
        section_order = ["summary", "education", "skills", "projects"]
    
    return template, exp_level, section_order


def generate_tailored_resume(resume: str, job_description: str, template_id: str = "professional") -> str:
    """
    Generate a resume tailored to the candidate's experience level and job description
    """
    try:
        experience_level = detect_experience_level(resume)
        section_order = get_section_order(experience_level)
        
        prompt = PromptTemplate.from_template("""
        Create an ATS-optimized resume based on the following resume content and job description.
        The candidate is a {experience_level} level professional.
        
        Structure the resume in this order:
        {section_order}
        
        Include these sections:
        - Name and contact info at top
        - Professional summary tailored to the job
        - Work experience with achievements and metrics (if applicable)
        - Education (include relevant coursework if entry-level)
        - Skills (technical and soft skills)
        - Projects (academic or professional)
        
        Return the resume in HTML format with clean, professional styling.
        Use semantic HTML tags and include CSS styling in the head section.
        
        Resume Content:
        {resume}
        
        Job Description:
        {jd}
        """)
        
        chain = LLMChain(llm=llm, prompt=prompt)
        html_content = chain.run(
            resume=resume,
            jd=job_description,
            experience_level=experience_level,
            section_order=", ".join(section_order)
        )
        
        # Apply the selected template
        return apply_resume_template(html_content, template_id)
    except Exception as e:
        raise Exception(f"Error generating tailored resume: {str(e)}")

def detect_experience_level(resume_text: str) -> str:
    """
    Detect experience level from resume text
    Returns: 'fresher', 'junior', 'mid', or 'senior'
    """
    try:
        exp_prompt = PromptTemplate.from_template("""
        Analyze this resume and determine the candidate's experience level:
        - 'fresher' if no experience
        - 'junior' if less than 1 year experience
        - 'mid' if 1-3 years experience
        - 'senior' if 4+ years experience
        
        Return only one of these four words in lowercase.
        
        Resume:
        {resume}
        """)
        
        exp_chain = LLMChain(llm=llm, prompt=exp_prompt)
        level = exp_chain.run(resume=resume_text).strip().lower()
        return level if level in ['fresher', 'junior', 'mid', 'senior'] else 'mid'
    except Exception:
        return 'mid'

def clean_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

def text_to_pdf(text: str) -> bytes:
    try:
        if isinstance(text, (bytes, bytearray)):
            return bytes(text)
        
        if "<html" in text.lower():
            return html_to_pdf(text)

        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)
        
        pdf.set_font("Arial", size=10)
        text = clean_text(text)
        lines = text.split('\n')
        
        for line in lines:
            pdf.multi_cell(0, 10, line)

        buffer = io.BytesIO()
        pdf.output(buffer)
        return buffer.getvalue()
    except Exception as e:
        print(f"Error converting text to PDF: {str(e)}")
        return b""

def html_to_pdf(html_content: str) -> bytes:
    """Convert HTML content to PDF bytes using pdfkit"""
    try:
        import pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': ''
        }
        
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        return pdf_bytes
        
    except ImportError:
        # Fallback to FPDF if pdfkit not available
        try:
            from xhtml2pdf import pisa
            from io import BytesIO
            
            pdf_bytes = BytesIO()
            pisa.CreatePDF(html_content, dest=pdf_bytes)
            return pdf_bytes.getvalue()
            
        except ImportError:
            # Final fallback - create simple text PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            
            # Clean HTML and convert to text
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text("\n")
            text = clean_text(text)
            
            # Add text to PDF
            for line in text.split('\n'):
                if line.strip():
                    pdf.multi_cell(0, 5, line)
            
            # Return PDF bytes
            return pdf.output(dest='S').encode('latin-1')
    
def parse_html_resume(html_content: str) -> dict:
    """Parse HTML resume into structured data for the visual editor"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        resume_data = {
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
        
        # Extract name (usually in h1 or .name class)
        name_tag = soup.find('h1') or soup.find(class_='name')
        if name_tag:
            resume_data['name'] = name_tag.get_text().strip()
        
        # Extract contact info (usually in the header)
        header = soup.find(class_='header') or soup.find('p')
        if header:
            contact_text = header.get_text()
            if "|" in contact_text:
                parts = [part.strip() for part in contact_text.split("|")]
                for part in parts:
                    if "@" in part and "." in part:
                        resume_data['email'] = part.strip()
                    elif part.startswith("http"):
                        resume_data['linkedin'] = part.strip()
                    elif any(c.isdigit() for c in part.replace(" ", "").replace("-", "")):
                        resume_data['phone'] = part.strip()
        
        # Extract summary
        for tag in soup.find_all(['h2', 'h3']):
            if 'summary' in tag.get_text().lower():
                next_tag = tag.find_next(['p', 'div'])
                if next_tag:
                    resume_data['summary'] = next_tag.get_text().strip()
                break
        
        # Extract skills
        for tag in soup.find_all(['h2', 'h3']):
            if 'skill' in tag.get_text().lower():
                skills_container = tag.find_next(['ul', 'div'])
                if skills_container:
                    if skills_container.name == 'ul':
                        resume_data['skills'] = [li.get_text().strip() for li in skills_container.find_all('li')]
                    elif skills_container.name == 'div' and 'skills' in skills_container.get('class', []):
                        resume_data['skills'] = [span.get_text().strip() for span in skills_container.find_all('span', class_='skill-tag')]
                break
        
        # Extract experience
        for tag in soup.find_all(['h2', 'h3']):
            if 'experience' in tag.get_text().lower():
                exp_items = []
                current_item = tag.find_next(['div', 'h4'])
                while current_item and 'experience' in current_item.find_previous(['h2', 'h3']).get_text().lower():
                    if current_item.name == 'h4':
                        exp_data = {
                            "title": current_item.get_text().strip(),
                            "company": "",
                            "duration": "",
                            "description": ""
                        }
                        
                        # Get company (usually next p or span)
                        company_tag = current_item.find_next(['p', 'span'])
                        if company_tag:
                            exp_data['company'] = company_tag.get_text().strip()
                        
                        # Get duration (often in same p as company or next p)
                        duration_tag = company_tag.find_next(['p', 'span']) if company_tag else None
                        if duration_tag and ("-" in duration_tag.get_text() or "present" in duration_tag.get_text().lower()):
                            exp_data['duration'] = duration_tag.get_text().strip()
                        
                        # Get description (usually ul or next p)
                        desc_tag = duration_tag.find_next(['ul', 'p']) if duration_tag else None
                        if desc_tag:
                            if desc_tag.name == 'ul':
                                exp_data['description'] = "\n".join([f"- {li.get_text().strip()}" for li in desc_tag.find_all('li')])
                            else:
                                exp_data['description'] = desc_tag.get_text().strip()
                        
                        exp_items.append(exp_data)
                    current_item = current_item.find_next(['div', 'h4'])
                resume_data['experience'] = exp_items
                break
        
        # Extract education
        for tag in soup.find_all(['h2', 'h3']):
            if 'education' in tag.get_text().lower():
                edu_tag = tag.find_next(['p', 'ul'])
                if edu_tag:
                    if edu_tag.name == 'ul':
                        resume_data['education'] = "\n".join([f"- {li.get_text().strip()}" for li in edu_tag.find_all('li')])
                    else:
                        resume_data['education'] = edu_tag.get_text().strip()
                break
        
        # Extract projects
        for tag in soup.find_all(['h2', 'h3']):
            if 'project' in tag.get_text().lower():
                projects_tag = tag.find_next(['ul', 'div'])
                if projects_tag:
                    if projects_tag.name == 'ul':
                        resume_data['projects'] = "\n".join([f"- {li.get_text().strip()}" for li in projects_tag.find_all('li')])
                    else:
                        resume_data['projects'] = projects_tag.get_text().strip()
                break
        
        return resume_data
    except Exception as e:
        print(f"Error parsing HTML resume: {str(e)}")
        return {
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

def update_html_resume(resume_data: dict, template_name: str = "professional") -> str:
    """Update HTML resume based on edited visual form data"""
    try:
        return generate_html_resume(resume_data, template_name)
    except Exception as e:
        print(f"Error updating HTML resume: {str(e)}")
        return ""
    
def update_resume_continuously(resume_data: dict, template_id: str = "professional") -> str:
    """Continuously update resume HTML based on changes"""
    try:
        # Generate the base HTML resume
        html_content = generate_html_resume(resume_data)
        
        # Apply the selected template styling
        styled_html = apply_resume_template(html_content, template_id)
        
        
        return styled_html
    except Exception as e:
        print(f"Error updating resume: {str(e)}")
        return ""
    
    
def generate_visual_editor(resume_data: dict) -> str:
    """Generate a visual form editor for the resume"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Resume Editor</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                line-height: 1.6; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 20px;
                background-color: white;
                color: black;
            }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ 
                display: block; 
                margin-bottom: 5px; 
                font-weight: bold;
                color: black;
            }}
            input[type="text"], textarea {{ 
                width: 100%; 
                padding: 8px; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                background-color: white;
                color: black;
            }}
            textarea {{ min-height: 100px; }}
            .section {{ 
                margin-bottom: 30px; 
                border: 1px solid #eee; 
                padding: 15px; 
                border-radius: 5px;
                background-color: white;
            }}
            .section-title {{ 
                font-size: 18px; 
                margin-top: 0; 
                color: black;
            }}
            .skill-tag {{ 
                background: #f0f0f0; 
                padding: 3px 8px; 
                border-radius: 3px; 
                display: inline-block; 
                margin-right: 5px; 
                margin-bottom: 5px;
                color: black;
            }}
            .add-btn {{ 
                background: #4CAF50; 
                color: white; 
                border: none; 
                padding: 5px 10px; 
                border-radius: 3px; 
                cursor: pointer; 
            }}
            .remove-btn {{ 
                background: #f44336; 
                color: white; 
                border: none; 
                padding: 2px 5px; 
                border-radius: 3px; 
                cursor: pointer; 
                margin-left: 5px; 
            }}
            .preview-btn {{ 
                background: #2196F3; 
                color: white; 
                padding: 10px 15px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 16px; 
            }}
        </style>
    </head>
    <body>
        <h1 style="color: black;">Resume Editor</h1>
        
        <div class="section">
            <h2 class="section-title">Personal Information</h2>
            <div class="form-group">
                <label for="name">Full Name</label>
                <input type="text" id="name" value="{resume_data.get('name', '')}">
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="text" id="email" value="{resume_data.get('email', '')}">
            </div>
            <div class="form-group">
                <label for="phone">Phone</label>
                <input type="text" id="phone" value="{resume_data.get('phone', '')}">
            </div>
            <div class="form-group">
                <label for="linkedin">LinkedIn URL</label>
                <input type="text" id="linkedin" value="{resume_data.get('linkedin', '')}">
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Summary</h2>
            <div class="form-group">
                <textarea id="summary">{resume_data.get('summary', '')}</textarea>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Skills</h2>
            <div id="skills-container">
                {"".join([f'<span class="skill-tag">{skill}<button class="remove-btn" onclick="removeSkill(this)">×</button></span>' for skill in resume_data.get('skills', [])])}
            </div>
            <div class="form-group" style="margin-top: 10px;">
                <input type="text" id="new-skill" placeholder="Add new skill">
                <button class="add-btn" onclick="addSkill()">Add Skill</button>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Experience</h2>
            <div id="experience-container">
                {"".join([f"""
                <div class="experience-item" style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
                    <div class="form-group">
                        <label>Job Title</label>
                        <input type="text" class="exp-title" value="{exp.get('title', '')}">
                    </div>
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" class="exp-company" value="{exp.get('company', '')}">
                    </div>
                    <div class="form-group">
                        <label>Duration</label>
                        <input type="text" class="exp-duration" value="{exp.get('duration', '')}">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea class="exp-description">{exp.get('description', '')}</textarea>
                    </div>
                    <button class="remove-btn" onclick="this.parentElement.remove()">Remove Experience</button>
                </div>
                """ for exp in resume_data.get('experience', [])])}
            </div>
            <button class="add-btn" onclick="addExperience()">Add Experience</button>
        </div>

        <div class="section">
            <h2 class="section-title">Education</h2>
            <div class="form-group">
                <label for="education">Education Details</label>
                <textarea id="education">{resume_data.get('education', '')}</textarea>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Projects</h2>
            <div class="form-group">
                <label for="projects">Project Details</label>
                <textarea id="projects">{resume_data.get('projects', '')}</textarea>
            </div>
        </div>

        <button class="preview-btn" onclick="updateResume()">Update Resume</button>

        <script>
            function addSkill() {{
                const skillInput = document.getElementById('new-skill');
                if (skillInput.value.trim() === '') return;
                
                const skillTag = document.createElement('span');
                skillTag.className = 'skill-tag';
                skillTag.innerHTML = `${{skillInput.value.trim()}}<button class="remove-btn" onclick="removeSkill(this)">×</button>`; 
                
                document.getElementById('skills-container').appendChild(skillTag);
                skillInput.value = '';
                updateResume();
            }}

            function removeSkill(button) {{
                button.parentElement.remove();
                updateResume();
            }}

            function addExperience() {{
                const expHtml = ` 
                <div class="experience-item" style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
                    <div class="form-group">
                        <label>Job Title</label>
                        <input type="text" class="exp-title" placeholder="Software Developer">
                    </div>
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" class="exp-company" placeholder="ABC Corp">
                    </div>
                    <div class="form-group">
                        <label>Duration</label>
                        <input type="text" class="exp-duration" placeholder="Jan 2020 - Present">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea class="exp-description" placeholder="Your responsibilities and achievements"></textarea>
                    </div>
                    <button class="remove-btn" onclick="this.parentElement.remove()">Remove Experience</button>
                </div>`;
                
                document.getElementById('experience-container').insertAdjacentHTML('beforeend', expHtml);
                updateResume();
            }}

            function updateResume() {{
                const resumeData = {{
                    name: document.getElementById('name').value,
                    email: document.getElementById('email').value,
                    phone: document.getElementById('phone').value,
                    linkedin: document.getElementById('linkedin').value,
                    summary: document.getElementById('summary').value,
                    skills: Array.from(document.querySelectorAll('.skill-tag')).map(el => el.textContent.replace('×', '').trim()),
                    experience: Array.from(document.querySelectorAll('.experience-item')).map(item => ({{
                        title: item.querySelector('.exp-title').value,
                        company: item.querySelector('.exp-company').value,
                        duration: item.querySelector('.exp-duration').value,
                        description: item.querySelector('.exp-description').value
                    }})),
                    education: document.getElementById('education').value,
                    projects: document.getElementById('projects').value
                }};
                
                window.parent.postMessage({{
                    type: 'UPDATE_RESUME',
                    data: resumeData
                }}, '*');
            }}

            document.querySelectorAll('input, textarea').forEach(element => {{
                element.addEventListener('input', updateResume);
            }});

            const observer = new MutationObserver(updateResume);
            observer.observe(document.getElementById('skills-container'), {{ 
                childList: true, 
                subtree: true 
            }});
            observer.observe(document.getElementById('experience-container'), {{ 
                childList: true, 
                subtree: true 
            }});
        </script>
    </body>
    </html>
    """
    return html_template

# Add these new functions to your existing backend code

def get_public_templates() -> List[Dict]:
    """Return templates that users can select and customize"""
    return [
        {
            "id": "professional",
            "name": "Professional Blue",
            "description": "Clean, corporate design with blue accents",
            "category": "all",
            "preview": "professional_preview.html"
        },
        {
            "id": "modern",
            "name": "Modern Green",
            "description": "Contemporary design with green accents",
            "category": "all",
            "preview": "modern_preview.html"
        },
        {
            "id": "minimal",
            "name": "Minimal Black",
            "description": "Ultra-clean black and white design",
            "category": "all",
            "preview": "minimal_preview.html"
        }
    ]

def save_custom_template(user_id: str, template_name: str, template_content: str) -> bool:
    """Save a custom template for a user"""
    try:
        if not os.path.exists('user_templates'):
            os.makedirs('user_templates')
            
        file_path = f"user_templates/{user_id}_{template_name}.html"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        return True
    except Exception as e:
        print(f"Error saving template: {str(e)}")
        return False

def get_custom_templates(user_id: str) -> List[Dict]:
    """Get all custom templates for a user"""
    templates = []
    if os.path.exists('user_templates'):
        for filename in os.listdir('user_templates'):
            if filename.startswith(user_id + "_"):
                template_name = filename[len(user_id)+1:-5]  # Remove userid_ and .html
                templates.append({
                    "id": filename,
                    "name": template_name.replace('_', ' '),
                    "description": f"Custom template by {user_id}",
                    "category": "custom"
                })
    return templates

def get_template_preview(template_id: str) -> str:
    """Get HTML preview of a template"""
    if template_id in TEMPLATE_STORAGE:
        return TEMPLATE_STORAGE[template_id]["content"]
    
    # Check for custom templates
    if os.path.exists('user_templates'):
        file_path = f"user_templates/{template_id}"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    return ""
# Add this to your existing backend code
def get_prebuilt_resumes() -> List[Dict]:
    """Return simplified pre-built resume templates with text structure"""
    return [
        {
            "id": "professional",
            "name": "Professional Resume",
            "description": "Standard format for corporate jobs",
            "category": "all",
            "structure": {
                "sections": ["summary", "experience", "skills", "education"],
                "experience_format": "detailed"
            }
        },
        
        {
            "id": "modern",
            "name": "Modern Resume",
            "description": "Contemporary design with skills focus",
            "category": "all",
            "structure": {
                "sections": ["summary", "skills", "experience", "education"],
                "experience_format": "concise"
            }
        },
        {
            "id": "fresher",
            "name": "Fresher Resume",
            "description": "For students and entry-level candidates",
            "category": "fresher",
            "structure": {
                "sections": ["summary", "education", "skills", "projects"],
                "experience_format": "simple"
            }
        }
    ]

def get_prebuilt_resume_content(resume_id: str) -> Dict:
    """Get sample content structure for a pre-built resume"""
    samples = {
        "professional": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(123) 456-7890",
            "linkedin": "linkedin.com/in/johndoe",
            "summary": "Experienced software engineer with 5+ years in full-stack development...",
            "skills": ["Python", "JavaScript", "SQL", "AWS"],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2020-Present",
                    "description": "Lead development team...\nImproved system performance..."
                }
            ],
            "education": "BSc Computer Science, University X, 2019"
        },
        "modern": {
            "name": "Jane Smith",
            "summary": "Innovative designer with UX/UI expertise...",
            "skills": ["Figma", "Adobe XD", "HTML/CSS", "User Research"],
            "experience": [
                {
                    "title": "UX Designer",
                    "company": "Design Studio",
                    "duration": "2021-Present",
                    "description": "Redesigned mobile app interface..."
                }
            ],
            "education": "BA Design, Art College, 2020"
        },
        "fresher": {
            "name": "Alex Johnson",
            "summary": "Recent computer science graduate seeking entry-level position...",
            "skills": ["Java", "Python", "Data Structures"],
            "education": "BSc Computer Science, State University, 2023",
            "projects": [
                "E-commerce website - Full stack project with React and Node.js",
                "Library management system - Java application with MySQL"
            ]
        }
    }
    return samples.get(resume_id, {})

def generate_resume_html(resume_data: Dict, template_id: str) -> str:
    """Convert structured resume data to HTML based on template"""
    template = get_prebuilt_resumes()[0]  # Default to first template
    for t in get_prebuilt_resumes():
        if t["id"] == template_id:
            template = t
            break
    
    # Generate HTML based on template structure
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{resume_data.get('name', 'Resume')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background-color:white; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .name {{ font-size: 24px; font-weight: bold; }}
            .section {{ margin-bottom: 20px; }}
            .section-title {{ font-weight: bold; font-size: 18px; border-bottom: 1px solid #ddd; }}
            .job-header {{ display: flex; justify-content: space-between; }}
            .skills {{ display: flex; flex-wrap: wrap; gap: 8px; }}
            .skill-tag {{ background: #f0f0f0; padding: 4px 8px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="name">{resume_data.get('name', 'Your Name')}</div>
            <div class="contact-info">
                {resume_data.get('email', '')} | {resume_data.get('phone', '')} | {resume_data.get('linkedin', '')}
            </div>
        </div>
    """
    
    # Add sections based on template structure
    for section in template["structure"]["sections"]:
        if section == "summary" and resume_data.get("summary"):
            html += f"""
            <div class="section">
                <h2 class="section-title">Summary</h2>
                <p>{resume_data['summary']}</p>
            </div>
            """
        elif section == "skills" and resume_data.get("skills"):
            html += f"""
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills">
                    {"".join([f'<span class="skill-tag">{skill}</span>' for skill in resume_data['skills']])}
                </div>
            </div>
            """
        elif section == "experience" and resume_data.get("experience"):
            html += """
            <div class="section">
                <h2 class="section-title">Experience</h2>
            """
            for exp in resume_data["experience"]:
                html += f"""
                <div class="job">
                    <div class="job-header">
                        <div>
                            <span class="job-title">{exp.get('title', '')}</span>
                            <span class="company">, {exp.get('company', '')}</span>
                        </div>
                        <span class="job-duration">{exp.get('duration', '')}</span>
                    </div>
                    <ul>
                        {"".join([f'<li>{bullet.strip()}</li>' for bullet in exp.get('description', '').split('\n') if bullet.strip()])}
                    </ul>
                </div>
                """
            html += "</div>"
        elif section == "education" and resume_data.get("education"):
            html += f"""
            <div class="section">
                <h2 class="section-title">Education</h2>
                <p>{resume_data['education']}</p>
            </div>
            """
        elif section == "projects" and resume_data.get("projects"):
            html += """
            <div class="section">
                <h2 class="section-title">Projects</h2>
                <ul>
            """
            for project in resume_data["projects"]:
                html += f'<li>{project}</li>'
            html += """
                </ul>
            </div>
            """
    
    html += """
    </body>
    </html>
    """
    return html 



def generate_resume_from_form(form_data: dict, template_id: str = "professional") -> str:
    """Generate resume HTML from form data using specified template"""
    try:
        # Ensure all sections exist even if empty
        form_data.setdefault("name", "Your Name")
        form_data.setdefault("email", "")
        form_data.setdefault("phone", "")
        form_data.setdefault("linkedin", "")
        form_data.setdefault("summary", "")
        form_data.setdefault("skills", [])
        form_data.setdefault("experience", [])
        form_data.setdefault("education", "")
        form_data.setdefault("projects", "")

        # Generate base HTML
        html_content = generate_html_resume(form_data)
        
        # Apply template styling
        styled_html = apply_resume_template(html_content, template_id)
        
        return styled_html
    except Exception as e:
        raise Exception(f"Error generating resume from form: {str(e)}")

def edit_template_content(template_id: str, new_content: str) -> bool:
    """Update template content in storage"""
    if template_id in TEMPLATE_STORAGE:
        TEMPLATE_STORAGE[template_id]["content"] = new_content
        return True
    return False


{

}
def generate_sample_resume(template_id: str = "professional") -> str:
    """
    Generate a sample resume for users to edit
    """
    sample_content = """
    <div class="header">
        <div class="name">YOUR NAME HERE</div>
        <p>
            your.email@example.com | 
            (123) 456-7890 | 
            linkedin.com/in/yourprofile
        </p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Summary</h2>
        <p>Professional summary highlighting your key qualifications and career goals.</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Skills</h2>
        <div class="skills">
            <span class="skill-tag">Skill 1</span>
            <span class="skill-tag">Skill 2</span>
            <span class="skill-tag">Skill 3</span>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Experience</h2>
        <div class="job">
            <div class="job-header">
                <h3>Job Title</h3>
                <p>Company Name</p>
            </div>
            <p>Month Year - Present</p>
            <ul>
                <li>Responsibility or achievement 1</li>
                <li>Responsibility or achievement 2</li>
            </ul>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">Education</h2>
        <p><strong>Degree Name</strong>, University Name, Graduation Year</p>
    </div>
    """
    
    html_template = generate_html_resume(sample_content)
    return apply_resume_template(html_template, template_id)