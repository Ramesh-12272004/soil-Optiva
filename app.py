import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO
import pandas as pd
import json
import os
import urllib.parse
import base64
import time

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="ANITS Soil Lab",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --------------------------
# USER DATABASE
# --------------------------
USER_DB_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

def register_user(name, email, password):
    users = load_users()
    if email in users:
        return False, "An account with this email already exists."
    users[email] = {"name": name, "password": password}
    save_users(users)
    return True, "Account created successfully!"

def login_user(email, password):
    users = load_users()
    if email not in users:
        return False, None, "No account found with this email."
    if users[email]["password"] != password:
        return False, None, "Incorrect password."
    return True, users[email]["name"], "Login successful!"

# --------------------------
# AI CHATBOT ENGINE
# --------------------------
def get_ai_response(query):
    q = query.lower().strip()
    if "cbr" in q and "low" in q:
        return "🔴 Low CBR means weak subgrade soil. You'll need soil stabilisation or a thicker pavement layer (IRC:37). CBR < 3% is not suitable for direct use."
    if "cbr" in q:
        return "📏 CBR (California Bearing Ratio) measures soil strength for road subgrade design. Higher CBR = stronger soil. CBR > 15% is ideal; < 3% needs stabilisation (IS 2720 Part 16)."
    if "liquid limit" in q or "ll" in q:
        return "💧 Liquid Limit is the water content where soil transitions from plastic to liquid state. Measured using Casagrande apparatus or Cone Penetrometer. LL > 50% = high compressibility (IS 2720 Part 5)."
    if "plastic limit" in q or "pl" in q:
        return "🧱 Plastic Limit is the minimum water content at which soil can be rolled into a 3mm thread without crumbling. Helps classify soil behaviour."
    if "plasticity index" in q or "pi" in q:
        return "📊 Plasticity Index = LL − PL. PI < 7 = low plasticity (good for subgrade). PI > 17 = high plasticity clay — risk of shrink-swell (IS 1904)."
    if "atterberg" in q:
        return "📋 Atterberg Limits include: Liquid Limit (LL), Plastic Limit (PL), and Shrinkage Limit (SL). They define soil consistency states and are key for soil classification (IS 1498)."
    if "shrinkage limit" in q:
        return "🔵 Shrinkage Limit is the water content below which soil volume doesn't reduce further on drying. Useful for expansive clay assessment."
    if "proctor" in q or "compaction" in q or "omc" in q or "mdd" in q:
        return "⚙️ Proctor Compaction test finds the Optimum Moisture Content (OMC) and Maximum Dry Density (MDD). MDD > 1.9 g/cc = dense soil suitable for embankments (IS 2720 Part 7)."
    if "shear strength" in q or "direct shear" in q:
        return "💪 Shear strength = c + σ·tan(φ). 'c' is cohesion, φ is friction angle. Measured via Direct Shear, Triaxial, or Vane Shear tests (IS 2720 Parts 12–13)."
    if "triaxial" in q:
        return "🔬 Triaxial test measures shear strength under controlled drainage. Types: UU, CU, CD. More accurate than direct shear for saturated clays."
    if "ucs" in q or "unconfined" in q:
        return "📐 UCS (Unconfined Compressive Strength) = 2c for saturated clays. qu < 25 kPa = very soft; > 100 kPa = stiff clay suitable for light structures (IS 6403)."
    if "vane shear" in q:
        return "🌀 Vane Shear test measures undrained shear strength in soft cohesive soils, often in situ. Used for embankment and foundation design."
    if "permeability" in q or "constant head" in q or "variable head" in q:
        return "💧 Permeability (k) controls drainage and seepage. Constant head for sandy soils; Variable/Falling head for fine-grained soils. Measured per IS 2720 Part 17."
    if "consolidation" in q or "settlement" in q:
        return "📉 Consolidation test gives Cv (coefficient of consolidation) and Cc (compression index). Low Cv = slow settlement. Used to predict long-term settlement (IS 2720 Part 15)."
    if "sieve" in q or "grain size" in q or "gradation" in q:
        return "🔎 Sieve Analysis classifies soil by particle size. D10, D30, D60 determine Cu (uniformity) and Cc (gradation). Well-graded soils compact better (IS 2720 Part 4)."
    if "specific gravity" in q:
        return "⚖️ Specific Gravity (Gs) of soil solids is typically 2.65–2.80. Used to compute void ratio, porosity, and degree of saturation (IS 2720 Part 3)."
    if "core cutter" in q or "bulk density" in q or "field density" in q:
        return "🔩 Core Cutter test determines in-situ bulk density and dry density. Quick method for cohesive soils without stones (IS 2720 Part 29)."
    if "uscs" in q or "classification" in q or "is 1498" in q:
        return "📚 IS 1498 / USCS classifies soils as GW, GP, GM, GC, SW, SP, SM, SC, ML, CL, MI, CI, MH, CH etc. based on grain size and Atterberg limits."
    if "expansive" in q or "black cotton" in q:
        return "⚠️ Expansive (Black Cotton) soils swell with moisture. Free Swell Index > 50% = problematic. Use granular fill, lime stabilisation, or under-reamed piles."
    if "foundation" in q:
        return "🏗️ Foundation type depends on soil bearing capacity and settlement. Soft clay → Raft or Pile. Medium soil → Isolated/Combined footings. Always check IS 1904 and IS 6403."
    if "bearing capacity" in q:
        return "📐 Bearing capacity depends on c, φ, and depth. Use Terzaghi's or Meyerhof's equation. Always apply FOS ≥ 3 for safe design (IS 6403)."
    if "pile" in q:
        return "🔩 Piles are used when surface soil is weak. Friction piles transfer load through skin friction; end-bearing piles rest on rock or hard stratum."
    if "stabiliz" in q or "lime" in q or "cement" in q:
        return "🛠️ Soil stabilisation improves weak soils. Lime reduces plasticity of clays. Cement increases strength. Fly ash / geotextiles also used (IS 6403, IRC:SP:20)."
    if "how to use" in q or "how do i" in q or "help" in q:
        return "📱 Select any test from the sidebar, enter your observations, and click Calculate. Results + IS Code recommendations + DOCX report are auto-generated."
    if "report" in q or "download" in q or "docx" in q:
        return "📥 Every test generates a downloadable DOCX report with procedure, formulas, results, graphs, and IS Code recommendations."
    if "share" in q or "whatsapp" in q:
        return "📤 You can share results via WhatsApp, Telegram, Email, or Twitter using the share buttons shown after each test result."
    if "history" in q:
        return "🕒 All your past tests are saved in 'Test History'. You can filter by test type and see IS Code recommendations for old results too."
    if "is 2720" in q:
        return "📖 IS 2720 is the Indian Standard for 'Methods of Test for Soils'. It has 40+ parts covering classification, compaction, shear, consolidation, and more."
    if "is code" in q or "irc" in q:
        return "📖 Key IS Codes: IS 1498 (Classification), IS 2720 (Test Methods), IS 1904 (Foundation Design), IS 6403 (Bearing Capacity), IRC:37 (Pavement Design)."
    return "🤖 I can answer questions about soil tests, IS codes, foundation design, soil classification, or app usage. Try: 'What is CBR?', 'Explain liquid limit', or 'Which foundation for soft clay?'"


