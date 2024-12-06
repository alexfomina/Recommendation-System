import gradio as gr
from db import db_ops

# Initialize Database Operations
db = db_ops()

# db.create_tables()
# db.populate()

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

def fetch_user_info(username, password):
    try:
        name = db.get_users_name(username, password)
        profile = db.get_users_profile(username, password)
        return name, profile
    except Exception as e:
        return None, None

def update_user_info(username, new_name=None, new_profile=None):
    messages = []
    if new_name:
        if db.update_user_name(username, new_name):
            messages.append("✅ Name updated successfully!")
        else:
            messages.append("❌ Error updating name.")
    if new_profile:
        if db.update_user_profile(username, new_profile):
            messages.append("✅ Profile updated successfully!")
        else:
            messages.append("❌ Error updating profile.")
    return " ".join(messages)

def render_page(page):
    global global_username, global_password
    if page == "Home":
        return (
            "<h1>Welcome to CourseCompass 🧭</h1>",
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),  # Hide update fields
            gr.update(visible=False),  # Hide update fields
            gr.update(visible=False)   # Hide update button
        )
    elif page == "Course List":
        courses = db.get_courses()
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
        return course_list, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
    elif page == "My Account":
        if not global_username or not global_password:
            return (
                "<h1>My Account</h1><p>⚠️ Please log in to view account details.</p>",
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False)
            )
        name, profile = fetch_user_info(global_username, global_password)
        if name is None or profile is None:
            return (
                "<h1>My Account</h1><p>❌ Error fetching account details.</p>",
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False)
            )
        return (
            f"<h1>My Account</h1><p>Welcome, {name}!</p><p>Profile: {profile}</p>",
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),  # Show update fields
            gr.update(visible=True),  # Show update fields
            gr.update(visible=True)   # Show update button
        )
    else:
        return (
            "❌ Page not found.",
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )

with gr.Blocks(css=".title {text-align: center; font-size: 2rem; color: #007BFF; margin-bottom: 1rem;}") as app:
    current_page = gr.State("Login")
    content = gr.Markdown("")
    nav_buttons = gr.Row(visible=False)
    auth_section = gr.Column(visible=True)
    update_message = gr.Textbox(visible=True, interactive=False)
    update_name = gr.Textbox(label="Update Name", visible=False)
    update_profile = gr.Textbox(label="Update Profile", visible=False)
    update_btn = gr.Button("Update Information", visible=False)

    with nav_buttons:
        gr.Button("Home").click(
            lambda: render_page("Home"), [], 
            [content, auth_section, nav_buttons, update_name, update_profile, update_btn]
        )
        gr.Button("Course List").click(
            lambda: render_page("Course List"), [], 
            [content, auth_section, nav_buttons, update_name, update_profile, update_btn]
        )
        gr.Button("My Account").click(
            lambda: render_page("My Account"), [], 
            [content, auth_section, nav_buttons, update_name, update_profile, update_btn]
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
        [content, auth_section, nav_buttons, update_name, update_profile, update_btn]
    )

    update_btn.click(
        lambda new_name, new_profile: update_user_info(global_username, new_name, new_profile),
        [update_name, update_profile],
        update_message
    )

app.launch(share=True)