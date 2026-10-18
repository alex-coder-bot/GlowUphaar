# GlowUphaar ✨ (featuring Mira)

**One-Line Pitch:** Skip the boring, overpriced soan papdi boxes— Mira is your personal festive bestie who turns your loved one's weird quirks and favorite things into a thoughtful, budget-friendly gift hamper in seconds.

---

### What it is and who it's for:

* **What it is:** Let’s be honest—festive shopping is stressful. Commercial gift hampers on Instagram and retail stores are packed with cheap fillers, marked up 3x, and feel totally soulless. GlowUphaar fixes that with "Mira," an AI gifting stylist with real personality. Instead of scrolling through endless catalogs, you just tell Mira about the person—like *"my sister who loves woody perfumes, dark chocolate, and minimal diwali jewelry"*—and she instantly hand-picks matching items, balances the math so you never cross your budget, gives you real shopping links, and even writes a sweet printable greeting card.

* **Who it's for:** Anyone who wants to give a genuinely thoughtful gift without spending three hours agonizing over what to buy—from college students on a tight budget to busy professionals, siblings, and parents.

---

### What I built:

* **The "Persona-to-Gift" Engine:** Powered by Google Gemini Flash Lite and Python/Streamlit. It reads natural human descriptions and figures out the perfect 3-item hamper combo while strictly respecting your spending limit.

* **Printable Keepsake Cards:** A built-in greeting card generator that writes heartfelt, handwritten-style festive notes you can actually print out or send on WhatsApp.

* **The "Festive Dupe & Deal" Radar:** A self-shopping corner for anyone tired of luxury beauty prices. Mira breaks down active ingredients to recommend Indian alternatives (like Plum and Minimalist) that deliver 95% identical results at a fraction of the cost.

* **Background Deal Watcher:** A background Python worker (`workflow_deal_checker.py`) running on Render Workflows that scans for flash price drops every 6 hours without slowing down the main app.

* **Live Analytics Telemetry:** A simple in-app SQLite tracker (`?admin=stats`) logging visitors, hampers built, and store clicks to measure real traction.

---

### What works today:

* **Live Demo:** [PASTE YOUR RENDER URL HERE]
* **GitHub Repository:** [PASTE YOUR GITHUB REPO URL HERE]
* **Demo Video:** [PASTE YOUR LOOM / YOUTUBE LINK HERE]

* **Try it yourself right now:**
  1. Describe any person with their quirks, likes, or dislikes.
  2. Pick your budget cap (from ₹600 to ₹3,500) and watch Mira assemble the box.
  3. Click through the live shopping buttons to verify real product links.
  4. Expand the printable keepsake card preview.
  5. Check out the luxury dupe comparisons in the second tab.
  6. Peek at live telemetry by adding `?admin=stats` to the URL.

---

### Earning Potential & Business Model (How This Makes Money):

1. **Free Hook vs. Paid Club:**
    * **Free Tier:** Everyone gets 3 free AI hamper curations and access to the Dupe Radar.
    * **Mira 2.0 Gold Club (₹149 Seasonal Pass or ₹49/month):** Unlocks unlimited persona-based curations, personalized printable gift cards with QR messages, and direct WhatsApp price-drop alerts.

2. **Why People Will Pay ₹149:**
   * It's an impulse buy during Diwali or for any occassion. A pre-made retail hamper costs ₹2,000+. Mira builds a better, personalized one for ₹1,100—saving the buyer  ₹800+ instantly. Paying ₹149 for that saving and zero shopping headache is a no-brainer.

3. **Affiliate Commerce (Passive Revenue):**
   * Every product card has a "Shop Live Across Stores" button. By routing through affiliate networks (Amazon Associates, Nykaa, brand partner programs), GlowUphaar earns 6%–10% on every checkout. With an average festive cart size of ₹1,200, that’s ₹70 to ₹120 per completed purchase.

4. **Getting Real Users by Oct 26:**
   * I'm going to be sharing side-by-side hamper breakdowns in student communities, Reddit (r/IndianSkincareAddicts, r/India), and WhatsApp family groups: *"I built an AI bestie that creates a personalized ₹900 gift hamper with woody mists + artisan dark chocolate + fairy lights."*
   * The built-in SQLite counter tracks every single visit and click to prove authentic traction.

---

### Use of Render Workflows:
* **How it works:** Real-time deal hunting shouldn't make the user's web app lag. For that, I used **Render Workflows (Scheduled Cron Workers)** to run `workflow_deal_checker.py` completely in the background every 6 hours. It monitors price fluctuations and flash discounts across popular festive gifting items and queues alerts, keeping the frontend fast and snappy.

---

### Honest Limitations & What’s Next:
* **Flash Stockouts:** During festive rushes, items on third-party sites can sell out quickly. Right now, Mira points users to live multi-store search feeds so they can pick alternative sellers if one runs out.

* **Multi-Store Checkout:** Today, users click out to buy items on individual partner stores. In Mira 2.0, the goal is to integrate unified cart checkout using quick-commerce APIs (Blinkit, Zepto) for 30-minute emergency festive delivery.

* **Voice & Vernacular Support:** Adding Hindi, Kannada,Tamil and other regional languages voice input using Gemini Live so parents and grandparents can comfortably talk to Mira without typing.

---

### Why GlowUphaar is Different:
Search engines just give you raw links. Corporate gift shops just sell you stale nuts and cheap incense. GlowUphaar gives you a caring, creative friend who listens to who your person is, respects your wallet, and helps you gift with intention and heart.