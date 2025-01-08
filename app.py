import streamlit as st
import asyncio

# Import your async function from mistral_api.py
from mistral_api import generate_mistral_small_latest_response_idea

############################################
# Essentials. Some basic CSS
############################################

def load_custom_css(file_name: str):
    """
    Reads the .css file and loads it into the Streamlit app using markdown.
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

############################################
# 1. Mistral AI Retrieval Function
############################################
def retrieve_text_from_mistral(prompt: str, max_tokens: int = 150) -> str:
    """
    Calls the async 'generate_mistral_small_latest_response_idea' function
    to get AI-generated text from Mistral in plain text (no JSON).
    """
    try:
        response_text = asyncio.run(generate_mistral_small_latest_response_idea(prompt))
        print("[DEBUG] Raw AI response:", response_text)
        return response_text or ""
    except Exception as e:
        print(f"Error retrieving text from Mistral: {str(e)}")
        return ""

############################################
# 2. Text Parsing Utilities
############################################

def parse_activity_details(generated_description: str) -> dict:
    """
    Parses a plain-text string with lines like:
      title: Some Title
      description: One-line description
      time_estimate: 30 min
      difficulty: Easy

    Returns a dict with those keys/values.
    """
    lines = generated_description.split("\n")
    data = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            # Split once at ": "
            key, value = line.split(": ", 1)
            data[key.lower()] = value.strip()
        except ValueError as ve:
            print(f"Failed to parse line: '{line}'. Error: {ve}")
            continue
    return data

def parse_quest_steps(generated_description: str) -> list:
    """
    Parses a plain-text string describing multiple steps.
    For example, we can prompt the AI to produce lines like:

      step1_title: ...
      step1_description: ...
      step1_time_estimate: ...
      step2_title: ...
      step2_description: ...
      step2_time_estimate: ...
      ...

    We'll collect them in a list of dicts. 
    Each dict will look like:
      {
        "step_title": ...,
        "step_description": ...,
        "time_estimate": ...
      }
    """
    lines = generated_description.split("\n")
    steps_data = []
    current_step = {}
    current_step_index = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            key, value = line.split(": ", 1)
            key = key.strip().lower()
            value = value.strip()
            if key.startswith("step"):
                underscore_index = key.find("_")
                if underscore_index != -1:
                    step_part = key[:underscore_index]     
                    field_part = key[underscore_index+1:]  
                    step_number = "".join(filter(str.isdigit, step_part)) or "1"
                    step_number = int(step_number)

                    if current_step_index is None or step_number != current_step_index:
                        if current_step:
                            steps_data.append(current_step)
                        current_step = {}
                        current_step_index = step_number
                    if field_part == "title":
                        current_step["step_title"] = value
                    elif field_part == "description":
                        current_step["step_description"] = value
                    elif field_part == "time_estimate":
                        current_step["time_estimate"] = value
                else:
                    print(f"Could not find underscore in '{key}'. Skipping line.")
            else:
                print(f"Line doesn't match step format: '{key}'. Skipping line.")

        except ValueError as ve:
            print(f"Failed to parse step line: '{line}'. Error: {ve}")
            continue
    if current_step:
        steps_data.append(current_step)

    return steps_data

def parse_challenge_activities(generated_description: str) -> list:
    """
    Similar approach to parse multiple activities from plain text.
    We might prompt the AI to produce lines for each activity:
      activity1_title: ...
      activity1_description: ...
      activity1_time_estimate: ...
      activity1_difficulty: ...
      activity2_title: ...
      ...
    We'll return a list of dicts for each activity.
    """
    lines = generated_description.split("\n")
    activities = []
    current_activity = {}
    current_activity_index = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            key, value = line.split(": ", 1)
            key = key.strip().lower()
            value = value.strip()

            if key.startswith("activity"):
                underscore_index = key.find("_")
                if underscore_index != -1:
                    act_part = key[:underscore_index]     
                    field_part = key[underscore_index+1:] 
                    activity_number = "".join(filter(str.isdigit, act_part)) or "1"
                    activity_number = int(activity_number)
                    if current_activity_index is None or activity_number != current_activity_index:
                        if current_activity:
                            activities.append(current_activity)
                        current_activity = {}
                        current_activity_index = activity_number

                    if field_part == "title":
                        current_activity["title"] = value
                    elif field_part == "description":
                        current_activity["description"] = value
                    elif field_part == "time_estimate":
                        current_activity["time_estimate"] = value
                    elif field_part == "difficulty":
                        current_activity["difficulty"] = value
                else:
                    print(f"Could not find underscore in '{key}'. Skipping line.")
            else:
                print(f"Line doesn't match activity format: '{key}'. Skipping line.")
        except ValueError as ve:
            print(f"Failed to parse activity line: '{line}'. Error: {ve}")
            continue

    if current_activity:
        activities.append(current_activity)

    return activities

############################################
# 3. Core Generation Logic (Plain Text)
############################################

def generate_activity(category: str, difficulty: str) -> dict:
    """
    Generates a single activity suggestion via Mistral AI in plain text.

    The AI prompt requests something like:

      title: Short Title
      description: One-line description
      time_estimate: 30 min
      difficulty: Easy

    We'll parse that string into a dict using parse_activity_details.
    """
    prompt = f"""
