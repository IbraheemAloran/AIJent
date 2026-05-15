import gradio as gr
import asyncio
from Resume_parser.parser_mcp_server import ResumeParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import json
import os
from datetime import datetime
from langchain.agents import create_agent
from Embedder.embedding_mcp_server import embed_profile

load_dotenv()

# ============= Global State =============
conversation_history = []
user_profile = {
    "location": "",
    "current_company": "",
    "skills": ["Python", "JavaScript", "AI/ML"],
    "experience": "5 years",
    "job_preference": "Remote AI Engineer",
    "canadian_citizen": False,
    "usa_citizen": False,
    "gender": "",
    "ethnicity": "",
    "disability": False,
    "veteran_status": False,
    "target_salary": "",
    "earliest_start_date": "",
    "willing_to_relocate": False
}

resume_data = {}
analytics_data = {
    "total_applications": 0,
    "interviews_scheduled": 0,
    "offers_received": 0,
    "response_rate": "0%",
    "top_skills": ["Python", "Machine Learning", "REST APIs"],
    "job_matches": 15
}

# ============= Resume Upload & Parsing =============
def parse_resume(file):
    """Parse uploaded resume"""
    try:
        if file is None:
            return "No file uploaded"        
 
        # Parse resume
        parser = ResumeParser()
        parser.parse(file)
        result = embed_profile()

        
        global resume_data
        resume_data = result if isinstance(result, dict) else {"parsed": str(result)}
        
        return json.dumps(resume_data, indent=2)
    except Exception as e:
        return f"Error parsing resume: {str(e)}"

# ============= Profile Management =============
def update_profile(location, current_company, experience, job_preference, canadian_citizen, usa_citizen, gender, ethnicity, disability, veteran_status, target_salary, earliest_start_date, willing_to_relocate):
    """Update user profile"""
    global user_profile
    
    user_profile = {
        "location": location,
        "current_company": current_company,
        "years_of_exp": experience,
        "job_preference": job_preference,
        "canadian_citizen": canadian_citizen,
        "usa_citizen": usa_citizen,
        "gender": gender,
        "ethnicity": ethnicity,
        "disability": disability,
        "veteran_status": veteran_status,
        "target_salary": target_salary,
        "earliest_start_date": earliest_start_date,
        "willing_to_relocate": willing_to_relocate
    }
    with open("profile.json", "rb") as f:
        data = json.load(f)
    
    data.update(user_profile)

    with open("profile.json", "w") as f:
        json.dump(data, f, indent=2)



    
    return f"✅ Profile updated successfully!\n\n{json.dumps(data, indent=2)}"

def get_profile_data():
    """Return current profile data for display"""
    return (
        user_profile.get("name", ""),
        user_profile.get("email", ""),
        ", ".join(user_profile.get("skills", [])),
        user_profile.get("experience", ""),
        user_profile.get("job_preference", "")
    )

# ============= Analytics =============
def update_analytics(applications, interviews, offers):
    """Update analytics data"""
    global analytics_data
    
    analytics_data["total_applications"] = int(applications)
    analytics_data["interviews_scheduled"] = int(interviews)
    analytics_data["offers_received"] = int(offers)
    
    # Calculate response rate
    if int(applications) > 0:
        response_rate = (int(interviews) / int(applications)) * 100
        analytics_data["response_rate"] = f"{response_rate:.1f}%"
    
    return generate_analytics_display()

def generate_analytics_display():
    """Generate formatted analytics display"""
    stats = f"""
    📊 Job Search Analytics
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📨 Total Applications: {analytics_data['total_applications']}
    📅 Interviews Scheduled: {analytics_data['interviews_scheduled']}
    🎉 Offers Received: {analytics_data['offers_received']}
    
    📈 Response Rate: {analytics_data['response_rate']}
    🎯 Job Matches Found: {analytics_data['job_matches']}
    
    💡 Top Skills:
    """
    for skill in analytics_data["top_skills"]:
        stats += f"\n       • {skill}"
    
    return stats

# ============= Chat with Model =============
def trim_message_history(keep_last=2):
    """Keep only last N messages"""
    global conversation_history
    if len(conversation_history) > keep_last:
        conversation_history = conversation_history[-keep_last:]

