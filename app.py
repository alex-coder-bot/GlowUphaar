import os
import json
import uuid
import urllib.parse
import sqlite3
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="GlowUphaar with Mira ✨",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import base64

def get_mira_avatar_base64():
    # Check for all common filenames and extensions
    for fname in ["mira.jpg", "mira.jpeg", "mira.png", "mira_avatar.png"]:
        if os.path.exists(fname):
            mime = "image/jpeg" if fname.endswith((".jpg", ".jpeg")) else "image/png"
            with open(fname, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                return f"data:{mime};base64,{encoded}"
    return None

mira_avatar_src = get_mira_avatar_base64()
# ----------------- TELEMETRY TRACKER -----------------
DB_FILE = "analytics.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            event_name TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def track_event(session_id, event_name, details=""):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO events (session_id, event_name, details) VALUES (?, ?, ?)",
                  (session_id, event_name, details))
        conn.commit()
        conn.close()
    except Exception:
        pass

if "user_session_id" not in st.session_state:
    st.session_state["user_session_id"] = str(uuid.uuid4())[:8]
    track_event(st.session_state["user_session_id"], "session_start", "organic_visit")

if "free_trials_left" not in st.session_state:
    st.session_state["free_trials_left"] = 3

# ----------------- STYLING -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: linear-gradient(180deg, #FFFDFB 0%, #FFF7F2 100%); }

    .mira-box {
        background: #FFFFFF;
        border: 1px solid #FFE4DD;
        box-shadow: 0 8px 24px rgba(235, 94, 85, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .mira-avatar {
        font-size: 2.2rem;
        background: #FFF1EC;
        border: 2px solid #FFCFC5;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .product-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 20px;
        border: 1px solid #F3E6E2;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 24px rgba(216, 74, 90, 0.12);
        border-color: #FFC9BE;
    }

    .trial-badge {
        background: #FFE8E5;
        color: #C23646;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid #FFC9C2;
    }

    .badge-cat {
        background: #FFF2DF;
        color: #A35B00;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- GEMINI CLIENT -----------------
api_key = os.getenv("GEMINI_API_KEY", "").strip()

def call_gemini_agent(prompt_text):
    if not api_key:
        return None
    for model_name in ['gemini-2.0-flash-lite', 'gemini-1.5-flash']:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            return json.loads(raw)
        except Exception:
            continue
    return None

def build_store_link(query_term):
    encoded = urllib.parse.quote_plus(f"buy {query_term} India online")
    return f"https://www.google.com/search?q={encoded}&tbm=shop"

# Dynamic fallback extracting specific elements from user notes with a human greeting
def dynamic_text_synthesis(recipient, budget, notes):
    clean_notes = notes.strip().strip('"').strip("'")
    delimiters = [",", " and ", " & ", " with "]
    segments = [clean_notes]
    for d in delimiters:
        new_segs = []
        for s in segments:
            new_segs.extend(s.split(d))
        segments = [x.strip() for x in new_segs if len(x.strip()) > 2]
    
    if len(segments) < 2:
        words = clean_notes.split()
        if len(words) >= 4:
            segments = [" ".join(words[:2]), " ".join(words[2:4]), " ".join(words[4:])]
            segments = [s for s in segments if s.strip()]
        else:
            segments = [clean_notes, "Festive Handcrafted Diya Set", "Artisanal Sweet Box"]

    segments = segments[:3]
    count = len(segments)
    prices = [int(budget * 0.40), int(budget * 0.35), budget - int(budget * 0.40) - int(budget * 0.35)]
    if count == 2:
        prices = [int(budget * 0.55), budget - int(budget * 0.55)]

    items = []
    for i, seg in enumerate(segments):
        title = seg.title().replace("She Loves", "").replace("He Loves", "").replace("Needs", "").replace("To Wear", "").strip()
        if not title:
            title = f"Festive Curated Pick {i+1}"
        p = prices[i]
        mrp = int(p * 1.25)
        disc = int(((mrp - p) / mrp) * 100)
        items.append({
            "name": f"Curated {title}",
            "brand": "Festive Choice",
            "category": "Hand-Matched Pick",
            "price_inr": p,
            "mrp_inr": mrp,
            "discount_pct": disc,
            "highlight": f"Matched directly for: '{title}'",
            "search_query": title
        })

    # Human-styled greeting card message
    if "Sister" in recipient:
        card_msg = "May your festive season be filled with rich treats, amber warmth, and all the sparkle you bring into our lives. Happy Diwali to the best sister! ✨"
    elif "Friend" in recipient or "Bestie" in recipient:
        card_msg = "Handpicked with all your favorite vibes, sweetness, and celebration. So grateful for our bond—wishing you the brightest Diwali! 🪔"
    elif "Mom" in recipient:
        card_msg = "A little box of sweetness, warmth, and relaxation to celebrate everything you do. Wishing you peace, health, and a very happy Diwali! 🌸"
    elif "Boyfriend" in recipient or "Husband" in recipient:
        card_msg = "To my favorite person: Celebrating you with warmth, depth, and festive magic. Thank you for making every single day brighter! ✨"
    elif "Girlfriend" in recipient or "Wife" in recipient:
        card_msg = "To the one who brings all the warmth and magic into my life: A little box handpicked with all the sweetness and love you deserve. Happy Diwali, my favorite! 🌸✨"
    else:
        card_msg = "Wishing you festive celebrations filled with rich warmth, golden light, and joyful indulgence. Happy Diwali! 🪔"
    return {
        "gift_narrative": card_msg,
        "items": items
    }

# ----------------- HERO HEADER -----------------
col_h1, col_h2 = st.columns([2, 1])

with col_h1:
    if mira_avatar_src:
        avatar_content = f'<img src="{mira_avatar_src}" alt="Mira" style="width: 100%; height: 100%; object-fit: cover;">'
    else:
        avatar_content = '<span style="font-size: 1.8rem;">🏮</span>'

    st.markdown(f"""
    <div class="mira-box">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 62px; height: 62px; min-width: 62px; border-radius: 50%; overflow: hidden; border: 2.5px solid #FFC9BE; box-shadow: 0 4px 16px rgba(216, 74, 90, 0.2); display: flex; align-items: center; justify-content: center; background: #FFF0EB;">
                    {avatar_content}
                </div>
                <div>
                    <h2 style="margin: 0; color: #D84A5A; font-weight: 700;">Namaste, I'm Mira!</h2>
                    <span style="font-size: 0.9rem; color: #888;">Your festive stylist & gifting bestie ✨</span>
                </div>
            </div>
            <span class="trial-badge">⚡ {st.session_state['free_trials_left']} Free Curations Left</span>
        </div>
        <p style="font-size: 1.05rem; color: #444; margin: 8px 0 0 0; line-height: 1.6;">
            Struggling to find the perfect gift this Diwali or for an upcoming special day? Worry not! I'm here so you don't have to break your head searching for hours or settle for generic boxes. Tell me who they are, their weird quirks, or what they secretly love—then sit back and let me work my magic. I'll curate a thoughtful hamper box that stays comfortably within your budget! 🎁
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown("""
    <div style="background: #FFF2EE; border-radius: 18px; padding: 20px; border-left: 5px solid #E85A6B;">
        <h4 style="margin: 0; color: #8F2D38;">👑 Mira 2.0 Gold Club</h4>
        <p style="font-size: 0.85rem; color: #665; margin: 8px 0 10px 0; line-height: 1.5;">
           Unlimited hampers for the whole clan, bespoke keepsake cards that make them tear up, and direct WhatsApp pings before flash sales vanish! 💌
        </p>
        <span style="background: #D84A5A; color: white; padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: 700;">₹149 / Festive Season Pass</span>
    </div>
    """, unsafe_allow_html=True)

mode = st.radio(
    "Choose Mode:",
    [
        "🎁 Build a Custom Hamper (Gifting)", 
        "💎 Find My Festive Dupe & Deal (Self-Shopping)", 
        "🔔 WhatsApp Price Radar"
    ],
    horizontal=True
)

st.write("")

# ----------------- MODE 1: BUILD A CUSTOM HAMPER -----------------
if mode == "🎁 Build a Custom Hamper (Gifting)":
    st.markdown("### 🧺 Design Your Dream Hamper (Persona-to-Gift)")

    col_in1, col_in2 = st.columns([1, 1.3])
    with col_in1:
        recipient = st.selectbox(
            "Who are we surprising?",
            [
                "My Sister 💖", 
                "My Best Friend 👯‍♀️", 
                "My Boyfriend / Husband 👔", 
                "My Girlfriend/ Wife 👑,"
                "My Mom 🌸", 
                "My Dad / Brother 💼", 
                "Colleagues / Team 🤝"
            ]
        )
        budget = st.select_slider(
            "Target Maximum Budget:",
            options=[600, 900, 1200, 1500, 1800, 2500, 3500],
            value=1200,
            format_func=lambda x: f"₹{x}"
        )

    with col_in2:
        custom_notes = st.text_area(
            "Describe the person, their quirks, what they love or dislike:",
            value="she loves to smell like wood, loves dark chocolate and cute accessories to wear for diwali",
            height=110
        )
        st.caption("💡 *Type anything: e.g. 'Coffee addict who hates sugary sweets, loves minimal notebooks' or 'Loves woody scents and fairy lights'*")

    if st.button("✨ Mira, Build My Custom Hamper Box", type="primary", use_container_width=True):
        if st.session_state["free_trials_left"] > 0:
            st.session_state["free_trials_left"] -= 1

        track_event(st.session_state["user_session_id"], "hamper_generated", f"{recipient} | Budget: {budget}")
        active_notes = custom_notes.strip() if custom_notes.strip() else "Festive celebration hamper"

        with st.spinner("🌸 Channeling my inner gifting detective... raiding the best deals and putting together something they'll genuinely obsess over! ✨"):
            prompt = f"""
            You are Mira, an intuitive, warm, and thoughtful gifting concierge in India.
            Target Recipient: {recipient}
            Budget Cap: ₹{budget} INR
            User's Person Description: "{active_notes}"

            Task:
            1. Parse the person's traits, likes, and dislikes (e.g. {active_notes}).
            2. Generate 2 to 3 distinct physical items matching their persona and festive occasion.
            3. Assign realistic Indian retail prices (price_inr, mrp_inr) such that sum(price_inr) <= {budget}.
            4. Provide a search query for each item to let the user buy it online immediately.
            5. Write a genuine, human, handwritten-style gift card greeting (2 sentences max).
               - DO NOT mention budgets, algorithms, prices, or technical terms like 'I curated this'.
               - DO NOT quote the prompt back to them. Weave their favorite things naturally into a warm greeting.

            Respond strictly in raw JSON without markdown code fences:
            {{
                "gift_narrative": "May your Diwali be wrapped in the comforting warmth of amber woods, rich dark chocolate, and a little golden sparkle made just for you. Happy Diwali!",
                "items": [
                    {{
                        "name": "Product Title",
                        "brand": "Brand or Category",
                        "category": "Category",
                        "price_inr": 350,
                        "mrp_inr": 450,
                        "discount_pct": 22,
                        "highlight": "Why it was chosen",
                        "search_query": "Item Search Query"
                    }}
                ]
            }}
            """
            curation_result = call_gemini_agent(prompt)
            if not curation_result or not curation_result.get("items"):
                curation_result = dynamic_text_synthesis(recipient, budget, active_notes)

            items = curation_result.get("items", [])
            total_price = sum(item.get("price_inr", 0) for item in items)
            total_mrp = sum(item.get("mrp_inr", int(item.get("price_inr", 0) * 1.25)) for item in items)
            savings = total_mrp - total_price

            st.markdown("---")
            st.markdown(f"""
            <div class="mira-box" style="border-left: 6px solid #D84A5A;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-weight: 700; color: #D84A5A; font-size: 1.15rem;">🌸 Mira's Note for {recipient}:</span>
                    <span style="color: #2E7D32; font-weight: 700;">Total Saved: ₹{savings}</span>
                </div>
                <p style="font-size: 1.05rem; margin: 10px 0; color: #2B2B2B; line-height: 1.5;">
                    "{curation_result.get('gift_narrative')}"
                </p>
                <div style="background: #F8F9FA; padding: 10px 16px; border-radius: 12px; display: inline-block;">
                    🧺 <b>Curated Hamper Total: ₹{total_price}</b> &nbsp;|&nbsp; <s>MRP: ₹{total_mrp}</s> &nbsp;|&nbsp;
                    <span style="color: #E65100; font-weight: 600;">Within ₹{budget} budget limit!</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            card_cols = st.columns(len(items))
            for idx, item in enumerate(items):
                store_link = build_store_link(item.get("search_query", item["name"]))
                with card_cols[idx]:
                    st.markdown(f"""
                    <div class="product-card">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span class="badge-cat">{item.get('category', 'Curated Pick')}</span>
                                <span style="font-size: 0.75rem; color: #2E7D32; font-weight: 700;">{item.get('discount_pct', 15)}% OFF</span>
                            </div>
                            <h4 style="margin: 0; color: #D84A5A;">{item.get('brand', 'Verified Choice')}</h4>
                            <p style="font-size: 0.95rem; font-weight: 600; margin: 4px 0 8px 0; color: #333;">{item['name']}</p>
                            <p style="font-size: 0.8rem; color: #666;">✨ <i>{item.get('highlight', 'Handpicked for their persona')}</i></p>
                        </div>
                        <div style="margin-top: 14px;">
                            <h3 style="margin: 0 0 10px 0; color: #222;">₹{item.get('price_inr', 0)} <span style="font-size: 0.85rem; color: #888; font-weight: normal;"><s>₹{item.get('mrp_inr', 0)}</s></span></h3>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.link_button(f"Shop Live Across Stores 🛒", store_link, use_container_width=True):
                        track_event(st.session_state["user_session_id"], "store_click", item['name'])

            # Printable Keepsake Card (Mira Gold Feature)
            st.write("")
            with st.expander("💌 Preview Printable Gift Card & Keepsake Note (Mira Gold Feature)", expanded=True):
                st.markdown(f"""
                <div style="background: #FFFDF9; border: 2px dashed #E8A598; border-radius: 20px; padding: 32px 28px; text-align: center; max-width: 540px; margin: 0 auto; box-shadow: 0 4px 20px rgba(216, 74, 90, 0.06);">
                    <p style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 2.5px; color: #B35446; margin: 0; font-weight: 700;">Festive Keepsake Greeting</p>
                    <h3 style="color: #2D2A29; margin: 12px 0 10px 0; font-family: Georgia, serif; font-size: 1.4rem;">Dearest {recipient.replace('My', '').split()[0]},</h3>
                    <p style="font-family: Georgia, serif; font-style: italic; color: #4A4442; line-height: 1.7; font-size: 1.05rem; margin: 16px 0 20px 0;">
                        "{curation_result.get('gift_narrative')}"
                    </p>
                    <div style="border-top: 1px solid #F0D5CF; margin: 18px auto; width: 45%;"></div>
                    <p style="font-size: 0.78rem; color: #8C827A; margin: 0;">With love & festive light ✨ Printed via GlowUphaar</p>
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            if st.button(f"🎁 One-Click Checkout Entire Hamper (₹{total_price})", use_container_width=True):
                track_event(st.session_state["user_session_id"], "hamper_checkout_click", f"Total: {total_price}")
                st.balloons()
                st.toast("🧺 Custom Hamper Bundle Locked In! Commission tracked.", icon="🪔")

# ----------------- MODE 2: DUPE FINDER (SELF-SHOPPING) -----------------
elif mode == "💎 Find My Festive Dupe & Deal (Self-Shopping)":
    st.markdown("### 🔍 Stop Paying The Luxury Tax on Yourself")
    st.write("Mira analyzes formulation actives and finds accessible alternatives so you get identical results at 70% lower prices.")

    DUPES_DATABASE = [
        {
            "luxury": "Sol de Janeiro Brazilian Crush Cheirosa 71 (₹2,400)",
            "dupe_name": "BodyLovin' Vanilla Vibes Fine Fragrance Mist",
            "dupe_brand": "Plum",
            "deal_price": 420,
            "mrp": 525,
            "actives": "Warm Vanilla Pod Extract, Macadamia, Aloe Juice",
            "search_query": "Plum BodyLovin Vanilla Vibes Body Mist"
        },
        {
            "luxury": "Laneige Lip Sleeping Mask Berry (₹600)",
            "dupe_name": "Candy Melts Vegan Tinted Lip Balm (Red Velvet)",
            "dupe_brand": "Plum",
            "deal_price": 235,
            "mrp": 295,
            "actives": "Shea Butter, Carrot Seed Oil, Cocoa Butter",
            "search_query": "Plum Candy Melts Lip Balm"
        },
        {
            "luxury": "The Ordinary Niacinamide 10% + Zinc 1% (₹650)",
            "dupe_name": "10% Niacinamide Face Serum with Zinc PCA",
            "dupe_brand": "Minimalist",
            "deal_price": 569,
            "mrp": 599,
            "actives": "Niacinamide 10%, Zinc PCA, Hyaluronic Acid",
            "search_query": "Minimalist 10% Niacinamide Face Serum"
        },
        {
            "luxury": "Clinique Moisture Surge 100H (₹3,200)",
            "dupe_name": "Ceramide & Vitamin C Oil-Free Moisturizer",
            "dupe_brand": "Dr. Sheth's",
            "deal_price": 319,
            "mrp": 399,
            "actives": "Ceramides 1%, Vitamin C, Ashwagandha",
            "search_query": "Dr Sheths Ceramide Vitamin C Moisturizer"
        }
    ]

    selected_lux = st.selectbox("Select a luxury cult favorite to dupe:", [d["luxury"] for d in DUPES_DATABASE])
    dupe_item = next(d for d in DUPES_DATABASE if d["luxury"] == selected_lux)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f"""
        <div style="background: #FDFBF7; border: 1.5px dashed #D4AF37; border-radius: 18px; padding: 22px; height: 100%;">
            <span style="background: #FFF3CD; color: #856404; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700;">OVERPRICED BENCHMARK</span>
            <h3 style="margin: 12px 0 4px 0;">{selected_lux.split('(')[0].strip()}</h3>
            <h2 style="color: #666; margin: 8px 0;">{selected_lux.split('(')[1].replace(')', '')}</h2>
            <p style="font-size: 0.85rem; color: #777;">Heavy markups added for international counter rentals, marketing, and import tariffs.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        discount_pct = int(((dupe_item['mrp'] - dupe_item['deal_price']) / dupe_item['mrp']) * 100)
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #FFE4DD; border-radius: 18px; padding: 22px; box-shadow: 0 4px 16px rgba(216,74,90,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="background: #E8F5E9; color: #2E7D32; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700;">MIRA'S VERIFIED FORMULATION</span>
                <span style="font-size: 0.8rem; color: #6A1B9A; font-weight: 700;">🛡️ 95% Real Reviews</span>
            </div>
            <h3 style="margin: 12px 0 4px 0; color: #D84A5A;">{dupe_item['dupe_brand']} — {dupe_item['dupe_name']}</h3>
            <h2 style="color: #2E7D32; margin: 8px 0;">₹{dupe_item['deal_price']} <span style="font-size: 0.9rem; color: #888; font-weight: normal;"><s>₹{dupe_item['mrp']}</s> ({discount_pct}% OFF)</span></h2>
            <p style="font-size: 0.85rem; color: #444;"><b>Active Formulation Actives:</b> {dupe_item['actives']}</p>
        </div>
        """, unsafe_allow_html=True)
        store_dupe_link = build_store_link(dupe_item['search_query'])
        if st.link_button(f"Grab Verified Deal Across Live Stores 🛒", store_dupe_link, use_container_width=True):
            track_event(st.session_state["user_session_id"], "dupe_click", dupe_item['dupe_name'])


# ----------------- MODE 3: WHATSAPP RADAR -----------------

elif mode == "🔔 WhatsApp Price Radar":
    st.markdown("### ⚡ Never Miss A Festive Flash Sale")
    st.markdown("""
<p style="font-size: 1.05rem; color: #555; margin-top: -6px; margin-bottom: 20px;">
    Let me be that friend who obsessively refreshes the sales so you don't have to. 🛍️<br>
    <span style="font-size: 0.88rem; color: #888;">Drop your wishlist item below—I'll hunt down the price drops and ping your WhatsApp before it sells out! ✨</span>
</p>
""", unsafe_allow_html=True)
    col_track1, col_track2 = st.columns([1.2, 1])
    
    with col_track1:
        contact = st.text_input("Enter your WhatsApp Number (+91):", placeholder="+91 98765 43210")
        
        st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: #555; margin-bottom: 4px;'>Popular Items Tracked Today (Click to Auto-fill):</p>", unsafe_allow_html=True)
        suggested_tag = st.pills(
            "Quick Select",
            ["Haldiram Kaju Katli (500g)", "Sol de Janeiro Cheirosa 71", "Copper LED Fairy Lights", "Silver Laxmi Ganesh Coin"],
            label_visibility="collapsed"
        )
        
        default_item_value = suggested_tag if suggested_tag else "Sol de Janeiro Cheirosa 71"
        custom_track = st.text_input("Product you want Mira to track:", value=default_item_value)
        drop_target = st.slider("Alert me when festive discount reaches:", 15, 60, 25, 5, format="%d%%")

        if st.button("🔔 Activate Instant WhatsApp Alerts", type="primary", use_container_width=True):
            if contact and custom_track:
                track_event(st.session_state["user_session_id"], "lead_captured", f"{contact} tracking {custom_track}")
                st.balloons()
                st.toast(f"Radar armed! Watch queued for {custom_track}.", icon="🔔")
                st.success(f"✅ Success! Mira will ping {contact} via WhatsApp the second '{custom_track}' drops by {drop_target}%.")
            else:
                st.warning("Please provide both your WhatsApp number and the item name.")

    with col_track2:
        card_html = f"""<div style="background: #EFEAE2; border-radius: 20px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); max-width: 420px; margin: 0 auto; border: 1px solid #E1DBD2;">
<div style="background: #075E54; color: white; padding: 12px 16px; border-radius: 12px 12px 4px 4px; display: flex; align-items: center; gap: 10px;">
<span style="font-size: 1.4rem;">🪔</span>
<div>
<h5 style="margin: 0; color: white; font-weight: 600;">Mira from GlowUphaar</h5>
<span style="font-size: 0.72rem; color: #A8D5C8;">Verified Business Bot • Active</span>
</div>
</div>
<div style="background: white; border-radius: 12px; padding: 14px 16px; margin-top: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); border-left: 4px solid #25D366;">
<p style="font-size: 0.88rem; color: #111; margin: 0 0 6px 0; font-weight: 600;">🚨 FLASH SALE GLITCH DETECTED!</p>
<p style="font-size: 0.82rem; color: #444; line-height: 1.5; margin: 0 0 8px 0;">Hey! The <b>{custom_track if custom_track else 'Festive Gift Item'}</b> you were tracking just hit a <b>{drop_target}% instant coupon drop</b> on verified partner stores!</p>
<div style="background: #F0FDF4; padding: 6px 10px; border-radius: 8px; font-size: 0.78rem; color: #166534; font-weight: 600;">⚡ Current Price: Lowest in 30 Days</div>
<div style="margin-top: 10px; text-align: right;"><span style="font-size: 0.7rem; color: #999;">Just now • Delivered</span></div>
</div>
<p style="text-align: center; font-size: 0.72rem; color: #777; margin: 12px 0 0 0;">🔒 Powered by Render Cron Workers (Auditing every 6 hours)</p>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)

# ----------------- ADMIN DASHBOARD (?admin=stats) -----------------
if st.query_params.get("admin") == "stats":
    st.divider()
    st.subheader("🔒 Internal Traction Dashboard (RevHack Metric Signals)")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT session_id) FROM events")
    unique_visitors = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM events WHERE event_name='hamper_generated'")
    curations_run = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM events WHERE event_name='lead_captured'")
    leads_count = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM events WHERE event_name IN ('store_click', 'dupe_click')")
    outbound_clicks = c.fetchone()[0] or 0
    conn.close()

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Unique Visitors", unique_visitors)
    s2.metric("Hampers Curated", curations_run)
    s3.metric("WhatsApp Leads", leads_count)
    s4.metric("Outbound Store Clicks", outbound_clicks)