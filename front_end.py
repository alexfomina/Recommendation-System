# import gradio as gr
# from datetime import datetime
# import uuid
# import mysql.connector
# from db import db_ops

# # Initialize Database Operations
# db = db_ops()
# #db.delete_everything()
# #db.initialize_database()  # Ensure tables exist

# #db.create_tables() run once
# db.create_user_account("test", "password123", "Test User", "This is a test profile.")  # Add a test user

# # Functions for App Logic
# def handle_action(action, username, password, name=None, profile=None):
#     """Handles user actions for sign-up or login."""
#     if action == "Sign Up":
#         if not username or not password or not name or not profile:
#             return "⚠️ All fields are required for sign-up!", None
        
#         try:
#             db.create_user_account(username, password, name, profile)
#             return "✅ Account created successfully!", username
#         except Exception as e:
#             return f"❌ Error during sign-up: {e}", None
    
#     elif action == "Log In":
#         try:
#             if db.check_user_account(username, password):
#                 return "✅ Login successful!", username
#             else:
#                 return "❌ Invalid username or password.", None
#         except Exception as e:
#             return f"❌ Error during login: {e}", None
#     else:
#         return "❌ Invalid action.", None


# def welcome_screen():
#     """Displays the welcome screen after login or sign-up."""
#     with gr.Blocks(css=".title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as welcome:
#         with gr.Row():
#             gr.Image(value="https://via.placeholder.com/150", label="Logo", show_label=False)  # Replace with your logo URL
#         with gr.Row():
#             gr.Markdown("<div class='title'> 🧭 Welcome to CourseCompass! 🧭</div>")
#     return welcome


# def profile_screen(username):
#     """Displays the profile screen for the logged-in user."""
#     user_details = db.get_user_details(username)
#     if not user_details:
#         return gr.Markdown("❌ Unable to fetch user details.")

#     with gr.Blocks(css=".profile-title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as profile:
#         with gr.Row():
#             gr.Markdown(f"<div class='profile-title'>👤 Profile Information</div>")
#         with gr.Column():
#             gr.Markdown(f"**Username**: {user_details['Username']}")
#             gr.Markdown(f"**Name**: {user_details['Name']}")
#             gr.Markdown(f"**Profile**: {user_details['Profile']}")
#             gr.Markdown(f"**Date Created**: {user_details['DateCreated']}")
#         with gr.Row():
#             back_btn = gr.Button("Back to Welcome Screen")
#         back_btn.click(fn=lambda: welcome_screen(), inputs=None, outputs=None)
#     return profile


# # Front-End Setup
# with gr.Blocks(css=".title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as app:
#     # Header
#     with gr.Row():
#         gr.Markdown("<div class='title'>🧭 Welcome to CourseCompass 🧭</div>")
    
#     # User Action Selection
#     action = gr.Radio(["Log In", "Sign Up"], label="Choose Action", type="value", value="Log In", interactive=True)
    
#     # Input Fields
#     with gr.Row():
#         with gr.Column():
#             username = gr.Textbox(label="Username", placeholder="Enter your username", interactive=True)
#             password = gr.Textbox(label="Password", placeholder="Enter your password", type="password", interactive=True)
#             name = gr.Textbox(label="Name (Sign Up Only)", placeholder="Enter your name", visible=False, interactive=True)
#             profile = gr.Textbox(label="Profile (Sign Up Only)", placeholder="Enter your profile description", visible=False, interactive=True)
        
#         # Update visibility of name and profile fields for Sign Up
#         def update_visibility(action):
#             return (gr.update(visible=action == "Sign Up"), gr.update(visible=action == "Sign Up"))

#         action.change(fn=update_visibility, inputs=action, outputs=[name, profile])
    
#     # Submit Button and Output
#     with gr.Row():
#         submit_btn = gr.Button("Submit", elem_id="submit-button")
#     with gr.Row():
#         output = gr.Textbox(label="Message", interactive=False, lines=2)

#     # Button Click Logic
#     submit_btn.click(
#         fn=handle_action,
#         inputs=[action, username, password, name, profile],
#         outputs=[output, gr.State()]
#     ).then(
#         fn=lambda username: welcome_screen() if username else None,
#         inputs=None,
#         outputs=None,
#         show_progress=False
#     ).then(
#         fn=lambda username: profile_screen(username) if username else None,
#         inputs=None,
#         outputs=None,
#         show_progress=False
#     )