def ai_chatbot(key_prefix="main"):
    chat_key  = f"chat_history_{key_prefix}"
    input_key = f"ai_input_{key_prefix}"
    ask_key   = f"ask_btn_{key_prefix}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            ("Bot", "👋 Hi! I'm your Soil Testing AI Assistant. Ask me anything about soil tests, IS codes, or foundation design!")
        ]
    st.markdown("### 🤖 AI Assistant")
    st.markdown("<small style='color:rgba(190,220,255,0.9);font-weight:600;'>💡 Quick Questions</small>", unsafe_allow_html=True)
    qcols = st.columns(2)
    quick_prompts = [
        ("What is CBR?", "What is CBR?"),
        ("Explain Liquid Limit", "Explain liquid limit"),
        ("Best foundation for soft clay?", "Best foundation for soft clay?"),
        ("What is shear strength?", "What is shear strength?"),
    ]
    for i, (label, prompt) in enumerate(quick_prompts):
        with qcols[i % 2]:
            if st.button(label, key=f"qp_{key_prefix}_{i}", use_container_width=True):
                resp = get_ai_response(prompt)
                st.session_state[chat_key].append(("You", label))
                st.session_state[chat_key].append(("Bot", resp))
                st.rerun()
    for role, msg in st.session_state[chat_key][-8:]:
        if role == "Bot":
            with st.chat_message("assistant"):
                st.markdown(msg)
        else:
            with st.chat_message("user"):
                st.markdown(msg)
    col_in, col_btn = st.columns([4, 1])
    with col_in:
        user_input = st.text_input("", placeholder="Ask about soil tests, IS codes…",
                                   key=input_key, label_visibility="collapsed")
    with col_btn:
        if st.button("Ask →", key=ask_key, use_container_width=True):
            if user_input and user_input.strip():
                resp = get_ai_response(user_input)
                st.session_state[chat_key].append(("You", user_input.strip()))
                st.session_state[chat_key].append(("Bot", resp))
                st.rerun()


# --------------------------
# IS CODE RECOMMENDATIONS
# --------------------------
def get_is_recommendations(test_name, result_dict):
    recs = []
    vals = {k.lower().replace(" ", "_"): v for k, v in result_dict.items() if isinstance(v, (int, float))}
    if "cbr" in test_name.lower():
        cbr = vals.get("cbr_%", vals.get("cbr_value", None))
        if cbr is not None:
            if cbr < 3:    recs.append(("🔴 CBR < 3%",   "Not suitable for subgrade. Soil stabilisation required (IS 2720 Part 16).", "danger"))
            elif cbr < 7:  recs.append(("🟡 CBR 3–7%",   "Weak subgrade. Requires thick pavement design (IRC:37).", "warning"))
            elif cbr < 15: recs.append(("🟢 CBR 7–15%",  "Moderate subgrade. Suitable for roads with appropriate pavement thickness.", "success"))
            else:           recs.append(("✅ CBR > 15%",  "Good subgrade. Economical pavement design possible (IRC:37).", "success"))
    if "liquid limit" in test_name.lower() or "ll" in vals:
        ll = vals.get("liquid_limit_%", vals.get("ll", None))
        if ll is not None:
            if ll < 35:    recs.append(("🟢 LL < 35%",   "Low plasticity soil (ML/CL). Good for earthworks (IS 1498).", "success"))
            elif ll < 50:  recs.append(("🟡 LL 35–50%",  "Medium plasticity (CI/MI). Use with caution in foundations.", "warning"))
            else:           recs.append(("🔴 LL > 50%",   "High compressibility (CH/MH). Not suitable for direct foundation (IS 1904).", "danger"))
    if "plastic" in test_name.lower():
        pi = vals.get("plasticity_index", vals.get("pi", None))
        if pi is not None:
            if pi < 7:     recs.append(("✅ PI < 7",      "Low plasticity. Suitable for pavement subgrade.", "success"))
            elif pi < 17:  recs.append(("🟡 PI 7–17",    "Medium plasticity. Monitor swelling potential.", "warning"))
            else:           recs.append(("🔴 PI > 17",    "High plasticity clay. Risk of shrink-swell. Avoid in foundations (IS 1904).", "danger"))
    if "compaction" in test_name.lower():
        mdd = vals.get("mdd_g/cc", vals.get("maximum_dry_density", None))
        if mdd is not None:
            if mdd > 1.9:   recs.append(("✅ MDD > 1.9 g/cc",    "Dense soil. Good for embankment and fill (IS 2720 Part 7).", "success"))
            elif mdd > 1.6: recs.append(("🟡 MDD 1.6–1.9 g/cc", "Moderate density. Suitable for general earthwork.", "warning"))
            else:            recs.append(("🔴 MDD < 1.6 g/cc",   "Low density. Compaction improvement needed.", "danger"))
    if "shear" in test_name.lower() or "ucs" in test_name.lower() or "triaxial" in test_name.lower():
        qu = vals.get("qu_kn/m²", vals.get("unconfined_compressive_strength", None))
        if qu is not None:
            if qu < 25:    recs.append(("🔴 qu < 25 kPa",   "Very soft clay. Not suitable for direct loading (IS 6403).", "danger"))
            elif qu < 100: recs.append(("🟡 qu 25–100 kPa", "Soft to medium clay. Requires bearing capacity check.", "warning"))
            else:           recs.append(("✅ qu > 100 kPa",  "Stiff clay. Good bearing capacity for light structures.", "success"))
    if "consolidation" in test_name.lower():
        cv = vals.get("cv_cm²/s", vals.get("coefficient_of_consolidation", None))
        if cv is not None:
            if cv < 0.001: recs.append(("🔴 Low Cv",      "Very slow consolidation. Expect large settlements (IS 2720 Part 15).", "danger"))
            else:           recs.append(("🟢 Adequate Cv", "Consolidation rate acceptable for design.", "success"))
    if not recs:
        recs.append(("ℹ️ No specific IS recommendation", "Manual interpretation required. Refer IS 2720 series.", "info"))
    return recs


def get_soil_classification(result_dict):
    vals = {k.lower().replace(" ", "_"): v for k, v in result_dict.items() if isinstance(v, (int, float))}
    ll = vals.get("liquid_limit_%", vals.get("ll", None))
    pi = vals.get("plasticity_index", vals.get("pi", None))
    if ll is not None and pi is not None:
        if ll < 35:   return ("ML","Silt of low plasticity","🟡") if pi < 7 else ("CL","Clay of low plasticity","🟢")
        elif ll < 50: return ("MI","Silt of intermediate plasticity","🟡") if pi < 7 else ("CI","Clay of intermediate plasticity","🟠")
        else:          return ("MH","Silt of high plasticity","🔴") if pi < 7 else ("CH","Clay of high plasticity","🔴")
    return None, None, None


# --------------------------
# SHARING
# --------------------------
def build_share_text(test_name, result_dict):
    lines = [f"🧪 *ANITS Soil Test Report*", f"Test: *{test_name}*", ""]
    for k, v in result_dict.items():
        if isinstance(v, (int, float)) and v is not None:
            lines.append(f"• {k}: {round(v, 3)}")
        elif isinstance(v, str) and k not in ("procedure","formulas") and len(v) < 120:
            lines.append(f"• {k}: {v}")
    lines.append("\n_Generated by ANITS Civil Dept – Soil Testing System_")
    return "\n".join(lines)


