import gradio as gr
from db import db_ops

# Initialize Database Operations
db = db_ops()
# db.create_tables()
# db.populate()
# db.delete_everything()

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


def fetch_courses():
    """Fetches all courses sorted alphabetically by Course Name."""
    try:
        courses = db.get_courses()  # Ensure this method fetches course data
        courses.sort(key=lambda x: x[0])  # Sort by Course Name (assume it's the first field)
        return courses
    except Exception as e:
        return f"Error fetching courses: {e}"


def render_page(page):
    """Renders the selected page."""
    if page == "Home":
        return (
            "<h1>Welcome to Home Page</h1>",
            gr.update(visible=False),
            gr.update(visible=True),
        )
    elif page == "Course List":
        courses = fetch_courses()
        if isinstance(courses, str):  # Handle error message
            course_list = f"<p>{courses}</p>"
        elif not courses:  # Handle empty course list
            course_list = "<p>No courses found.</p>"
        else:  # Render the sorted course list
            course_list = "<h1>Course List</h1>"
            for course in courses:
                course_list += f"""
                <div class='course-entry'>
                    <p><strong>{course[0]} by {course[3]} ({course[2]})</strong></p>
                    <button onclick="alert(`Course Name: {course[0]}\\nInstructor: {course[3]}\\nCategory: {course[2]}\\nDescription: {course[1]}\\nAverage Rating: {course[4]}`)">View More</button>
                </div>
                """
        return course_list, gr.update(visible=False), gr.update(visible=True)
    elif page == "My Account":
        content, auth_visible, nav_visible = render_account()
        return content, auth_visible, nav_visible
    else:
        return (
            "❌ Page not found.",
            gr.update(visible=True),
            gr.update(visible=False),
        )


def render_account():
    """Fetches and displays user account information."""
    global global_username, global_password
    if not global_username or not global_password:
        return (
            "<h1>My Account</h1><p>⚠️ Please log in to view account details.</p>",
            gr.update(visible=True),
            gr.update(visible=False),
        )
    try:
        name = db.get_users_name(global_username, global_password)
        profile = db.get_users_profile(global_username, global_password)
    except Exception as e:
        return (
            f"<h1>My Account</h1><p>❌ Error fetching account details: {str(e)}</p>",
            gr.update(visible=True),
            gr.update(visible=False),
        )
    return (
        f"<h1>My Account</h1><p>Welcome, {name}!</p><p>Profile: {profile}</p>",
        gr.update(visible=False),
        gr.update(visible=True),
    )


# Front-End Setup
with gr.Blocks(css="""
    .title { text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem; }
    .course-entry { margin-bottom: 10px; }
    .course-list { margin-top: 20px; }
""") as app:
    current_page = gr.State("Login")

    # Header
    with gr.Row():
        gr.Markdown("<div class='title'>🧭 Welcome to CourseCompass 🧭</div>")

    # Dynamic Content
    content = gr.Markdown("Welcome! Use the navigation buttons to explore.")
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
        outputs=[content, auth_section, nav_buttons],
    )

app.launch(share=True)
