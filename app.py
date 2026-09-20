# ============================================================
# HireFlow
# AI Candidate Screening & Interview Intelligence Agent
#
# Streamlit Frontend
# ============================================================

import html
import json
import time
from pathlib import Path

import streamlit as st

from core import report
from core.parser import extract_text
from core.analyzer import analyze_job_description, analyze_candidate
from core.matcher import (
    build_match_result,
    unresolved_requirements,
    evidence_counts,
)
from core.interview import (
    generate_question,
    evaluate_answer,
    apply_evaluation,
)
from core.report import generate_report


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="HireFlow — AI Candidate Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "job": None,
    "job_text": "",
    "candidates": {},
    "selected_candidate": None,
    "interviews": {},
    "active_requirement": None,
    "question": None,
    "last_evaluation": None,
    "final_report": None,
    "page": "Dashboard",
}


def init_state():
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ============================================================
# HTML HELPERS
# ============================================================

def esc(value):
    """
    Safely escape dynamic text before inserting it into HTML.
    """
    if value is None:
        return ""

    return html.escape(str(value))


def render_html(content):
    """
    Render HTML using Streamlit's native HTML renderer.
    """
    st.html(content)


# ============================================================
# UNIVERSE BACKGROUND
# ============================================================

def render_universe():
    """
    Render the animated deep-space background.

    The background is built entirely with HTML + CSS.
    No image files are required.
    No JavaScript is required.
    """

    universe_html = r"""
    <style>

    /* ========================================================
       HIRE FLOW
       REALISTIC SPACE BACKGROUND
       ======================================================== */

    .hf-universe {
        position: fixed;
        inset: 0;

        width: 100vw;
        height: 100vh;

        overflow: hidden;

        pointer-events: none;

        z-index: 0;

        background:
            radial-gradient(
                ellipse at 18% 15%,
                rgba(91, 33, 182, 0.18),
                transparent 34%
            ),
            radial-gradient(
                ellipse at 85% 70%,
                rgba(30, 64, 175, 0.16),
                transparent 38%
            ),
            radial-gradient(
                ellipse at 50% 100%,
                rgba(124, 58, 237, 0.10),
                transparent 38%
            ),
            #02030a;
    }


    /* ========================================================
       DEEP NEBULA
       ======================================================== */

    .hf-nebula {

        position: absolute;

        width: 1000px;
        height: 560px;

        left: 50%;
        top: 50%;

        transform:
            translate(-50%, -50%)
            rotate(-18deg);

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse at center,

                rgba(196, 181, 253, 0.07) 0%,

                rgba(139, 92, 246, 0.14) 12%,

                rgba(79, 70, 229, 0.10) 30%,

                rgba(59, 130, 246, 0.06) 48%,

                transparent 72%
            );

        filter: blur(35px);

        opacity: 0.75;

        animation:
            hfNebulaDrift 32s ease-in-out infinite alternate;
    }


    /* ========================================================
       SECOND NEBULA
       ======================================================== */

    .hf-nebula-two {

        position: absolute;

        width: 700px;
        height: 420px;

        left: 12%;
        top: 65%;

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse,
                rgba(37, 99, 235, 0.08),
                rgba(124, 58, 237, 0.06) 35%,
                transparent 70%
            );

        filter: blur(50px);

        animation:
            hfNebulaTwo 40s ease-in-out infinite alternate;
    }


    /* ========================================================
       GALAXY
       ======================================================== */

    .hf-galaxy {

        position: absolute;

        width: 650px;
        height: 260px;

        left: 73%;
        top: 22%;

        transform:
            translate(-50%, -50%)
            rotate(-22deg);

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse at center,

                rgba(255,255,255,0.92) 0%,

                rgba(221,214,254,0.55) 2%,

                rgba(196,181,253,0.25) 8%,

                rgba(139,92,246,0.16) 18%,

                rgba(79,70,229,0.09) 35%,

                rgba(59,130,246,0.03) 50%,

                transparent 72%
            );

        box-shadow:
            0 0 50px rgba(139,92,246,0.16),
            0 0 110px rgba(59,130,246,0.08);

        opacity: 0.68;

        animation:
            hfGalaxyDrift 45s ease-in-out infinite alternate;
    }


    /* ========================================================
       GALAXY DISK
       ======================================================== */

    .hf-galaxy::before {

        content: "";

        position: absolute;

        left: 5%;
        right: 5%;

        top: 28%;
        bottom: 28%;

        border-radius: 50%;

        border-top:
            2px solid
            rgba(196,181,253,0.18);

        border-bottom:
            2px solid
            rgba(96,165,250,0.12);

        box-shadow:
            0 0 30px rgba(139,92,246,0.10);

        filter: blur(1.5px);

        transform: rotate(-5deg);
    }


    /* ========================================================
       GALAXY CORE
       ======================================================== */

    .hf-galaxy::after {

        content: "";

        position: absolute;

        width: 20px;
        height: 20px;

        left: 50%;
        top: 50%;

        transform:
            translate(-50%, -50%);

        border-radius: 50%;

        background: white;

        box-shadow:
            0 0 10px white,
            0 0 25px rgba(221,214,254,0.95),
            0 0 55px rgba(139,92,246,0.70),
            0 0 100px rgba(124,58,237,0.35);
    }


    /* ========================================================
       SMALLER DISTANT GALAXY
       ======================================================== */

    .hf-small-galaxy {

        position: absolute;

        width: 250px;
        height: 90px;

        left: 15%;
        top: 25%;

        border-radius: 50%;

        transform: rotate(24deg);

        background:
            radial-gradient(
                ellipse,

                rgba(255,255,255,0.65),

                rgba(147,197,253,0.18) 12%,

                rgba(59,130,246,0.07) 35%,

                transparent 70%
            );

        filter: blur(1px);

        opacity: 0.35;

        animation:
            hfSmallGalaxy 55s linear infinite;
    }


    /* ========================================================
       STAR BASE
       ======================================================== */

    .hf-star {

        position: absolute;

        width: 2px;
        height: 2px;

        border-radius: 50%;

        background: rgba(255,255,255,0.85);

        box-shadow:
            0 0 5px rgba(255,255,255,0.75);

        animation:
            hfStarPulse 4s ease-in-out infinite;
    }


    /* ========================================================
       BRIGHT STARS
       ======================================================== */

    .hf-star-bright {

        position: absolute;

        width: 3px;
        height: 3px;

        border-radius: 50%;

        background: white;

        box-shadow:
            0 0 6px white,
            0 0 14px rgba(147,197,253,0.75),
            0 0 25px rgba(139,92,246,0.35);

        animation:
            hfBrightStar 5s ease-in-out infinite;
    }


    /* ========================================================
       STAR CROSS
       ======================================================== */

    .hf-star-cross {

        position: absolute;

        width: 5px;
        height: 5px;

        border-radius: 50%;

        background: white;

        box-shadow:
            0 0 7px white,
            0 0 15px rgba(147,197,253,0.80);
    }

    .hf-star-cross::before,
    .hf-star-cross::after {

        content: "";

        position: absolute;

        left: 50%;
        top: 50%;

        transform: translate(-50%, -50%);

        background:
            linear-gradient(
                transparent,
                rgba(255,255,255,0.8),
                transparent
            );
    }

    .hf-star-cross::before {

        width: 24px;
        height: 1px;
    }

    .hf-star-cross::after {

        width: 1px;
        height: 24px;
    }


    /* ========================================================
       METEOR
       ======================================================== */

    .hf-meteor {

        position: absolute;

        width: 5px;
        height: 5px;

        border-radius: 50%;

        background: white;

        box-shadow:
            0 0 7px white,
            0 0 15px rgba(147,197,253,0.95),
            0 0 30px rgba(96,165,250,0.60);

        opacity: 0;

        transform: rotate(-35deg);

        animation:
            hfMeteor 11s linear infinite;
    }


    .hf-meteor::after {

        content: "";

        position: absolute;

        width: 170px;
        height: 2px;

        right: 3px;
        top: 2px;

        transform-origin: right center;

        background:
            linear-gradient(
                to left,
                rgba(255,255,255,0.85),
                rgba(147,197,253,0.35),
                transparent
            );

        filter: blur(1px);
    }


    .hf-meteor-two {

        top: 28%;
        left: 20%;

        animation:
            hfMeteorTwo 15s linear infinite;

        animation-delay: 5s;
    }


    .hf-meteor-three {

        top: 60%;
        left: 45%;

        animation:
            hfMeteorThree 18s linear infinite;

        animation-delay: 9s;
    }


    /* ========================================================
       FLOATING COSMIC DUST
       ======================================================== */

    .hf-dust {

        position: absolute;

        width: 1px;
        height: 1px;

        border-radius: 50%;

        background: rgba(196,181,253,0.5);

        animation:
            hfDustFloat 20s ease-in-out infinite;
    }


    /* ========================================================
       ANIMATIONS
       ======================================================== */

    @keyframes hfNebulaDrift {

        0% {

            transform:
                translate(-50%, -50%)
                rotate(-18deg)
                scale(0.94);

            opacity: 0.48;
        }

        50% {

            transform:
                translate(-46%, -53%)
                rotate(-11deg)
                scale(1.06);

            opacity: 0.72;
        }

        100% {

            transform:
                translate(-54%, -47%)
                rotate(-23deg)
                scale(1.02);

            opacity: 0.58;
        }
    }


    @keyframes hfNebulaTwo {

        0% {

            transform:
                translate(0,0)
                scale(0.9);

            opacity: 0.25;
        }

        50% {

            transform:
                translate(70px,-40px)
                scale(1.08);

            opacity: 0.45;
        }

        100% {

            transform:
                translate(-40px,60px)
                scale(0.98);

            opacity: 0.30;
        }
    }


    @keyframes hfGalaxyDrift {

        0% {

            transform:
                translate(-50%, -50%)
                rotate(-22deg)
                scale(0.96);
        }

        50% {

            transform:
                translate(-48%, -53%)
                rotate(-13deg)
                scale(1.04);
        }

        100% {

            transform:
                translate(-52%, -47%)
                rotate(-25deg)
                scale(1.00);
        }
    }


    @keyframes hfSmallGalaxy {

        0% {

            transform:
                rotate(24deg)
                translate(0,0);
        }

        50% {

            transform:
                rotate(28deg)
                translate(25px,-15px);
        }

        100% {

            transform:
                rotate(24deg)
                translate(0,0);
        }
    }


    @keyframes hfStarPulse {

        0%,
        100% {

            opacity: 0.20;

            transform:
                scale(0.75);
        }

        50% {

            opacity: 0.95;

            transform:
                scale(1.35);
        }
    }


    @keyframes hfBrightStar {

        0%,
        100% {

            opacity: 0.35;

            transform:
                scale(0.75);
        }

        50% {

            opacity: 1;

            transform:
                scale(1.5);
        }
    }


    @keyframes hfMeteor {

        0% {

            transform:
                translate(-250px,-150px)
                rotate(-35deg);

            opacity: 0;
        }

        5% {

            opacity: 1;
        }

        23% {

            transform:
                translate(115vw,75vh)
                rotate(-35deg);

            opacity: 0;
        }

        24%,
        100% {

            opacity: 0;
        }
    }


    @keyframes hfMeteorTwo {

        0% {

            transform:
                translate(-300px,100px)
                rotate(-35deg);

            opacity: 0;
        }

        5% {

            opacity: 1;
        }

        22% {

            transform:
                translate(110vw,60vh)
                rotate(-35deg);

            opacity: 0;
        }

        23%,
        100% {

            opacity: 0;
        }
    }


    @keyframes hfMeteorThree {

        0% {

            transform:
                translate(-300px,-100px)
                rotate(-35deg);

            opacity: 0;
        }

        6% {

            opacity: 1;
        }

        24% {

            transform:
                translate(115vw,80vh)
                rotate(-35deg);

            opacity: 0;
        }

        25%,
        100% {

            opacity: 0;
        }
    }


    @keyframes hfDustFloat {

        0% {

            transform:
                translate(0,0)
                scale(0.8);

            opacity: 0.15;
        }

        50% {

            transform:
                translate(30px,-25px)
                scale(1.2);

            opacity: 0.55;
        }

        100% {

            transform:
                translate(-20px,30px)
                scale(0.9);

            opacity: 0.20;
        }
    }


    /* ========================================================
       STREAMLIT LAYERING
       ======================================================== */

    [data-testid="stAppViewContainer"] {

        position: relative;

        z-index: 1;
    }


    [data-testid="stHeader"] {

        background: transparent !important;

        z-index: 5;
    }


    [data-testid="stSidebar"] {

        position: relative;

        z-index: 10;
    }


    [data-testid="stMainBlockContainer"] {

        position: relative;

        z-index: 3;
    }


    /* ========================================================
       REDUCED MOTION
       ======================================================== */

    @media (prefers-reduced-motion: reduce) {

        .hf-universe *,
        .hf-universe {

            animation: none !important;
        }
    }

    </style>


    <!-- ======================================================
         UNIVERSE
         ====================================================== -->

    <div class="hf-universe">

        <div class="hf-nebula"></div>

        <div class="hf-nebula-two"></div>

        <div class="hf-galaxy"></div>

        <div class="hf-small-galaxy"></div>


        <!-- ===================== STARS ===================== -->

        <div class="hf-star" style="left:4%;top:8%;animation-delay:.5s;"></div>
        <div class="hf-star" style="left:8%;top:22%;animation-delay:1.8s;"></div>
        <div class="hf-star-bright" style="left:13%;top:11%;animation-delay:2.2s;"></div>
        <div class="hf-star" style="left:18%;top:38%;animation-delay:.9s;"></div>
        <div class="hf-star" style="left:23%;top:7%;animation-delay:3.1s;"></div>
        <div class="hf-star-bright" style="left:29%;top:25%;animation-delay:1.2s;"></div>
        <div class="hf-star" style="left:34%;top:13%;animation-delay:2.7s;"></div>
        <div class="hf-star" style="left:39%;top:44%;animation-delay:.4s;"></div>
        <div class="hf-star-cross" style="left:46%;top:16%;"></div>
        <div class="hf-star" style="left:52%;top:35%;animation-delay:1.7s;"></div>
        <div class="hf-star-bright" style="left:58%;top:9%;animation-delay:2.9s;"></div>
        <div class="hf-star" style="left:64%;top:43%;animation-delay:.8s;"></div>
        <div class="hf-star" style="left:71%;top:12%;animation-delay:1.4s;"></div>
        <div class="hf-star-bright" style="left:78%;top:38%;animation-delay:2.4s;"></div>
        <div class="hf-star" style="left:84%;top:16%;animation-delay:1.1s;"></div>
        <div class="hf-star" style="left:91%;top:29%;animation-delay:3.4s;"></div>
        <div class="hf-star-cross" style="left:96%;top:10%;"></div>


        <div class="hf-star" style="left:5%;top:57%;animation-delay:1.9s;"></div>
        <div class="hf-star-bright" style="left:11%;top:78%;animation-delay:2.8s;"></div>
        <div class="hf-star" style="left:17%;top:65%;animation-delay:.7s;"></div>
        <div class="hf-star" style="left:24%;top:91%;animation-delay:1.5s;"></div>
        <div class="hf-star-cross" style="left:31%;top:70%;"></div>
        <div class="hf-star" style="left:38%;top:82%;animation-delay:2.6s;"></div>
        <div class="hf-star-bright" style="left:44%;top:62%;animation-delay:1.0s;"></div>
        <div class="hf-star" style="left:51%;top:90%;animation-delay:3.0s;"></div>
        <div class="hf-star" style="left:57%;top:73%;animation-delay:.3s;"></div>
        <div class="hf-star-bright" style="left:63%;top:88%;animation-delay:2.1s;"></div>
        <div class="hf-star" style="left:70%;top:65%;animation-delay:1.3s;"></div>
        <div class="hf-star-cross" style="left:76%;top:82%;"></div>
        <div class="hf-star" style="left:83%;top:73%;animation-delay:2.5s;"></div>
        <div class="hf-star-bright" style="left:89%;top:91%;animation-delay:.6s;"></div>
        <div class="hf-star" style="left:96%;top:70%;animation-delay:1.8s;"></div>


        <!-- ===================== DUST ===================== -->

        <div class="hf-dust" style="left:10%;top:45%;animation-delay:.5s;"></div>
        <div class="hf-dust" style="left:21%;top:52%;animation-delay:3s;"></div>
        <div class="hf-dust" style="left:35%;top:58%;animation-delay:6s;"></div>
        <div class="hf-dust" style="left:48%;top:47%;animation-delay:2s;"></div>
        <div class="hf-dust" style="left:61%;top:54%;animation-delay:8s;"></div>
        <div class="hf-dust" style="left:75%;top:50%;animation-delay:4s;"></div>
        <div class="hf-dust" style="left:87%;top:44%;animation-delay:7s;"></div>


        <!-- ===================== METEORS ===================== -->

        <div
            class="hf-meteor"
            style="top:7%;left:3%;"
        ></div>

        <div
            class="hf-meteor hf-meteor-two"
        ></div>

        <div
            class="hf-meteor hf-meteor-three"
        ></div>

    </div>
    """

    render_html(universe_html)