def build_ai_prompt(test_name, result_dict):
    lines = [
        f"I have soil test results from '{test_name}' conducted at ANITS Civil Engineering Laboratory.",
        "Please analyse these results and provide engineering recommendations based on Indian Standard codes.\n",
        "Test Results:"
    ]
    for k, v in result_dict.items():
        if isinstance(v, (int, float)) and v is not None:
            lines.append(f"  - {k}: {round(v, 3)}")
        elif isinstance(v, str) and k not in ("procedure","formulas","data","graph","diagram") and len(v) < 120:
            lines.append(f"  - {k}: {v}")
    lines += ["\nPlease provide:",
              "1. Interpretation of each result",
              "2. Relevant IS Code references (IS 1498, IS 2720, IS 1904, IS 6403, IRC:37)",
              "3. Foundation / pavement / earthwork recommendations",
              "4. Any soil stabilisation suggestions if required"]
    return "\n".join(lines)


def share_buttons(test_name, result_dict, doc_bytes=None, inside_expander=False):
    text         = build_share_text(test_name, result_dict)
    ai_prompt    = build_ai_prompt(test_name, result_dict)
    encoded_text = urllib.parse.quote(text)
    encoded_ai   = urllib.parse.quote(ai_prompt)

    wa_url       = f"https://api.whatsapp.com/send?text={encoded_text}"
    telegram_url = f"https://t.me/share/url?url=&text={encoded_text}"
    mail_subject = urllib.parse.quote(f"ANITS Soil Test Report – {test_name}")
    mail_body    = urllib.parse.quote(text.replace("*", ""))
    mail_url     = f"mailto:?subject={mail_subject}&body={mail_body}"
    twitter_url  = f"https://twitter.com/intent/tweet?text={encoded_text}"
    chatgpt_url  = f"https://chat.openai.com/?q={encoded_ai}"
    copilot_url  = "https://copilot.microsoft.com/"
    search_query = urllib.parse.quote(f"{test_name} IS code soil test India")
    google_url   = f"https://www.google.com/search?q={search_query}"
    scholar_url  = f"https://scholar.google.com/scholar?q={search_query}"

    st.markdown("#### 📤 Share Results")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.link_button("💬 WhatsApp",  wa_url,       use_container_width=True)
    with c2: st.link_button("✈️ Telegram",  telegram_url, use_container_width=True)
    with c3: st.link_button("📧 Email",     mail_url,     use_container_width=True)
    with c4: st.link_button("🐦 Twitter/X", twitter_url,  use_container_width=True)

    st.markdown("#### 🔍 Search & AI Assistants")
    st.markdown(
        "<p style='color:rgba(190,220,255,0.88);font-size:0.82rem;margin-bottom:8px;'>"
        "Search IS codes online, or open an AI. "
        "For Copilot, copy the prompt below and paste it after opening.</p>",
        unsafe_allow_html=True
    )
    cg, cs, cgpt, ccop = st.columns(4)
    with cg:   st.link_button("🔍 Google Search",  google_url,  use_container_width=True)
    with cs:   st.link_button("📚 Google Scholar", scholar_url, use_container_width=True)
    with cgpt: st.link_button("🟢 Ask ChatGPT",    chatgpt_url, use_container_width=True)
    with ccop: st.link_button("🔵 Open Copilot",   copilot_url, use_container_width=True)

    safe_key = f"copilot_ta_{abs(hash(test_name + str(id(result_dict))))}"
    st.markdown(
        "<p style='color:rgba(190,220,255,0.88);font-size:0.82rem;margin-top:10px;margin-bottom:4px;'>"
        "📋 <b style='color:#fff;'>Copilot Prompt</b> — Copy &amp; paste into Copilot:</p>",
        unsafe_allow_html=True
    )
    st.text_area("", value=ai_prompt, height=130, key=safe_key, label_visibility="collapsed")

    if doc_bytes:
        st.download_button(
            label="📥 Download Report (.docx)",
            data=doc_bytes,
            file_name=f"ANITS_{test_name.replace(' ', '_')}_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )


# --------------------------
# DOCX BUILDERS
# --------------------------
def _fill_doc_for_test(doc, test_name, res):
    doc.add_heading(test_name, 1)
    if "procedure" in res:
        doc.add_heading("Procedure", 2)
        for line in str(res["procedure"]).split("\n"):
            if line.strip(): doc.add_paragraph(line.strip())
    if "formulas" in res:
        doc.add_heading("Formulas", 2)
        for line in str(res["formulas"]).split("\n"):
            if line.strip(): doc.add_paragraph(line.strip())
    if "data" in res and isinstance(res["data"], pd.DataFrame):
        df = res["data"]
        doc.add_heading("Results Data", 2)
        tbl = doc.add_table(rows=1, cols=len(df.columns))
        tbl.style = "Table Grid"
        for i, col in enumerate(df.columns):
            tbl.rows[0].cells[i].text = str(col)
        for _, row in df.iterrows():
            cells = tbl.add_row().cells
            for i, val in enumerate(row):
                cells[i].text = str(val)
    if "graph" in res and res["graph"] is not None:
        doc.add_heading("Graph", 2)
        try:
            res["graph"].seek(0)
            doc.add_picture(res["graph"], width=Inches(5))
        except Exception: pass
    if "diagram" in res and res["diagram"] is not None:
        doc.add_heading("Diagram", 2)
        try:
            res["diagram"].seek(0)
            doc.add_picture(res["diagram"], width=Inches(4))
        except Exception: pass
    recs = get_is_recommendations(test_name, res)
    doc.add_heading("IS Code Recommendations", 2)
    for title, body, _ in recs:
        doc.add_paragraph(f"{title}: {body}")
    for key, value in res.items():
        if isinstance(value, str) and key not in ["procedure","formulas","data","graph","diagram"]:
            doc.add_paragraph(f"{key}: {value}")
    return recs


def build_single_test_docx(test_name, res, recs=None):
    doc = Document()
    doc.add_heading(f"ANITS Soil Test Report – {test_name}", 0)
    _fill_doc_for_test(doc, test_name, res)
    buf = BytesIO(); doc.save(buf); buf.seek(0)
    return buf.getvalue()


def build_all_tests_docx(completed_tests):
    doc = Document()
    doc.add_heading("ANITS Soil Test Report – All Tests", 0)
    first = True
    for name, res in completed_tests.items():
        if not first: doc.add_page_break()
        first = False
        _fill_doc_for_test(doc, name, res)
    buf = BytesIO(); doc.save(buf); buf.seek(0)
    return buf.getvalue()


# --------------------------
# LOGO HELPER
# --------------------------
def _logo_b64():
    try:
        with open("assets/anits_logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

_LOGO = _logo_b64()

def logo_html(size=110, radius=20):
    if _LOGO:
        return (
            f'<img src="data:image/png;base64,{_LOGO}" '
            f'style="width:{size}px;height:{size}px;border-radius:{radius}px;'
            f'object-fit:contain;background:white;padding:6px;'
            f'border:2px solid rgba(0,160,255,0.4);'
            f'box-shadow:0 0 40px rgba(0,120,255,0.35);margin-bottom:18px;display:block;margin-left:auto;margin-right:auto;"/>'
        )
    return f'<div style="font-size:{int(size*0.35)}px;margin-bottom:18px;filter:drop-shadow(0 0 16px rgba(0,160,255,0.5));text-align:center;">🏛️</div>'





# ==========================
# CSS
# ==========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
* { font-family: 'Sora', sans-serif !important; }

/* ══ ROOT — fixed height viewport, children scroll independently ══ */
html, body {
    height: 100% !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    background: #03050f !important;
}

/* ══ APP CONTAINER — full height, flex row ══ */
.stApp {
    background: #03050f !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    display: flex !important;
}
.stApp::before {
    content: ''; position: fixed; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background:
        radial-gradient(ellipse 60% 40% at 20% 20%, rgba(0,100,255,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 40% 60% at 80% 80%, rgba(0,200,180,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(20,60,120,0.15) 0%, transparent 70%);
    animation: bgPulse 12s ease-in-out infinite alternate;
    z-index: 0; pointer-events: none;
}
@keyframes bgPulse { 0%{transform:scale(1) rotate(0deg)} 100%{transform:scale(1.08) rotate(3deg)} }

/* ══ SIDEBAR — fixed height, scrolls independently ══ */
section[data-testid="stSidebar"] {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    -webkit-overflow-scrolling: touch !important;
    background: rgba(4,10,28,0.97) !important;
    border-right: 1px solid rgba(0,100,200,0.22) !important;
    backdrop-filter: blur(20px) !important;
    flex-shrink: 0 !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 100 !important;
}
section[data-testid="stSidebar"] * { color: rgba(210,232,255,0.92) !important; }
section[data-testid="stSidebar"] > div {
    height: 100% !important;
    overflow-y: auto !important;
    -webkit-overflow-scrolling: touch !important;
    padding-bottom: 30px !important;
}

/* ══ MAIN CONTENT — fills remaining space, scrolls independently ══ */
section.main,
.main,
div[data-testid="stAppViewContainer"] > section.main {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    -webkit-overflow-scrolling: touch !important;
    flex: 1 !important;
    overscroll-behavior: contain !important;
}

/* ══ INNER CONTENT — natural height, no restrictions ══ */
section.main > div,
.main > div,
.block-container,
div[data-testid="stAppViewBlockContainer"],
div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    overflow: visible !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
}

.main .block-container {
    position: relative; z-index: 1;
    padding-top: 1.5rem !important;
    padding-bottom: 5rem !important;
    max-width: 1200px !important;
    width: 100% !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ══ MOBILE BACK BUTTON ══ */
.mobile-back-btn {
    position: fixed; bottom: 20px; left: 50%;
    transform: translateX(-50%); z-index: 9999;
    background: linear-gradient(135deg, rgba(0,100,255,0.95), rgba(0,60,200,1));
    color: #fff !important; border: 2px solid rgba(0,200,255,0.5);
    border-radius: 50px; padding: 12px 32px;
    font-size: 1rem; font-weight: 800;
    box-shadow: 0 6px 28px rgba(0,100,255,0.5);
    cursor: pointer; display: flex; align-items: center;
    gap: 8px; white-space: nowrap; transition: all 0.2s ease;
}

/* ══ MOBILE RESPONSIVE ══ */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-bottom: 80px !important;
    }
    .header-banner h2 { font-size: 1rem !important; }
    .header-banner p  { font-size: 0.72rem !important; }
    .feat-grid { grid-template-columns: repeat(2,1fr) !important; }
    .metric-row { flex-direction: column !important; }
    .welcome-h1 { font-size: 1.6rem !important; }
    .auth-card { padding: 24px 20px !important; }
    div[data-testid="stLinkButton"] > a { font-size: 0.75rem !important; padding: 0.4rem !important; }
}

/* ══ SIDEBAR MOBILE — always visible, proper toggle ══ */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        z-index: 999 !important;
        width: 80vw !important;
        max-width: 300px !important;
        transform: translateX(0) !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
    }
    section.main {
        width: 100% !important;
        margin-left: 0 !important;
    }
}