You are an AI that generates a local activity in Churchgate, Mumbai.
Category: {category}
Difficulty: {difficulty}

Return the result in plain text, with one field per line:
title: <short title>
description: <one-line description>
time_estimate: <e.g. '30 min'>
difficulty: <same difficulty above or a variation>

No JSON. Just plain text.
"""

    ai_response = retrieve_text_from_mistral(prompt, max_tokens=150)
    parsed_data = parse_activity_details(ai_response)

    for key in ["title", "description", "time_estimate", "difficulty"]:
        if key not in parsed_data:
            parsed_data[key] = "Missing"

    parsed_data["category"] = category
    return parsed_data

def generate_quest(difficulty: str, num_steps: int = 3) -> list:
    """
    Generates a multi-step quest in plain text, e.g.:

      step1_title: ...
      step1_description: ...
      step1_time_estimate: ...
      step2_title: ...
      ...

    We parse it into a list of step dicts using parse_quest_steps.
    """
    prompt = f"""
You are an AI that generates a themed quest (adventure) in Churchgate, Mumbai.
Difficulty: {difficulty}
Number of steps: {num_steps}

Return the result in plain text, each step in separate lines, exactly as below:
step1_title: ...
step1_description: ...
step1_time_estimate: ...
step2_title: ...
etc.

Make it realistic as in something people can explore and do in real life
No JSON. Just plain text, no markdown language as well.
"""
    ai_response = retrieve_text_from_mistral(prompt, max_tokens=300)
    ai_response = ai_response.replace('"', '')
    ai_response = ai_response.replace('*', '')
    steps_data = parse_quest_steps(ai_response)

    if not steps_data:
        return [{
            "step_title": "Untitled Step",
            "step_description": "No valid lines returned by AI.",
            "time_estimate": "N/A"
        }]
    return steps_data

def generate_challenge(num_activities: int = 3) -> list:
    """
    Generates multiple activities in plain text:
      activity1_title: ...
      activity1_description: ...
      activity1_time_estimate: ...
      activity1_difficulty: ...
      activity2_title: ...
      ...

    We'll parse them with parse_challenge_activities.
    """
    prompt = f"""
You are an AI that generates a challenge-mode set of activities in Churchgate, Mumbai.
Number of activities: {num_activities}

Return them in plain text, each activity in lines like:
activity1_title: ...
activity1_description: ...
activity1_time_estimate: ...
activity1_difficulty: ...
activity2_title: ...
etc.

