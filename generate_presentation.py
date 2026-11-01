import os
import shutil
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

    # Professional Theme Color Palette
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
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), Inches(2.6), Inches(0.32)
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
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.4), Inches(0.42), Inches(1.13), Inches(0.32)
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

        # Slide Title
        title_box = slide.shapes.add_textbox(
            Inches(0.8), Inches(0.8), Inches(10.4), Inches(0.6)
        )
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = Inches(0)
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Arial"
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_DARK

        # Subtle Accent Divider
        divider = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02)
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
    # SLIDE 1: Title Slide (Dark Hero Aesthetic)
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, BG_DARK)

    # Accent vertical glow bar
    glow_bar = slide1.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(0.1), Inches(5.9)
    )
    glow_bar.fill.solid()
    glow_bar.fill.fore_color.rgb = PRIMARY_GLOW
    glow_bar.line.color.rgb = PRIMARY_GLOW

    # Top Tag
    top_badge = slide1.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.15), Inches(0.8), Inches(4.3), Inches(0.38)
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

    # Main Title Box
    title_box = slide1.shapes.add_textbox(
        Inches(1.15), Inches(1.35), Inches(11.35), Inches(2.3)
    )
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = 0

    p1 = tf1.paragraphs[0]
    p1.text = "Python Programming & Software Engineering"
    p1.font.name = "Arial"
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_after = Pt(8)

    p2 = tf1.add_paragraph()
    p2.text = "Capstone Project: Live Weather Tracker"
    p2.font.name = "Arial"
    p2.font.size = Pt(21)
    p2.font.bold = True
    p2.font.color.rgb = PRIMARY_GLOW
    p2.space_after = Pt(6)

    p3 = tf1.add_paragraph()
    p3.text = "A Trilingual, Zero-Key Meteorological & Agricultural Intelligence Platform for 550,000+ Indian Villages"
    p3.font.name = "Arial"
    p3.font.size = Pt(13.5)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # Candidate Card
    c1 = create_card(slide1, Inches(1.15), Inches(3.95), Inches(5.6), Inches(2.75), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    c1_tf = c1.text_frame
    c1_tf.word_wrap = True
    c1_tf.margin_left = c1_tf.margin_top = Inches(0.28)
    c1_tf.margin_right = Inches(0.28)

    p = c1_tf.paragraphs[0]
    p.text = "CANDIDATE DETAILS"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(10)

    rows_c1 = [
        ("Student Name", "Sonali Kumari"),
        ("Roll Number", "26DCSE26"),
        ("Branch / Degree", "Computer Science & Engineering (B.Tech CSE)"),
        ("Institution", "Government Engineering College, Sheikhpura")
    ]
    for lbl, val in rows_c1:
        pr = c1_tf.add_paragraph()
        pr.space_after = Pt(5)
        run_l = pr.add_run()
        run_l.text = f"{lbl}:  "
        run_l.font.name = "Arial"
        run_l.font.size = Pt(11.5)
        run_l.font.color.rgb = RGBColor(148, 163, 184)
        run_v = pr.add_run()
        run_v.text = val
        run_v.font.name = "Arial"
        run_v.font.size = Pt(11.5)
        run_v.font.bold = True
        run_v.font.color.rgb = RGBColor(255, 255, 255)

    # Organization Card
    c2 = create_card(slide1, Inches(7.05), Inches(3.95), Inches(5.45), Inches(2.75), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    c2_tf = c2.text_frame
    c2_tf.word_wrap = True
    c2_tf.margin_left = c2_tf.margin_top = Inches(0.28)
    c2_tf.margin_right = Inches(0.28)

    p = c2_tf.paragraphs[0]
    p.text = "TRAINING & EVALUATION"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(10)

    rows_c2 = [
        ("Host Organization", "INTELLIO INTERN (AICTE Recognized)"),
        ("Internship Domain", "Python Programming & Web Architecture"),
        ("Duration", "25/09/2026 - 08/10/2026 (2 Weeks Intensive)"),
        ("Evaluation Result", "Grade A+ (91%)  |  Cert ID: BQTA26319")
    ]
    for lbl, val in rows_c2:
        pr = c2_tf.add_paragraph()
        pr.space_after = Pt(5)
        run_l = pr.add_run()
        run_l.text = f"{lbl}:  "
        run_l.font.name = "Arial"
        run_l.font.size = Pt(11.5)
        run_l.font.color.rgb = RGBColor(148, 163, 184)
        run_v = pr.add_run()
        run_v.text = val
        run_v.font.name = "Arial"
        run_v.font.size = Pt(11.5)
        run_v.font.bold = True
        run_v.font.color.rgb = RGBColor(255, 255, 255) if "Grade" not in lbl else RGBColor(52, 211, 153)

    # ==========================================
    # SLIDE 2: About the Organization & Training
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, BG_LIGHT)
    add_header(slide2, "About INTELLIO INTERN & Training Program", "Organization Profile", "02 / 12")

    col_w = Inches(3.68)
    col_gap = Inches(0.34)
    top_y = Inches(1.72)
    h_card = Inches(5.25)

    # Box 1: Organization Profile
    b1 = create_card(slide2, Inches(0.8), top_y, col_w, h_card)
    tf1 = b1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = tf1.margin_top = Inches(0.28)

    p = tf1.paragraphs[0]
    p.text = "HOST ORGANIZATION"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    p_title = tf1.add_paragraph()
    p_title.text = "INTELLIO INTERN"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(17)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(10)

    bullet_points1 = [
        ("AICTE Recognized Entity:", " Certified technical education training partner offering structured engineering internships."),
        ("Domain Expertise:", " Specializes in Python Programming, Data Engineering, Web Systems, and Cloud-native technologies."),
        ("Industry Alignment:", " Focuses on real-world engineering paradigms, modular code design, and version control."),
        ("Mentorship Model:", " Guided by experienced software developers providing architectural reviews and code feedback.")
    ]
    for b_title, b_desc in bullet_points1:
        pr = tf1.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = "• " + b_title
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = b_desc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    # Box 2: Training Structure & Mode
    b2 = create_card(slide2, Inches(0.8) + col_w + col_gap, top_y, col_w, h_card)
    tf2 = b2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_right = tf2.margin_top = Inches(0.28)

    p = tf2.paragraphs[0]
    p.text = "INTERNSHIP STRUCTURE"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    p_title = tf2.add_paragraph()
    p_title.text = "Mode & Pedagogy"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(17)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(10)

    bullet_points2 = [
        ("Duration:", " 2-Week Intensive Program (25 Sept 2026 - 08 Oct 2026)."),
        ("Delivery Mode:", " 100% Online & Hands-on, combining live technical sessions with daily coding tasks."),
        ("Learning Methodology:", " Practical exercise-first approach; students write production code rather than passive theory."),
        ("Evaluation Rigor:", " Daily deliverables, milestone reviews, and final live viva evaluation with code demonstration.")
    ]
    for b_title, b_desc in bullet_points2:
        pr = tf2.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = "• " + b_title
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = b_desc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    # Box 3: Timeline & Capstone Focus
    b3 = create_card(slide2, Inches(0.8) + (col_w + col_gap) * 2, top_y, col_w, h_card)
    tf3 = b3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_right = tf3.margin_top = Inches(0.28)

    p = tf3.paragraphs[0]
    p.text = "PROGRAM TIMELINE"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    p_title = tf3.add_paragraph()
    p_title.text = "Milestones & Delivery"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(17)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(10)

    bullet_points3 = [
        ("Week 1 Milestone:", " Core Python mastery, object-oriented design, custom exceptions, file I/O, and SQLite storage."),
        ("Week 2 Milestone:", " REST API integration (Open-Meteo), geospatial indexing, trilingual i18n localization engine."),
        ("Independent Capstone:", " Designed and built the 'Live Weather Tracker' independently following mentor reviews."),
        ("Final Outcome:", " Successfully achieved Grade A+ (91%) with verified certificate credential BQTA26319.")
    ]
    for b_title, b_desc in bullet_points3:
        pr = tf3.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = "• " + b_title
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = b_desc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 3: Purpose and Objectives
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, BG_LIGHT)
    add_header(slide3, "Internship Purpose, Motivation & Core Objectives", "Project Motivation", "03 / 12")

    # Left Column: Problem Motivation
    card_l = create_card(slide3, Inches(0.8), Inches(1.72), Inches(5.65), Inches(5.25))
    tf_l = card_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = Inches(0.3)

    p = tf_l.paragraphs[0]
    p.text = "WHY THIS INTERNSHIP & PROJECT?"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    p_t = tf_l.add_paragraph()
    p_t.text = "Motivation & Problem Context"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(17)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_after = Pt(12)

    m_points = [
        ("Bridging Academic Theory with Production Code:", " College coursework focuses on synthetic CLI scripts; the primary goal was to architect an end-to-end web system with real API feeds, caching, and scalable state handling."),
        ("The Rural Meteorological Divide in India:", " Commercial weather applications (AccuWeather, Apple Weather) cater predominantly to tier-1 metropolitan cities. Over 550,000 rural villages and 763 districts are neglected or buried behind paywalls."),
        ("Eliminating Paywalls & Vendor Lock-In:", " Weather services often enforce costly API key restrictions. This project was motivated by building a completely free, zero-key, open-access intelligence platform for common citizens and farmers.")
    ]
    for pt, desc in m_points:
        pr = tf_l.add_paragraph()
        pr.space_after = Pt(9)
        r1 = pr.add_run()
        r1.text = "• " + pt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = desc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    # Right Column Top: Main Objectives
    card_rt = create_card(slide3, Inches(6.8), Inches(1.72), Inches(5.73), Inches(2.5))
    tf_rt = card_rt.text_frame
    tf_rt.word_wrap = True
    tf_rt.margin_left = tf_rt.margin_right = tf_rt.margin_top = Inches(0.28)

    p = tf_rt.paragraphs[0]
    p.text = "PRIMARY TECHNICAL OBJECTIVES"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)

    p_t = tf_rt.add_paragraph()
    p_t.text = "What I Aimed to Build"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_after = Pt(6)

    objs = [
        ("All-India Coverage: ", "Index and search 565,000+ Indian villages and all 763 districts with instant sub-millisecond autocomplete."),
        ("Agro-Meteorology: ", "Deliver actionable soil moisture, soil temperature (6cm), and rainfall history specifically for farmers."),
        ("Trilingual Accessibility: ", "Provide full localization in English, Hindi, and Bhojpuri without cloud API translation lag.")
    ]
    for ot, od in objs:
        pr = tf_rt.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + ot
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = od
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    # Right Column Bottom: Expected Skills
    card_rb = create_card(slide3, Inches(6.8), Inches(4.45), Inches(5.73), Inches(2.52))
    tf_rb = card_rb.text_frame
    tf_rb.word_wrap = True
    tf_rb.margin_left = tf_rb.margin_right = tf_rb.margin_top = Inches(0.28)

    p = tf_rb.paragraphs[0]
    p.text = "KEY SKILLS DEVELOPED"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)

    p_t = tf_rb.add_paragraph()
    p_t.text = "Software Engineering Competencies"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_after = Pt(6)

    skills = [
        ("Modular Python: ", "Separation of concerns into decoupled modules (weather, geo, places, i18n, ui)."),
        ("Database & Compression: ", "Managing and querying compressed SQLite (.sqlite.gz) datasets on demand."),
        ("Dual Deployment: ", "Deploying reactive Python apps on Streamlit Cloud and static edge apps on Cloudflare Pages.")
    ]
    for st, sd in skills:
        pr = tf_rb.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + st
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = sd
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 4: Technologies / Tools / Skills Learned
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, BG_LIGHT)
    add_header(slide4, "Technologies, Frameworks & Development Tools", "Technology Stack", "04 / 12")

    grid_w = Inches(5.68)
    grid_h = Inches(2.52)
    left1 = Inches(0.8)
    left2 = Inches(6.85)
    row1_t = Inches(1.72)
    row2_t = Inches(4.45)

    # Card 1: Core Programming & Frontend
    c4_1 = create_card(slide4, left1, row1_t, grid_w, grid_h)
    tf4_1 = c4_1.text_frame
    tf4_1.word_wrap = True
    tf4_1.margin_left = tf4_1.margin_right = tf4_1.margin_top = Inches(0.24)
    p = tf4_1.paragraphs[0]
    p.text = "1. PROGRAMMING & CLIENT-SIDE"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_title = tf4_1.add_paragraph()
    p_title.text = "Core Languages & UI"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(15)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(6)

    t1_bullets = [
        ("Python 3.10+:", " Object-oriented design, custom exceptions, lazy loading, in-memory decompressions."),
        ("JavaScript (ES6+):", " Client-side DOM manipulation, async/await fetch, live tabs, and UI toggles."),
        ("HTML5 & Modern CSS3:", " Responsive flex/grid cards, glassmorphic styles, and animated sky condition banners.")
    ]
    for bt, bd in t1_bullets:
        pr = tf4_1.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + bt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = bd
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    # Card 2: APIs & Meteorological Data
    c4_2 = create_card(slide4, left2, row1_t, grid_w, grid_h)
    tf4_2 = c4_2.text_frame
    tf4_2.word_wrap = True
    tf4_2.margin_left = tf4_2.margin_right = tf4_2.margin_top = Inches(0.24)
    p = tf4_2.paragraphs[0]
    p.text = "2. APIS & GEOSPATIAL DATA"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_title = tf4_2.add_paragraph()
    p_title.text = "Data Feeds & Geocoding"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(15)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(6)

    t2_bullets = [
        ("Open-Meteo REST API:", " Hourly & 7-day meteorological forecasts, soil moisture & temperature (Zero API Key)."),
        ("GeoNames India Database:", " CC BY 4.0 extract covering 565,000+ Indian villages, tehsils, and towns."),
        ("Photon & Nominatim:", " OpenStreetMap-backed autocomplete fallback for PIN codes and remote hamlets.")
    ]
    for bt, bd in t2_bullets:
        pr = tf4_2.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + bt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = bd
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    # Card 3: Storage & Databases
    c4_3 = create_card(slide4, left1, row2_t, grid_w, grid_h)
    tf4_3 = c4_3.text_frame
    tf4_3.word_wrap = True
    tf4_3.margin_left = tf4_3.margin_right = tf4_3.margin_top = Inches(0.24)
    p = tf4_3.paragraphs[0]
    p.text = "3. STORAGE & DATA WRANGLING"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_title = tf4_3.add_paragraph()
    p_title.text = "SQLite & Edge SQL"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(15)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(6)

    t3_bullets = [
        ("SQLite3 (.sqlite.gz):", " Gzip-compressed bundled database for sub-10ms local prefix search on villages."),
        ("Cloudflare D1:", " Distributed SQLite edge database for instant serverless query lookups worldwide."),
        ("Pandas Library:", " Tabular data restructuring and 7-day temperature/rain trend calculations.")
    ]
    for bt, bd in t3_bullets:
        pr = tf4_3.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + bt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = bd
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    # Card 4: Deployment & Dev Tools
    c4_4 = create_card(slide4, left2, row2_t, grid_w, grid_h)
    tf4_4 = c4_4.text_frame
    tf4_4.word_wrap = True
    tf4_4.margin_left = tf4_4.margin_right = tf4_4.margin_top = Inches(0.24)
    p = tf4_4.paragraphs[0]
    p.text = "4. DEPLOYMENT & DEV TOOLS"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_title = tf4_4.add_paragraph()
    p_title.text = "Cloud Hosting & Version Control"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(15)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(6)

    t4_bullets = [
        ("Streamlit Web Framework:", " Interactive data application development with state caching (@st.cache_data)."),
        ("Cloudflare Pages & Workers:", " Serverless edge architecture (`functions/api/`) and global CDN edge caching."),
        ("Git & GitHub / Linux:", " Source management (`sonalikumari09/live-weather-tracker`), bash automation scripts.")
    ]
    for bt, bd in t4_bullets:
        pr = tf4_4.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + bt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = bd
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 5: Work / Training Completed
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, BG_LIGHT)
    add_header(slide5, "Practical Work & Training Modules Completed", "Work Completed", "05 / 12")

    mod_w = Inches(2.72)
    mod_gap = Inches(0.28)
    mod_h = Inches(3.65)
    mod_y = Inches(1.72)

    modules_data = [
        ("MODULE 1", "Python Core & Architecture", [
            ("OOP Principles:", " Classes, encapsulation, and modular design."),
            ("Error Handling:", " Custom exception hierarchy for network timeouts."),
            ("Data Compression:", " Gzip decompression of bundled databases into RAM."),
            ("Code Standards:", " PEP 8 compliance and strict typing.")
        ]),
        ("MODULE 2", "APIs & Data Engineering", [
            ("REST Client:", " Built robust HTTP client using Python Requests."),
            ("Open-Meteo Integration:", " Parsed multi-layer weather and soil parameters."),
            ("Payload Sanitization:", " Resilient JSON extraction and type validation."),
            ("Failure Recovery:", " Fallback strategies for offline/slow connections.")
        ]),
        ("MODULE 3", "Database & Search Index", [
            ("GeoNames Parsing:", " Processed 565,000+ Indian geo-coordinates."),
            ("SQLite Storage:", " Created lightweight indexed database for India places."),
            ("Ranked Search:", " Hierarchical sorting prioritizing cities & districts."),
            ("Hybrid Fallback:", " Nominatim & Photon fallback for unlisted hamlets.")
        ]),
        ("MODULE 4", "UI & Vernacular Localization", [
            ("Trilingual i18n:", " Built instant dictionary for English, Hindi, Bhojpuri."),
            ("Streamlit UI:", " Designed responsive tabs and interactive selectors."),
            ("Dynamic Styling:", " Crafted custom CSS themes and animated sky effects."),
            ("Edge Adaptation:", " Ported application to Cloudflare Pages edge.")
        ])
    ]

    for i, (m_tag, m_title, m_items) in enumerate(modules_data):
        bx = create_card(slide5, Inches(0.8) + (mod_w + mod_gap) * i, mod_y, mod_w, mod_h)
        tf = bx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)

        p = tf.paragraphs[0]
        p.text = m_tag
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(2)

        pt = tf.add_paragraph()
        pt.text = m_title
        pt.font.name = "Arial"
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(8)

        for it, idesc in m_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(4)
            r1 = pr.add_run()
            r1.text = "• " + it
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(10.5)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(10.5)
            r2.font.color.rgb = TEXT_BODY

    # Bottom Banner: Assessment & Certification
    bot_card = create_card(slide5, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.35), EMERALD_BG, EMERALD_BORDER, 1.5)
    tf_bot = bot_card.text_frame
    tf_bot.word_wrap = True
    tf_bot.margin_left = tf_bot.margin_right = Inches(0.3)
    tf_bot.margin_top = Inches(0.18)

    p = tf_bot.paragraphs[0]
    p.text = "TRAINING EVALUATION & CERTIFICATION OUTCOME"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = EMERALD_TEXT
    p.space_after = Pt(4)

    p_desc = tf_bot.add_paragraph()
    r1 = p_desc.add_run()
    r1.text = "Successfully satisfied all weekly project deliverables, technical code audits, and final capstone evaluation. "
    r1.font.name = "Arial"
    r1.font.size = Pt(11.5)
    r1.font.color.rgb = RGBColor(15, 23, 42)

    r2 = p_desc.add_run()
    r2.text = "Awarded Grade A+ (91%) by INTELLIO INTERN (AICTE Recognized). Certificate ID: BQTA26319 (Issued 08 Oct 2026)."
    r2.font.name = "Arial"
    r2.font.size = Pt(11.5)
    r2.font.bold = True
    r2.font.color.rgb = EMERALD_TEXT

    # ==========================================
    # SLIDE 6: Project Overview - Live Weather Tracker
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, BG_LIGHT)
    add_header(slide6, "Project Overview - Live Weather Tracker", "Project Architecture", "06 / 12")

    # Left Column: Problem & Solution
    card6_l = create_card(slide6, Inches(0.8), Inches(1.72), Inches(5.65), Inches(5.25))
    tf6_l = card6_l.text_frame
    tf6_l.word_wrap = True
    tf6_l.margin_left = tf6_l.margin_right = tf6_l.margin_top = Inches(0.3)

    p = tf6_l.paragraphs[0]
    p.text = "PROBLEM STATEMENT & VALUE PROPOSITION"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf6_l.add_paragraph()
    pt.text = "Hyperlocal Weather for All India"
    pt.font.name = "Arial"
    pt.font.size = Pt(17)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(10)

    p6_items = [
        ("The Problem:", " Mainstream weather apps cater only to major metropolitan cities, bombard users with ads, enforce expensive API subscriptions, and lack rural language support."),
        ("Our Solution:", " Live Weather Tracker is a fast, clean, zero-key, privacy-friendly meteorological web portal providing instant weather forecasts for 763 districts and 550,000+ villages across India."),
        ("Target Users:", " Farmers needing soil & rain data, daily rural commuters, interstate travelers, and citizens seeking ad-free forecasts."),
        ("Vernacular First:", " Native trilingual support in English, Hindi (हिन्दी), and Bhojpuri (भोजपुरी) for maximum regional inclusivity.")
    ]
    for it, idesc in p6_items:
        pr = tf6_l.add_paragraph()
        pr.space_after = Pt(8)
        r1 = pr.add_run()
        r1.text = "• " + it
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = idesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    # Right Column: 5 Modes & Architecture
    card6_r = create_card(slide6, Inches(6.8), Inches(1.72), Inches(5.73), Inches(5.25))
    tf6_r = card6_r.text_frame
    tf6_r.word_wrap = True
    tf6_r.margin_left = tf6_r.margin_right = tf6_r.margin_top = Inches(0.3)

    p = tf6_r.paragraphs[0]
    p.text = "5 APPLICATION MODES & WORKFLOW"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf6_r.add_paragraph()
    pt.text = "Feature Capabilities"
    pt.font.name = "Arial"
    pt.font.size = Pt(17)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(10)

    modes = [
        ("1. Single Place:", " Real-time temp, feels-like, wind, humidity, 7-day forecast."),
        ("2. Farmer Mode:", " Soil temperature (6cm), moisture levels, 7-day rain history, and localized agricultural advisories."),
        ("3. Travel Packer:", " Smart packing recommendations based on rain probability, temperature, and wind speed."),
        ("4. Morning Alerts:", " Early warning system for extreme heatwaves, coldwaves, severe thunderstorms, or heavy downpours."),
        ("5. Compare Places:", " Side-by-side weather comparisons for 2 to 4 locations.")
    ]
    for mt, mdesc in modes:
        pr = tf6_r.add_paragraph()
        pr.space_after = Pt(5)
        r1 = pr.add_run()
        r1.text = mt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = PRIMARY
        r2 = pr.add_run()
        r2.text = mdesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    pr_pipe = tf6_r.add_paragraph()
    pr_pipe.space_before = Pt(8)
    r1 = pr_pipe.add_run()
    r1.text = "Pipeline: "
    r1.font.name = "Arial"
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = TEXT_DARK
    r2 = pr_pipe.add_run()
    r2.text = "Query ➔ Compressed SQLite / Edge D1 ➔ Open-Meteo REST ➔ i18n Engine ➔ Dynamic Client View"
    r2.font.name = "Arial"
    r2.font.size = Pt(11)
    r2.font.bold = True
    r2.font.color.rgb = PRIMARY

    # ==========================================
    # SLIDE 7: Individual Contribution
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, BG_LIGHT)
    add_header(slide7, "My Individual Contribution & Core Modules Built", "Individual Contribution", "07 / 12")

    c7_1 = create_card(slide7, left1, row1_t, grid_w, grid_h)
    tf7_1 = c7_1.text_frame
    tf7_1.word_wrap = True
    tf7_1.margin_left = tf7_1.margin_right = tf7_1.margin_top = Inches(0.24)
    p = tf7_1.paragraphs[0]
    p.text = "1. WEATHER ENGINE & AGRO-LOGIC (weather.py)"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_t = tf7_1.add_paragraph()
    p_t.text = "Meteorological Core"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_after = Pt(6)

    c1_pts = [
        ("API Consumption: ", "Designed REST endpoints fetching current, 7-day, and agricultural telemetry from Open-Meteo."),
        ("Farmer Intelligence: ", "Synthesized 6cm soil warmth, root moisture, and 7-day rain accumulation into practical advisories."),
        ("Rule-Based Triggers: ", "Built dynamic logic for Travel Packer checklists and Morning Severe Weather Alert checks.")
    ]
    for pt, pdesc in c1_pts:
        pr = tf7_1.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + pt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = pdesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    c7_2 = create_card(slide7, left2, row1_t, grid_w, grid_h)
    tf7_2 = c7_2.text_frame
    tf7_2.word_wrap = True
    tf7_2.margin_left = tf7_2.margin_right = tf7_2.margin_top = Inches(0.24)
    p = tf7_2.paragraphs[0]
    p.text = "2. GEOCODING & LOCAL DATABASE (geo.py, places.py)"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_t = tf7_2.add_paragraph()
    p_t.text = "Search & Indexing Engine"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_after = Pt(6)

    c2_pts = [
        ("Offline SQLite Index: ", "Processed 565,000+ Indian geo-entities into a compressed SQLite store (`india_places.sqlite.gz`)."),
        ("Sub-10ms Prefix Search: ", "Implemented SQL prefix autocomplete with ranking that prioritizes districts and major towns."),
        ("Multi-Tier Fallback: ", "Created graceful fallback to Photon / OSM / Nominatim for PIN codes and unlisted hamlets.")
    ]
    for pt, pdesc in c2_pts:
        pr = tf7_2.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + pt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = pdesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    c7_3 = create_card(slide7, left1, row2_t, grid_w, grid_h)
    tf7_3 = c7_3.text_frame
    tf7_3.word_wrap = True
    tf7_3.margin_left = tf7_3.margin_right = tf7_3.margin_top = Inches(0.24)
    p = tf7_3.paragraphs[0]
    p.text = "3. TRILINGUAL LOCALIZATION (i18n.py)"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_t = tf7_3.add_paragraph()
    p_t.text = "Vernacular Language Engine"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_after = Pt(6)

    c3_pts = [
        ("Zero-Lag Translation: ", "Engineered a static dictionary mapping strings into English, Hindi, and regional Bhojpuri."),
        ("Full Domain Coverage: ", "Translated all UI labels, meteorological status codes (WMO), agricultural advisories, and tips."),
        ("Cultural Idioms: ", "Ensured agricultural and weather descriptions feel natural to rural northern/eastern Indian speakers.")
    ]
    for pt, pdesc in c3_pts:
        pr = tf7_3.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + pt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = pdesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    c7_4 = create_card(slide7, left2, row2_t, grid_w, grid_h)
    tf7_4 = c7_4.text_frame
    tf7_4.word_wrap = True
    tf7_4.margin_left = tf7_4.margin_right = tf7_4.margin_top = Inches(0.24)
    p = tf7_4.paragraphs[0]
    p.text = "4. UI/UX & DUAL CLOUD ARCHITECTURE"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(3)
    p_t = tf7_4.add_paragraph()
    p_t.text = "Frontend & Serverless Edge"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_after = Pt(6)

    c4_pts = [
        ("Streamlit Interface: ", "Built responsive UI (`app.py`) with theme toggle, animated sky banners, and custom CSS."),
        ("Cloudflare Serverless: ", "Configured edge functions (`functions/api/`) and client web app (`public/app.js`)."),
        ("Tiered Caching: ", "Implemented memory caching (`@st.cache_data`) and HTTP edge cache headers (600s TTL).")
    ]
    for pt, pdesc in c4_pts:
        pr = tf7_4.add_paragraph()
        pr.space_after = Pt(3)
        r1 = pr.add_run()
        r1.text = "• " + pt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = pdesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 8: Demonstration / Evidence of Work
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, BG_LIGHT)
    add_header(slide8, "Demonstration, UI Screens & Certification Evidence", "Project Evidence", "08 / 12")

    # Left Box: AICTE Recognized Certificate
    card8_l = create_card(slide8, Inches(0.8), Inches(1.72), Inches(5.65), Inches(4.35))
    tf8_l = card8_l.text_frame
    tf8_l.word_wrap = True
    tf8_l.margin_left = tf8_l.margin_right = tf8_l.margin_top = Inches(0.18)
    p = tf8_l.paragraphs[0]
    p.text = "COMPLETION CERTIFICATE (INTELLIO INTERN)"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    # Insert Certificate Image inside left box
    cert_img_path = "/home/rohit/Downloads/funproject/weather/presentation_assets/certificate-1.png"
    if os.path.exists(cert_img_path):
        slide8.shapes.add_picture(
            cert_img_path, Inches(1.0), Inches(2.12), width=Inches(5.25), height=Inches(3.35)
        )

    # Caption box for certificate
    cap_cert = slide8.shapes.add_textbox(Inches(0.9), Inches(5.55), Inches(5.45), Inches(0.45))
    tf_cc = cap_cert.text_frame
    tf_cc.word_wrap = True
    tf_cc.margin_left = tf_cc.margin_top = 0
    p_cc = tf_cc.paragraphs[0]
    p_cc.text = "AICTE Recognized Certificate | Sonali Kumari (26DCSE26) | Grade A+ (91%) | ID: BQTA26319"
    p_cc.font.name = "Arial"
    p_cc.font.size = Pt(9.5)
    p_cc.font.bold = True
    p_cc.font.color.rgb = EMERALD_TEXT

    # Right Box: Live Weather Tracker Application Screenshot
    card8_r = create_card(slide8, Inches(6.8), Inches(1.72), Inches(5.73), Inches(4.35))
    tf8_r = card8_r.text_frame
    tf8_r.word_wrap = True
    tf8_r.margin_left = tf8_r.margin_right = tf8_r.margin_top = Inches(0.18)
    p = tf8_r.paragraphs[0]
    p.text = "LIVE WEATHER TRACKER - PRODUCTION APPLICATION"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    # Insert Weather App Screenshot inside right box
    app_img_path = "/home/rohit/Downloads/funproject/weather/presentation_assets/weather_app_live.png"
    if os.path.exists(app_img_path):
        slide8.shapes.add_picture(
            app_img_path, Inches(7.0), Inches(2.12), width=Inches(5.33), height=Inches(3.35)
        )

    # Caption box for weather app
    cap_app = slide8.shapes.add_textbox(Inches(6.9), Inches(5.55), Inches(5.5), Inches(0.45))
    tf_ca = cap_app.text_frame
    tf_ca.word_wrap = True
    tf_ca.margin_left = tf_ca.margin_top = 0
    p_ca = tf_ca.paragraphs[0]
    p_ca.text = "Live Web Interface | All-India Place Search | 5 Modes | Trilingual (EN / HI / BHO)"
    p_ca.font.name = "Arial"
    p_ca.font.size = Pt(9.5)
    p_ca.font.bold = True
    p_ca.font.color.rgb = PRIMARY

    # Bottom Repository / Deployment Evidence Bar
    bar8 = create_card(slide8, Inches(0.8), Inches(6.18), Inches(11.733), Inches(0.92))
    tf_bar = bar8.text_frame
    tf_bar.word_wrap = True
    tf_bar.margin_left = tf_bar.margin_right = Inches(0.25)
    tf_bar.margin_top = Inches(0.12)

    p = tf_bar.paragraphs[0]
    r1 = p.add_run()
    r1.text = "Source Code Repository:  "
    r1.font.name = "Arial"
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = TEXT_DARK
    r2 = p.add_run()
    r2.text = "https://github.com/sonalikumari09/live-weather-tracker   (Public / Main Branch)\n"
    r2.font.name = "Arial"
    r2.font.size = Pt(11)
    r2.font.bold = True
    r2.font.color.rgb = PRIMARY

    r3 = p.add_run()
    r3.text = "Dual Deployment Architecture:  "
    r3.font.name = "Arial"
    r3.font.bold = True
    r3.font.size = Pt(10.5)
    r3.font.color.rgb = TEXT_DARK
    r4 = p.add_run()
    r4.text = "Streamlit Cloud (Data App)  +  Cloudflare Pages Edge (*.pages.dev) with D1 SQLite & Serverless Functions"
    r4.font.name = "Arial"
    r4.font.size = Pt(10.5)
    r4.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 9: Challenges and How You Solved Them
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, BG_LIGHT)
    add_header(slide9, "Challenges Faced & Problem-Solving Approach", "Technical Challenges", "09 / 12")

    ch_w = Inches(11.733)
    ch_h = Inches(1.58)
    top_c1 = Inches(1.72)
    top_c2 = Inches(3.48)
    top_c3 = Inches(5.24)

    challenges = [
        ("CHALLENGE 1: Sub-Second Geocoding for 550,000+ Indian Villages Without Paid APIs",
         "Commercial geocoding APIs (Google Maps) are prohibitively expensive; free public endpoints (Nominatim) rate-limit to 1 req/sec and fail under rapid typing.",
         "Pre-processed the entire GeoNames India dataset into a local SQLite database compressed with gzip (india_places.sqlite.gz).",
         "Decompress on first use into memory, query via indexed SQL prefix matching, and rank results by administrative hierarchy with Photon fallback.",
         "Instant autocomplete search (<15ms latency) with zero external API dependencies and zero operating cost."),
         
        ("CHALLENGE 2: Transforming Complex Agro-Telemetry into Actionable Farmer Advice",
         "Raw meteorological data (volumetric soil moisture m³/m³, soil warmth at 6cm, WMO codes) is unintelligible and unusable for rural farmers.",
         "Researched agronomic thresholds for Indian crops, root depth dynamics, and seasonal precipitation trends.",
         "Created rule-based algorithms synthesizing 7-day cumulative rainfall, 6cm soil temperature, and moisture into clear text advisories.",
         "Farmers receive direct, practical guidance (e.g., 'Soil moisture adequate for sowing', 'Irrigation recommended') in their regional tongue."),

        ("CHALLENGE 3: Seamless Trilingual Experience Without External Translation Latency",
         "Third-party translation APIs (Google Cloud Translate) add 300-600ms network latency per request, require quotas, and produce robotic translations of rural idioms.",
         "Designed a centralized in-memory static dictionary mapping inside i18n.py and public/app.js.",
         "Pre-mapped all UI labels, meteorological codes, agricultural tips, and packing advice into structured key-value stores for English, Hindi, and Bhojpuri.",
         "Instantaneous (<1ms) language toggle with 100% offline accuracy, cultural phrasing, and zero network overhead.")
    ]

    for i, (c_tag, prob, appr, sol, res) in enumerate(challenges):
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
        p.space_after = Pt(2)

        p_body = tf.add_paragraph()
        p_body.space_after = Pt(0)

        # Problem
        r1 = p_body.add_run()
        r1.text = "Problem: "
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = ROSE_TEXT
        r2 = p_body.add_run()
        r2.text = prob + "  "
        r2.font.name = "Arial"
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_BODY

        # Approach & Solution
        r3 = p_body.add_run()
        r3.text = "Approach & Solution: "
        r3.font.name = "Arial"
        r3.font.bold = True
        r3.font.size = Pt(10)
        r3.font.color.rgb = PRIMARY
        r4 = p_body.add_run()
        r4.text = f"{appr} {sol}  "
        r4.font.name = "Arial"
        r4.font.size = Pt(10)
        r4.font.color.rgb = TEXT_BODY

        # Result
        r5 = p_body.add_run()
        r5.text = "Result: "
        r5.font.name = "Arial"
        r5.font.bold = True
        r5.font.size = Pt(10)
        r5.font.color.rgb = EMERALD_TEXT
        r6 = p_body.add_run()
        r6.text = res
        r6.font.name = "Arial"
        r6.font.size = Pt(10)
        r6.font.bold = True
        r6.font.color.rgb = EMERALD_TEXT

    # ==========================================
    # SLIDE 10: What I Learned
    # ==========================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, BG_LIGHT)
    add_header(slide10, "Key Learnings & Skill Acquisition", "Learning Outcomes", "10 / 12")

    # Left: Technical Learnings
    card10_l = create_card(slide10, Inches(0.8), Inches(1.72), Inches(5.65), Inches(5.25))
    tf10_l = card10_l.text_frame
    tf10_l.word_wrap = True
    tf10_l.margin_left = tf10_l.margin_right = tf10_l.margin_top = Inches(0.3)

    p = tf10_l.paragraphs[0]
    p.text = "TECHNICAL LEARNINGS"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf10_l.add_paragraph()
    pt.text = "Engineering & Systems Mastery"
    pt.font.name = "Arial"
    pt.font.size = Pt(17)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(10)

    tech_learnings = [
        ("Modular Python Programming:", " Designing clean, decoupled architectures adhering to PEP 8 standards, custom exceptions, and type hints."),
        ("REST API & Telemetry Integration:", " Consuming multi-endpoint meteorological APIs, robust timeout handling, and payload normalization."),
        ("Database Optimization:", " Structuring SQLite databases, building prefix search indices, and implementing on-demand gzip decompression in memory."),
        ("Full-Stack & Cloud Deployment:", " Developing reactive dashboards in Streamlit and configuring Cloudflare Pages serverless edge functions with D1 database."),
        ("Performance Caching Strategies:", " Implementing tiered in-memory caching (@st.cache_data) and HTTP Cache-Control headers to reduce load times to <50ms.")
    ]
    for lt, ldesc in tech_learnings:
        pr = tf10_l.add_paragraph()
        pr.space_after = Pt(6)
        r1 = pr.add_run()
        r1.text = "• " + lt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = ldesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    # Right: Professional & Soft Skills
    card10_r = create_card(slide10, Inches(6.8), Inches(1.72), Inches(5.73), Inches(5.25))
    tf10_r = card10_r.text_frame
    tf10_r.word_wrap = True
    tf10_r.margin_left = tf10_r.margin_right = tf10_r.margin_top = Inches(0.3)

    p = tf10_r.paragraphs[0]
    p.text = "PROFESSIONAL & DESIGN LEARNINGS"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(4)

    pt = tf10_r.add_paragraph()
    pt.text = "Product Thinking & Execution"
    pt.font.name = "Arial"
    pt.font.size = Pt(17)
    pt.font.bold = True
    pt.font.color.rgb = TEXT_DARK
    pt.space_after = Pt(10)

    soft_learnings = [
        ("Social Impact Engineering:", " Designing technology with empathy for non-metro, rural communities, ensuring accessibility for non-English speakers."),
        ("Problem Decomposition:", " Breaking down a large-scale project into discrete, manageable, testable components and milestones."),
        ("Version Control & Collaboration:", " Structuring clear git commits, writing descriptive README documentation, and setting up automated deployment scripts."),
        ("Time Management:", " Successfully taking a project from conceptualization to full cloud deployment within a strict 2-week internship timeline."),
        ("Areas for Further Growth:", " Enhancing automated unit test coverage with pytest, implementing Docker containers, and setting up CI/CD GitHub Actions.")
    ]
    for lt, ldesc in soft_learnings:
        pr = tf10_r.add_paragraph()
        pr.space_after = Pt(6)
        r1 = pr.add_run()
        r1.text = "• " + lt
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = pr.add_run()
        r2.text = ldesc
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 11: Future Improvements & Roadmap
    # ==========================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, BG_LIGHT)
    add_header(slide11, "Future Enhancements & Scalability Roadmap", "Future Roadmap", "11 / 12")

    future_data = [
        ("1. LIVE RADAR & SATELLITE OVERLAYS", "Visual Storm Tracking", [
            ("INSAT & IMD Integration: ", "Incorporate live INSAT-3D/3DR satellite imagery and Indian Meteorological Department Doppler radar overlays."),
            ("Precipitation Trajectory: ", "Provide visual cloud trajectory maps, cyclone path estimations, and lightning hazard zones."),
            ("Real-Time Animation: ", "Enable time-scrubbing weather radar loops for farmers and disaster management teams.")
        ]),
        ("2. VOICE VERNACULAR ASSISTANT", "Spoken Language Querying", [
            ("Web Speech API Integration: ", "Allow farmers to simply tap a microphone and speak village names or ask queries."),
            ("Regional Dialects: ", "Support voice inputs in Hindi, Bhojpuri, Maithili, and Bengali to eliminate literacy barriers."),
            ("Voice Audio Responses: ", "Synthesize spoken weather summaries for audio playback on mobile browsers.")
        ]),
        ("3. SMS & WHATSAPP BROADCAST ALERTS", "Low-Connectivity Access", [
            ("Feature Phone Inclusivity: ", "Connect Twilio / Indian SMS gateway to send automated morning weather summaries via SMS."),
            ("Severe Warning Push: ", "Trigger automated SMS/WhatsApp alerts for heatwaves, sudden frost, and severe thunderstorms."),
            ("Zero Data Requirement: ", "Ensure critical agricultural advisories reach farmers without requiring smartphones or 4G data.")
        ]),
        ("4. PROGRESSIVE WEB APP (PWA) & IOT", "Offline Resilience & Precision", [
            ("PWA Service Workers: ", "Cache the last 7 days of forecasts locally so the app works completely offline in remote villages."),
            ("Micro-Climate Sensors: ", "Provide API hooks to interface with low-cost LoRaWAN soil moisture and micro-weather hardware sensors."),
            ("Installable App: ", "One-click install directly from browser to Android home screens without Google Play Store dependencies.")
        ])
    ]

    for i, (f_tag, f_title, f_items) in enumerate(future_data):
        curr_left = left1 if i % 2 == 0 else left2
        curr_top = row1_t if i < 2 else row2_t

        card = create_card(slide11, curr_left, curr_top, grid_w, grid_h)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.24)

        p = tf.paragraphs[0]
        p.text = f_tag
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        p.space_after = Pt(2)

        pt = tf.add_paragraph()
        pt.text = f_title
        pt.font.name = "Arial"
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_DARK
        pt.space_after = Pt(6)

        for it, idesc in f_items:
            pr = tf.add_paragraph()
            pr.space_after = Pt(3)
            r1 = pr.add_run()
            r1.text = "• " + it
            r1.font.name = "Arial"
            r1.font.bold = True
            r1.font.size = Pt(11)
            r1.font.color.rgb = TEXT_DARK
            r2 = pr.add_run()
            r2.text = idesc
            r2.font.name = "Arial"
            r2.font.size = Pt(11)
            r2.font.color.rgb = TEXT_BODY

    # ==========================================
    # SLIDE 12: Conclusion & Viva Voce (Dark Hero Theme)
    # ==========================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, BG_DARK)

    # Decorative glow bar
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
    p_12p.text = "SUMMARY & VIVA VOCE"
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
        Inches(1.15), Inches(1.3), Inches(11.35), Inches(1.1)
    )
    tf12 = title12_box.text_frame
    tf12.word_wrap = True
    tf12.margin_left = tf12.margin_top = 0
    p1 = tf12.paragraphs[0]
    p1.text = "Conclusion & Project Defense"
    p1.font.name = "Arial"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_after = Pt(4)
    p2 = tf12.add_paragraph()
    p2.text = "Summary of Internship Deliverables & Technical Achievements"
    p2.font.name = "Arial"
    p2.font.size = Pt(15)
    p2.font.color.rgb = PRIMARY_GLOW

    # Middle 2 Cards
    c12_l = create_card(slide12, Inches(1.15), Inches(2.6), Inches(5.6), Inches(2.65), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    tf12_l = c12_l.text_frame
    tf12_l.word_wrap = True
    tf12_l.margin_left = tf12_l.margin_right = tf12_l.margin_top = Inches(0.25)
    p = tf12_l.paragraphs[0]
    p.text = "INTERNSHIP OUTCOMES"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(6)

    c12_pts1 = [
        ("Completed 2-Week Intensive Internship", " in Python Programming at INTELLIO INTERN (AICTE Recognized)."),
        ("Achieved Grade A+ (91%)", " in final assessment and technical project evaluation (Certificate ID: BQTA26319)."),
        ("Built 'Live Weather Tracker'", " from scratch, providing hyper-local forecasts for 763 districts and 550,000+ villages across India.")
    ]
    for ct, cd in c12_pts1:
        pr = tf12_l.add_paragraph()
        pr.space_after = Pt(5)
        r1 = pr.add_run()
        r1.text = "• " + ct
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = RGBColor(255, 255, 255)
        r2 = pr.add_run()
        r2.text = cd
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = RGBColor(148, 163, 184)

    c12_r = create_card(slide12, Inches(7.05), Inches(2.6), Inches(5.45), Inches(2.65), BG_CARD_DARK, CARD_BORDER_DARK, 1)
    tf12_r = c12_r.text_frame
    tf12_r.word_wrap = True
    tf12_r.margin_left = tf12_r.margin_right = tf12_r.margin_top = Inches(0.25)
    p = tf12_r.paragraphs[0]
    p.text = "CORE IMPACT & TAKEAWAY"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GLOW
    p.space_after = Pt(6)

    c12_pts2 = [
        ("Bridged Academic & Industry Skills:", " Gained production-ready mastery in Python, REST APIs, SQLite indexing, and serverless edge deployment."),
        ("Social Impact Focus:", " Solved real-world rural challenges with trilingual accessibility (English, Hindi, Bhojpuri) and agricultural telemetry."),
        ("Scalable Open Architecture:", " Engineered 100% free, zero-key infrastructure running seamlessly on Streamlit and Cloudflare Pages.")
    ]
    for ct, cd in c12_pts2:
        pr = tf12_r.add_paragraph()
        pr.space_after = Pt(5)
        r1 = pr.add_run()
        r1.text = "• " + ct
        r1.font.name = "Arial"
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = RGBColor(255, 255, 255)
        r2 = pr.add_run()
        r2.text = cd
        r2.font.name = "Arial"
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = RGBColor(148, 163, 184)

    # Bottom Call to Action Hero Card
    hero12 = create_card(slide12, Inches(1.15), Inches(5.45), Inches(11.35), Inches(1.3), RGBColor(30, 41, 59), PRIMARY, 1.5)
    tf_hero = hero12.text_frame
    tf_hero.word_wrap = True
    tf_hero.margin_left = tf_hero.margin_right = Inches(0.3)
    tf_hero.margin_top = Inches(0.18)

    p_h = tf_hero.paragraphs[0]
    p_h.alignment = PP_ALIGN.CENTER
    r1 = p_h.add_run()
    r1.text = "Thank You! Ready for Live Demonstration & Technical Q&A\n"
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
    print(f"Presentation saved successfully to {output_pptx} and {workspace_pptx}")

if __name__ == "__main__":
    create_presentation()