/* ══ EXPANDER FIX — clear text, proper icon ══ */
div[data-testid="stExpander"] {
    background: rgba(0,20,60,0.45) !important;
    border: 1px solid rgba(0,100,200,0.28) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] summary {
    color: rgba(205,228,255,0.95) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 12px 16px !important;
    list-style: none !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    background: rgba(0,40,100,0.35) !important;
}
div[data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
div[data-testid="stExpander"] summary::marker { display: none !important; }
div[data-testid="stExpander"] > div {
    padding: 12px 16px !important;
    color: rgba(205,228,255,0.9) !important;
}

/* ══ PAGE TRANSITION — prevent flash ══ */
.stApp {
    animation: fadeIn 0.3s ease-in-out !important;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
.stDeployButton { display: none; }

/* ══════════════════════
   WELCOME PAGE
══════════════════════ */
.welcome-wrap {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 30px 20px 20px 20px;
    min-height: auto;
}
.welcome-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,100,255,0.15); border: 1px solid rgba(0,160,255,0.35);
    border-radius: 100px; padding: 6px 18px;
    font-size: 0.76rem; font-weight: 700; color: rgba(200,230,255,0.95);
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 16px;
}
.welcome-h1 {
    font-size: clamp(2rem,4.5vw,3rem); font-weight: 900; color: #fff;
    line-height: 1.15; margin-bottom: 12px; letter-spacing: -0.02em;
}
.welcome-h1 span {
    background: linear-gradient(135deg,#0099ff,#00ddbb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.welcome-sub {
    font-size: 0.95rem; color: rgba(185,218,255,0.85);
    line-height: 1.65; margin-bottom: 22px; max-width: 480px;
}
.feat-grid {
    display: grid; grid-template-columns: repeat(3,1fr);
    gap: 8px; margin-bottom: 36px; width: 100%; max-width: 560px;
}
.feat-item {
    background: rgba(0,60,160,0.25); border: 1px solid rgba(0,120,255,0.25);
    border-radius: 10px; padding: 9px 12px;
    font-size: 0.78rem; color: rgba(200,230,255,0.92); font-weight: 600;
    display: flex; align-items: center; gap: 6px;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1);
}
.feat-item:hover {
    background: rgba(0,100,220,0.38); border-color: rgba(0,180,255,0.5);
    transform: translateY(-3px) scale(1.02); color: #fff;
}

/* ══════════════════════
   AUTH CARD
══════════════════════ */
.auth-page-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 85vh;
    padding: 20px;
}
.auth-card {
    background: rgba(6,12,36,0.93);
    border: 1px solid rgba(0,120,255,0.28); border-radius: 24px;
    padding: 36px 44px 30px 44px;
    backdrop-filter: blur(32px);
    box-shadow: 0 0 0 1px rgba(0,80,200,0.1), 0 30px 100px rgba(0,0,0,0.7);
    position: relative; overflow: hidden;
    width: 100%; max-width: 480px;
    margin: 0 auto;
}
.auth-card::before {
    content: ''; position: absolute; top: -1px; left: 12%; right: 12%; height: 2px;
    background: linear-gradient(90deg,transparent,rgba(0,180,255,0.9),transparent);
    animation: shimmer 3s ease-in-out infinite;
}
@keyframes shimmer { 0%,100%{opacity:0.3} 50%{opacity:1} }

.auth-logo-wrap { display: flex; justify-content: center; margin-bottom: 12px; }
.auth-logo-img {
    width: 90px; height: 90px; border-radius: 16px;
    object-fit: contain; background: white; padding: 6px;
    border: 2px solid rgba(0,160,255,0.38);
    box-shadow: 0 0 28px rgba(0,120,255,0.32);
    animation: logoFloat 4s ease-in-out infinite;
}
@keyframes logoFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }

.auth-logo-emoji {
    font-size: 4.5rem; text-align: center; display: block;
    filter: drop-shadow(0 0 18px rgba(0,160,255,0.6));
    margin-bottom: 10px; animation: logoFloat 4s ease-in-out infinite;
}
.auth-title { font-size: 1.5rem; font-weight: 800; color: #fff; text-align: center; margin-bottom: 4px; }
.auth-subtitle { font-size: 0.84rem; color: rgba(175,215,255,0.8); text-align: center; margin-bottom: 22px; letter-spacing: 0.04em; }
.auth-divider {
    display: flex; align-items: center; gap: 10px;
    margin: 16px 0; color: rgba(150,190,230,0.6);
    font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase;
}
.auth-divider::before, .auth-divider::after { content:""; flex:1; height:1px; background:rgba(0,100,200,0.22); }

/* ══════════════════════
   GLOBAL BUTTONS — normal flow (no fixed positioning)
══════════════════════ */
div.stButton > button {
    position: relative !important;
    left: auto !important;
    bottom: auto !important;
    transform: none !important;
    background: linear-gradient(135deg, rgba(0,100,255,0.88), rgba(0,60,200,0.96)) !important;
    color: #ffffff !important;
    border: 1px solid rgba(0,160,255,0.45) !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 16px rgba(0,80,200,0.28) !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    width: auto !important;
    white-space: nowrap !important;
    cursor: pointer !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,150,255,0.96), rgba(0,90,240,1)) !important;
    border-color: rgba(0,210,255,0.7) !important;
    box-shadow: 0 10px 32px rgba(0,150,255,0.5) !important;
    transform: translateY(-3px) scale(1.02) !important;
    color: #fff !important;
}
div.stButton > button:active {
    transform: translateY(-1px) scale(1.00) !important;
}

/* Welcome launch button — centered, larger */
.welcome-launch-btn div.stButton > button {
    font-size: 1.1rem !important;
    padding: 0.75rem 3rem !important;
    border-radius: 50px !important;
    border: 2px solid rgba(0,210,255,0.55) !important;
    box-shadow: 0 6px 32px rgba(0,120,255,0.55) !important;
    min-width: 240px !important;
}
.welcome-launch-btn div.stButton > button:hover {
    box-shadow: 0 14px 44px rgba(0,160,255,0.7) !important;
    transform: translateY(-5px) scale(1.04) !important;
}

/* ══════════════════════
   SIDEBAR
══════════════════════ */
section[data-testid="stSidebar"] {
    background: rgba(4,10,28,0.97) !important;
    border-right: 1px solid rgba(0,100,200,0.22) !important;
    backdrop-filter: blur(20px) !important;
}
section[data-testid="stSidebar"] * { color: rgba(210,232,255,0.92) !important; }
.greet-bar {
    background: linear-gradient(135deg,rgba(0,100,255,0.35),rgba(0,180,200,0.25));
    border: 1px solid rgba(0,140,255,0.42); color: #fff !important;
    padding: 11px 14px; border-radius: 11px; font-weight: 700;
    font-size: 0.9rem; text-align: center; margin-bottom: 6px;
}

