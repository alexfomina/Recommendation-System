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

# 🚀 Added Course Interaction and Selection Functionality
def handle_interaction(course_id, interaction_type, rating=None):
    global global_username
    if not global_username:
        return "❌ Please log in to interact with courses."
    try:
        if interaction_type == "rate" and rating is not None:
            db.add_interaction(interaction_type, global_username, course_id, rating=rating)
        else:
            db.add_interaction(interaction_type, global_username, course_id)
        return f"✅ {interaction_type.capitalize()} action completed successfully!"
    except Exception as e:
        return f"❌ Error performing {interaction_type}: {e}"

def render_page(page, selected_course_id=None):
    global global_username, global_password
    if page == "Course List":
        courses = db.get_courses()
        if isinstance(courses, str):
            course_list = f"<p>{courses}</p>"
        elif not courses:
            course_list = "<p>No courses found.</p>"
        else:
            course_list = "<h1>Course List</h1><div style='display: flex; flex-wrap: wrap;'>"
            for course in courses:
                course_list += (
                    f"<div style='border: 1px solid #ddd; padding: 10px; margin: 10px; width: 300px;'>"
                    f"<h3>{course[0]}</h3>" 
                    f"<p><strong>Instructor:</strong> {course[3]}</p>"
                    f"<p><strong>Category:</strong> {course[2]}</p>"
                    f"<p><strong>Description:</strong> {course[1]}</p>"
                    f"<p><strong>Average Rating:</strong> {course[4]}</p>"
                    f"<button onclick=\"select_course('{course[0]}')\">Select</button>"
                    f"</div>"
                )
            course_list += "</div>"
        return course_list, gr.update(visible=True), gr.update(visible=False)
    elif page == "Interaction" and selected_course_id:
        return (
            f"<h1>Interact with {selected_course_id}</h1>"
            f"<p>Choose an interaction type and proceed:</p>",
            gr.update(visible=True), gr.update(visible=True)
        )
    else:
        return "❌ Page not found.", gr.update(visible=True), gr.update(visible=False)

def select_course(course_id):
    return course_id, "Interaction"

# Update the Gradio app
with gr.Blocks() as app:
    current_page = gr.State("Course List")
    selected_course_id = gr.State(None)
    content = gr.Markdown("")
    interaction_type = gr.Radio(["view", "rate", "favorite", "register"], label="Choose Interaction Type")
    rating_input = gr.Slider(1, 5, label="Rating (only for 'rate')", visible=False)
    submit_btn = gr.Button("Submit Interaction")
    message = gr.Textbox(label="Message", interactive=False)

    interaction_type.change(
        lambda interaction: gr.update(visible=(interaction == "rate")),
        interaction_type, rating_input
    )

    submit_btn.click(
        handle_interaction,
        [selected_course_id, interaction_type, rating_input],
        message
    )

    app.load(
        lambda: render_page("Course List"),
        [], [content, interaction_type, rating_input]
    )

app.launch()



import gradio as gr
from db import db_ops

# Initialize Database Operations
db = db_ops()

# Global variables for username and password
global_username = None
global_password = None
global_course_name = None

def handle_action(action, username, password, name=None, profile=None):
    """
    Handles user actions: Sign Up and Log In.
    """
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
                # Unpack if tuple
                global_username = global_username[0] if isinstance(global_username, tuple) else global_username
                global_password = global_password[0] if isinstance(global_password, tuple) else global_password
                return "✅ Login successful!", "Home"
            else:
                return "❌ Invalid username or password.", None
        except Exception as e:
            return f"❌ Error during login: {e}", None
    else:
        return "❌ Invalid action.", None

def fetch_user_info(username, password):
    """
    Fetches user information like name and profile from the database.
    """
    try:
        name = db.get_users_name(username, password)
        profile = db.get_users_profile(username, password)
        return name, profile
    except Exception:
        return None, None

def update_user_info(username, new_name=None, new_profile=None):
    """
    Updates user information in the database.
    """
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

