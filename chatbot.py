import streamlit as st
import google.generativeai as genai
import random

# --- CONFIG ---
# Load API Key securely from Streamlit secrets
# Before running, ensure you have a .streamlit/secrets.toml file with:
# GEMINI_API_KEY="YOUR_API_KEY_HERE"
try:
    GOOGLE_API_KEY = "AIzaSyDjmihPbXZMe4r4gFJIFZpUcAwDoG5O6UU"
    genai.configure(api_key=GOOGLE_API_KEY)
    #if "" in st.secrets:
    #    genai.configure(api_key=st.secrets[""])
    #else:
    #   st.error("Gemini API key not found in Streamlit secrets. Please configure 'GEMINI_API_KEY'.")
except Exception as e:
    st.error(f"Error configuring Gemini: {e}")
    model = None

# FIX: Using the correct, stable model identifier for the flash model.
MODEL_NAME = "gemini-2.5-flash"

try:
    # Initialize the model
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    # This block handles the case where the key is invalid or the model name is wrong
    st.warning(f"Could not load Gemini model '{MODEL_NAME}'. Check your API key and model name. Error: {e}")
    model = None

# --- CAT FACTS ---
cat_facts = [
    "Cats can rotate their ears 180 degrees 👂🐱",
    "A group of cats is called a *clowder* 😸",
    "The oldest known pet cat was found in a 9,500-year-old grave 🐾",
    "Cats sleep about 70% of their lives 💤",
    "Some cats can run up to 30 miles per hour! 🏃‍♂️🐈"
]

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferences" not in st.session_state:
    st.session_state.preferences = {}

# --- GEMINI RESPONSE ---
def get_gemini_recommendation(preferences):
    if model is None:
        return "Sorry, I can't recommend a cat right now. My AI brains aren't working because the API key is missing or invalid! 😵‍💫"

    prompt = f"""
    You are CatBuddy 🐱 — a friendly, funny assistant that helps humans pick their purrfect cat breed.
    Use emojis often, sprinkle in light-hearted cat jokes, but stay helpful.
    
    The user gave these preferences:
    {preferences}

    1. If info is missing, ask more questions (fur length, activity level, size preference, grooming needs, etc.).
    2. Try hardest to suggest only ONE cat breed that matches. If multiple breeds fit, list them all.
    3. For each breed: give a fun but detailed description (size, temperament, care needs).
    4. Take into account budget 💰 and location 🌍 if given.
    """

    # Added a try-except block for robustness during API calls
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Oops! I hit a snag while trying to talk to the AI. Error: {e}. Check your API key and quota! 🙈"

# --- PROGRESS TRACKER ---
def calculate_progress(preferences):
    # 'initial_prompt' is only set after the first chat interaction, which is fine for progress
    required_fields = ["budget", "city", "experience", "living_space", "allergies", "initial_prompt"]
    # Check if the field exists and has a truthy value (i.e., not "", None, or default selection)
    filled = sum(1 for field in required_fields if field in preferences and preferences[field])
    return filled, len(required_fields)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🐾 CatBuddy Sidebar")

    # Budget
    budget = st.text_input("Your Budget (in USD): 💰", placeholder="e.g. 800")
    if budget:
        st.session_state.preferences["budget"] = budget
    else:
        st.session_state.preferences["budget"] = ""

    # City
    city = st.text_input("Your City 🌍", placeholder="e.g. Kuala Lumpur")
    if city:
        st.session_state.preferences["city"] = city
    else:
        st.session_state.preferences["city"] = ""

    # Experience level
    experience = st.selectbox(
        "Your Cat Experience Level:",
        ["First-time owner 🍼", "Some experience 🐾", "Pro cat-parent 👑"]
    )
    st.session_state.preferences["experience"] = experience

    # Living situation
    living_space = st.radio(
        "Your Living Space:",
        ["Apartment 🏢", "House 🏡", "Farm 🌾"]
    )
    st.session_state.preferences["living_space"] = living_space

    # Allergy sensitivity
    allergies = st.checkbox("I have cat allergies 🤧")
    st.session_state.preferences["allergies"] = "Yes" if allergies else "No"

    # Progress tracker
    # Ensure initial_prompt is included in preferences for progress tracking, even if empty
    if "initial_prompt" not in st.session_state.preferences:
        st.session_state.preferences["initial_prompt"] = ""
        
    filled, total = calculate_progress(st.session_state.preferences)
    st.progress(filled / total)
    st.write(f"✅ Preferences filled: {filled}/{total}")

    # Random cat fact
    st.info(f"🐱 Fun Cat Fact: {random.choice(cat_facts)}")

# --- MAIN CHAT ---
st.title("😸 Welcome to CatBuddy!")
st.write("Let's find your purrfect kitty 🐾. Tell me what kind of cat you're dreaming about!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Type your cat wish here..."):
    # Show user message
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.preferences["initial_prompt"] = prompt

    # Get Gemini recommendation
    response = get_gemini_recommendation(st.session_state.preferences)

    # Show assistant message
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
