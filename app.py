import streamlit as st
import pandas as pd
import requests
from datetime import date

# Set up the app page configuration
st.set_page_config(page_title="PrimalMacro: Custom Tracker", layout="centered", page_icon="🥩")

st.title("🥩 PrimalMacro Calculator & Tracker")
st.write("A specialized macro calculator and automated food search tracker tailored for individuals aged 25–60.")

# ==========================================
# SIDEBAR: USER PARAMETERS INPUT
# ==========================================
st.sidebar.header("1. Biological Profile")
gender = st.sidebar.selectbox("Biological Sex", ["Female", "Male"])

age = st.sidebar.slider("Age", min_value=25, max_value=60, value=54, step=1)
height_ft = st.sidebar.number_input("Height (Feet)", min_value=4, max_value=7, value=5)
height_in = st.sidebar.number_input("Height (Inches)", min_value=0, max_value=11, value=4)
weight_lbs = st.sidebar.number_input("Current Weight (lbs)", min_value=90, max_value=400, value=180)

st.sidebar.header("2. Exercise Level")
workout_days = st.sidebar.slider("Workout Frequency (Days/Week)", min_value=0, max_value=7, value=3, step=1)

st.sidebar.header("3. Health Conditions & Tweaks")
if gender == "Female":
    condition = st.sidebar.selectbox(
        "Medical/Hormonal Factors",
        ["None", "Hypothyroidism", "PCOS (Polycystic Ovary Syndrome)", "Post-Menopausal/Menopause Transition"]
    )
else:
    condition = st.sidebar.selectbox(
        "Medical/Hormonal Factors",
        ["None", "Hypothyroidism", "Low Testosterone (Low T)"]
    )

st.sidebar.header("4. Physical & Body Limitations")
limitation = st.sidebar.selectbox(
    "Do you have physical limitations?",
    ["None", "Joint Pain / Arthritis", "Low Mobility / Injury recovery", "Cardiovascular restrictions"]
)

st.sidebar.header("5. Your Diet Goal")
goal = st.sidebar.radio("Select Target Ratio", ["Aggressive Low-Carb Paleo", "Balanced Fat Loss", "High Protein Lean Muscle"])

# ==========================================
# APP LOGIC & FORMULA CALCULATIONS
# ==========================================
height_cm = ((height_ft * 12) + height_in) * 2.54
weight_kg = weight_lbs * 0.453592

if gender == "Female":
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
else:
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5

if workout_days == 0:
    activity_multiplier = 1.2
elif 1 <= workout_days <= 2:
    activity_multiplier = 1.375
elif 3 <= workout_days <= 5:
    activity_multiplier = 1.55
else:
    activity_multiplier = 1.725

if limitation in ["Joint Pain / Arthritis", "Low Mobility / Injury recovery"] and activity_multiplier > 1.375:
    activity_multiplier = 1.375

calories = bmr * activity_multiplier

if gender == "Female":
    if age >= 50 or condition == "Post-Menopausal/Menopause Transition":
        calories *= 0.93  
else:
    if age >= 50 or condition == "Low Testosterone (Low T)":
        calories *= 0.95  

if condition == "Hypothyroidism":
    calories *= 0.88
elif condition == "PCOS (Polycystic Ovary Syndrome)":
    calories *= 0.88

target_calories = int(round(calories))

if goal == "Aggressive Low-Carb Paleo":
    p_pct, f_pct, c_pct = 0.45, 0.40, 0.15
elif goal == "Balanced Fat Loss":
    p_pct, f_pct, c_pct = 0.35, 0.30, 0.35
else: 
    p_pct, f_pct, c_pct = 0.40, 0.30, 0.30

protein_g = int(round((target_calories * p_pct) / 4))
fat_g = int(round((target_calories * f_pct) / 9))
carb_g = int(round((target_calories * c_pct) / 4))
target_water = int(round((weight_lbs * 0.5) + (workout_days * 4)))

# Display targets dashboard
st.header("🎯 Your Personalized Daily Targets")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Calories", f"{target_calories} kcal")
col2.metric("🥩 Protein", f"{protein_g}g")
col3.metric("🥑 Fats", f"{fat_g}g")
col4.metric("🥦 Carbs", f"{carb_g}g")
col5.metric("💧 Water Target", f"{target_water} oz")

