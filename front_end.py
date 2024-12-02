import gradio as gr
from db import db_ops

# Initialize Database Operations
db = db_ops()

# Global variables for username and password
global_username = None
global_password = None


def handle_action(action, username, password, name=None, profile=None):
    """Handles user actions for sign-up or login."""
    global global_username, global_password
    if action == "Sign Up":
        if not username or not password or not name or not profile:
            return "⚠️ All fields are required for sign-up!", None
        try:
            db.create_user_account(username, password, name, profile)
            global_username = username
            global_password = password
            return "✅ Account created successfully!", "Home"
        except Exception as e:
            return f"❌ Error during sign-up: {e}", None
    elif action == "Log In":
        try:
            if db.check_user_account(username, password):
                global_username = username
                global_password = password
                return "✅ Login successful!", "Home"
            else:
                return "❌ Invalid username or password.", None
        except Exception as e:
            return f"❌ Error during login: {e}", None
    else:
        return "❌ Invalid action.", None


def render_page(page):
    """Renders the selected page."""
    if page == "Home":
        return (
            "<h1>Welcome to Home Page</h1>",
            gr.update(visible=False),  # Hide auth_section
            gr.update(visible=True),  # Show nav_buttons
        )
    elif page == "Course List":
        return (
            "<h1>View all courses</h1>",
            gr.update(visible=False),
            gr.update(visible=True),
        )
    elif page == "My Account":
        # Process outputs from render_account
        content, auth_visible, nav_visible = render_account()
        return content, auth_visible, nav_visible
    else:
        return (
            "❌ Page not found.",
            gr.update(visible=True),  # Show auth_section
            gr.update(visible=False),  # Hide nav_buttons
        )



def render_account():
    print("Inside render account")
    """Fetches and displays user account information."""
    global global_username, global_password
    if not global_username or not global_password:
        # Return values for content, auth_section visibility, nav_buttons visibility
        return (
            "<h1>My Account</h1><p>⚠️ Please log in to view account details.</p>",
            gr.update(visible=True),  # Show auth_section
            gr.update(visible=False),  # Hide nav_buttons
        )
    
    try:
        print("Inside try statement")
        # Retrieve user data
        print(global_username)
        print(global_password)
        name = db.get_users_name(global_username, global_password)
        profile = db.get_users_profile(global_username, global_password)
        print("Name " + name)
        print("Profile " + profile)
    except Exception as e:
        return (
            f"<h1>My Account</h1><p>❌ Error fetching account details: {str(e)}</p>",
            gr.update(visible=True),
            gr.update(visible=False),
        )
    
    # If successful, return user data and updated visibility states
    return (
        f"<h1>My Account</h1><p>Welcome, {name}!</p><p>Profile: {profile}</p>",
        gr.update(visible=False),
        gr.update(visible=True),
    )


# Front-End Setup
with gr.Blocks(css=".title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as app:
    # State for Page Navigation
    current_page = gr.State("Login")

    # Header
    with gr.Row():
        gr.Markdown("<div class='title'>🧭 Welcome to CourseCompass 🧭</div>")

    # Dynamic Content
    content = gr.Markdown("")
    nav_buttons = gr.Row(visible=False)
    auth_section = gr.Column(visible=True)

    # Navigation Buttons
    with nav_buttons:
        gr.Button("Home").click(
            fn=lambda: render_page("Home"), 
            inputs=[], 
            outputs=[content, auth_section, nav_buttons]
        )
        gr.Button("Course List").click(
            fn=lambda: render_page("Course List"), 
            inputs=[], 
            outputs=[content, auth_section, nav_buttons]
        )
        gr.Button("My Account").click(
            fn=lambda: render_page("My Account"),
            inputs=[],
            outputs=[content, auth_section, nav_buttons]
        )

    # Login/Signup Section
    with auth_section:
        action = gr.Radio(["Log In", "Sign Up"], label="Choose Action", value="Log In", interactive=True)
        username = gr.Textbox(label="Username", interactive=True)
        password = gr.Textbox(label="Password", type="password", interactive=True)
        name = gr.Textbox(label="Name", visible=False, interactive=True)
        profile = gr.Textbox(label="Profile", visible=False, interactive=True)
        submit_btn = gr.Button("Submit")
        output = gr.Textbox(label="Message", interactive=False)

    # Update visibility of name and profile fields for Sign Up
    def update_visibility(action):
        return gr.update(visible=action == "Sign Up"), gr.update(visible=action == "Sign Up")

    action.change(fn=update_visibility, inputs=action, outputs=[name, profile])

    # Button Click Logic
    submit_btn.click(
        fn=handle_action,
        inputs=[action, username, password, name, profile],
        outputs=[output, current_page],
    ).then(
        fn=render_page,
        inputs=[current_page],
        outputs=[content, auth_section, nav_buttons],  # Ensure these match render_page outputs
    )


# Launch the App
app.launch(share=True)