from gradio import ChatMessage


async def chat_with_agent(user_message, chat_history):
    """Chat with AI agent for job search"""
    try:
        if not user_message.strip():
            return chat_history
        
        # Add user message to history
        conversation_history.append(HumanMessage(content=user_message))
        trim_message_history(keep_last=2)
        
        # Initialize model
        model = ChatGoogleGenerativeAI(model="gemma-4-31b-it")
        agent = create_agent(
            model=model,
                # system_prompt="You are a job search agent. Use your tools to search and return jobs. Search for all jobs on https://hiring.cafe/. the website does not have a search button, you will have to type in the search bar and click the drop down menu that appears to search. Return one job posting",
            system_prompt="You are a chatbot."
        )
        
        
        # Create messages for the model (with trimmed history)
        messages_for_model = [HumanMessage(content=user_message)]
        
        # Get response from model
        response = await agent.ainvoke(
            {"messages": messages_for_model},
            
        )
        assistant_message = response['messages'][-1].content[-1]

        
        
    
        
        # Update chat history for display (Gradio expects tuples)
        chat_history.append({"role": "user", "content": assistant_message})
        chat_history.append({"role": "assistant", "content": assistant_message})
        
        return chat_history
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        chat_history.append((user_message, error_msg))
        return chat_history

def chat_wrapper(user_message, chat_history):
    """Wrapper to handle async chat"""
    return asyncio.run(chat_with_agent(user_message, chat_history))