def handle_interaction(interaction_type, rating=None):
    """
    Handles interactions (register, view, rate, favorite) using the global course name.
    """
    global global_username, global_course_name
    print(f"DEBUG: interaction_type={interaction_type}, rating={rating}")
    print(f"DEBUG: global_username={global_username}, global_course_name={global_course_name}")

    if not global_username:
        return "❌ Please log in to interact with courses."
    if not global_course_name:
        return "❌ No course selected. Please select a course."

    try:
        if interaction_type == "rate" and rating is not None:
            db.add_interaction(interaction_type, global_username, global_course_name, rating=rating)
        else:
            db.add_interaction(interaction_type, global_username, global_course_name)
        return f"✅ {interaction_type.capitalize()} action completed successfully!"
    except Exception as e:
        return f"❌ Error performing {interaction_type}: {e}"


def render_page(page, selected_course_name = None):
    """
    Renders the specified page: Home, Course List, My Account, or Course Interaction.
    """
    global global_username, global_password

    if page == "Home":
        return (
            "<h1>Welcome to CourseCompass 🧭</h1><p>Navigate to explore Courses or view your Account details.</p>",
            gr.update(visible=True),  # Show navigation
            gr.update(visible=False),  # Hide authentication
            gr.update(visible=False),  # Hide update message
            gr.update(visible=False),  # Hide name/profile input
            gr.update(visible=False),  # Hide update button
        )
    elif page == "Course List":
        courses = db.get_courses()
        if not courses:
            course_list = "<p>No courses found.</p>"
        else:
            course_list = "<h1>Course List</h1><div style='display: flex; flex-wrap: wrap;'>"
            for course in courses:
                course_list += (
                    f"<div style='border: 1px solid #ddd; padding: 10px; margin: 10px; width: 300px;'>"
                    f"<h3>{course[0]}</h3>"
                    f"<p><strong>Description:</strong> {course[1]}</p>"
                    f"<p><strong>Category:</strong> {course[2]}</p>"
                    f"<p><strong>Instructor:</strong> {course[3]}</p>"
                    f"<p><strong>Average Rating:</strong> {course[4]}</p>"
                    f"<button onclick=\"select_course('{course[0]}')\">Select</button>"
                    f"</div>"
                )
            course_list += "</div>"
        return (
            course_list,
            gr.update(visible=True),  # Show navigation
            gr.update(visible=False),  # Hide authentication
            gr.update(visible=False),  # Hide update message
            gr.update(visible=False),  # Hide name/profile input
            gr.update(visible=False),  # Hide update button
        )
    elif page == "Interaction":
        if not global_course_name:
            return (
                "<h1>❌ No course selected</h1><p>Please go back and select a course to interact with.</p>",
                gr.update(visible=True),  # Show navigation
                gr.update(visible=False),  # Hide authentication
                gr.update(visible=False),  # Hide update message
                gr.update(visible=False),  # Hide name/profile input
                gr.update(visible=False),  # Hide update button
            )
        return (
            f"<h1>Interact with {global_course_name}</h1>"
            "<p>Choose an interaction type and proceed:</p>",
            gr.update(visible=True),  # Show navigation
            gr.update(visible=True),  # Show interaction components
            gr.update(visible=False),  # Hide update message
            gr.update(visible=False),  # Hide name/profile input
            gr.update(visible=False),  # Hide update button
        )

    elif page == "My Account":
        if not global_username or not global_password:
            return (
                "<h1>My Account</h1><p>⚠️ Please log in to view account details.</p>",
                gr.update(visible=False),  # Hide navigation
                gr.update(visible=True),  # Show authentication
                gr.update(visible=False),  # Hide update message
                gr.update(visible=False),  # Hide name/profile input
                gr.update(visible=False),  # Hide update button
            )
        name, profile = fetch_user_info(global_username, global_password)
        if name is None or profile is None:
            return (
                "<h1>My Account</h1><p>❌ Error fetching account details.</p>",
                gr.update(visible=True),  # Show navigation
                gr.update(visible=False),  # Hide authentication
                gr.update(visible=False),  # Hide update message
                gr.update(visible=False),  # Hide name/profile input
                gr.update(visible=False),  # Hide update button
            )
        return (
            f"<h1>My Account</h1><p>Welcome, {name}!</p><p>Profile: {profile}</p>",
            gr.update(visible=True),  # Show navigation
            gr.update(visible=False),  # Hide authentication
            gr.update(visible=True),  # Show update message
            gr.update(visible=True),  # Show name/profile input
            gr.update(visible=True),  # Show update button
        )
    else:
        return (
            "❌ Page not found.",
            gr.update(visible=True),  # Show navigation
            gr.update(visible=False),  # Hide authentication
            gr.update(visible=False),  # Hide update message
            gr.update(visible=False),  # Hide name/profile input
            gr.update(visible=False),  # Hide update button
        )

