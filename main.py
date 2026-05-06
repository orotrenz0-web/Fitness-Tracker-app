import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import datetime
import plotly.express as px

st.set_page_config(page_title="Fitness Tracker", layout="wide")


def init_db():
    conn = sqlite3.connect('fitness_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, gender TEXT)''')

    c.execute('DROP TABLE IF EXISTS logs')
    c.execute('''CREATE TABLE logs 
                 (username TEXT, date TEXT, weight REAL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS workouts 
                 (username TEXT, date TEXT, exercise TEXT, sets INTEGER, reps INTEGER, weight REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS intake 
                 (username TEXT, date TEXT, type TEXT, amount INTEGER, detail TEXT)''')
    conn.commit()
    return conn


conn = init_db()


def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def apply_theme():
    bg_img = "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070"
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url("{bg_img}");
            background-size: cover;
            color: #FFFFFF;
        }}
        /* UI IMPROVEMENT: Glassmorphism Cards */
        .metric-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        /* AI INSIGHT STYLING */
        .ai-box {{
            background: linear-gradient(135deg, rgba(230, 57, 70, 0.2), rgba(69, 123, 157, 0.2));
            border-left: 5px solid #e63946;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0px;
        }}
        h1, h2, h3, p, label {{
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,1);
        }}
        .stButton>button {{
            width: 100%;
            border-radius: 10px;
            background-color: #e63946 !important;
            color: white !important;
            font-weight: bold;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            transform: scale(1.02);
            background-color: #ff4d5a !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def get_ai_advice(bmi, total_water, total_caff):
    advice = []
    if bmi < 18.5:
        advice.append("Lower BMI detected. Focus on caloric surplus and progressive overload.")
    elif 18.5 <= bmi <= 24.9:
        advice.append("BMI is optimal. Maintenance or 'Lean Bulk' recommended.")
    else:
        advice.append("BMI is high. Prioritize protein intake and high-intensity steady-state cardio.")

    if total_water < 2000:
        advice.append("Hydration is low. Muscle recovery might be hindered.")

    if total_caff >= 3:
        advice.append("High stimulant intake. Monitor your sleep quality tonight.")

    return advice


def get_body_type(bmi, waist, gender):
    if gender == "Male":
        if waist < 85:
            return "Ectomorph (Lean/Fast Metabolism)"
        elif 85 <= waist <= 95:
            return "Mesomorph (Athletic/Balanced)"
        else:
            return "Endomorph (Strong/Slower Metabolism)"
    else:
        if waist < 70:
            return "Ectomorph (Slim/Lean)"
        elif 70 <= waist <= 80:
            return "Mesomorph (Toned/Athletic)"
        else:
            return "Endomorph (Strong Frame)"


def main():
    apply_theme()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("Fitness Tracker")
            choice = st.tabs(["Login", "Register"])
            with choice[0]:
                u = st.text_input("Username", key="l_u")
                p = st.text_input("Password", type="password", key="l_p")
                if st.button("Enter Gym"):
                    c = conn.cursor()
                    c.execute('SELECT password, gender FROM users WHERE username=?', (u,))
                    res = c.fetchone()
                    if res and res[0] == make_hash(p):
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.session_state.gender = res[1]
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
            with choice[1]:
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                ng = st.selectbox("Gender", ["Male", "Female"])
                if st.button("Sign Up"):
                    try:
                        c = conn.cursor()
                        c.execute('INSERT INTO users VALUES (?,?,?)', (nu, make_hash(np), ng))
                        conn.commit()
                        st.success("Account created!")
                    except:
                        st.error("Username taken.")
    else:
        st.sidebar.title(f"Stay hard, {st.session_state.username}!")
        motivate = ["Don'compare your self to other, Compare your self from Before to After'.",
                    "Don't stop hangga't hindi kapa masarap'.", "Day one or One day.", "Remember why you started."]
        st.sidebar.info(f"{motivate[datetime.datetime.now().day % len(motivate)]}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        tabs = st.tabs(["🏠 Dashboard", "🏋️ Workout", "🥗 Intake Tracker", "📊 Macros", "📈 Progress", "🏆 Squad"])

        with tabs[0]:
            st.header("Health Dashboard")
            c1, c2, c3 = st.columns(3)
            weight = c1.number_input("Weight (kg)", 40.0, 200.0, 70.0)
            height = c2.number_input("Height (cm)", 100.0, 250.0, 170.0)
            waist = c3.number_input("Waist (cm)", 40.0, 150.0, 80.0)
            bmi = weight / ((height / 100) ** 2)

            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.markdown(f"""<div class="metric-card">
                    <h3>Profile Overview</h3>
                    <p><b>BMI:</b> {bmi:.2f} | <b>Body Type:</b> {get_body_type(bmi, waist, st.session_state.gender)}</p>
                    <p><b>Insight:</b> {"Compound movements are key." if st.session_state.gender == "Male" else "Focus on muscle-mind connection."}</p>
                </div>""", unsafe_allow_html=True)

            with col_right:
                st.markdown('<div class="ai-box"><b>🤖 Smart Tracker Coach</b>', unsafe_allow_html=True)

                c = conn.cursor()
                c.execute("SELECT SUM(amount) FROM intake WHERE username=? AND date=? AND type='Water'",
                          (st.session_state.username, str(datetime.date.today())))
                total_w = c.fetchone()[0] or 0
                c.execute("SELECT SUM(amount) FROM intake WHERE username=? AND date=? AND type='Caffeine'",
                          (st.session_state.username, str(datetime.date.today())))
                total_c = c.fetchone()[0] or 0

                insights = get_ai_advice(bmi, total_w, total_c)
                for tip in insights:
                    st.caption(f"• {tip}")
                st.markdown('</div>', unsafe_allow_html=True)

        with tabs[1]:
            st.header("Workout Log")
            with st.form("w_form", clear_on_submit=True):
                ex = st.text_input("Exercise")
                s, r, w_l = st.columns(3)
                sets = s.number_input("Sets", 1, 10, 3)
                reps = r.number_input("Reps", 1, 50, 10)
                wt = w_l.number_input("Weight (kg)", 0.0, 500.0, 20.0)
                if st.form_submit_button("Save Session"):
                    c = conn.cursor()
                    c.execute('INSERT INTO workouts VALUES (?,?,?,?,?,?)',
                              (st.session_state.username, str(datetime.date.today()), ex, sets, reps, wt))
                    conn.commit()
                    st.success("Logged!")
            c = conn.cursor()
            c.execute('SELECT exercise, sets, reps, weight FROM workouts WHERE username=? AND date=?',
                      (st.session_state.username, str(datetime.date.today())))

            for row in c.fetchall():
                st.info(f"🏋️ {row[0]} | {row[1]} sets x {row[2]} reps - {row[3]}kg")

        with tabs[2]:
            st.header("Dynamic Intake")
            col_w, col_f = st.columns(2)

            with col_w:
                st.subheader("Hydration & Caffeine")

                c = conn.cursor()
                c.execute("SELECT SUM(amount) FROM intake WHERE username=? AND date=? AND type='Water'",
                          (st.session_state.username, str(datetime.date.today())))
                total_water = c.fetchone()[0] or 0

                c.execute("SELECT SUM(amount) FROM intake WHERE username=? AND date=? AND type='Caffeine'",
                          (st.session_state.username, str(datetime.date.today())))
                total_caff = c.fetchone()[0] or 0

                target_water = 3000
                water_percentage = min(total_water / target_water, 1.0)
                st.write(f"Daily Water: {total_water}ml / {target_water}ml")
                st.progress(water_percentage)

                wat_amt = st.number_input("Amount to add (ml)", 0, 1000, 250, step=250)
                if st.button("Log Water"):
                    c.execute('INSERT INTO intake VALUES (?,?,?,?,?)',
                              (st.session_state.username, str(datetime.date.today()), "Water", wat_amt, "None"))
                    conn.commit()
                    st.rerun()

                st.divider()

                st.write(f"☕ Caffeine/Pre-workouts today: {total_caff} servings")
                if st.button("Log Caffeine/Pre-Workout"):
                    c.execute('INSERT INTO intake VALUES (?,?,?,?,?)',
                              (st.session_state.username, str(datetime.date.today()), "Caffeine", 1, "Scoop/Cup"))
                    conn.commit()
                    st.rerun()

                if total_caff >= 3:
                    st.warning("You've had a lot of caffeine today. Stay hydrated!")

            with col_f:
                st.subheader("Meal Timing & Protein")
                timing = st.selectbox("Timing", ["Standard", "Pre-Workout", "Post-Workout"])
                kcal = st.number_input("Calories", 0, 2000, 500)
                prot = st.number_input("Protein (g)", 0, 150)
                if st.button("Log Food"):
                    density = "High Protein" if (prot * 4) / (kcal if kcal > 0 else 1) > 0.3 else "Low Protein"
                    c = conn.cursor()
                    c.execute('INSERT INTO intake VALUES (?,?,?,?,?)',
                              (st.session_state.username, str(datetime.date.today()), f"Food ({timing})", kcal,
                               f"{prot}g Prot - {density}"))
                    conn.commit()
                    st.success(f"Logged as {density}!")

            st.divider()
            st.subheader("Micronutrient Checklist")
            st.checkbox("Magnesium (Greens/Nuts)")
            st.checkbox("Iron (Meat/Spinach)")
            st.checkbox("Electrolytes (Salt/Potassium)")

        with tabs[3]:
            st.header("Nutrient Calculator")
            st.markdown(f"""<div class="metric-card">
                <h4>Daily Targets</h4>
                <p><b>Protein:</b> {int(weight * 2.2)}g | <b>Magnesium:</b> 400mg</p>
                <p><b>Iron:</b> {"8mg" if st.session_state.gender == "Male" else "18mg"} | <b>Vitamins:</b> Multi-focused</p>
            </div>""", unsafe_allow_html=True)

        with tabs[4]:
            st.header("Progress Tracking")
            img = st.file_uploader("Upload Photo", type=['jpg', 'png'])
            if img: st.image(img, width=250)

            target_w = st.number_input("Goal Weight (kg)", 40.0, 200.0, 65.0)
            st.write(f"Timeline: {int(abs(weight - target_w) / 0.5 * 7)} days to goal.")

            if st.button("Save Weight"):
                c = conn.cursor()
                c.execute('INSERT INTO logs VALUES (?,?,?)',
                          (st.session_state.username, str(datetime.date.today()), weight))
                conn.commit()
                st.toast("Progress Saved!")

            c.execute('SELECT date, weight FROM logs WHERE username=? ORDER BY date ASC', (st.session_state.username,))
            hist = pd.DataFrame(c.fetchall(), columns=['Date', 'Weight'])

            if not hist.empty:
                fig = px.line(hist, x='Date', y='Weight', title="Weight Journey", markers=True)
                fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

            if st.button("Reset Data"):
                c.execute('DELETE FROM logs WHERE username=?', (st.session_state.username,))
                c.execute('DELETE FROM workouts WHERE username=?', (st.session_state.username,))
                c.execute('DELETE FROM intake WHERE username=?', (st.session_state.username,))
                conn.commit()
                st.rerun()

        with tabs[5]:
            st.header("🏆 Squad Leaderboard")
            q = '''SELECT username, COUNT(DISTINCT date) as days FROM 
                   (SELECT username, date FROM logs UNION SELECT username, date FROM workouts)
                   GROUP BY username ORDER BY days DESC LIMIT 5'''
            c.execute(q)
            for i, l in enumerate(c.fetchall()):
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.1); padding:10px; border-radius:10px; margin-bottom:10px;">
                🔥 <b>#{i + 1} {l[0]}</b> — {l[1]} active days
                </div>
                """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()