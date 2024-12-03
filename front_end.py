import gradio as gr
from db import db_ops

# Initialize Database Operations
db = db_ops()

# Global variables for username and password
global_username = None
global_password = None

def handle_action(action, username, password, name=None, profile=None):
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
    try:
        courses = db.get_courses()
        return courses
    except Exception as e:
        return f"Error fetching courses: {e}"

def render_page(page):
    if page == "Home":
        return (
            "<h1>Welcome to CourseCompass 🧭</h1>",
            gr.update(visible=False),
            gr.update(visible=True)
        )
    elif page == "Course List":
        courses = fetch_courses()
        if isinstance(courses, str):
            course_list = f"<p>{courses}</p>"
        elif not courses:
            course_list = "<p>No courses found.</p>"
        else:
            course_list = "<h1>Course List</h1><div style='display: flex; flex-wrap: wrap;'>"
            for course in courses:
                course_list += (
                    f"<div style='border: 1px solid #ddd; padding: 10px; margin: 10px; width: 300px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>"
                    f"<h3>{course[0]}</h3>"
                    f"<p><strong>Instructor:</strong> {course[3]}</p>"
                    f"<p><strong>Category:</strong> {course[2]}</p>"
                    f"<p><strong>Description:</strong> {course[1]}</p>"
                    f"<p><strong>Average Rating:</strong> {course[4]}</p>"
                    f"</div>"
                )
            course_list += "</div>"
        return course_list, gr.update(visible=False), gr.update(visible=True)
    elif page == "My Account":
        return render_account()
    else:
        return (
            "❌ Page not found.",
            gr.update(visible=True),
            gr.update(visible=False)
        )

def render_account():
    global global_username, global_password
    if not global_username or not global_password:
        return (
            "<h1>My Account</h1><p>⚠️ Please log in to view account details.</p>",
            gr.update(visible=True),
            gr.update(visible=False)
        )
    try:
        name = db.get_users_name(global_username, global_password)
        profile = db.get_users_profile(global_username, global_password)
    except Exception as e:
        return (
            f"<h1>My Account</h1><p>❌ Error fetching account details: {e}</p>",
            gr.update(visible=True),
            gr.update(visible=False)
        )
    return (
        f"<h1>My Account</h1><p>Welcome, {name}!</p><p>Profile: {profile}</p>",
        gr.update(visible=False),
        gr.update(visible=True)
    )

with gr.Blocks(css=".title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as app:
    current_page = gr.State("Login")

    # Add header back
    with gr.Row():
        gr.Markdown("<div class='title'>🧭 Welcome to CourseCompass 🧭</div>")

    content = gr.Markdown("")
    nav_buttons = gr.Row(visible=False)
    auth_section = gr.Column(visible=True)

    with nav_buttons:
        gr.Button("Home").click(
            lambda: render_page("Home"), [], 
            [content, auth_section, nav_buttons]
        )
        gr.Button("Course List").click(
            lambda: render_page("Course List"), [], 
            [content, auth_section, nav_buttons]
        )
        gr.Button("My Account").click(
            lambda: render_page("My Account"), [], 
            [content, auth_section, nav_buttons]
        )

    with auth_section:
        action = gr.Radio(["Log In", "Sign Up"], label="Choose Action", value="Log In", interactive=True)
        username = gr.Textbox(label="Username", interactive=True)
        password = gr.Textbox(label="Password", type="password", interactive=True)
        name = gr.Textbox(label="Name", visible=False, interactive=True)
        profile = gr.Textbox(label="Profile", visible=False, interactive=True)
        submit_btn = gr.Button("Submit")
        output = gr.Textbox(label="Message", interactive=False)

    action.change(
        lambda a: (gr.update(visible=a == "Sign Up"), gr.update(visible=a == "Sign Up")),
        action, [name, profile]
    )

    submit_btn.click(
        handle_action,
        [action, username, password, name, profile],
        [output, current_page]
    ).then(
        render_page,
        current_page,
        [content, auth_section, nav_buttons]
    )

app.launch(share=True)