def select_course(course_name):
    """
    Updates the global course name when a course is selected.
    """
    global global_course_name
    global_course_name = course_name  # Set the global course name
    print(f"DEBUG: Course selected - {global_course_name}")
    return global_course_name, "Interaction"  # Update the course name and navigate to Interaction page

    
# Gradio interface setup
with gr.Blocks() as app:
    current_page = gr.State("Login")  # State to manage the current page
    selected_course_name = gr.State(None)  # State to hold the selected course name
    content = gr.Markdown("")  # Markdown for displaying dynamic content
    navigation = gr.Row(visible=False)  # Navigation buttons, initially hidden
    authentication = gr.Column(visible=True)  # Authentication section, initially visible
    update_message = gr.Textbox(visible=False, interactive=False)  # Message for updates
    update_name = gr.Textbox(label="Update Name", visible=False)  # Name update field
    update_profile = gr.Textbox(label="Update Profile", visible=False)  # Profile update field
    update_btn = gr.Button("Update Information", visible=False)  # Button to update account info
    interaction_message = gr.Textbox(visible=False)  # Message box for interactions

    # Navigation buttons
    with navigation:
        gr.Button("Home").click(
            lambda: render_page("Home"), [], 
            [content, navigation, authentication, update_name, update_profile, update_btn]
        )
        gr.Button("Courses").click(
            lambda: render_page("Course List"), [], 
            [content, navigation, authentication, update_name, update_profile, update_btn]
        )
        gr.Button("My Account").click(
            lambda: render_page("My Account"), [], 
            [content, navigation, authentication, update_name, update_profile, update_btn]
        )

    # Authentication section
    with authentication:
        action = gr.Radio(["Log In", "Sign Up"], label="Choose Action", value="Log In", interactive=True)
        username = gr.Textbox(label="Username", interactive=True)
        password = gr.Textbox(label="Password", type="password", interactive=True)
        name = gr.Textbox(label="Name", visible=False, interactive=True)
        profile = gr.Textbox(label="Profile", visible=False, interactive=True)
        submit_btn = gr.Button("Submit")
        message = gr.Textbox(label="Message", interactive=False)

    # Toggle visibility for sign-up fields
    action.change(
        lambda a: (gr.update(visible=a == "Sign Up"), gr.update(visible=a == "Sign Up")),
        action, [name, profile]
    )

    # Handle login/sign-up and redirect to Home
    submit_btn.click(
        handle_action,
        [action, username, password, name, profile],
        [message, current_page]
    ).then(
        render_page,
        current_page,
        [content, navigation, authentication, update_name, update_profile, update_btn]
    )

    # Edit account functionality
    update_btn.click(
        lambda new_name, new_profile: update_user_info(global_username, new_name, new_profile),
        [update_name, update_profile],
        update_message
    )
    
    # Dynamically Render Courses
    with gr.Row(visible=False) as course_buttons_section:
        courses = db.get_courses()  # Fetch courses dynamically
        for course in courses:
            course_name_input = gr.Textbox(value=course[0], visible=False)  # Hidden input for course name
            button = gr.Button(f"Select {course[0]}")  # Button for each course
            button.click(
                select_course,  # Bind to select_course function
                inputs=[course_name_input],  # Pass course name
                outputs=[selected_course_name, current_page]  # Update selected course and navigate
            )

    # Handle interactions
    interaction_type = gr.Radio(["register", "view", "rate", "favorite"], label="Choose Interaction Type")
    rating_input = gr.Slider(1, 5, label="Rate (only for 'rate')", visible=False)
    submit_btn_interaction = gr.Button("Submit Interaction")
    message_interaction = gr.Textbox(label="Message", interactive=False)

    interaction_type.change(
        lambda interaction: gr.update(visible=(interaction == "rate")),
        interaction_type, rating_input
    )

    submit_btn_interaction.click(
        handle_interaction,
        [interaction_type, rating_input],
        message_interaction
    )

app.launch()
