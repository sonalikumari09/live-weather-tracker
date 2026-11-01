import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Clean, Modern Palette
    BG_DARK = RGBColor(15, 23, 42)          # Deep Slate 900
    BG_CARD_DARK = RGBColor(30, 41, 59)     # Slate 800
    BG_LIGHT = RGBColor(248, 250, 252)      # Slate 50
    CARD_BG = RGBColor(255, 255, 255)       # Pure White
    CARD_BORDER = RGBColor(226, 232, 240)   # Slate 200
    CARD_BORDER_DARK = RGBColor(51, 65, 85) # Slate 700

    PRIMARY = RGBColor(2, 132, 199)         # Sky 600
    PRIMARY_LIGHT = RGBColor(224, 242, 254) # Sky 100
    PRIMARY_GLOW = RGBColor(56, 189, 248)   # Sky 400

    TEXT_DARK = RGBColor(15, 23, 42)        # Slate 900
    TEXT_MUTED = RGBColor(100, 116, 139)    # Slate 500
    TEXT_BODY = RGBColor(51, 65, 85)        # Slate 700
    
    EMERALD_BG = RGBColor(236, 253, 245)    # Emerald 50
    EMERALD_TEXT = RGBColor(5, 150, 105)    # Emerald 600
    EMERALD_BORDER = RGBColor(167, 243, 208)

    ROSE_TEXT = RGBColor(225, 29, 72)       # Rose 600

    def set_slide_background(slide, color):
        background = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5)
        )
        background.fill.solid()
        background.fill.fore_color.rgb = color
        background.line.color.rgb = color
        return background

    def add_header(slide, title_text, category_text, slide_num_str):
        # Category Pill
        pill = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(2.5), Inches(0.32)
        )
        pill.fill.solid()
        pill.fill.fore_color.rgb = PRIMARY_LIGHT
        pill.line.color.rgb = PRIMARY
        pill.line.width = Pt(1)
        tf_pill = pill.text_frame
        tf_pill.word_wrap = False
        tf_pill.margin_top = Inches(0.04)
        p_pill = tf_pill.paragraphs[0]
        p_pill.text = category_text.upper()
        p_pill.font.name = "Arial"
        p_pill.font.size = Pt(10)
        p_pill.font.bold = True
        p_pill.font.color.rgb = PRIMARY
        p_pill.alignment = PP_ALIGN.CENTER

        # Slide Number Pill
        num_pill = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.4), Inches(0.45), Inches(1.13), Inches(0.32)
        )
        num_pill.fill.solid()
        num_pill.fill.fore_color.rgb = RGBColor(241, 245, 249)
        num_pill.line.color.rgb = RGBColor(203, 213, 225)
        num_pill.line.width = Pt(0.75)
        tf_num = num_pill.text_frame
        tf_num.word_wrap = False
        tf_num.margin_top = Inches(0.04)
        p_num = tf_num.paragraphs[0]
        p_num.text = slide_num_str
        p_num.font.name = "Arial"
        p_num.font.size = Pt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = TEXT_MUTED
        p_num.alignment = PP_ALIGN.CENTER

        # Title Box
        title_box = slide.shapes.add_textbox(
            Inches(0.8), Inches(0.85), Inches(10.4), Inches(0.55)
        )
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = Inches(0)
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Arial"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_DARK

        # Clean Accent Divider
        divider = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.48), Inches(11.733), Inches(0.02)
        )
        divider.fill.solid()
        divider.fill.fore_color.rgb = RGBColor(226, 232, 240)
        divider.line.color.rgb = RGBColor(226, 232, 240)

    def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER, border_width=1):
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
        )
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
        return card

    # ==========================================
    # SLIDE 1: Title Slide (Minimal Dark Hero)
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, BG_DARK)

    # Cyan vertical accent bar
    glow_bar = slide1.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(0.1), Inches(5.9)
    )
    glow_bar.fill.solid()
    glow_bar.fill.fore_color.rgb = PRIMARY_GLOW
    glow_bar.line.color.rgb = PRIMARY_GLOW

    # Top Tag
    top_badge = slide1.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.15), Inches(0.8), Inches(4.2), Inches(0.38)
    )
    top_badge.fill.solid()
    top_badge.fill.fore_color.rgb = RGBColor(30, 41, 59)
    top_badge.line.color.rgb = PRIMARY_GLOW
    top_badge.line.width = Pt(1)
    tf_b = top_badge.text_frame
    tf_b.margin_top = Inches(0.05)
    p_b = tf_b.paragraphs[0]
    p_b.text = "AICTE RECOGNIZED INTERNSHIP DEFENSE"
    p_b.font.name = "Arial"
    p_b.font.size = Pt(10.5)
    p_b.font.bold = True
    p_b.font.color.rgb = PRIMARY_GLOW

    # Title & Subtitle Box
    title_box = slide1.shapes.add_textbox(
        Inches(1.15), Inches(1.4), Inches(11.35), Inches(2.2)
    )
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = 0

    p1 = tf1.paragraphs[0]
    p1.text = "Live Weather Tracker"
    p1.font.name = "Arial"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_after = Pt(8)

    p2 = tf1.add_paragraph()
    p2.text = "Python Programming & Applied Software Engineering"
    p2.font.name = "Arial"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = PRIMARY_GLOW
    p2.space_after = Pt(6)

    p3 = tf1.add_paragraph()
    p3.text = "Hyperlocal weather and farming intelligence for 550,000+ Indian villages - 100% free, trilingual, zero keys."
    p3.font.name = "Arial"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # Two Simple Cards at Bottom
    # Candidate Card
    c1 = create_card(slide1, Inches(1.15), Inches(4.0), Inches(5.6), Inches(2.7), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    c1_tf = c1.text_frame
    c1_tf.word_wrap = True
    c1_tf.margin_left = c1_tf.margin_top = Inches(0.3)
    c1_tf.margin_right = Inches(0.3)

    p = c1_tf.paragraphs[0]
    p.text = "CANDIDATE"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(8)

    p_name = c1_tf.add_paragraph()
    p_name.text = "Sonali Kumari"
    p_name.font.name = "Arial"
    p_name.font.size = Pt(20)
    p_name.font.bold = True
    p_name.font.color.rgb = RGBColor(255, 255, 255)
    p_name.space_after = Pt(6)

    p_sub = c1_tf.add_paragraph()
    p_sub.text = "Roll No: 26DCSE26\nComputer Science & Engineering (B.Tech CSE)\nGovernment Engineering College, Sheikhpura"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = RGBColor(148, 163, 184)

    # Organization Card
    c2 = create_card(slide1, Inches(7.05), Inches(4.0), Inches(5.45), Inches(2.7), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    c2_tf = c2.text_frame
    c2_tf.word_wrap = True
    c2_tf.margin_left = c2_tf.margin_top = Inches(0.3)
    c2_tf.margin_right = Inches(0.3)

    p = c2_tf.paragraphs[0]
    p.text = "ORGANIZATION & RESULT"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(8)

    p_org = c2_tf.add_paragraph()
    p_org.text = "INTELLIO INTERN"
    p_org.font.name = "Arial"
    p_org.font.size = Pt(20)
    p_org.font.bold = True
    p_org.font.color.rgb = RGBColor(255, 255, 255)
    p_org.space_after = Pt(6)

    p_org_sub = c2_tf.add_paragraph()
    p_org_sub.text = "AICTE Recognized Partner\nDuration: 25 Sept 2026 - 08 Oct 2026 (2 Weeks)\nResult: Grade A+ (91%)  |  Cert ID: BQTA26319"
    p_org_sub.font.name = "Arial"
    p_org_sub.font.size = Pt(12)
    p_org_sub.font.color.rgb = RGBColor(148, 163, 184)

    # ==========================================
    # SLIDE 2: About the Organization & Training
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, BG_LIGHT)
    add_header(slide2, "About INTELLIO INTERN & Training", "Organization Profile", "02 / 12")

    col_w = Inches(3.68)
    col_gap = Inches(0.34)
    top_y = Inches(1.8)
    h_card = Inches(5.1)

    cards2_data = [
        ("HOST ORGANIZATION", "INTELLIO INTERN", [
            ("AICTE Recognized:", " Certified technical training partner for engineering students."),
            ("Domain Focus:", " Python Programming, web systems, and cloud architecture."),
            ("Industry Standards:", " Emphasis on modular architecture, clean code, and git."),
            ("Mentorship:", " Regular code reviews and architectural guidance from mentors.")
        ]),
        ("INTERNSHIP FORMAT", "100% Online & Hands-on", [
            ("Duration:", " 2-Week Intensive Program (25/09/2026 - 08/10/2026)."),
            ("Practical Focus:", " Daily problem-solving and coding tasks over passive theory."),
            ("Real Deliverables:", " Students build production-ready software independently."),
            ("Live Evaluation:", " Technical defense and live project demonstration.")
        ]),
        ("FINAL OUTCOME", "Grade A+ (91%)", [
            ("Verified Credential:", " Certificate ID: BQTA26319 (Issued 08 Oct 2026)."),
            ("Top Evaluation:", " Achieved 91% score in final code audit and project viva."),
            ("Independent Capstone:", " Designed, engineered, and deployed the complete project."),
            ("Key Achievement:", " Complete transition from classroom theory to live web app.")
        ])
    ]

    for i, (c_tag, c_title, c_items) in enumerate(cards2_data):
        bx = create_card(slide2, Inches(0.8) + (col_w + col_gap) * i, top_y, col_w, h_card)
        tf = bx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.3)

        p = tf.paragraphs[0]
        p.text = c_tag
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(4)

        pt = tf.add_paragraph()
        pt.text = c_title
        pt.font.name = "Arial"
        pt.font.size = Pt(18)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(14)

        for it, idesc in c_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(10)
            r1 = pr.add_run()
            r1.text = "• " + it + " "
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(12)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(12)
            r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 3: Purpose and Objectives
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, BG_LIGHT)
    add_header(slide3, "Why This Project Matters", "Purpose & Motivation", "03 / 12")

    cards3_data = [
        ("THE PROBLEM", "What is Broken Today?", [
            ("Metro-Centric Apps:", " Mainstream weather apps focus only on Tier-1 cities."),
            ("550,000+ Villages Left Out:", " Rural districts and villages are neglected or missing."),
            ("Language Barrier:", " English-only interfaces lock out rural Indian farmers."),
            ("Expensive Paywalls:", " Commercial APIs demand costly subscriptions and keys.")
        ]),
        ("OUR SOLUTION", "Live Weather Tracker", [
            ("All-India Coverage:", " All 763 districts and 550,000+ villages supported."),
            ("Trilingual First:", " Full support in English, Hindi (हिन्दी), and Bhojpuri (भोजपुरी)."),
            ("100% Free Forever:", " Zero API keys, zero subscription fees, zero user ads."),
            ("Agro-Intelligence:", " Dedicated soil moisture, soil temperature, and rain history.")
        ]),
        ("MY GOALS", "What I Aimed to Achieve", [
            ("Real-World Python:", " Move from textbook CLI scripts to a deployed web system."),
            ("Instant Local Search:", " Build a sub-15ms search engine for 565,000+ places."),
            ("Farmer Focus:", " Deliver practical farming advice instead of confusing charts."),
            ("Dual Deployment:", " Deploy on both Streamlit and Cloudflare serverless edge.")
        ])
    ]

    for i, (c_tag, c_title, c_items) in enumerate(cards3_data):
        bx = create_card(slide3, Inches(0.8) + (col_w + col_gap) * i, top_y, col_w, h_card)
        tf = bx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.3)

        p = tf.paragraphs[0]
        p.text = c_tag
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(4)

        pt = tf.add_paragraph()
        pt.text = c_title
        pt.font.name = "Arial"
        pt.font.size = Pt(18)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(14)

        for it, idesc in c_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(10)
            r1 = pr.add_run()
            r1.text = "• " + it + " "
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(12)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(12)
            r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 4: Technologies / Tools / Skills Learned
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, BG_LIGHT)
    add_header(slide4, "Tools & Technologies Learned", "Technology Stack", "04 / 12")

    grid_w = Inches(5.68)
    grid_h = Inches(2.45)
    left1 = Inches(0.8)
    left2 = Inches(6.85)
    row1_t = Inches(1.8)
    row2_t = Inches(4.45)

    cards4_data = [
        (left1, row1_t, "1. CORE LANGUAGES & UI", "Python & Frontend", [
            ("Python 3.10+:", " Object-oriented design, modular code, custom error handling."),
            ("JavaScript (ES6+):", " Dynamic tabs, asynchronous API fetch, and theme toggling."),
            ("HTML5 & Modern CSS3:", " Clean responsive card layouts and animated sky themes.")
        ]),
        (left2, row1_t, "2. APIS & GEOSPATIAL DATA", "Open Data Feeds", [
            ("Open-Meteo REST API:", " Hourly/daily weather and agricultural telemetry with zero API keys."),
            ("GeoNames India:", " Open dataset covering 565,000+ villages, tehsils, and towns."),
            ("Photon & OSM:", " Free geocoding fallback for PIN codes and remote hamlets.")
        ]),
        (left1, row2_t, "3. STORAGE & DATABASES", "SQLite & Edge SQL", [
            ("SQLite3 (.sqlite.gz):", " Compressed local database enabling sub-15ms village searches."),
            ("Cloudflare D1:", " Serverless SQL database running queries at the global edge."),
            ("Pandas:", " Data restructuring for 7-day temperature trends and rainfall history.")
        ]),
        (left2, row2_t, "4. CLOUD & DEV TOOLS", "Deployment & Version Control", [
            ("Streamlit:", " Rapid interactive data application framework in pure Python."),
            ("Cloudflare Pages:", " Edge serverless architecture with global CDN caching."),
            ("Git & GitHub:", " Version control repository (`sonalikumari09/live-weather-tracker`).")
        ])
    ]

    for c_left, c_top, c_tag, c_title, c_items in cards4_data:
        bx = create_card(slide4, c_left, c_top, grid_w, grid_h)
        tf = bx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.26)

        p = tf.paragraphs[0]
        p.text = c_tag
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(2)

        pt = tf.add_paragraph()
        pt.text = c_title
        pt.font.name = "Arial"
        pt.font.size = Pt(16)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(8)

        for it, idesc in c_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(4)
            r1 = pr.add_run()
            r1.text = "• " + it + " "
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(11.5)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(11.5)
            r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 5: Work / Training Completed
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, BG_LIGHT)
    add_header(slide5, "Training Modules & Work Done", "Work Completed", "05 / 12")

    mod_w = Inches(2.72)
    mod_gap = Inches(0.28)
    mod_h = Inches(3.6)
    mod_y = Inches(1.8)

    modules_data = [
        ("MODULE 1", "Python Core", [
            ("OOP & Structure:", " Clean modular design across decoupled scripts."),
            ("Error Handling:", " Resilient handling of timeouts and network drops."),
            ("Compression:", " On-demand gzip decompression of databases into RAM.")
        ]),
        ("MODULE 2", "REST APIs", [
            ("HTTP Client:", " Built API queries with Python Requests."),
            ("Open-Meteo Integration:", " Parsed multi-layer weather and soil data."),
            ("Data Cleaning:", " Extracted clean JSON without crashes.")
        ]),
        ("MODULE 3", "Fast Search", [
            ("565k Records:", " Indexed 565,000+ Indian geo-coordinates in SQLite."),
            ("Prefix Autocomplete:", " Instant sub-15ms search as the user types."),
            ("Graceful Fallback:", " Photon & Nominatim fallback for missing hamlets.")
        ]),
        ("MODULE 4", "UI & Deployment", [
            ("Trilingual Engine:", " Built instant dictionary (English, Hindi, Bhojpuri)."),
            ("Responsive UI:", " Streamlit tabs, sky animations, and light/dark mode."),
            ("Cloud Hosting:", " Deployed on Streamlit Cloud & Cloudflare Pages.")
        ])
    ]

    for i, (m_tag, m_title, m_items) in enumerate(modules_data):
        bx = create_card(slide5, Inches(0.8) + (mod_w + mod_gap) * i, mod_y, mod_w, mod_h)
        tf = bx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.22)

        p = tf.paragraphs[0]
        p.text = m_tag
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(2)

        pt = tf.add_paragraph()
        pt.text = m_title
        pt.font.name = "Arial"
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(10)

        for it, idesc in m_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(6)
            r1 = pr.add_run()
            r1.text = "• " + it + " "
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(11)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(11)
            r2.font.color.rgb = TEXT_BODY

    # Bottom Banner: Assessment & Certification
    bot_card = create_card(slide5, Inches(0.8), Inches(5.65), Inches(11.733), Inches(1.25), EMERALD_BG, EMERALD_BORDER, 1.5)
    tf_bot = bot_card.text_frame
    tf_bot.word_wrap = True
    tf_bot.margin_left = tf_bot.margin_right = Inches(0.3)
    tf_bot.margin_top = Inches(0.18)

    p = tf_bot.paragraphs[0]
    p.text = "TRAINING EVALUATION & CERTIFICATE"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = EMERALD_TEXT
    p.space_after = Pt(3)

    p_desc = tf_bot.add_paragraph()
    r1 = p_desc.add_run()
    r1.text = "Successfully satisfied all weekly assignments, code audits, and capstone evaluation. "
    r1.font.name = "Arial"
    r1.font.size = Pt(12)
    r1.font.color.rgb = RGBColor(15, 23, 42)

    r2 = p_desc.add_run()
    r2.text = "Awarded Grade A+ (91%) by INTELLIO INTERN (AICTE Recognized). Certificate ID: BQTA26319."
    r2.font.name = "Arial"
    r2.font.size = Pt(12)
    r2.font.bold = True
    r2.font.color.rgb = EMERALD_TEXT

    # ==========================================
    # SLIDE 6: Project Overview - Live Weather Tracker
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, BG_LIGHT)
    add_header(slide6, "Live Weather Tracker at a Glance", "Project Overview", "06 / 12")

    # Left: 5 Modes
    card6_l = create_card(slide6, Inches(0.8), Inches(1.8), Inches(5.65), Inches(5.1))
    tf6_l = card6_l.text_frame
    tf6_l.word_wrap = True
    tf6_l.margin_left = tf6_l.margin_right = tf6_l.margin_top = Inches(0.3)

    p = tf6_l.paragraphs[0]
    p.text = "5 FOCUSED MODES"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf6_l.add_paragraph()
    pt.text = "Core Features"
    pt.font.name = "Arial"
    pt.font.size = Pt(18)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(12)

    modes = [
        ("1. Single Place:", " Current temp, feels-like, wind, humidity, and 7-day forecast."),
        ("2. Farmer Mode:", " Soil temperature (6cm), soil moisture, 7-day rain, and farming tips."),
        ("3. Travel Packer:", " Smart clothing advice based on temperature and rain probability."),
        ("4. Morning Alerts:", " Early warnings for heatwaves, coldwaves, storms, and downpours."),
        ("5. Compare Places:", " Side-by-side weather comparisons for 2 to 4 locations.")
    ]
    for mt, mdesc in modes:
        pr = tf6_l.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = mt + " "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = PRIMARY
        r2 = pr.add_run()
        r2.text = mdesc
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.color.rgb = TEXT_BODY

    # Right: High Impact Numbers & Flow
    card6_r = create_card(slide6, Inches(6.8), Inches(1.8), Inches(5.73), Inches(5.1))
    tf6_r = card6_r.text_frame
    tf6_r.word_wrap = True
    tf6_r.margin_left = tf6_r.margin_right = tf6_r.margin_top = Inches(0.3)

    p = tf6_r.paragraphs[0]
    p.text = "IMPACT & ARCHITECTURE"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf6_r.add_paragraph()
    pt.text = "Key Numbers"
    pt.font.name = "Arial"
    pt.font.size = Pt(18)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(12)

    stats = [
        ("550,000+ Villages:", " Every Indian village, tehsil, and district indexed."),
        ("3 Languages:", " Native English, Hindi (हिन्दी), and Bhojpuri (भोजपुरी)."),
        ("Zero API Keys:", " 100% free with no rate limits or user tracking."),
        ("Dual Deployment:", " Runs on Streamlit Cloud and Cloudflare Pages Edge.")
    ]
    for st, sdesc in stats:
        pr = tf6_r.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = "• " + st + " "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = sdesc
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.color.rgb = TEXT_BODY

    pr_pipe = tf6_r.add_paragraph()
    pr_pipe.space_before = Pt(8)
    r1 = pr_pipe.add_run()
    r1.text = "Simple Flow: "
    r1.font.name = "Arial"
    r1.font.bold = True
    r1.font.size = Pt(11.5)
    r1.font.color.rgb = TEXT_DARK
    r2 = pr_pipe.add_run()
    r2.text = "Search ➔ Local SQLite ➔ Open-Meteo API ➔ Instant i18n ➔ UI"
    r2.font.name = "Arial"
    r2.font.size = Pt(11.5)
    r2.font.bold = True
    r2.font.color.rgb = PRIMARY

    # ==========================================
    # SLIDE 7: Individual Contribution
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, BG_LIGHT)
    add_header(slide7, "What I Built Individually", "My Contribution", "07 / 12")

    cards7_data = [
        (left1, row1_t, "1. WEATHER CORE (weather.py)", "Meteorological Engine", [
            ("API Data Pipeline:", " Fetched real-time conditions, 7-day daily forecasts, and soil telemetry."),
            ("Farmer Advice Logic:", " Synthesized soil temperature, moisture, and rain history into clear tips."),
            ("Automated Checks:", " Created logic for Travel Packer checklists and Severe Weather Morning Alerts.")
        ]),
        (left2, row1_t, "2. GEO-SEARCH (geo.py, places.py)", "Instant Search Engine", [
            ("Compressed Database:", " Built `india_places.sqlite.gz` with 565,000+ Indian geo-entities."),
            ("Fast Prefix Search:", " Implemented sub-15ms SQL autocomplete prioritizing districts and towns."),
            ("Smart Fallbacks:", " Integrated Photon and Nominatim for PIN codes and unlisted hamlets.")
        ]),
        (left1, row2_t, "3. LOCALIZATION (i18n.py)", "Trilingual Translation", [
            ("Zero-Lag Dictionary:", " Built in-memory translation for English, Hindi, and Bhojpuri."),
            ("Full UI Coverage:", " Localized all labels, weather conditions, farming tips, and packing advice."),
            ("Natural Regional Phrasing:", " Used cultural, relatable phrasing for rural Indian communities.")
        ]),
        (left2, row2_t, "4. FRONTEND & CLOUD", "UI & Serverless Edge", [
            ("Interactive UI (`app.py`):", " Created Streamlit app with theme switcher and animated sky banners."),
            ("Cloudflare Serverless:", " Configured edge functions (`functions/api/`) and static frontend."),
            ("Smart Caching:", " Added tiered caching (`@st.cache_data`) cutting API calls by >80%.")
        ])
    ]

    for c_left, c_top, c_tag, c_title, c_items in cards7_data:
        bx = create_card(slide7, c_left, c_top, grid_w, grid_h)
        tf = bx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.26)

        p = tf.paragraphs[0]
        p.text = c_tag
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(2)

        pt = tf.add_paragraph()
        pt.text = c_title
        pt.font.name = "Arial"
        pt.font.size = Pt(16)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(8)

        for it, idesc in c_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(4)
            r1 = pr.add_run()
            r1.text = "• " + it + " "
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(11.5)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(11.5)
            r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 8: Demonstration / Evidence of Work
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, BG_LIGHT)
    add_header(slide8, "Proof of Work & Certification", "Project Evidence", "08 / 12")

    # Left: Certificate
    card8_l = create_card(slide8, Inches(0.8), Inches(1.8), Inches(5.65), Inches(4.3))
    tf8_l = card8_l.text_frame
    tf8_l.word_wrap = True
    tf8_l.margin_left = tf8_l.margin_right = tf8_l.margin_top = Inches(0.18)
    p = tf8_l.paragraphs[0]
    p.text = "AICTE RECOGNIZED CERTIFICATE"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    cert_img_path = "/home/rohit/Downloads/funproject/weather/presentation_assets/certificate-1.png"
    if os.path.exists(cert_img_path):
        slide8.shapes.add_picture(
            cert_img_path, Inches(1.0), Inches(2.2), width=Inches(5.25), height=Inches(3.3)
        )

    cap_cert = slide8.shapes.add_textbox(Inches(0.9), Inches(5.58), Inches(5.45), Inches(0.45))
    tf_cc = cap_cert.text_frame
    tf_cc.word_wrap = True
    tf_cc.margin_left = tf_cc.margin_top = 0
    p_cc = tf_cc.paragraphs[0]
    p_cc.text = "Sonali Kumari (26DCSE26)  |  Grade A+ (91%)  |  ID: BQTA26319"
    p_cc.font.name = "Arial"
    p_cc.font.size = Pt(10)
    p_cc.font.bold = True
    p_cc.font.color.rgb = EMERALD_TEXT

    # Right: Web App
    card8_r = create_card(slide8, Inches(6.8), Inches(1.8), Inches(5.73), Inches(4.3))
    tf8_r = card8_r.text_frame
    tf8_r.word_wrap = True
    tf8_r.margin_left = tf8_r.margin_right = tf8_r.margin_top = Inches(0.18)
    p = tf8_r.paragraphs[0]
    p.text = "LIVE WEATHER TRACKER APPLICATION"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    app_img_path = "/home/rohit/Downloads/funproject/weather/presentation_assets/weather_app_live.png"
    if os.path.exists(app_img_path):
        slide8.shapes.add_picture(
            app_img_path, Inches(7.0), Inches(2.2), width=Inches(5.33), height=Inches(3.3)
        )

    cap_app = slide8.shapes.add_textbox(Inches(6.9), Inches(5.58), Inches(5.5), Inches(0.45))
    tf_ca = cap_app.text_frame
    tf_ca.word_wrap = True
    tf_ca.margin_left = tf_ca.margin_top = 0
    p_ca = tf_ca.paragraphs[0]
    p_ca.text = "Live Web Interface  |  5 Modes  |  Trilingual (EN / HI / BHO)  |  Zero API Keys"
    p_ca.font.name = "Arial"
    p_ca.font.size = Pt(10)
    p_ca.font.bold = True
    p_ca.font.color.rgb = PRIMARY

    # Bottom Repository Bar
    bar8 = create_card(slide8, Inches(0.8), Inches(6.2), Inches(11.733), Inches(0.85))
    tf_bar = bar8.text_frame
    tf_bar.word_wrap = True
    tf_bar.margin_left = tf_bar.margin_right = Inches(0.25)
    tf_bar.margin_top = Inches(0.12)

    p = tf_bar.paragraphs[0]
    r1 = p.add_run()
    r1.text = "Source Code Repository:  "
    r1.font.name = "Arial"
    r1.font.bold = True
    r1.font.size = Pt(11.5)
    r1.font.color.rgb = TEXT_DARK
    r2 = p.add_run()
    r2.text = "https://github.com/sonalikumari09/live-weather-tracker  (Main Branch)\n"
    r2.font.name = "Arial"
    r2.font.size = Pt(11.5)
    r2.font.bold = True
    r2.font.color.rgb = PRIMARY

    r3 = p.add_run()
    r3.text = "Dual Live Deployment:  "
    r3.font.name = "Arial"
    r3.font.bold = True
    r3.font.size = Pt(11)
    r3.font.color.rgb = TEXT_DARK
    r4 = p.add_run()
    r4.text = "Streamlit Cloud Dashboard  +  Cloudflare Pages Edge (*.pages.dev)"
    r4.font.name = "Arial"
    r4.font.size = Pt(11)
    r4.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 9: Challenges and How You Solved Them
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, BG_LIGHT)
    add_header(slide9, "Challenges & Simple Solutions", "Technical Challenges", "09 / 12")

    ch_w = Inches(11.733)
    ch_h = Inches(1.55)
    top_c1 = Inches(1.8)
    top_c2 = Inches(3.52)
    top_c3 = Inches(5.24)

    challenges = [
        ("CHALLENGE 1: Searching 550,000+ Villages Without Paid APIs",
         "Commercial maps APIs cost too much; free public APIs rate-limit typing.",
         "Compressed the full Indian GeoNames dataset into a local SQLite database (`india_places.sqlite.gz`).",
         "Instant (<15ms) prefix autocomplete with zero API costs and 100% offline reliability."),
         
        ("CHALLENGE 2: Making Raw Weather Data Useful for Farmers",
         "Raw scientific numbers (soil moisture in m³/m³, soil warmth) confuse farmers.",
         "Created simple rules combining 6cm soil temp, moisture, and 7-day rain into plain advice.",
         "Actionable guidance in regional language (e.g. 'Adequate soil moisture for sowing')."),

        ("CHALLENGE 3: Seamless Trilingual Switching Without Delay",
         "Cloud translation APIs are slow (500ms lag) and sound robotic in regional dialects.",
         "Built a lightweight in-memory dictionary directly in Python and JavaScript.",
         "Instant (<1ms) language toggle with natural phrasing in English, Hindi, and Bhojpuri.")
    ]

    for i, (c_tag, prob, sol, res) in enumerate(challenges):
        curr_top = [top_c1, top_c2, top_c3][i]
        card = create_card(slide9, Inches(0.8), curr_top, ch_w, ch_h)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.12)

        p = tf.paragraphs[0]
        p.text = c_tag
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(3)

        p_body = tf.add_paragraph()

        # Problem
        r1 = p_body.add_run()
        r1.text = "Problem: "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = ROSE_TEXT
        r2 = p_body.add_run()
        r2.text = prob + "  "
        r2.font.name = "Arial"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_BODY

        # Solution
        r3 = p_body.add_run()
        r3.text = "Solution: "
        r3.font.name = "Arial"
        r3.font.bold = True
        r3.font.size = Pt(10.5)
        r3.font.color.rgb = PRIMARY
        r4 = p_body.add_run()
        r4.text = sol + "  "
        r4.font.name = "Arial"
        r4.font.size = Pt(10.5)
        r4.font.color.rgb = TEXT_BODY

        # Result
        r5 = p_body.add_run()
        r5.text = "Result: "
        r5.font.name = "Arial"
        r5.font.bold = True
        r5.font.size = Pt(10.5)
        r5.font.color.rgb = EMERALD_TEXT
        r6 = p_body.add_run()
        r6.text = res
        r6.font.name = "Arial"
        r6.font.bold = True
        r6.font.size = Pt(10.5)
        r6.font.color.rgb = EMERALD_TEXT

    # ==========================================
    # SLIDE 10: What I Learned
    # ==========================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, BG_LIGHT)
    add_header(slide10, "What I Learned", "Learning Outcomes", "10 / 12")

    # Left: Technical
    card10_l = create_card(slide10, Inches(0.8), Inches(1.8), Inches(5.65), Inches(5.1))
    tf10_l = card10_l.text_frame
    tf10_l.word_wrap = True
    tf10_l.margin_left = tf10_l.margin_right = tf10_l.margin_top = Inches(0.3)

    p = tf10_l.paragraphs[0]
    p.text = "TECHNICAL SKILLS"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf10_l.add_paragraph()
    pt.text = "Engineering Mastery"
    pt.font.name = "Arial"
    pt.font.size = Pt(18)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(12)

    tech_learnings = [
        ("Production Python:", " Clean, modular, and maintainable code adhering to PEP 8."),
        ("REST API Integration:", " Fetching live meteorological data and handling timeouts."),
        ("Database Optimization:", " Indexing and querying compressed SQLite files in memory."),
        ("Full-Stack Deployment:", " Deploying interactive apps to Streamlit and Cloudflare edge."),
        ("Smart Caching:", " Using `@st.cache_data` and HTTP cache headers to speed up responses.")
    ]
    for lt, ldesc in tech_learnings:
        pr = tf10_l.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = "• " + lt + " "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = ldesc
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.color.rgb = TEXT_BODY

    # Right: Professional
    card10_r = create_card(slide10, Inches(6.8), Inches(1.8), Inches(5.73), Inches(5.1))
    tf10_r = card10_r.text_frame
    tf10_r.word_wrap = True
    tf10_r.margin_left = tf10_r.margin_right = tf10_r.margin_top = Inches(0.3)

    p = tf10_r.paragraphs[0]
    p.text = "PROFESSIONAL SKILLS"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf10_r.add_paragraph()
    pt.text = "Product Thinking"
    pt.font.name = "Arial"
    pt.font.size = Pt(18)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(12)

    soft_learnings = [
        ("Solving Real Problems:", " Designing software for underserved rural communities."),
        ("User-Centric Design:", " Making tools easy to use in native languages (Hindi/Bhojpuri)."),
        ("Project Discipline:", " Delivering a complete full-stack product within 2 weeks."),
        ("Git & Documentation:", " Writing clean commit logs and comprehensive README files."),
        ("Next Growth Area:", " Expanding unit tests (`pytest`) and Docker containerization.")
    ]
    for lt, ldesc in soft_learnings:
        pr = tf10_r.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = "• " + lt + " "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = ldesc
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 11: Future Improvements & Roadmap
    # ==========================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, BG_LIGHT)
    add_header(slide11, "What I Would Build Next", "Future Roadmap", "11 / 12")

    future_data = [
        (left1, row1_t, "1. RADAR & SATELLITE", "Live Weather Maps", [
            ("IMD Radar Feeds:", " Add real-time radar maps to track storm and rain paths visually."),
            ("Satellite Overlays:", " Display live INSAT satellite cloud movement.")
        ]),
        (left2, row1_t, "2. VOICE SEARCH", "Regional Voice Queries", [
            ("Speak in Native Language:", " Allow farmers to speak village names in Hindi or Bhojpuri."),
            ("Voice Advisories:", " Read aloud farming tips for users who cannot read.")
        ]),
        (left1, row2_t, "3. SMS & WHATSAPP", "Feature Phone Support", [
            ("No Smartphone Needed:", " Send morning forecast SMS alerts to basic 2G feature phones."),
            ("Storm Alerts:", " Push immediate hazard warnings for sudden frost or heatwaves.")
        ]),
        (left2, row2_t, "4. OFFLINE APP (PWA)", "Works Without Internet", [
            ("Offline Caching:", " Cache the last 7 days of forecasts for remote rural areas."),
            ("Direct Mobile Install:", " Install directly on Android without app store downloads.")
        ])
    ]

    for c_left, c_top, c_tag, c_title, c_items in future_data:
        bx = create_card(slide11, c_left, c_top, grid_w, grid_h)
        tf = bx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.26)

        p = tf.paragraphs[0]
        p.text = c_tag
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(2)

        pt = tf.add_paragraph()
        pt.text = c_title
        pt.font.name = "Arial"
        pt.font.size = Pt(16)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(8)

        for it, idesc in c_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(4)
            r1 = pr.add_run()
            r1.text = "• " + it + " "
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(11.5)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(11.5)
            r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 12: Conclusion & Viva Voce (Dark Hero)
    # ==========================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, BG_DARK)

    # Accent glow bar
    glow_bar12 = slide12.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(0.1), Inches(5.9)
    )
    glow_bar12.fill.solid()
    glow_bar12.fill.fore_color.rgb = PRIMARY_GLOW
    glow_bar12.line.color.rgb = PRIMARY_GLOW

    # Top Pill
    pill12 = slide12.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.15), Inches(0.8), Inches(3.2), Inches(0.38)
    )
    pill12.fill.solid()
    pill12.fill.fore_color.rgb = RGBColor(30, 41, 59)
    pill12.line.color.rgb = PRIMARY_GLOW
    pill12.line.width = Pt(1)
    tf12_p = pill12.text_frame
    tf12_p.margin_top = Inches(0.05)
    p_12p = tf12_p.paragraphs[0]
    p_12p.text = "CONCLUSION & VIVA"
    p_12p.font.name = "Arial"
    p_12p.font.size = Pt(10.5)
    p_12p.font.bold = True
    p_12p.font.color.rgb = PRIMARY_GLOW

    # Slide Number Pill
    num12 = slide12.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.4), Inches(0.8), Inches(1.13), Inches(0.38)
    )
    num12.fill.solid()
    num12.fill.fore_color.rgb = RGBColor(30, 41, 59)
    num12.line.color.rgb = RGBColor(71, 85, 105)
    num12.line.width = Pt(0.75)
    tf_num12 = num12.text_frame
    tf_num12.margin_top = Inches(0.05)
    p_n12 = tf_num12.paragraphs[0]
    p_n12.text = "12 / 12"
    p_n12.font.name = "Arial"
    p_n12.font.size = Pt(10.5)
    p_n12.font.bold = True
    p_n12.font.color.rgb = RGBColor(148, 163, 184)
    p_n12.alignment = PP_ALIGN.CENTER

    # Main Title
    title12_box = slide12.shapes.add_textbox(
        Inches(1.15), Inches(1.35), Inches(11.35), Inches(1.1)
    )
    tf12 = title12_box.text_frame
    tf12.word_wrap = True
    tf12.margin_left = tf12.margin_top = 0
    p1 = tf12.paragraphs[0]
    p1.text = "Summary & Technical Q&A"
    p1.font.name = "Arial"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_after = Pt(4)
    p2 = tf12.add_paragraph()
    p2.text = "Successfully delivered and deployed the Live Weather Tracker capstone project."
    p2.font.name = "Arial"
    p2.font.size = Pt(16)
    p2.font.color.rgb = PRIMARY_GLOW

    # Middle 2 Cards
    c12_l = create_card(slide12, Inches(1.15), Inches(2.65), Inches(5.6), Inches(2.55), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    tf12_l = c12_l.text_frame
    tf12_l.word_wrap = True
    tf12_l.margin_left = tf12_l.margin_right = tf12_l.margin_top = Inches(0.28)
    p = tf12_l.paragraphs[0]
    p.text = "KEY ACHIEVEMENTS"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(6)

    c12_pts1 = [
        ("Completed Internship:", " 2-week intensive Python program at INTELLIO INTERN."),
        ("Grade A+ (91%):", " Verified completion certificate (ID: BQTA26319)."),
        ("Live Web App:", " Deployed and accessible on Streamlit & Cloudflare Pages.")
    ]
    for ct, cd in c12_pts1:
        pr = tf12_l.add_paragraph()
        pr.space_after = Pt(6)
        r1 = pr.add_run()
        r1.text = "• " + ct + " "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = RGBColor(255, 255, 255)
        r2 = pr.add_run()
        r2.text = cd
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.color.rgb = RGBColor(148, 163, 184)

    c12_r = create_card(slide12, Inches(7.05), Inches(2.65), Inches(5.45), Inches(2.55), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    tf12_r = c12_r.text_frame
    tf12_r.word_wrap = True
    tf12_r.margin_left = tf12_r.margin_right = tf12_r.margin_top = Inches(0.28)
    p = tf12_r.paragraphs[0]
    p.text = "REAL-WORLD IMPACT"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(6)

    c12_pts2 = [
        ("Bridged the Divide:", " Gave 550,000+ villages the same weather tools as metro cities."),
        ("Farmer Empowered:", " Soil data and farming tips delivered in Hindi & Bhojpuri."),
        ("Zero Running Cost:", " Free APIs and serverless edge hosting with zero upkeep fee.")
    ]
    for ct, cd in c12_pts2:
        pr = tf12_r.add_paragraph()
        pr.space_after = Pt(6)
        r1 = pr.add_run()
        r1.text = "• " + ct + " "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = RGBColor(255, 255, 255)
        r2 = pr.add_run()
        r2.text = cd
        r2.font.name = "Arial"
        r2.font.size = Pt(12)
        r2.font.color.rgb = RGBColor(148, 163, 184)

    # Bottom Hero Card
    hero12 = create_card(slide12, Inches(1.15), Inches(5.45), Inches(11.35), Inches(1.3), RGBColor(30, 41, 59), PRIMARY, 1.5)
    tf_hero = hero12.text_frame
    tf_hero.word_wrap = True
    tf_hero.margin_left = tf_hero.margin_right = Inches(0.3)
    tf_hero.margin_top = Inches(0.18)

    p_h = tf_hero.paragraphs[0]
    p_h.alignment = PP_ALIGN.CENTER
    r1 = p_h.add_run()
    r1.text = "Thank You! Ready for Live Demo & Viva Questions\n"
    r1.font.name = "Arial"
    r1.font.size = Pt(16)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(255, 255, 255)

    r2 = p_h.add_run()
    r2.text = "Presenter: Sonali Kumari (Roll No: 26DCSE26)  |  GEC Sheikhpura  |  GitHub: sonalikumari09/live-weather-tracker"
    r2.font.name = "Arial"
    r2.font.size = Pt(12)
    r2.font.bold = True
    r2.font.color.rgb = PRIMARY_GLOW

    # Save to Downloads and workspace
    output_pptx = "/home/rohit/Downloads/Live_Weather_Tracker_Internship_Presentation.pptx"
    prs.save(output_pptx)
    workspace_pptx = "/home/rohit/Downloads/funproject/weather/Live_Weather_Tracker_Internship_Presentation.pptx"
    prs.save(workspace_pptx)
    print(f"Minimal presentation saved to {output_pptx} and {workspace_pptx}")

if __name__ == "__main__":
    create_presentation()