No JSON. Just plain text.
"""
    ai_response = retrieve_text_from_mistral(prompt, max_tokens=400)
    challenge_data = parse_challenge_activities(ai_response)

    if not challenge_data:
        return [{
            "title": "Untitled",
            "description": "No valid lines returned by AI.",
            "time_estimate": "N/A",
            "difficulty": "Medium"
        }]
    return challenge_data

############################################
# 4. Achievements & Points Logic
############################################

def award_points_for_activity(activity: dict) -> int:
    """
    Simple logic for awarding points based on difficulty.
    """
    difficulty = activity.get("difficulty", "Easy").lower()
    if difficulty == "hard":
        return 20
    elif difficulty == "medium":
        return 15
    return 10  

def check_and_unlock_achievements():
    """
    Example logic to unlock achievements based on completed activities.
    - "Mumbai Foodie": Complete 5 'Food' category or food-related activities
    - "Urban Explorer": Finish 3 Hard-level activities
    """
    foodie_count = sum(
        1 for act in st.session_state.completed_activities
        if act.get("category", "").lower() == "food"
    )
    hard_count = sum(
        1 for act in st.session_state.completed_activities
        if act.get("difficulty", "").lower() == "hard"
    )

    if foodie_count >= 5 and "Mumbai Foodie" not in st.session_state.achievements:
        st.session_state.achievements.append("Mumbai Foodie")
        st.success("New Achievement Unlocked: Mumbai Foodie!")

    if hard_count >= 3 and "Urban Explorer" not in st.session_state.achievements:
        st.session_state.achievements.append("Urban Explorer")
        st.success("New Achievement Unlocked: Urban Explorer!")

############################################
# 5. Main Streamlit App
############################################

def main():
    st.set_page_config(page_title="Wanderlust", layout="wide")
    # load_custom_css("app.css")  unimplemented
    # Session state initialization
    if "points" not in st.session_state:
        st.session_state.points = 0
    if "completed_activities" not in st.session_state:
        st.session_state.completed_activities = []
    if "saved_activities" not in st.session_state:
        st.session_state.saved_activities = []
    if "achievements" not in st.session_state:
        st.session_state.achievements = []
    if "username" not in st.session_state:
        st.session_state.username = "Wanderer"

    # Sidebar navigation
    st.sidebar.title("Wanderlust Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
            "Home",
            "Quest",
            "Challenges",
            "Community (Coming Soon)",
            "Profile",
            "Help & Support (Coming Soon)"
        ]
    )

    # HOME PAGE
    if page == "Home":
        st.title("Wanderlust Home")
        st.write("Generate AI-powered activities in Churchgate, Mumbai!")
        
        category = st.selectbox("Activity Category", ["Food", "Culture", "Adventure"])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        if st.button("Generate a Wander"):
            activity = generate_activity(category, difficulty)

            st.subheader(f"**Title**: {activity['title']}")
            st.write(f"**Description**: {activity['description']}")
            st.write(f"**Time Estimate**: {activity['time_estimate']}")
            st.write(f"**Difficulty**: {activity['difficulty']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Complete Activity"):
                    st.session_state.completed_activities.append(activity)
                    points_gained = award_points_for_activity(activity)
                    st.session_state.points += points_gained
                    st.success(f"Activity completed! You earned {points_gained} points.")
                    check_and_unlock_achievements()
            with col2:
                if st.button("Save Activity"):
                    st.session_state.saved_activities.append(activity)
                    st.info("Activity saved for later!")

        # Quick profile snapshot
        st.write("### Profile Snapshot")
        st.write(f"**Username**: {st.session_state.username}")
        st.write(f"**Points**: {st.session_state.points}")
        st.write(f"**Completed Activities**: {len(st.session_state.completed_activities)}")

    # QUEST PAGE
    elif page == "Quest":
        st.title("Quest Generator")
        st.write("Create a multi-step mini-adventure!")

        difficulty = st.selectbox("Quest Difficulty", ["Easy", "Medium", "Hard"])
        num_steps = st.slider("Number of Steps", 3, 5, 3)

        if st.button("Generate Quest"):
            steps = generate_quest(difficulty, num_steps)
            if steps:
                st.subheader(f"{num_steps}-Step Quest ({difficulty}):")
                for idx, step in enumerate(steps, start=1):
                    st.markdown(f"**Step {idx}:** {step.get('step_title', '')}")
                    st.write(step.get("step_description", ""))
                    st.write(f"_Time Estimate:_ {step.get('time_estimate', '')}\n")
            else:
                st.warning("No quest steps generated.")

    # CHALLENGES PAGE
    elif page == "Challenges":
        st.title("Challenge Mode")
        st.write("Generate multiple related activities for a mini-adventure.")

        num_activities = st.slider("Number of Activities", 2, 5, 3)
        if st.button("Generate Challenge"):
            challenge_activities = generate_challenge(num_activities)
            st.subheader("Your Challenge Activities:")
            for i, act in enumerate(challenge_activities, start=1):
                st.write(f"**Activity {i}:** {act.get('title', '')}")
                st.write(act.get("description", ""))
                st.write(f"_Time Estimate:_ {act.get('time_estimate', '')}")
                st.write(f"_Difficulty:_ {act.get('difficulty', '')}")
                st.markdown("---")

    # COMMUNITY PAGE (Coming Soon)
    elif page == "Community (Coming Soon)":
        st.title("Community Feed (Coming Soon)")
        st.info("Stay tuned for user-generated content, social features, and more.")

    # PROFILE PAGE
    elif page == "Profile":
        st.title("Your Profile")
        st.write(f"**Username**: {st.session_state.username}")

        new_username = st.text_input("Update Username", value=st.session_state.username)
        if new_username != st.session_state.username:
            st.session_state.username = new_username
            st.success("Username updated!")

        st.write(f"**Total Points**: {st.session_state.points}")

        st.write("### Achievements:")
        if st.session_state.achievements:
            for ach in st.session_state.achievements:
                st.write(f"- {ach}")
        else:
            st.write("No achievements yet. Complete activities to unlock them!")

        st.write("### Completed Activities:")
        if st.session_state.completed_activities:
            for i, act in enumerate(st.session_state.completed_activities, start=1):
                st.write(
                    f"**{i}.** {act['title']} - {act['description']} "
                    f"(_Difficulty: {act['difficulty']}_)"
                )
        else:
            st.write("You haven't completed any activities yet.")

        st.write("### Saved Activities:")
        if st.session_state.saved_activities:
            for i, act in enumerate(st.session_state.saved_activities, start=1):
                st.write(f"**{i}.** {act['title']} - {act['description']}")
        else:
            st.write("No activities saved.")

    # HELP & SUPPORT (Coming Soon)
    else:
        st.title("Help & Support (Coming Soon)")
        st.info("FAQs, articles, and support contact will appear here soon!")


if __name__ == "__main__":
    
    main()