# ============= Gradio Interface =============
def create_interface():
    """Create Gradio interface with tabs"""
    
    with gr.Blocks(title="AIJent - Job Search Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🤖 AIJent - Intelligent Job Search Assistant")
        gr.Markdown("Your AI-powered companion for finding the perfect job")
        
        with gr.Tabs():
            # ========== Resume & Profile Tab ==========
            with gr.Tab("📄 Resume & Profile"):
                gr.Markdown("### Manage Your Resume and Profile")
                
                with gr.Row():
                    # ===== LEFT SIDE: Resume Upload =====
                    with gr.Column():
                        gr.Markdown("#### 📤 Upload Resume")
                        resume_file = gr.File(
                            label="Upload Resume (PDF/DOCX/TXT)",
                            file_types=[".pdf", ".docx", ".txt"]
                        )
                        parse_btn = gr.Button("📤 Parse Resume", variant="primary", size="lg")
                        
                        resume_output = gr.Textbox(
                            label="Parsed Resume Data",
                            lines=20,
                            interactive=False
                        )
                        
                        parse_btn.click(
                            fn=parse_resume,
                            inputs=resume_file,
                            outputs=resume_output
                        )
                    
                    # ===== RIGHT SIDE: Profile Management =====
                    with gr.Column():
                        gr.Markdown("#### 👤 Your Profile")
                        
                        # Basic Info
                        profile_location = gr.Textbox(
                            label="Location",
                            value=user_profile.get("location", "")
                        )
                        profile_current_company = gr.Textbox(
                            label="Current Company",
                            value=user_profile.get("current_company", "")
                        )
                        
                    
                        profile_experience = gr.Textbox(
                            label="Years of Experience",
                            value=user_profile.get("experience", "")
                        )
                        profile_job_pref = gr.Textbox(
                            label="Job Preference",
                            value=user_profile.get("job_preference", "")
                        )
                        
                        # Citizenship
                        profile_canadian_citizen = gr.Checkbox(
                            label="Canadian Citizen",
                            value=user_profile.get("canadian_citizen", False)
                        )
                        profile_usa_citizen = gr.Checkbox(
                            label="USA Citizen",
                            value=user_profile.get("usa_citizen", False)
                        )
                        
                        # Demographics
                        profile_gender = gr.Dropdown(
                            choices=["", "Male", "Female", "Non-binary", "Prefer not to say"],
                            label="Gender",
                            value=user_profile.get("gender", "")
                        )
                        profile_ethnicity = gr.Dropdown(
                            choices=["", "Asian", "Black", "Hispanic/Latino", "Middle Eastern/North African", "Native American/Alaska Native", "Native Hawaiian/Pacific Islander", "White", "Multiracial", "Prefer not to say"],
                            label="Ethnicity",
                            value=user_profile.get("ethnicity", "")
                        )
                        profile_disability = gr.Checkbox(
                            label="Person with Disability",
                            value=user_profile.get("disability", False)
                        )
                        profile_veteran = gr.Checkbox(
                            label="Veteran Status",
                            value=user_profile.get("veteran_status", False)
                        )
                        
                        # Job Details
                        profile_target_salary = gr.Textbox(
                            label="Target Salary (e.g., 80k-100k)",
                            value=user_profile.get("target_salary", "")
                        )
                        profile_start_date = gr.Textbox(
                            label="Earliest Start Date",
                            value=user_profile.get("earliest_start_date", "")
                        )
                        profile_willing_relocate = gr.Checkbox(
                            label="Willing to Relocate",
                            value=user_profile.get("willing_to_relocate", False)
                        )
                        
                        update_profile_btn = gr.Button(
                            "💾 Save Profile",
                            variant="primary",
                            size="lg"
                        )
                        
                        profile_output = gr.Textbox(
                            label="Profile Status",
                            interactive=False,
                            lines=10
                        )
                        
                        update_profile_btn.click(
                            fn=update_profile,
                            inputs=[
                                profile_location,
                                profile_current_company,
                                profile_experience,
                                profile_job_pref,
                                profile_canadian_citizen,
                                profile_usa_citizen,
                                profile_gender,
                                profile_ethnicity,
                                profile_disability,
                                profile_veteran,
                                profile_target_salary,
                                profile_start_date,
                                profile_willing_relocate
                            ],
                            outputs=profile_output
                        )
            
            # ========== Analytics Tab ==========
            with gr.Tab("📊 Analytics"):
                gr.Markdown("### Job Search Analytics Dashboard")
                
                with gr.Row():
                    with gr.Column():
                        applications_input = gr.Number(
                            label="Total Applications",
                            value=analytics_data["total_applications"],
                            precision=0
                        )
                        interviews_input = gr.Number(
                            label="Interviews Scheduled",
                            value=analytics_data["interviews_scheduled"],
                            precision=0
                        )
                        offers_input = gr.Number(
                            label="Offers Received",
                            value=analytics_data["offers_received"],
                            precision=0
                        )
                        update_analytics_btn = gr.Button(
                            "📈 Update Analytics",
                            variant="primary"
                        )
                    
                    with gr.Column():
                        analytics_output = gr.Textbox(
                            label="Analytics Summary",
                            value=generate_analytics_display(),
                            interactive=False,
                            lines=15
                        )
                
                update_analytics_btn.click(
                    fn=update_analytics,
                    inputs=[applications_input, interviews_input, offers_input],
                    outputs=analytics_output
                )
            
            # ========== Chat Tab ==========
            with gr.Tab("💬 Chat with AI"):
                gr.Markdown("### Chat with Your Job Search Assistant")
                gr.Markdown("Get personalized advice, job recommendations, and interview tips")
                
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=400,
                    show_label=True
                )
                
                with gr.Row():
                    user_input = gr.Textbox(
                        label="Your Message",
                        placeholder="Ask me about job opportunities, interview tips, resume improvements...",
                        scale=5
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Examples
                gr.Examples(
                    examples=[
                        ["What jobs match my profile?"],
                        ["How can I improve my resume for AI engineer roles?"],
                        ["Give me interview tips for senior positions"],
                        ["What skills should I learn next?"],
                    ],
                    inputs=user_input,
                    label="Example Prompts"
                )
                
                send_btn.click(
                    fn=chat_wrapper,
                    inputs=[user_input, chatbot],
                    outputs=chatbot
                ).then(
                    lambda: gr.Textbox(value=""),
                    outputs=user_input
                )
                
                user_input.submit(
                    fn=chat_wrapper,
                    inputs=[user_input, chatbot],
                    outputs=chatbot
                ).then(
                    lambda: gr.Textbox(value=""),
                    outputs=user_input
                )
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