# ============================================================
# GLOBAL UI STYLE
# ============================================================

def render_global_style():

    css = r"""
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {

        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(124,58,237,0.05),
                transparent 35%
            ),
            #02030a !important;
    }


    /* ========================================================
       REMOVE DEFAULT TOP SPACE
       ======================================================== */

    .block-container {

        padding-top: 2rem !important;

        position: relative;

        z-index: 4;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                rgba(8,10,24,0.94),
                rgba(3,5,15,0.97)
            ) !important;

        border-right:
            1px solid
            rgba(139,92,246,0.12);
    }


    /* ========================================================
       GLASS CARD
       ======================================================== */

    .hf-card {

        background:
            linear-gradient(
                135deg,
                rgba(255,255,255,0.055),
                rgba(255,255,255,0.018)
            );

        border:
            1px solid
            rgba(255,255,255,0.08);

        border-radius: 22px;

        padding: 26px;

        backdrop-filter:
            blur(18px);

        -webkit-backdrop-filter:
            blur(18px);

        box-shadow:
            0 20px 70px rgba(0,0,0,0.25);

        margin-bottom: 20px;
    }


    .hf-card:hover {

        border-color:
            rgba(139,92,246,0.24);

        box-shadow:
            0 25px 80px rgba(0,0,0,0.35);
    }


    /* ========================================================
       BRAND
       ======================================================== */

    .hf-brand {

        font-size: 27px;

        font-weight: 800;

        letter-spacing: -1px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c4b5fd,
                #93c5fd
            );

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;
    }


    .hf-brand-sub {

        color:
            rgba(226,232,240,0.52);

        font-size: 12px;

        margin-top: 3px;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hf-hero {

        padding:
            50px 20px 35px;

        text-align: center;
    }


    .hf-hero-kicker {

        display: inline-flex;

        align-items: center;

        gap: 8px;

        padding:
            8px 14px;

        border-radius: 999px;

        background:
            rgba(139,92,246,0.09);

        border:
            1px solid
            rgba(139,92,246,0.20);

        color:
            #c4b5fd;

        font-size: 12px;

        font-weight: 600;

        letter-spacing: 0.4px;

        margin-bottom: 20px;
    }


    .hf-live-dot {

        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: #a78bfa;

        box-shadow:
            0 0 12px
            rgba(167,139,250,0.9);

        animation:
            hfPulse 2s ease-in-out infinite;
    }


    .hf-hero-title {

        font-size: clamp(42px, 6vw, 76px);

        line-height: 0.98;

        font-weight: 850;

        letter-spacing: -4px;

        margin: 0;

        background:
            linear-gradient(
                100deg,
                #ffffff 15%,
                #c4b5fd 45%,
                #93c5fd 80%
            );

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;
    }


    .hf-hero-description {

        max-width: 720px;

        margin:
            22px auto 0;

        color:
            rgba(226,232,240,0.58);

        font-size: 16px;

        line-height: 1.7;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .hf-section-title {

        font-size: 21px;

        font-weight: 750;

        color: #f8fafc;

        margin-bottom: 5px;
    }


    .hf-section-subtitle {

        color:
            rgba(226,232,240,0.48);

        font-size: 13px;

        margin-bottom: 22px;
    }


    /* ========================================================
       METRIC
       ======================================================== */

    .hf-metric {

        text-align: center;

        padding: 20px 10px;
    }


    .hf-metric-number {

        font-size: 32px;

        font-weight: 800;

        color: #f8fafc;
    }


    .hf-metric-label {

        color:
            rgba(226,232,240,0.48);

        font-size: 11px;

        margin-top: 4px;

        text-transform: uppercase;

        letter-spacing: 0.8px;
    }


    /* ========================================================
       STATUS BADGES
       ======================================================== */

    .hf-badge {

        display: inline-flex;

        align-items: center;

        padding:
            5px 10px;

        border-radius: 999px;

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.3px;
    }


    .hf-matched {

        color: #86efac;

        background:
            rgba(34,197,94,0.10);

        border:
            1px solid
            rgba(34,197,94,0.20);
    }


    .hf-unclear {

        color: #fcd34d;

        background:
            rgba(245,158,11,0.10);

        border:
            1px solid
            rgba(245,158,11,0.20);
    }


    .hf-missing {

        color: #fca5a5;

        background:
            rgba(239,68,68,0.10);

        border:
            1px solid
            rgba(239,68,68,0.20);
    }


    /* ========================================================
       REQUIREMENT ROW
       ======================================================== */

    .hf-requirement {

        padding: 17px;

        margin-bottom: 10px;

        border-radius: 15px;

        background:
            rgba(255,255,255,0.025);

        border:
            1px solid
            rgba(255,255,255,0.06);
    }


    .hf-requirement-name {

        color: #f8fafc;

        font-weight: 650;

        font-size: 14px;

        margin-bottom: 7px;
    }


    .hf-reasoning {

        color:
            rgba(226,232,240,0.55);

        font-size: 12px;

        line-height: 1.6;
    }


    /* ========================================================
       EVIDENCE
       ======================================================== */

    .hf-evidence-box {

        margin-top: 12px;

        padding: 13px 15px;

        border-left:
            2px solid
            rgba(139,92,246,0.65);

        background:
            rgba(139,92,246,0.045);

        border-radius:
            0 10px 10px 0;
    }


    .hf-evidence-label {

        font-size: 10px;

        text-transform: uppercase;

        letter-spacing: 0.8px;

        color:
            rgba(196,181,253,0.70);

        margin-bottom: 5px;
    }


    .hf-evidence-text {

        font-size: 12px;

        line-height: 1.6;

        color:
            rgba(241,245,249,0.72);
    }


    /* ========================================================
       AGENT ORB
       ======================================================== */

    .hf-agent-wrap {

        display: flex;

        justify-content: center;

        align-items: center;

        padding:
            20px 0 30px;
    }


    .hf-agent-orb {

        width: 115px;
        height: 115px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle at 35% 30%,
                #ddd6fe,
                #8b5cf6 35%,
                #4c1d95 70%,
                #17102f 100%
            );

        box-shadow:
            0 0 30px
            rgba(139,92,246,0.35),

            0 0 80px
            rgba(124,58,237,0.18);

        animation:
            hfOrb 4s ease-in-out infinite;
    }


    .hf-agent-status {

        text-align: center;

        color:
            rgba(226,232,240,0.60);

        font-size: 12px;
    }


    /* ========================================================
       THINKING DOTS
       ======================================================== */

    .hf-thinking {

        display: inline-flex;

        gap: 5px;

        margin-left: 6px;
    }


    .hf-thinking span {

        width: 5px;
        height: 5px;

        border-radius: 50%;

        background: #a78bfa;

        animation:
            hfThink 1.2s infinite;
    }


    .hf-thinking span:nth-child(2) {

        animation-delay:
            0.15s;
    }


    .hf-thinking span:nth-child(3) {

        animation-delay:
            0.30s;
    }


    /* ========================================================
       CHAT
       ======================================================== */

    .hf-chat-user {

        margin-left: auto;

        max-width: 80%;

        padding: 14px 17px;

        border-radius:
            18px 18px 4px 18px;

        background:
            rgba(139,92,246,0.14);

        border:
            1px solid
            rgba(139,92,246,0.20);

        color:
            rgba(248,250,252,0.85);

        font-size: 13px;

        line-height: 1.6;
    }


    .hf-chat-agent {

        max-width: 80%;

        padding: 14px 17px;

        border-radius:
            18px 18px 18px 4px;

        background:
            rgba(255,255,255,0.035);

        border:
            1px solid
            rgba(255,255,255,0.07);

        color:
            rgba(248,250,252,0.78);

        font-size: 13px;

        line-height: 1.6;

        margin-bottom: 14px;
    }


    /* ========================================================
       REPORT
       ======================================================== */

    .hf-report-header {

        padding: 30px;

        border-radius: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(139,92,246,0.12),
                rgba(59,130,246,0.06)
            );

        border:
            1px solid
            rgba(139,92,246,0.16);
    }


    .hf-report-name {

        font-size: 27px;

        font-weight: 800;

        color: #f8fafc;
    }


    .hf-report-role {

        margin-top: 5px;

        color:
            rgba(226,232,240,0.48);

        font-size: 13px;
    }


    /* ========================================================
       WORKFLOW
       ======================================================== */

    .hf-workflow {

        display: flex;

        align-items: center;

        justify-content: center;

        gap: 10px;

        margin:
            12px 0 30px;

        flex-wrap: wrap;
    }


    .hf-step {

        padding:
            8px 12px;

        border-radius: 999px;

        background:
            rgba(255,255,255,0.035);

        border:
            1px solid
            rgba(255,255,255,0.07);

        color:
            rgba(226,232,240,0.50);

        font-size: 10px;

        text-transform: uppercase;

        letter-spacing: 0.5px;
    }


    .hf-step-active {

        background:
            rgba(139,92,246,0.12);

        border-color:
            rgba(139,92,246,0.25);

        color:
            #c4b5fd;
    }


    .hf-arrow {

        color:
            rgba(167,139,250,0.35);

        font-size: 13px;
    }


    /* ========================================================
       ANIMATIONS
       ======================================================== */

    @keyframes hfPulse {

        0%,
        100% {

            opacity: 0.45;

            transform: scale(0.8);
        }

        50% {

            opacity: 1;

            transform: scale(1.25);
        }
    }


    @keyframes hfOrb {

        0%,
        100% {

            transform:
                scale(0.96);

            box-shadow:
                0 0 30px
                rgba(139,92,246,0.30),

                0 0 70px
                rgba(124,58,237,0.12);
        }

        50% {

            transform:
                scale(1.04);

            box-shadow:
                0 0 45px
                rgba(139,92,246,0.48),

                0 0 100px
                rgba(124,58,237,0.22);
        }
    }


    @keyframes hfThink {

        0%,
        60%,
        100% {

            opacity: 0.25;

            transform:
                translateY(0);
        }

        30% {

            opacity: 1;

            transform:
                translateY(-4px);
        }
    }


    </style>
    """

    render_html(css)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        render_html(
    """
    <div style="padding:10px 4px 25px;">
        <div class="hf-brand">HireFlow</div>
        <div class="hf-brand-sub">AI Candidate Intelligence</div>
    </div>
    """, 
)

        st.markdown(
            """
            <div style="
                font-size:10px;
                color:rgba(226,232,240,.38);
                text-transform:uppercase;
                letter-spacing:1px;
                margin-bottom:8px;
            ">
                Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )

        pages = [
            ("Dashboard", "⌂"),
            ("Evidence", "◈"),
            ("Interview Agent", "✦"),
            ("Final Report", "▣"),
        ]

        for page_name, icon in pages:

            active = (
                st.session_state.page == page_name
            )

            if active:

                label = f"●  {icon}  {page_name}"

            else:

                label = f"○  {icon}  {page_name}"

            if st.button(
                label,
                key=f"nav_{page_name}",
                use_container_width=True,
            ):

                st.session_state.page = page_name

                st.rerun()

        render_html("""
                 <div style="
    margin-top:30px;
    padding:15px;
    border-radius:14px;
    background:rgba(255,255,255,.025);
    border:1px solid rgba(255,255,255,.06);
">
    <div style="
        font-size:10px;
        text-transform:uppercase;
        letter-spacing:.8px;
        color:rgba(226,232,240,.35);
    ">
        Human Review
    </div>

    <div style="
        font-size:11px;
        line-height:1.6;
        color:rgba(226,232,240,.48);
        margin-top:7px;
    ">
        HireFlow organizes evidence and
        supports structured interviews.
        Final employment decisions remain
        with human reviewers.
    </div>
</div>
""")


# ============================================================
# WORKFLOW HEADER
# ============================================================

def render_workflow(active_step):

    steps = [
        "JD Analysis",
        "Evidence",
        "Interview",
        "Report",
    ]

    html_parts = []

    for index, step in enumerate(steps):

        if index == active_step:

            cls = "hf-step hf-step-active"

        else:

            cls = "hf-step"

        html_parts.append(
            f'<span class="{cls}">{esc(step)}</span>'
        )

        if index < len(steps) - 1:

            html_parts.append(
                '<span class="hf-arrow">→</span>'
            )

    render_html(
        '<div class="hf-workflow">'
        + "".join(html_parts)
        + "</div>"
    )


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():

    render_workflow(0)

    render_html(
        """
        <div class="hf-hero">

            <div class="hf-hero-kicker">

                <span class="hf-live-dot"></span>

                AGENTIC CANDIDATE INTELLIGENCE

            </div>

            <h1 class="hf-hero-title">
                HireFlow
            </h1>

            <div class="hf-hero-description">

                Turn resumes and job descriptions into
                structured evidence, targeted interviews,
                and auditable candidate reports.

            </div>

        </div>
        """
    )

    col1, col2 = st.columns(
        [1.15, 0.85],
        gap="large",
    )

    with col1:

        render_html(
            """
            <div class="hf-card">

                <div class="hf-section-title">
                    Start a candidate analysis
                </div>

                <div class="hf-section-subtitle">
                    Upload the role requirements and candidate resumes.
                </div>

            </div>
            """
        )

        jd_file = st.file_uploader(
            "Job description",
            type=["pdf", "txt", "md"],
            key="jd_upload",
        )

        resume_files = st.file_uploader(
            "Candidate resumes",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            key="resume_upload",
        )

        launch = st.button(
            "✦  Launch HireFlow Agent",
            use_container_width=True,
            type="primary",
        )

        if launch:

            if jd_file is None:

                st.error(
                    "Please upload a job description first."
                )

                return

            if not resume_files:

                st.error(
                    "Please upload at least one resume."
                )

                return

            progress = st.empty()

            try:

                progress.info(
                    "Analyzing job requirements..."
                )

                jd_text = extract_text(jd_file)

                job = analyze_job_description(
                    jd_text
                )

                st.session_state.job = job
                st.session_state.job_text = jd_text

                time.sleep(0.2)

                progress.info(
                    "Checking candidate evidence..."
                )

                candidates = {}

                for resume_file in resume_files:

                    resume_text = extract_text(
                        resume_file
                    )

                    candidate_analysis = (
                        analyze_candidate(
                            resume_text,
                            job,
                        )
                    )

                    match_result = build_match_result(
                        candidate_analysis,
                        job,
                    )

                    # IMPORTANT:
                    # build_match_result returns a LIST.
                    evidence = match_result

                    candidate_name = (
                        Path(
                            resume_file.name
                        ).stem
                    )

                    candidates[candidate_name] = {
                        "name": candidate_name,
                        "resume_text": resume_text,
                        "analysis": candidate_analysis,
                        "evidence": evidence,
                    }

                st.session_state.candidates = candidates

                if candidates:

                    st.session_state.selected_candidate = (
                        list(candidates.keys())[0]
                    )

                st.session_state.page = "Evidence"

                progress.success(
                    "Analysis complete."
                )

                time.sleep(0.5)

                st.rerun()

            except Exception as e:

                progress.empty()

                st.error(
                    f"Error: {e}"
                )


    with col2:

        render_html(
            """
            <div class="hf-card">

                <div class="hf-section-title">
                    Agent workflow
                </div>

                <div class="hf-section-subtitle">
                    HireFlow continuously updates candidate evidence.
                </div>

                <div style="
                    margin-top:25px;
                ">

                    <div class="hf-requirement">

                        <div class="hf-requirement-name">
                            01 · Understand role
                        </div>

                        <div class="hf-reasoning">
                            Extract requirements and expected evidence.
                        </div>

                    </div>

                    <div class="hf-requirement">

                        <div class="hf-requirement-name">
                            02 · Inspect candidate
                        </div>

                        <div class="hf-reasoning">
                            Connect resume evidence to each requirement.
                        </div>

                    </div>

                    <div class="hf-requirement">

                        <div class="hf-requirement-name">
                            03 · Find uncertainty
                        </div>

                        <div class="hf-reasoning">
                            Identify requirements that remain unclear.
                        </div>

                    </div>

                    <div class="hf-requirement">

                        <div class="hf-requirement-name">
                            04 · Ask targeted questions
                        </div>

                        <div class="hf-reasoning">
                            Generate questions specifically for evidence gaps.
                        </div>

                    </div>

                    <div class="hf-requirement">

                        <div class="hf-requirement-name">
                            05 · Update evidence
                        </div>

                        <div class="hf-reasoning">
                            Incorporate interview responses into the evidence map.
                        </div>

                    </div>

                </div>

            </div>
            """
        )


# ============================================================
# EVIDENCE STATUS BADGE
# ============================================================

def status_badge(status):

    status_text = str(status or "UNCLEAR").upper()

    if status_text in ("MATCHED", "VALIDATED"):
        label = (
            "VALIDATED"
            if status_text == "VALIDATED"
            else "MATCHED"
        )

        return (
            '<span class="hf-badge hf-matched">'
            + label
            + '</span>'
        )

    if status_text == "PARTIAL":
        return (
            '<span class="hf-badge hf-unclear">'
            'PARTIAL'
            '</span>'
        )

    if status_text in ("MISSING", "INSUFFICIENT"):
        label = (
            "INSUFFICIENT"
            if status_text == "INSUFFICIENT"
            else "MISSING"
        )

        return (
            '<span class="hf-badge hf-missing">'
            + label
            + '</span>'
        )

    return (
        '<span class="hf-badge hf-unclear">'
        'UNCLEAR'
        '</span>'
    )


# ============================================================
# EVIDENCE PAGE
# ============================================================

def render_evidence():

    render_workflow(1)

    render_html(
        """
        <div class="hf-hero" style="padding-bottom:25px;">

            <div class="hf-hero-kicker">
                EVIDENCE ENGINE
            </div>

            <h1 class="hf-hero-title"
                style="font-size:48px;">
                Evidence Map
            </h1>

            <div class="hf-hero-description">
                See exactly what the resume proves,
                what remains uncertain, and what needs verification.
            </div>

        </div>
        """
    )

    if not st.session_state.candidates:

        st.info(
            "No candidate analysis exists yet. "
            "Return to Dashboard and upload a job description and resumes."
        )

        return

    candidate_names = list(
        st.session_state.candidates.keys()
    )

    selected = st.selectbox(
        "Candidate",
        candidate_names,
        index=candidate_names.index(
            st.session_state.selected_candidate
        )
        if st.session_state.selected_candidate in candidate_names
        else 0,
    )

    st.session_state.selected_candidate = selected

    candidate = st.session_state.candidates[selected]

    evidence = candidate.get(
        "evidence",
        [],
    )

    try:

        matched, unclear, missing = (
            evidence_counts(evidence)
        )

    except Exception:

        matched = sum(
            1
            for item in evidence
            if str(
                getattr(item, "status", "")
            ).upper()
            == "MATCHED"
        )

        unclear = sum(
            1
            for item in evidence
            if str(
                getattr(item, "status", "")
            ).upper()
            == "UNCLEAR"
        )

        missing = sum(
            1
            for item in evidence
            if str(
                getattr(item, "status", "")
            ).upper()
            == "MISSING"
        )

    total = len(evidence)

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        render_html(
            f"""
            <div class="hf-card hf-metric">

                <div class="hf-metric-number">
                    {total}
                </div>

                <div class="hf-metric-label">
                    Requirements
                </div>

            </div>
            """
        )

    with col2:

        render_html(
            f"""
            <div class="hf-card hf-metric">

                <div class="hf-metric-number">
                    {matched}
                </div>

                <div class="hf-metric-label">
                    Matched
                </div>

            </div>
            """
        )

    with col3:

        render_html(
            f"""
            <div class="hf-card hf-metric">

                <div class="hf-metric-number">
                    {unclear}
                </div>

                <div class="hf-metric-label">
                    Unclear
                </div>

            </div>
            """
        )

    with col4:

        render_html(
            f"""
            <div class="hf-card hf-metric">

                <div class="hf-metric-number">
                    {missing}
                </div>

                <div class="hf-metric-label">
                    Missing
                </div>

            </div>
            """
        )

    render_html(
        """
        <div class="hf-card">

            <div class="hf-section-title">
                Requirement-by-requirement evidence
            </div>

            <div class="hf-section-subtitle">
                Evidence is organized for human review.
            </div>

        </div>
        """
    )

    for item in evidence:

        requirement_name = getattr(
            item,
            "requirement_name",
            "Requirement",
        )

        status = getattr(
            item,
            "status",
            "UNCLEAR",
        )

        reasoning = getattr(
            item,
            "reasoning",
            "",
        )

        evidence_text = getattr(
            item,
            "evidence",
            "",
        )

        source = getattr(
            item,
            "source",
            "",
        )

        confidence = getattr(
            item,
            "confidence",
            None,
        )

        if confidence is not None:

            try:

                confidence_text = (
                    f"{float(confidence) * 100:.0f}%"
                )

            except Exception:

                confidence_text = str(
                    confidence
                )

        else:

            confidence_text = "—"

        badge = status_badge(status)

        render_html(
            f"""
            <div class="hf-card">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:15px;
                ">

                    <div class="hf-requirement-name">
                        {esc(requirement_name)}
                    </div>

                    {badge}

                </div>

                <div class="hf-reasoning"
                     style="margin-top:10px;">
                    {esc(reasoning)}
                </div>

                <div class="hf-evidence-box">

                    <div class="hf-evidence-label">
                        Evidence
                    </div>

                    <div class="hf-evidence-text">
                        {esc(evidence_text) if evidence_text else "No direct evidence recorded."}
                    </div>

                </div>

                <div style="
                    display:flex;
                    gap:25px;
                    margin-top:14px;
                    color:rgba(226,232,240,.40);
                    font-size:10px;
                ">

                    <span>
                        Source:
                        {esc(source) if source else "Resume"}
                    </span>

                    <span>
                        Confidence:
                        {esc(confidence_text)}
                    </span>

                </div>

            </div>
            """
        )

    unresolved = unresolved_requirements(
        evidence
    )

    if unresolved:

        st.markdown("")

        render_html(
            """
            <div class="hf-card">

                <div class="hf-section-title">
                    Evidence gaps detected
                </div>

                <div class="hf-section-subtitle">
                    HireFlow can investigate unresolved requirements
                    through a targeted interview.
                </div>

            </div>
            """
        )

        if st.button(
            "✦  Open Interview Agent",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Interview Agent"
            )

            st.rerun()


# ============================================================
# INTERVIEW PAGE
# ============================================================

def render_interview():

    render_workflow(2)

    render_html(
        """
        <div class="hf-hero" style="padding-bottom:20px;">

            <div class="hf-hero-kicker">
                ADAPTIVE INTERVIEW AGENT
            </div>

            <h1 class="hf-hero-title"
                style="font-size:48px;">
                Verify the Unknown
            </h1>

            <div class="hf-hero-description">
                Ask focused questions only where resume evidence
                is incomplete or uncertain.
            </div>

        </div>
        """
    )

    if not st.session_state.candidates:

        st.info(
            "Run a candidate analysis first."
        )

        return

    candidate_names = list(
        st.session_state.candidates.keys()
    )

    selected_candidate = st.selectbox(
        "Candidate",
        candidate_names,
        index=candidate_names.index(
            st.session_state.selected_candidate
        )
        if st.session_state.selected_candidate in candidate_names
        else 0,
        key="interview_candidate",
    )

    st.session_state.selected_candidate = (
        selected_candidate
    )

    candidate = st.session_state.candidates[
        selected_candidate
    ]

    evidence = candidate["evidence"]

    unresolved = unresolved_requirements(
        evidence
    )

    if not unresolved:

        render_html(
            """
            <div class="hf-card">

                <div class="hf-section-title">
                    No unresolved requirements
                </div>

                <div class="hf-section-subtitle">
                    The current evidence map does not contain
                    requirements requiring additional interview verification.
                </div>

            </div>
            """
        )

        return

    requirement_options = []

    for req in unresolved:

        requirement_options.append(
            req
        )

    selected_requirement = st.selectbox(
        "Requirement to investigate",
        requirement_options,
        format_func=lambda x: getattr(
            x,
            "requirement_name",
            str(x),
        ),
    )

    requirement_id = getattr(
        selected_requirement,
        "requirement_id",
        getattr(
            selected_requirement,
            "id",
            str(
                getattr(
                    selected_requirement,
                    "requirement_name",
                    "",
                )
            ),
        ),
    )

    requirement_name = getattr(
        selected_requirement,
        "requirement_name",
        str(selected_requirement),
    )

    col1, col2 = st.columns(
        [0.8, 1.2],
        gap="large",
    )

    with col1:

        render_html(
            f"""
            <div class="hf-card">

                <div class="hf-agent-wrap">

                    <div class="hf-agent-orb"></div>

                </div>

                <div class="hf-agent-status">

                    Agent ready

                    <span class="hf-thinking">
                        <span></span>
                        <span></span>
                        <span></span>
                    </span>

                </div>

            </div>

            <div class="hf-card">

                <div class="hf-section-title">
                    Investigation target
                </div>

                <div class="hf-section-subtitle">
                    {esc(requirement_name)}
                </div>

                <div class="hf-requirement">

                    <div class="hf-requirement-name">
                        Why this is being investigated
                    </div>

                    <div class="hf-reasoning">
                        Resume evidence is currently
                        incomplete or uncertain.
                    </div>

                </div>

            </div>
            """
        )

    with col2:

        if st.session_state.active_requirement != requirement_id:

            st.session_state.active_requirement = (
                requirement_id
            )

            st.session_state.question = None

            st.session_state.last_evaluation = None

        if st.session_state.question is None:

            if st.button(
                "✦  Generate Targeted Question",
                use_container_width=True,
                type="primary",
            ):

                try:
                    previous_context = st.session_state.interviews.get(
                        selected_candidate,
                        [],
                    )

                    question = generate_question(
                        selected_requirement,
                        previous_context=json.dumps(
                            previous_context,
                            default=str,
                        ),
                    )

                    st.session_state.question = question
                    st.rerun()

                except Exception as e:
                    st.error(
                        f"Question generation error: {e}"
                    )

        if st.session_state.question is not None:

            question = st.session_state.question

            question_text = getattr(
                question,
                "question",
                str(question),
            )

            objective = getattr(
                question,
                "objective",
                "",
            )

            render_html(
                f"""
                <div class="hf-card">

                    <div class="hf-section-title">
                        Targeted question
                    </div>

                    <div class="hf-chat-agent"
                         style="margin-top:18px;">

                        {esc(question_text)}

                    </div>

                    <div class="hf-evidence-box">

                        <div class="hf-evidence-label">
                            Objective
                        </div>

                        <div class="hf-evidence-text">
                            {esc(objective)}
                        </div>

                    </div>

                </div>
                """
            )

            answer = st.text_area(
                "Candidate response",
                height=180,
                placeholder=(
                    "Enter the candidate's response..."
                ),
                key="candidate_answer",
            )

            if st.button(
                "Evaluate Response",
                use_container_width=True,
                type="primary",
            ):

                if not answer.strip():

                    st.warning(
                        "Enter a candidate response first."
                    )

                else:

                    try:

                        previous_context = (
                            st.session_state.interviews.get(
                                selected_candidate,
                                [],
                            )
                        )

                        evaluation = evaluate_answer(
                         selected_requirement,
                         question_text,
                         answer,
                          json.dumps(
        previous_context,
        default=str,
    ),
)

                        st.session_state.last_evaluation = (
                            evaluation
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Evaluation error: {e}"
                        )

        if st.session_state.last_evaluation is not None:

            evaluation = (
                st.session_state.last_evaluation
            )

            eval_status = getattr(
                evaluation,
                "status",
                "UNCLEAR",
            )

            eval_evidence = getattr(
                evaluation,
                "evidence_found",
                "",
            )

            eval_reasoning = getattr(
                evaluation,
                "reasoning",
                "",
            )

            next_action = getattr(
                evaluation,
                "next_action",
                "",
            )

            follow_up = getattr(
                evaluation,
                "follow_up_question",
                "",
            )

            render_html(
                f"""
                <div class="hf-card">

                    <div class="hf-section-title">
                        Evidence evaluation
                    </div>

                    <div style="
                        margin-top:15px;
                    ">
                        {status_badge(eval_status)}
                    </div>

                    <div class="hf-evidence-box">

                        <div class="hf-evidence-label">
                            Evidence found
                        </div>

                        <div class="hf-evidence-text">
                            {esc(eval_evidence)}
                        </div>

                    </div>

                    <div class="hf-evidence-box">

                        <div class="hf-evidence-label">
                            Reasoning
                        </div>

                        <div class="hf-evidence-text">
                            {esc(eval_reasoning)}
                        </div>

                    </div>

                    <div style="
                        margin-top:14px;
                        color:rgba(226,232,240,.48);
                        font-size:11px;
                    ">
                        Next action:
                        {esc(next_action)}
                    </div>

                </div>
                """
            )

            if st.button(
                "Update Evidence Map",
                use_container_width=True,
                type="primary",
            ):

                try:
                    # Apply the interview evaluation to the current
                    # evidence list.
                    updated_evidence = []

                    for item in evidence:
                        current_requirement_id = getattr(
                            item,
                            "requirement_id",
                            None,
                        )

                        evaluation_requirement_id = getattr(
                            evaluation,
                            "requirement_id",
                            None,
                        )

                        if (
                            evaluation_requirement_id is not None
                            and current_requirement_id == evaluation_requirement_id
                        ):
                            try:
                                updated_item = apply_evaluation(
                                    item,
                                    evaluation,
                                )
                            except TypeError:
                                updated_item = item

                                if hasattr(
                                    evaluation,
                                    "status",
                                ):
                                    updated_item.status = (
                                        evaluation.status
                                    )

                                if hasattr(
                                    evaluation,
                                    "evidence_found",
                                ):
                                    updated_item.evidence = (
                                        evaluation.evidence_found
                                    )

                                if hasattr(
                                    evaluation,
                                    "reasoning",
                                ):
                                    updated_item.reasoning = (
                                        evaluation.reasoning
                                    )

                            updated_evidence.append(
                                updated_item
                            )
                        else:
                            updated_evidence.append(
                                item
                            )

                    candidate["evidence"] = updated_evidence

                    candidate.setdefault(
                        "interview_findings",
                        [],
                    ).append(
                        {
                            "requirement_id": str(
                                requirement_id
                            ),
                            "question": question_text,
                            "answer": answer,
                            "evaluation": {
                                "status": eval_status,
                                "evidence_found": eval_evidence,
                                "reasoning": eval_reasoning,
                            },
                        }
                    )

                    st.session_state.candidates[
                        selected_candidate
                    ] = candidate

                    st.session_state.interviews[
                        selected_candidate
                    ] = candidate.get(
                        "interview_findings",
                        [],
                    )

                    st.session_state.question = None

                    st.session_state.last_evaluation = (
                        None
                    )

                    st.success(
                        "Evidence map updated."
                    )

                    time.sleep(0.4)

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Evidence update error: {e}"
                    )

            if follow_up:

                render_html(
                    f"""
                    <div class="hf-card">

                        <div class="hf-section-title">
                            Follow-up suggested
                        </div>

                        <div class="hf-chat-agent"
                             style="margin-top:15px;">

                            {esc(follow_up)}

                        </div>

                    </div>
                    """
                )


# ============================================================
# FINAL REPORT
# ============================================================

def render_report():

    render_workflow(3)

    render_html(
        """
        <div class="hf-hero" style="padding-bottom:20px;">

            <div class="hf-hero-kicker">
                EVIDENCE-BACKED REPORT
            </div>

            <h1 class="hf-hero-title"
                style="font-size:48px;">
                Final Report
            </h1>

            <div class="hf-hero-description">
                A structured review of candidate evidence,
                unresolved requirements, and interview findings.
            </div>

        </div>
        """
    )

    if not st.session_state.candidates:

        st.info(
            "Run a candidate analysis first."
        )

        return

    candidate_names = list(
        st.session_state.candidates.keys()
    )

    selected = st.selectbox(
        "Candidate",
        candidate_names,
        index=candidate_names.index(
            st.session_state.selected_candidate
        )
        if st.session_state.selected_candidate in candidate_names
        else 0,
        key="report_candidate",
    )

    st.session_state.selected_candidate = selected

    candidate = st.session_state.candidates[
        selected
    ]

    evidence = candidate.get(
        "evidence",
        [],
    )

    role = getattr(
        st.session_state.job,
        "role",
        "Target Role",
    )

    if st.button(
        "✦  Generate Final Report",
        type="primary",
        use_container_width=True,
    ):

        try:

            interview_findings = candidate.get(
                "interview_findings",
                [],
            )

            report = generate_report(
                candidate_name=selected,
                role=role,
                evidence=evidence,
                interview_findings=interview_findings,
            )

            st.session_state.final_report = report

        except Exception as e:

            st.error(
                f"Report generation error: {e}"
            )

    report = st.session_state.final_report

    if report is None:

        render_html(
            """
            <div class="hf-card">

                <div class="hf-agent-wrap">

                    <div class="hf-agent-orb"></div>

                </div>

                <div style="
                    text-align:center;
                    color:rgba(226,232,240,.48);
                    font-size:12px;
                ">
                    Generate the report to assemble
                    the evidence trail.
                </div>

            </div>
            """
        )

        return

    report_name = report.get(
    "candidate_name",
    selected,
)

    report_role = report.get(
    "role",
    role,
)

    summary = report.get(
    "summary",
    "",
)

    strengths = report.get(
    "strengths",
    [],
)

    unresolved_items = report.get(
    "unresolved_items",
    [],
)

    interview_findings = report.get(
    "interview_findings",
    [],
)
    render_html(
        f"""
        <div class="hf-report-header">

            <div class="hf-report-name">
                {esc(report_name)}
            </div>

            <div class="hf-report-role">
                {esc(report_role)}
            </div>

        </div>
        """
    )

    render_html(
        f"""
        <div class="hf-card">

            <div class="hf-section-title">
                Executive summary
            </div>

            <div class="hf-reasoning"
                 style="
                    font-size:14px;
                    margin-top:15px;
                 ">

                {esc(summary)}

            </div>

        </div>
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        render_html(
            """
            <div class="hf-card">

                <div class="hf-section-title">
                    Evidence-backed strengths
                </div>

            </div>
            """
        )

        if strengths:

            for strength in strengths:

                render_html(
                    f"""
                    <div class="hf-card">

                        <div style="
                            color:#86efac;
                            font-size:14px;
                            line-height:1.6;
                        ">
                            ✓ {esc(strength)}
                        </div>

                    </div>
                    """
                )

        else:

            st.info(
                "No strengths were recorded."
            )

    with col2:

        render_html(
            """
            <div class="hf-card">

                <div class="hf-section-title">
                    Open questions
                </div>

            </div>
            """
        )

        if unresolved_items:

            for item in unresolved_items:

                render_html(
                    f"""
                    <div class="hf-card">

                        <div style="
                            color:#fcd34d;
                            font-size:14px;
                            line-height:1.6;
                        ">
                            • {esc(item)}
                        </div>

                    </div>
                    """
                )

        else:

            st.info(
                "No unresolved items were recorded."
            )

    if interview_findings:

        render_html(
            """
            <div class="hf-card">

                <div class="hf-section-title">
                    Interview findings
                </div>

                <div class="hf-section-subtitle">
                    Evidence gathered during targeted questioning.
                </div>

            </div>
            """
        )

        for finding in interview_findings:

            if isinstance(
                finding,
                dict,
            ):

                question = finding.get(
                    "question",
                    "",
                )

                answer = finding.get(
                    "answer",
                    "",
                )

                evaluation = finding.get(
                    "evaluation",
                    {},
                )

                status = evaluation.get(
                    "status",
                    "UNCLEAR",
                )

                reasoning = evaluation.get(
                    "reasoning",
                    "",
                )

            else:

                question = ""

                answer = ""

                status = "UNCLEAR"

                reasoning = str(
                    finding
                )

            render_html(
                f"""
                <div class="hf-card">

                    <div class="hf-chat-agent">

                        <strong>
                            Question
                        </strong>

                        <br><br>

                        {esc(question)}

                    </div>

                    <div class="hf-chat-user">

                        {esc(answer)}

                    </div>

                    <div style="
                        margin-top:15px;
                    ">
                        {status_badge(status)}
                    </div>

                    <div class="hf-reasoning"
                         style="
                            margin-top:12px;
                         ">

                        {esc(reasoning)}

                    </div>

                </div>
                """
            )

    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    try:

        report_dict = report

        report_json = json.dumps(
            report_dict,
            indent=2,
            default=str,
        )

        st.download_button(
            "Download Evidence Report JSON",
            data=report_json,
            file_name=(
                f"{selected}_hireflow_report.json"
            ),
            mime="application/json",
            use_container_width=True,
        )

    except Exception as e:

        st.warning(
            f"Could not prepare report download: {e}"
        )


# ============================================================
# MAIN APPLICATION ROUTER
# ============================================================

def main():

    # Render background first.
    render_universe()

    # Render global HireFlow styling.
    render_global_style()

    # Render sidebar navigation.
    render_sidebar()

    # Route pages.
    page = st.session_state.page

    if page == "Dashboard":

        render_dashboard()

    elif page == "Evidence":

        render_evidence()

    elif page == "Interview Agent":

        render_interview()

    elif page == "Final Report":

        render_report()

    else:

        st.session_state.page = "Dashboard"

        render_dashboard()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