/* ══════════════════════
   HEADER BANNER
══════════════════════ */
.header-banner {
    background: linear-gradient(135deg,rgba(0,60,180,0.65),rgba(0,120,200,0.45),rgba(0,80,160,0.65));
    border: 1px solid rgba(0,150,255,0.28); padding: 18px 28px;
    border-radius: 16px; text-align: center; margin-bottom: 24px;
    backdrop-filter: blur(20px); box-shadow: 0 8px 32px rgba(0,0,0,0.45);
}
.header-banner h2 { font-size:clamp(1.1rem,2.5vw,1.5rem) !important; font-weight:800 !important; margin:0 0 4px 0 !important; color:#fff !important; }
.header-banner p  { margin:0 !important; color:rgba(195,228,255,0.9) !important; font-size:0.83rem !important; text-transform:uppercase !important; letter-spacing:0.06em !important; }

/* ══════════════════════
   METRIC CARDS
══════════════════════ */
.metric-row { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
.metric-card {
    background:rgba(0,40,120,0.3); border:1px solid rgba(0,120,255,0.22);
    border-radius:13px; padding:14px 20px; flex:1; min-width:120px;
    backdrop-filter:blur(12px); transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1); cursor:default;
}
.metric-card:hover { background:rgba(0,60,180,0.4); transform:translateY(-5px); box-shadow:0 10px 30px rgba(0,100,255,0.2); }
.metric-label { font-size:0.7rem; color:rgba(160,205,255,0.85); font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:3px; }
.metric-value { font-size:1.3rem; font-weight:800; color:#fff; font-family:'JetBrains Mono',monospace !important; }

/* ══════════════════════
   REC CARDS
══════════════════════ */
.rec-card { border-radius:11px; padding:13px 17px; margin-bottom:8px; transition:all 0.25s ease; }
.rec-card:hover { transform:translateX(4px); }
.rec-card.danger  { background:rgba(200,40,40,0.12);  border:1px solid rgba(200,40,40,0.25);  border-left:4px solid #ff4444; }
.rec-card.warning { background:rgba(200,150,0,0.12);  border:1px solid rgba(200,150,0,0.25);  border-left:4px solid #ffaa00; }
.rec-card.success { background:rgba(0,180,100,0.12);  border:1px solid rgba(0,180,100,0.25);  border-left:4px solid #00cc66; }
.rec-card.info    { background:rgba(0,120,220,0.12);  border:1px solid rgba(0,120,220,0.25);  border-left:4px solid #4488ff; }
.rec-title { font-size:0.9rem; font-weight:800; color:#fff; margin-bottom:4px; }
.rec-body  { font-size:0.81rem; color:rgba(210,232,255,0.85); line-height:1.55; }
.rec-section-title { font-size:0.95rem; font-weight:800; color:rgba(100,210,255,0.95); letter-spacing:0.06em; text-transform:uppercase; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid rgba(0,120,200,0.3); }

/* ══════════════════════
   SOIL BADGE
══════════════════════ */
.soil-badge {
    display:inline-flex; align-items:center; gap:12px;
    background:linear-gradient(135deg,rgba(0,60,180,0.5),rgba(0,120,200,0.35));
    border:1px solid rgba(0,160,255,0.45); border-radius:100px; padding:11px 24px; margin:10px 0;
    transition:all 0.3s ease;
}
.soil-badge:hover { transform:scale(1.03); box-shadow:0 6px 20px rgba(0,140,255,0.25); }
.soil-badge-symbol { font-size:1.45rem; font-weight:900; color:#00d4ff; font-family:'JetBrains Mono',monospace !important; }
.soil-badge-name   { font-size:0.9rem; font-weight:600; color:rgba(200,235,255,0.95); }

/* ══════════════════════
   HISTORY CARDS
══════════════════════ */
.hist-card {
    background:rgba(0,20,60,0.55); border:1px solid rgba(0,100,200,0.22);
    border-radius:13px; padding:16px 20px 12px 20px; margin-bottom:12px;
    backdrop-filter:blur(12px); border-left:4px solid rgba(0,140,255,0.65);
    transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.hist-card:hover { background:rgba(0,40,100,0.65); transform:translateX(5px); box-shadow:0 6px 24px rgba(0,100,255,0.18); }
.hist-test-name { font-size:0.96rem; font-weight:800; color:#fff; margin-bottom:2px; }
.hist-time { font-size:0.74rem; color:rgba(160,200,245,0.75); margin-bottom:8px; }
.hist-prop {
    display:inline-block; background:rgba(0,80,200,0.28); border:1px solid rgba(0,120,255,0.28);
    color:rgba(200,230,255,0.95); border-radius:5px; padding:2px 9px;
    font-size:0.74rem; font-weight:700; margin:2px 3px 2px 0;
    font-family:'JetBrains Mono',monospace !important;
}

/* ══════════════════════
   CLASS SECTION
══════════════════════ */
.class-section { background:rgba(0,40,100,0.38); border:1px solid rgba(0,140,255,0.28); border-radius:13px; padding:18px 22px; margin-bottom:14px; backdrop-filter:blur(12px); }

/* ══════════════════════
   LINK BUTTONS
══════════════════════ */
div[data-testid="stLinkButton"] > a {
    background: linear-gradient(135deg,rgba(0,100,255,0.75),rgba(0,60,185,0.85)) !important;
    color: #fff !important; border: 1px solid rgba(0,140,255,0.38) !important;
    border-radius: 10px !important; font-weight: 700 !important; font-size: 0.86rem !important;
    text-decoration: none !important; transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    box-shadow: 0 3px 14px rgba(0,60,185,0.22) !important; display: block !important;
}
div[data-testid="stLinkButton"] > a:hover {
    background: rgba(0,150,255,0.9) !important; transform: translateY(-5px) scale(1.03) !important;
    box-shadow: 0 10px 28px rgba(0,150,255,0.45) !important;
    border-color: rgba(0,210,255,0.65) !important; color: #fff !important;
}

div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg,rgba(0,170,120,0.88),rgba(0,100,80,0.96)) !important;
    border-color: rgba(0,210,150,0.48) !important; color: #fff !important;
    box-shadow: 0 4px 16px rgba(0,120,90,0.28) !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-5px) scale(1.03) !important;
    box-shadow: 0 10px 28px rgba(0,190,120,0.45) !important;
    border-color: rgba(0,230,160,0.65) !important; color: #fff !important;
}

/* ══════════════════════
   INPUTS
══════════════════════ */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
    background: rgba(0,20,60,0.55) !important; border: 1px solid rgba(0,100,200,0.38) !important;
    border-radius: 9px !important; color: #fff !important; font-size: 0.92rem !important;
    padding: 0.6rem 1rem !important; backdrop-filter: blur(8px) !important;
    transition: all 0.25s ease !important; width: 100% !important;
}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder { color: rgba(140,180,230,0.55) !important; }
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(0,190,255,0.65) !important; box-shadow: 0 0 0 3px rgba(0,150,255,0.14) !important; outline: none !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextArea"] label { color: rgba(200,228,255,0.95) !important; font-weight: 600 !important; font-size: 0.86rem !important; }
div[data-testid="stSelectbox"] > div > div { background: rgba(0,20,60,0.55) !important; border: 1px solid rgba(0,100,200,0.35) !important; border-radius: 9px !important; color: #fff !important; }
div[data-testid="stRadio"] label, div[data-testid="stRadio"] span { color: rgba(205,228,255,0.92) !important; }

/* ══════════════════════
   TABS
══════════════════════ */
div[data-testid="stTabs"] button { color:rgba(180,215,255,0.78) !important; font-weight:600 !important; border-radius:8px 8px 0 0 !important; transition:all 0.2s ease !important; }
div[data-testid="stTabs"] button:hover { color:#fff !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#fff !important; background:rgba(0,80,200,0.32) !important; border-bottom:2px solid rgba(0,190,255,0.75) !important; }

/* ══════════════════════
   SHARE SECTION
══════════════════════ */
.share-section { background:rgba(0,30,80,0.55); border:1px solid rgba(0,120,200,0.28); border-radius:14px; padding:22px 26px; margin-top:24px; backdrop-filter:blur(16px); border-top:3px solid rgba(0,185,255,0.45); }

/* ══════════════════════
   CHAT
══════════════════════ */
div[data-testid="stChatMessage"] { background:rgba(0,20,60,0.45) !important; border:1px solid rgba(0,100,200,0.22) !important; border-radius:13px !important; margin-bottom:8px !important; }
div[data-testid="stChatMessage"] p { color:rgba(215,235,255,0.92) !important; }

/* ══════════════════════
   TEXT VISIBILITY
══════════════════════ */
.stMarkdown p,.stMarkdown li { color:rgba(205,228,255,0.9) !important; }
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 { color:#fff !important; }
.stMarkdown a { color:rgba(100,190,255,0.95) !important; }
p, span { color:rgba(205,228,255,0.88); }
small, caption { color:rgba(170,205,245,0.82) !important; }
b, strong { color:#fff !important; }

[data-testid="stDataFrame"] { background:rgba(0,20,60,0.45) !important; border:1px solid rgba(0,100,200,0.22) !important; border-radius:10px !important; }
div[data-testid="stExpander"] { background:rgba(0,20,60,0.38) !important; border:1px solid rgba(0,100,200,0.22) !important; border-radius:12px !important; transition:all 0.2s ease !important; }
div[data-testid="stExpander"]:hover { border-color:rgba(0,150,255,0.38) !important; }
div[data-testid="stExpander"] summary { color:rgba(205,228,255,0.92) !important; font-weight:600 !important; }

::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:rgba(0,20,60,0.3); }
::-webkit-scrollbar-thumb { background:rgba(0,100,200,0.45); border-radius:3px; }

.appview-container .main .block-container { padding-top:1rem !important; max-width:1200px !important; }
.stSpinner > div { border-top-color:#0088ff !important; }
div[data-testid="stAlert"] p { color:#fff !important; }
div[data-testid="stNumberInput"] button { color:rgba(180,220,255,0.9) !important; background:rgba(0,40,120,0.4) !important; border:1px solid rgba(0,100,200,0.3) !important; transition:all 0.2s ease !important; }
div[data-testid="stNumberInput"] button:hover { background:rgba(0,80,200,0.5) !important; transform:scale(1.08) !important; }
</style>
""", unsafe_allow_html=True)

# --------------------------
# SESSION STATE
# --------------------------
for key, default in {
    "app_started": False,
    "auth_screen": "login",
    "logged_in": False,
    "user_name": "",
    "user_email": "",
    "completed_tests": {},
    "view_mode": "test",
    "last_result": None,
    "last_test_name": None,
    "page_history": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# --------------------------
# BACK BUTTON HELPER
# --------------------------
def show_back_button():
    """Show a back button if there is navigation history."""
    if len(st.session_state.page_history) > 0:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅️  Back to Previous Page", key="back_btn_main", use_container_width=True):
                prev = st.session_state.page_history.pop()
                st.session_state.view_mode = prev
                st.rerun()
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ==========================
# WELCOME SCREEN
# ==========================
if not st.session_state.app_started:

    st.markdown(f"""
    <div class="welcome-wrap">
        {logo_html(size=118, radius=22)}
        <div class="welcome-badge">🏗️ ANITS · Civil Engineering</div>
        <div class="welcome-h1">Soil Testing<br><span>Analysis System</span></div>
        <div class="welcome-sub">
            Professional soil lab platform with IS Code recommendations,
            AI classification, auto-generated reports, and multi-platform sharing.
        </div>
        <div class="feat-grid">
            <div class="feat-item">🧪 15 IS Standard Tests</div>
            <div class="feat-item">📋 IS Code Recommendations</div>
            <div class="feat-item">🤖 AI Soil Classification</div>
            <div class="feat-item">📥 Auto DOCX Reports</div>
            <div class="feat-item">📊 Charts &amp; Graphs</div>
            <div class="feat-item">📤 Share via WhatsApp</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered launch button — normal flow, no fixed positioning
    col_left, col_center, col_right = st.columns([2, 1, 2])
    with col_center:
        st.markdown('<div class="welcome-launch-btn">', unsafe_allow_html=True)
        if st.button("🚀  Launch App →", key="welcome_launch_btn", use_container_width=True):
            st.session_state.app_started = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()  # ← prevent any other screen from flashing below


# ==========================
# AUTH SCREEN
# ==========================
elif not st.session_state.logged_in:

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    # Use columns to center the form
    _, mid, _ = st.columns([1, 2, 1])

    with mid:
        # ── Logo ──
        if _LOGO:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:10px;">'
                f'<img src="data:image/png;base64,{_LOGO}" '
                f'style="width:90px;height:90px;border-radius:16px;object-fit:contain;'
                f'background:white;padding:6px;border:2px solid rgba(0,160,255,0.38);'
                f'box-shadow:0 0 28px rgba(0,120,255,0.32);"/>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div style="text-align:center;font-size:3.5rem;">🏛️</div>', unsafe_allow_html=True)

        # ── Card wrapper (styling only, no widgets inside) ──
        if st.session_state.auth_screen == "login":
            st.markdown("""
            <div style="text-align:center;margin-bottom:4px;">
                <span style="font-size:1.4rem;font-weight:800;color:#fff;">Welcome Back 👋</span>
            </div>
            <div style="text-align:center;margin-bottom:20px;">
                <span style="font-size:0.84rem;color:rgba(175,215,255,0.8);">ANITS · Soil Testing System</span>
            </div>
            """, unsafe_allow_html=True)

            email    = st.text_input("📧  Email address", key="login_email", placeholder="you@example.com")
            password = st.text_input("🔒  Password", type="password", key="login_pass", placeholder="Enter your password")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            if st.button("🔐  Sign In", use_container_width=True, key="signin_btn"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, name, msg = login_user(email.strip().lower(), password)
                    if ok:
                        st.session_state.logged_in  = True
                        st.session_state.user_name  = name
                        st.session_state.user_email = email.strip().lower()
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("<div style='text-align:center;margin:12px 0;color:rgba(150,190,230,0.6);font-size:0.8rem;'>── or ──</div>", unsafe_allow_html=True)

            if st.button("✏️  Create a New Account", use_container_width=True, key="goto_signup"):
                st.session_state.auth_screen = "signup"
                st.rerun()

        else:
            st.markdown("""
            <div style="text-align:center;margin-bottom:4px;">
                <span style="font-size:1.4rem;font-weight:800;color:#fff;">Create Account 🎓</span>
            </div>
            <div style="text-align:center;margin-bottom:20px;">
                <span style="font-size:0.84rem;color:rgba(175,215,255,0.8);">Join ANITS Soil Testing System</span>
            </div>
            """, unsafe_allow_html=True)

            full_name        = st.text_input("👤  Full Name",        key="reg_name",  placeholder="e.g. Ravi Kumar")
            email            = st.text_input("📧  Email Address",    key="reg_email", placeholder="you@example.com")
            password         = st.text_input("🔒  Password",         type="password", key="reg_pass",  placeholder="Min. 6 characters")
            confirm_password = st.text_input("🔒  Confirm Password", type="password", key="reg_pass2", placeholder="Re-enter password")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            if st.button("🎓  Create Account", use_container_width=True, key="create_btn"):
                if not full_name or not email or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(full_name.strip(), email.strip().lower(), password)
                    if ok:
                        st.success(msg + " Please sign in.")
                        st.session_state.auth_screen = "login"
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("<div style='text-align:center;margin:12px 0;color:rgba(150,190,230,0.6);font-size:0.8rem;'>── or ──</div>", unsafe_allow_html=True)

            if st.button("🔐  Sign In Instead", use_container_width=True, key="goto_login"):
                st.session_state.auth_screen = "login"
                st.rerun()

    st.stop()  # ← prevent main app from flashing below auth screen


# ==========================
# MAIN APP
# ==========================
else:
    try:
        from history_manager import load_history, save_history, clear_history
    except ImportError:
        def load_history(email): return []
        def save_history(email, name, result): pass
        def clear_history(email): pass

    try:
        from tabs import (
            sieve_analysis, liquid_limit_casagrande, liquid_limit_cone,
            plastic_limit, core_cutter, specific_gravity, constant_head,
            variable_head, light_compaction, direct_shear, ucs_test,
            consolidation, cbr_test, vane_shear, triaxial_test
        )
        tests = {
            "Sieve Analysis":            sieve_analysis,
            "Liquid Limit (Casagrande)": liquid_limit_casagrande,
            "Liquid Limit (Cone)":       liquid_limit_cone,
            "Plastic Limit":             plastic_limit,
            "Core Cutter":               core_cutter,
            "Specific Gravity":          specific_gravity,
            "Constant Head":             constant_head,
            "Variable Head":             variable_head,
            "Light Compaction":          light_compaction,
            "Direct Shear":              direct_shear,
            "UCS Test":                  ucs_test,
            "Triaxial Test":             triaxial_test,
            "Vane Shear":                vane_shear,
            "CBR Test":                  cbr_test,
            "Consolidation Test":        consolidation,
        }
    except ImportError:
        tests = {"Demo Test": None}

    # ── SIDEBAR ──
    st.sidebar.markdown('<div style="display:flex;justify-content:center;padding:10px 0 6px 0;">', unsafe_allow_html=True)
    try:
        st.sidebar.image("assets/anits_logo.png", width=90)
    except Exception:
        st.sidebar.markdown('<div style="text-align:center;font-size:2.5rem;filter:drop-shadow(0 0 10px rgba(0,160,255,0.5));">🏛️</div>', unsafe_allow_html=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown(f'<div class="greet-bar">👋 Hello, {st.session_state.user_name}!</div>', unsafe_allow_html=True)

    history_all = load_history(st.session_state.user_email)
    st.sidebar.markdown(
        f"<small style='display:block;text-align:center;color:rgba(185,222,255,0.88);margin-bottom:8px;'>"
        f"📊 <b style='color:rgba(215,238,255,0.95);'>{len(history_all)}</b> tests &nbsp;|&nbsp; "
        f"<b style='color:rgba(215,238,255,0.95);'>{len(set(e['test_name'] for e in history_all))}</b> types</small>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    nav = st.sidebar.radio(
        "Navigation",
        ["🧪  Run Tests", "🕒  Test History", "🤖  AI Assistant"],
        index=0 if st.session_state.view_mode == "test" else (1 if st.session_state.view_mode == "history" else 2)
    )
    # Track page history for back button
    new_mode = "test" if "Run" in nav else ("history" if "History" in nav else "ai")
    if new_mode != st.session_state.view_mode:
        st.session_state.page_history.append(st.session_state.view_mode)
        st.session_state.view_mode = new_mode

    selected_test   = None
    selected_module = None
    if st.session_state.view_mode == "test":
        st.sidebar.markdown("---")
        st.sidebar.subheader("Select Test")
        selected_test   = st.sidebar.radio("", list(tests.keys()))
        selected_module = tests[selected_test]

    st.sidebar.markdown("---")

    if st.session_state.completed_tests:
        n = len(st.session_state.completed_tests)
        st.sidebar.markdown(
            f"<small style='color:rgba(185,222,255,0.9);display:block;margin-bottom:6px;'>"
            f"✅ <b style='color:white;'>{n}</b> test(s) in session</small>",
            unsafe_allow_html=True
        )
        all_bytes = build_all_tests_docx(st.session_state.completed_tests)
        st.sidebar.download_button(
            label="📥 Download Full Report",
            data=all_bytes,
            file_name="ANITS_All_Tests_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    if st.sidebar.button("🚪  Logout", use_container_width=True):
        for key in ["logged_in","user_name","user_email","completed_tests",
                    "app_started","auth_screen","view_mode","last_result","last_test_name"]:
            st.session_state.pop(key, None)
        st.rerun()

    # ── HEADER ──
    st.markdown("""
    <div class="header-banner">
        <h2>🏗️ Soil Tests Analysis Dashboard</h2>
        <p>ANITS · Department of Civil Engineering · Professional Lab System</p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================
    # AI ASSISTANT VIEW
    # ==========================
    if st.session_state.view_mode == "ai":
        show_back_button()
        st.markdown('<p style="font-size:1.25rem;font-weight:800;color:#fff;margin-bottom:4px;">🤖 AI Soil Assistant</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.84rem;color:rgba(180,215,255,0.82);margin-bottom:16px;">Ask anything about soil tests, IS codes, or engineering design.</p>', unsafe_allow_html=True)
        ai_chatbot(key_prefix="inapp")

    # ==========================
    # HISTORY VIEW
    # ==========================
    elif st.session_state.view_mode == "history":
        show_back_button()
        history = load_history(st.session_state.user_email)
        col_title, col_clear = st.columns([5, 1])
        with col_title:
            st.markdown('<p style="font-size:1.25rem;font-weight:800;color:#fff;margin-bottom:2px;">🕒 Test History</p>', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.84rem;color:rgba(180,215,255,0.8);">All previously performed soil tests — newest first.</p>', unsafe_allow_html=True)
        with col_clear:
            if history and st.button("🗑️ Clear All"):
                clear_history(st.session_state.user_email)
                st.success("History cleared.")
                st.rerun()

        if not history:
            st.markdown("""
            <div style="text-align:center;padding:60px 20px;color:rgba(160,200,245,0.7);">
                <div style="font-size:3.5rem;margin-bottom:14px;">🧪</div>
                <b style="font-size:1rem;color:rgba(185,222,255,0.82);">No test history yet.</b><br>
                <span style="font-size:0.84rem;">Complete a soil test and results will appear here.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            unique_types = set(e["test_name"] for e in history)
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card"><div class="metric-label">Total Tests</div><div class="metric-value">{len(history)}</div></div>
                <div class="metric-card"><div class="metric-label">Test Types</div><div class="metric-value">{len(unique_types)}</div></div>
                <div class="metric-card"><div class="metric-label">Latest Test</div><div class="metric-value" style="font-size:0.85rem;">{history[0]['test_name']}</div></div>
            </div>
            """, unsafe_allow_html=True)

            filter_choice = st.selectbox("🔍 Filter by test type", ["All Tests"] + sorted(unique_types))
            filtered = history if filter_choice == "All Tests" else [e for e in history if e["test_name"] == filter_choice]
            st.markdown(f"<p style='color:rgba(185,222,255,0.85);font-weight:600;margin-bottom:8px;'>{len(filtered)} record(s)</p>", unsafe_allow_html=True)

            for entry in filtered:
                test_name = entry["test_name"]
                timestamp = entry["timestamp"]
                summary   = entry.get("summary", {})

                pills = []
                for k, v in summary.items():
                    if isinstance(v, (int, float)):
                        pills.append(f"{k}: {round(v, 3)}")
                    elif isinstance(v, str) and len(v) < 80 and k not in ("procedure","formulas"):
                        pills.append(f"{k}: {v}")
                pill_html = "".join(f'<span class="hist-prop">{p}</span>' for p in pills[:8])

                st.markdown(f"""
                <div class="hist-card">
                    <div class="hist-test-name">🧪 {test_name}</div>
                    <div class="hist-time">🕐 {timestamp}</div>
                    {pill_html or '<span style="color:rgba(140,180,230,0.6);font-size:0.8rem;">No scalar results stored.</span>'}
                </div>
                """, unsafe_allow_html=True)

                recs = get_is_recommendations(test_name, summary)
                if recs and recs[0][2] != "info":
                    with st.expander(f"📋 IS Code Recommendations — {test_name}"):
                        for title, body, level in recs:
                            st.markdown(f'<div class="rec-card {level}"><div class="rec-title">{title}</div><div class="rec-body">{body}</div></div>', unsafe_allow_html=True)

                df_entries = {k: v for k, v in summary.items() if isinstance(v, list)}
                if df_entries:
                    with st.expander(f"📊 Data Table — {test_name}  |  {timestamp}"):
                        for label, records in df_entries.items():
                            try:
                                df = pd.DataFrame(records)
                                st.markdown(f"**{label}**")
                                st.dataframe(df, use_container_width=True)
                            except Exception: pass

                with st.expander(f"📤 Share — {test_name}"):
                    share_buttons(test_name, summary, inside_expander=True)

    # ==========================
    # TEST VIEW
    # ==========================
    else:
        if selected_module is not None:
            result = selected_module.run()
        else:
            st.info("Test module not available in this environment.")
            result = None

        if result is not None:
            st.session_state.completed_tests[selected_test] = result
            st.session_state.last_result    = result
            st.session_state.last_test_name = selected_test
            save_history(st.session_state.user_email, selected_test, result)
            st.toast(f"✅ '{selected_test}' saved to history!", icon="🕒")

        if st.session_state.last_result and st.session_state.last_test_name == selected_test:
            res = st.session_state.last_result
            recs = get_is_recommendations(selected_test, res)

            st.markdown("---")
            st.markdown('<div class="rec-section-title">📋 IS Code Recommendations</div>', unsafe_allow_html=True)
            for title, body, level in recs:
                st.markdown(f'<div class="rec-card {level}"><div class="rec-title">{title}</div><div class="rec-body">{body}</div></div>', unsafe_allow_html=True)

            sym, name_cls, emoji = get_soil_classification(res)
            if sym:
                st.markdown('<div class="rec-section-title" style="margin-top:18px;">🤖 AI Soil Classification (IS 1498 / USCS)</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="class-section">
                    <div class="soil-badge">
                        <span class="soil-badge-symbol">{sym}</span>
                        <span class="soil-badge-name">{emoji} {name_cls}</span>
                    </div>
                    <p style="font-size:0.81rem;color:rgba(185,222,255,0.8);margin-top:7px;">
                        Classification based on Atterberg limits per IS 1498 (USCS method).
                    </p>
                </div>
                """, unsafe_allow_html=True)

            single_doc_bytes = build_single_test_docx(selected_test, res, recs)

            st.markdown('<div class="share-section">', unsafe_allow_html=True)
            share_buttons(selected_test, res, doc_bytes=single_doc_bytes, inside_expander=False)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================
    # FLOATING SCROLL-TO-TOP BTN
    # (mobile WebView helper)
    # ==========================
    st.markdown("""
    <button onclick="window.scrollTo({top:0,behavior:'smooth'})"
        style="
            position:fixed; bottom:24px; right:18px; z-index:9999;
            background:linear-gradient(135deg,rgba(0,100,255,0.92),rgba(0,60,200,1));
            color:#fff; border:2px solid rgba(0,200,255,0.5);
            border-radius:50%; width:48px; height:48px;
            font-size:1.3rem; font-weight:900;
            box-shadow:0 4px 20px rgba(0,100,255,0.5);
            cursor:pointer; display:flex; align-items:center; justify-content:center;
            line-height:1;
        "
        title="Scroll to top">
        ↑
    </button>
    """, unsafe_allow_html=True)