# ==========================================
# OPEN INTERNET NUTRITION ENGINE (NUTROLA)
# ==========================================
st.header("🔍 Intelligent Food Lookup Engine")
st.write("Type a food item to instantly pull its nutritional breakdown (e.g., *'chicken breast'*, *'avocado'*, *'egg'*).")

food_query = st.text_input("What food item are you looking up?", placeholder="Type food item here...")

searched_calories = 0.0
searched_protein = 0.0
searched_fat = 0.0
searched_carbs = 0.0

if food_query:
    url = f"https://nutrola.app{food_query}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            foods = data.get("foods", [])
            if foods:
                top_food = foods
                st.success(f"**Found item:** {top_food.get('name', food_query).title()} (Per 100g standard serving)")
                
                searched_calories = float(top_food.get("calories", 0))
                searched_protein = float(top_food.get("protein", 0))
                searched_fat = float(top_food.get("fat", 0))
                searched_carbs = float(top_food.get("carbs", 0))
                
                f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                f_col1.write(f"🔥 **Calories:** {int(round(searched_calories))} kcal")
                f_col2.write(f"🥩 **Protein:** {int(round(searched_protein))}g")
                f_col3.write(f"🥑 **Fat:** {int(round(searched_fat))}g")
                f_col4.write(f"🥦 **Carbs:** {int(round(searched_carbs))}g")
            else:
                st.warning("Food item not found in the open directory. Try a broader term.")
        else:
            st.error("The open database server is currently busy. You can still manually type your totals below.")
    except Exception:
         st.error("Network connection timeout. Please enter metrics manually in the tracker section below.")

# ==========================================
# USER INPUT WORKSPACE: LOGGING TRACKER
# ==========================================
st.header("📝 Daily Performance Tracker")
st.write("Review your macro entries below and click save to commit them to your history log:")

if 'tracker_db' not in st.session_state:
    st.session_state.tracker_db = pd.DataFrame(columns=["Date", "Weight (lbs)", "Protein (g)", "Fat (g)", "Carbs (g)", "Water (oz)"])

with st.form("log_form", clear_on_submit=False):
    t_date = st.date_input("Tracking Date", date.today())
    t_weight = st.number_input("Today's Weight (lbs)", min_value=80.0, max_value=400.0, value=float(weight_lbs), step=0.1)
    
    t_prot = st.number_input("Logged Protein (g)", min_value=0, max_value=300, value=int(round(searched_protein)))
    t_fat = st.number_input("Logged Fat (g)", min_value=0, max_value=200, value=int(round(searched_fat)))
    t_carb = st.number_input("Logged Carbs (g)", min_value=0, max_value=500, value=int(round(searched_carbs)))
    t_water = st.number_input("Logged Water Intake (oz)", min_value=0, max_value=300, value=0)
    
    submit_button = st.form_submit_button("Save Entry to Dashboard Log")

if submit_button:
    new_row = pd.DataFrame([{
        "Date": t_date, "Weight (lbs)": t_weight, "Protein (g)": t_prot, "Fat (g)": t_fat, "Carbs (g)": t_carb, "Water (oz)": t_water
    }])
    st.session_state.tracker_db = pd.concat([st.session_state.tracker_db, new_row], ignore_index=True)
    st.success("Entry recorded successfully!")

if not st.session_state.tracker_db.empty:
    st.subheader("📋 Your Saved Metric Log History")
    st.dataframe(st.session_state.tracker_db, use_container_width=True)
    
    st.subheader("📊 Your Performance Averages")
    avg_weight = st.session_state.tracker_db["Weight (lbs)"].mean()
    avg_prot = st.session_state.tracker_db["Protein (g)"].mean()
    avg_fat = st.session_state.tracker_db["Fat (g)"].mean()
    avg_carb = st.session_state.tracker_db["Carbs (g)"].mean()
    avg_water = st.session_state.tracker_db["Water (oz)"].mean()
    
    a_col1, a_col2, a_col3, a_col4, a_col5 = st.columns(5)
    a_col1.metric("Avg Weight", f"{avg_weight:.1f} lbs")
    a_col2.metric("Avg Protein", f"{int(round(avg_prot))}g")
    a_col3.metric("Avg Fat", f"{int(round(avg_fat))}g")
    a_col4.metric("Avg Carbs", f"{int(round(avg_carb))}g")
    a_col5.metric("Avg Water", f"{int(round(avg_water))} oz")
else:
    st.warning("No tracking data logged yet. Fill out the form above to display your personal tracking dashboard table and averages.")
