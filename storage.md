import gradio as gr
from db import db_ops

# Initialize Database Operations
db = db_ops()

# Functions for App Logic
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


def render_page(page, username=None, password=None):
    """Renders the selected page."""
    if page == "Home":
        return "<h1>Welcome to Home Page</h1>", gr.update(visible=False), gr.update(visible=True)
    elif page == "Course List":
        return "<h1>View all courses</h1>", gr.update(visible=False), gr.update(visible=True)
    elif page == "My Account":
        return render_account(username, password)
    else:
        return "❌ Page not found.", gr.update(visible=False), gr.update(visible=False)


def render_account(username, password):
    """Fetches and displays user account information."""
    if not username or not password:
        # Handle case where username or password is missing
        return (
            "<h1>My Account</h1><p>⚠️ Please log in to view account details.</p>",
            {"value": "", "visible": False},
            {"value": "", "visible": False},
        )
    
    try:
        # Retrieve user data
        name = db.get_users_name(username, password)
        profile = db.get_users_profile(username, password)
    except Exception as e:
        # Handle any exceptions that occur during data fetching
        return (
            f"<h1>My Account</h1><p>❌ Error fetching account details: {str(e)}</p>",
            {"value": "", "visible": False},
            {"value": "", "visible": False},
        )
    
    # If successful, display user data
    return (
        f"<h1>My Account</h1><p>Welcome, {name}!</p>",
        {"value": name, "visible": True},
        {"value": profile, "visible": True},
    )



def update_account(field_to_edit, new_value, username, password):
    """Updates user account information."""
    try:
        db.edit_account(username, password, field_to_edit, new_value)
        return f"✅ {field_to_edit} updated successfully!"
    except Exception as e:
        return f"❌ Error updating {field_to_edit}: {e}"


# Front-End Setup
with gr.Blocks(css=".title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as app:
    # State for Page Navigation
    current_page = gr.State("Login")
    current_user = gr.State("")
    current_password = gr.State("")

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
            fn=lambda username, password: render_page("My Account", username, password),
            inputs=[current_user, current_password],
            outputs=[content, auth_section, nav_buttons]
        )

    # Login/Signup Section
    with auth_section:
        action = gr.Radio(["Log In", "Sign Up"], label="Choose Action", type="value", value="Log In", interactive=True)
        username = gr.Textbox(label="Username", placeholder="Enter your username", interactive=True)
        password = gr.Textbox(label="Password", placeholder="Enter your password", type="password", interactive=True)
        name = gr.Textbox(label="Name", placeholder="Enter your name", visible=False, interactive=True)
        profile = gr.Textbox(label="Profile", placeholder="Enter your profile description", visible=False, interactive=True)
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
        outputs=[output, current_page],
    ).then(
        lambda page: render_page(page),
        inputs=current_page,
        outputs=[content, auth_section, nav_buttons],
    )

    # My Account Editing Section
    name_field = gr.Textbox(label="Edit Name", value="None", visible=False, interactive=True)
    profile_field = gr.Textbox(label="Edit Profile", value="None", visible=False, interactive=True)
    update_name_btn = gr.Button("Update Name", visible=False)
    update_profile_btn = gr.Button("Update Profile", visible=False)
    update_output = gr.Textbox(label="Update Status", visible=False, interactive=False)

    update_name_btn.click(
        fn=lambda new_value, username, password: update_account("Name", new_value, username, password),
        inputs=[name_field, current_user, current_password],
        outputs=[update_output],
    )

    update_profile_btn.click(
        fn=lambda new_value, username, password: update_account("Profile", new_value, username, password),
        inputs=[profile_field, current_user, current_password],
        outputs=[update_output],
    )

# Launch the App
app.launch(share=True)