# # CSS for Styling
# app.css = """
# body {
#     background-color: #f7f9fc;
#     font-family: 'Arial', sans-serif;
# }

# .title {
#     text-align: center;
#     font-size: 2rem;
#     color: #007BFF;
#     margin-bottom: 1rem;
# }

# .gr-button {
#     background-color: #007BFF !important;
#     color: white !important;
#     border-radius: 5px !important;
#     border: none !important;
#     font-size: 1rem !important;
#     padding: 10px 20px !important;
# }

# .gr-textbox {
#     font-size: 1rem !important;
#     padding: 10px !important;
#     border: 1px solid #d1d9e6 !important;
#     border-radius: 5px !important;
# }

# .gr-radio {
#     font-size: 1rem !important;
# }

# #submit-button {
#     margin-top: 10px;
# }

# .gr-textbox .gr-box {
#     width: 100% !important;
# }
# """

# # Launch the App
# app.launch(share=True)
import gradio as gr
from db import db_ops

# Initialize Database Operations
db = db_ops()
#db.delete_everything()
#db.initialize_database()  # Ensure tables exist

#db.create_tables() run once
db.create_user_account("test_user", "password123", "Test User", "This is a test profile.")  # Add a test user
db.populate_courses('courses.csv') #run once

# Functions for App Logic

# Pages
def render_page(page):
    """Renders the selected page."""
    if page == "Home":
        return "<h1>Welcome to Home Page</h1>", gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
    elif page == "Course List":
        return "<h1>View all courses</h1>", gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
    elif page == "My Account":
        return "<h1>Welcome to your account</h1>", gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
    else:
        return "❌ Page not found.", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def handle_action(action, username, password, name=None, profile=None):
    """Handles user actions for sign-up or login."""
    if action == "Sign Up":
        if not username or not password or not name or not profile:
            return "⚠️ All fields are required for sign-up!", None
        
        try:
            db.create_user_account(username, password, name, profile)
            return "✅ Account created successfully!", "Home"
        except Exception as e:
            return f"❌ Error during sign-up: {e}", None
    
    elif action == "Log In":
        try:
            if db.check_user_account(username, password):
                return "✅ Login successful!", "Home"
            else:
                return "❌ Invalid username or password.", None
        except Exception as e:
            return f"❌ Error during login: {e}", None
    else:
        return "❌ Invalid action.", None

# Front-End Setup
with gr.Blocks(css=".title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as app:
    # State for Page Navigation
    current_page = gr.State("Login")
    
    # Header
    with gr.Row():
        gr.Markdown("<div class='title'>🧭 Welcome to CourseCompass 🧭</div>")
    
    # Dynamic Content
    content = gr.Markdown("")
    
    # Navigation Buttons
    with gr.Row(visible=False) as nav_buttons:
        gr.Button("Home").click(lambda: ("Home",) + render_page("Home"), None, [current_page, content, nav_buttons])
        gr.Button("Course List").click(lambda: ("Course List",) + render_page("Course List"), None, [current_page, content, nav_buttons])
        gr.Button("My Account").click(lambda: ("My Account",) + render_page("My Account"), None, [current_page, content, nav_buttons])
    
    # Login/Signup Section
    with gr.Row(visible=True) as auth_section:
        action = gr.Radio(["Log In", "Sign Up"], label="Choose Action", type="value", value="Log In", interactive=True)
        username = gr.Textbox(label="Username", placeholder="Enter your username", interactive=True)
        password = gr.Textbox(label="Password", placeholder="Enter your password", type="password", interactive=True)
        name = gr.Textbox(label="Name (Sign Up Only)", placeholder="Enter your name", visible=False, interactive=True)
        profile = gr.Textbox(label="Profile (Sign Up Only)", placeholder="Enter your profile description", visible=False, interactive=True)
        submit_btn = gr.Button("Submit")
        output = gr.Textbox(label="Message", interactive=False, lines=2)
    
    # Update visibility of name and profile fields for Sign Up
    def update_visibility(action):
        return gr.update(visible=action == "Sign Up"), gr.update(visible=action == "Sign Up")

    action.change(fn=update_visibility, inputs=action, outputs=[name, profile])
    
    # Button Click Logic
    submit_btn.click(
        fn=handle_action,
        inputs=[action, username, password, name, profile],
        outputs=[output, current_page]
    ).then(
        fn=render_page,
        inputs=current_page,
        outputs=[content, auth_section, nav_buttons]
    )

# Launch the App
app.launch(share=True)
