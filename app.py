import streamlit as st
import pandas as pd
from datetime import date

# Set up the app page configuration
st.set_page_config(page_title="FemmeMacro Pro: Women's Custom Tracker", layout="centered", page_icon="💪")

st.title("🙋‍♀️ FemmeMacro Pro Calculator & Tracker")
st.write("A specialized macro calculator and daily tracker tailored for women aged 25–60.")

# ==========================================
# SIDEBAR: USER PARAMETERS INPUT
# ==========================================
st.sidebar.header("1. Your Profile")
age = st.sidebar.slider("Age", min_value=25, max_value=60, value=54, step=1)
height_ft = st.sidebar.number_input("Height (Feet)", min_value=4, max_value=7, value=5)
height_in = st.sidebar.number_input("Height (Inches)", min_value=0, max_value=11, value=4)
weight_lbs = st.sidebar.number_input("Current Weight (lbs)", min_value=90, max_value=400, value=180)

st.sidebar.header("2. Exercise Level")
workout_days = st.sidebar.slider("Workout Frequency (Days/Week)", min_value=0, max_value=7, value=3, step=1)

st.sidebar.header("3. Health Conditions & Tweaks")
condition = st.sidebar.selectbox(
    "Medical/Hormonal Factors",
    ["None", "Hypothyroidism", "PCOS (Polycystic Ovary Syndrome)", "Post-Menopausal/Menopause Transition"]
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
# Step 1: Calculate Base Energy Expenditure (Mifflin-St Jeor Formula for Women)
height_cm = ((height_ft * 12) + height_in) * 2.54
weight_kg = weight_lbs * 0.453592
bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

# Step 2: Dynamically calculate activity multiplier based on workout days
if workout_days == 0:
    activity_multiplier = 1.2      # Sedentary
elif 1 <= workout_days <= 2:
    activity_multiplier = 1.375    # Lightly Active
elif 3 <= workout_days <= 5:
    activity_multiplier = 1.55     # Moderately Active
else:
    activity_multiplier = 1.725    # Highly Active

# Safety Tweak: Cap multiplier if physical limitations exist to avoid overestimating burn
if limitation in ["Joint Pain / Arthritis", "Low Mobility / Injury recovery"] and activity_multiplier > 1.375:
    activity_multiplier = 1.375
    st.sidebar.warning("Activity multiplier capped slightly for workout safety due to listed physical limitation.")

calories = bmr * activity_multiplier

# Step 3: Apply Age & Hormonal Tweaks
if age >= 50 or condition == "Post-Menopausal/Menopause Transition":
    calories *= 0.93  # 7% reduction for post-menopausal slowing
if condition in ["Hypothyroidism", "PCOS (Polycystic Ovary Syndrome)"]:
    calories *= 0.88  # 12% reduction for medically documented lower metabolic rate

# Round final baseline calories safely
target_calories = int(round(calories))

# Step 4: Define Macro Ratio Splits
if goal == "Aggressive Low-Carb Paleo":
    p_pct, f_pct, c_pct = 0.45, 0.40, 0.15
elif goal == "Balanced Fat Loss":
    p_pct, f_pct, c_pct = 0.35, 0.30, 0.35
else:  # High Protein Lean Muscle
    p_pct, f_pct, c_pct = 0.40, 0.30, 0.30

# Step 5: Convert Calories to Target Grams Using Fixed Math Values
protein_g = int(round((target_calories * p_pct) / 4))
fat_g = int(round((target_calories * f_pct) / 9))
carb_g = int(round((target_calories * c_pct) / 4))

# Step 6: Target Water Intake Calculation (Baseline 0.5 oz per lb of body weight + exercise bonus)
target_water = int(round((weight_lbs * 0.5) + (workout_days * 4)))

# ==========================================
# DISPLAY SYSTEM SECTION: PARAMETERS OUTPUT
# ==========================================
st.header("🎯 Your Personalized Daily Targets")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Calories", f"{target_calories} kcal")
col2.metric("🥩 Protein", f"{protein_g}g")
col3.metric("🥑 Fats", f"{fat_g}g")
col4.metric("🥦 Carbs", f"{carb_g}g")
col5.metric("💧 Water Target", f"{target_water} oz")

st.info(f"**App Logic Notice:** Your profile dynamically adjusted targets based on: *Age {age}* + *{workout_days} Workouts/Week* + *Condition: {condition}* + *Limitation: {limitation}*.")

# ==========================================
# CONTEXTUAL EDUCATION & LINKS SECTION
# ==========================================
st.header("📚 Recommended Smart Resources")
st.write("Verified informational portals loaded dynamically for your current situation:")

if condition == "Post-Menopausal/Menopause Transition" or age >= 50:
    st.markdown("- [The Menopause Society Guidelines](https://menopause.org) — Scientific approaches to managing fat distribution and cardiovascular health during midlife transitions.")
if condition == "PCOS (Polycystic Ovary Syndrome)":
    st.markdown("- [PCOS Nutrition Center](https://pcosnutrition.com) — Expert nutritional guides detailing insulin management and carbohydrate tolerances for women with PCOS.")
if condition == "Hypothyroidism":
    st.markdown("- [American Thyroid Association](https://thyroid.org) — Direct access to information detailing how thyroid hormones regulate resting energy expenditure.")
if limitation == "Joint Pain / Arthritis":
    st.markdown("- [Arthritis Foundation: Exercise Rules](https://arthritis.org) — Low-impact exercise modifications, tracking guidelines, and pain-management strategies for resistance training.")
if goal == "Aggressive Low-Carb Paleo":
    st.markdown("- [Cronometer Nutrition Tracker](https://cronometer.com) — The recommended tracking utility optimized for logging micronutrients and strict carbohydrate limits.")

st.markdown("- [National Institutes of Health (NIH) Dietary Guidelines](https://nih.gov) — General nutritional targets, safe macro ranges, and hydration baselines for adult females.")

# ==========================================
# USER INPUT WORKSPACE: LOGGING TRACKER
# ==========================================
st.header("📝 Daily Performance Tracker")
st.write("Log your real-world daily values below to compare them directly against your target goals:")

# Initialize database to include water tracking
if 'tracker_db' not in st.session_state:
    st.session_state.tracker_db = pd.DataFrame(columns=["Date", "Weight (lbs)", "Protein (g)", "Fat (g)", "Carbs (g)", "Water (oz)"])

with st.form("log_form", clear_on_submit=True):
    t_date = st.date_input("Tracking Date", date.today())
    t_weight = st.number_input("Today's Weight (lbs)", min_value=80.0, max_value=400.0, value=float(weight_lbs), step=0.1)
    t_prot = st.number_input("Logged Protein (g)", min_value=0, max_value=300, value=0)
    t_fat = st.number_input("Logged Fat (g)", min_value=0, max_value=200, value=0)
    t_carb = st.number_input("Logged Carbs (g)", min_value=0, max_value=500, value=0)
    t_water = st.number_input("Logged Water Intake (oz)", min_value=0, max_value=300, value=0)
    submit_button = st.form_submit_button("Save Entry to Dashboard Log")

if submit_button:
    new_row = pd.DataFrame([{
        "Date": t_date, "Weight (lbs)": t_weight, "Protein (g)": t_prot, "Fat (g)": t_fat, "Carbs (g)": t_carb, "Water (oz)": t_water
    }])
    st.session_state.tracker_db = pd.concat([st.session_state.tracker_db, new_row], ignore_index=True)
    st.success("Entry recorded successfully!")

# Display current log history if data exists
if not st.session_state.tracker_db.empty:
    st.subheader("📋 Your Saved Metric Log History")
    st.dataframe(st.session_state.tracker_db, use_container_width=True)
else:
    st.warning("No tracking data logged yet. Fill out the form above to display your personal tracking dashboard table.")
