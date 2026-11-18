import streamlit as st
import pandas as pd
from engine import SocialPost, resolve_attribution

# 1. Page Configuration & Custom Dark Theme Styling
st.set_page_config(
    page_title="ReplyCorp — Lurker Engine V2",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #09090B;
        color: #F4F4F5;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background-color: #111114;
        border-bottom: 1px solid #27272A;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    .nav-title {
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #FAFAFA;
    }
    .live-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        color: #10B981;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }

    /* Founder Banner */
    .founder-banner {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.12) 0%, rgba(16, 185, 129, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-left: 4px solid #6366F1;
        padding: 14px 20px;
        border-radius: 8px;
        color: #E4E4E7;
        font-size: 0.92rem;
        margin-bottom: 20px;
    }

    .metric-card {
        background-color: #111114;
        border: 1px solid #27272A;
        padding: 16px 18px;
        border-radius: 10px;
        text-align: left;
    }
    .metric-label {
        font-size: 0.74rem;
        color: #A1A1AA;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .metric-sub {
        font-size: 0.74rem;
        color: #10B981;
        margin-top: 4px;
    }

    .section-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: #FAFAFA;
        margin-bottom: 14px;
        border-left: 3px solid #6366F1;
        padding-left: 10px;
    }

    .pipeline-box {
        background-color: #111114;
        border: 1px solid #27272A;
        padding: 14px;
        border-radius: 8px;
        text-align: center;
    }
    .pipeline-step {
        font-size: 0.72rem;
        color: #6366F1;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .pipeline-text {
        font-size: 0.88rem;
        color: #E4E4E7;
    }

    .timeline-node {
        background-color: #111114;
        border: 1px solid #27272A;
        border-top: 3px solid #10B981;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
    }
    .timeline-time {
        font-size: 0.75rem;
        font-weight: 700;
        color: #10B981;
        margin-bottom: 4px;
    }
    .timeline-event {
        font-size: 0.85rem;
        font-weight: 600;
        color: #FAFAFA;
    }
    .timeline-desc {
        font-size: 0.72rem;
        color: #A1A1AA;
        margin-top: 3px;
    }

    .lb-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #111114;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #27272A;
        margin-bottom: 14px;
    }
    .lb-table th {
        text-align: left;
        padding: 10px 14px;
        font-size: 0.73rem;
        color: #A1A1AA;
        text-transform: uppercase;
        border-bottom: 1px solid #27272A;
        background-color: #16161A;
    }
    .lb-table td {
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #E4E4E7;
        border-bottom: 1px solid #27272A;
    }

    .exec-box {
        background: linear-gradient(135deg, #111114 0%, #16161D 100%);
        border: 1px solid #27272A;
        border-left: 4px solid #10B981;
        padding: 20px;
        border-radius: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Session State Initialization
if "simulated" not in st.session_state:
    st.session_state.simulated = False
if "recovered_revenue" not in st.session_state:
    st.session_state.recovered_revenue = 28450
if "recovered_signups" not in st.session_state:
    st.session_state.recovered_signups = 142
if "lurker_only_signups" not in st.session_state:
    st.session_state.lurker_only_signups = 87
if "avg_confidence" not in st.session_state:
    st.session_state.avg_confidence = 92
if "coverage_after" not in st.session_state:
    st.session_state.coverage_after = 92
if "selected_post_idx" not in st.session_state:
    st.session_state.selected_post_idx = 0
if "collision_mode" not in st.session_state:
    st.session_state.collision_mode = False

# Mock Database of Passive Exposure Posts + Paired Realistic Onboarding Surveys
posts_db = [
    SocialPost(
        post_id="post_01",
        platform="X / Twitter",
        author="@david_saas",
        post_text="Just migrated our entire billing pipeline to ReplyCorp for linkless attribution. Finally capturing all that dark social traffic without UTMs.",
        timestamp_mins_ago=9,
        baseline_traffic=12.0,
        current_traffic=54.0,
        engagement_likes=840
    ),
    SocialPost(
        post_id="post_02",
        platform="Reddit (r/SaaS)",
        author="u/growth_geek",
        post_text="How are you guys measuring word-of-mouth signups when users don't click links? We started using ReplyCorp and discovered 40% of our MRR came from unlinked mentions.",
        timestamp_mins_ago=12,
        baseline_traffic=15.0,
        current_traffic=68.0,
        engagement_likes=920
    ),
    SocialPost(
        post_id="post_03",
        platform="LinkedIn",
        author="Sarah Jenkins (VP Growth)",
        post_text="Stop relying solely on UTM parameters. Most B2B buyers lurk on social, read discussions, and type your URL directly into Google later. ReplyCorp solves this exact blind spot.",
        timestamp_mins_ago=15,
        baseline_traffic=10.0,
        current_traffic=42.0,
        engagement_likes=610
    )
]

paired_surveys = {
    "post_01": "Saw david_saas post on twitter about migrating billing pipeline and linkless attribution for dark social traffic without UTMs.",
    "post_02": "Found your tool mentioned on a reddit saas thread by growth_geek about measuring unlinked word-of-mouth signups and MRR.",
    "post_03": "Read Sarah Jenkins post on LinkedIn about B2B buyers lurking on social without UTM parameters and typing URL directly.",
    "post_viral_reddit": "Saw the viral reddit entrepreneur thread on unlinked attribution recovering direct traffic signups from dark social."
}

if st.session_state.simulated:
    posts_db.insert(0, SocialPost(
        post_id="post_viral_reddit",
        platform="Reddit (r/entrepreneur)",
        author="u/founder_diaries",
        post_text="Unlinked attribution is the biggest growth hack of 2026. Here is how ReplyCorp helped us recover $10k in direct traffic signups from dark social.",
        timestamp_mins_ago=6,
        baseline_traffic=8.0,
        current_traffic=98.0,
        engagement_likes=1240
    ))

top_post = max(posts_db, key=lambda p: p.current_traffic)

# 3. Top Navbar
st.markdown("""
<div class="nav-container">
    <div class="nav-title">ReplyCorp &nbsp;—&nbsp; LURKER ENGINE V2 &nbsp;·&nbsp; PASSIVE DISCOVERY</div>
    <div class="live-badge">
        <div class="pulse-dot"></div>
        ACTIVE PASSIVE LISTENER
    </div>
</div>
""", unsafe_allow_html=True)

# 4. Polish #1: Founder Mode Banner
st.markdown("""
<div class="founder-banner">
    <b>💡 Passive Discovery Engine:</b> Lurker Engine V2 recovers conversions from users who <b>never click a link</b>, <b>never engage publicly</b>, and <b>never connect a social account</b> — bridging the gap beyond deterministic attribution.
</div>
""", unsafe_allow_html=True)

# 5. Action Bar
col_btn1, col_btn2, col_spacer = st.columns([2, 2, 3])
with col_btn1:
    if st.button("🚀 Simulate Viral Reddit Thread", use_container_width=True):
        st.session_state.recovered_revenue += 1450
        st.session_state.recovered_signups += 15
        st.session_state.lurker_only_signups += 12
        st.session_state.avg_confidence = 95
        st.session_state.coverage_after = 94
        st.session_state.simulated = True
        st.session_state.selected_post_idx = 0
        st.session_state.collision_mode = False
        st.rerun()

with col_btn2:
    if st.button("⚡ Test 2-Post Collision", use_container_width=True):
        st.session_state.collision_mode = True
        st.rerun()

st.write("")

# 6. 5 KPI Cards (Including Polish #3: Attribution Coverage Lift)
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Recovered Revenue</div>
        <div class="metric-value">${st.session_state.recovered_revenue:,}</div>
        <div class="metric-sub">+28.4% dark social lift</div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Recovered Signups</div>
        <div class="metric-value">{st.session_state.recovered_signups}</div>
        <div class="metric-sub">{st.session_state.lurker_only_signups} Zero-Click Lurkers</div>
    </div>
    """, unsafe_allow_html=True)
with kpi3:
    lift_val = st.session_state.coverage_after - 71
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Attribution Coverage</div>
        <div class="metric-value">{st.session_state.coverage_after}%</div>
        <div class="metric-sub">Before V2: 71% (+{lift_val}% Lift)</div>
    </div>
    """, unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Top Peak Driver</div>
        <div class="metric-value">{top_post.author}</div>
        <div class="metric-sub">{top_post.current_traffic} visits/hr spike</div>
    </div>
    """, unsafe_allow_html=True)
with kpi5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Match Confidence</div>
        <div class="metric-value">{st.session_state.avg_confidence}%</div>
        <div class="metric-sub">3-Signal Validation</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 7. Revenue Recovery Timeline
st.markdown('<div class="section-header">Live Revenue Recovery Timeline (Single Lurker Journey)</div>', unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.columns(5)
timeline_steps = [
    ("10:00 AM", "Post Published", "Unlinked post goes live on X/Reddit"),
    ("10:08 AM", "Engagement Spike", "Replies & impressions accelerate 4.2x"),
    ("10:18 AM", "Direct Traffic Surge", "Unattributed visits jump +310%"),
    ("10:25 AM", "Passive Signup", "Lurker signs up (0 clicks, 0 UTMs)"),
    ("10:29 AM", "Paid Conversion", "$199/mo plan attributed @ 94% conf.")
]
for col, (t_time, t_title, t_desc) in zip([t1, t2, t3, t4, t5], timeline_steps):
    with col:
        st.markdown(f"""
        <div class="timeline-node">
            <div class="timeline-time">{t_time}</div>
            <div class="timeline-event">{t_title}</div>
            <div class="timeline-desc">{t_desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.markdown("---")

# 8. 7-Day Revenue Recovery Trend + Top Attribution Drivers & Creator Chart (Polish #2)
col_trend, col_leader = st.columns([1.1, 1.1], gap="large")

with col_trend:
    st.markdown('<div class="section-header">Recovered Revenue Trend (Last 7 Days)</div>', unsafe_allow_html=True)
    trend_df = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Recovered Revenue ($)": [3200, 4100, 5400, 6800, 8950, 10200, 12400]
    }).set_index("Day")
    st.bar_chart(trend_df, height=280)

with col_leader:
    st.markdown('<div class="section-header">Top Attribution Drivers & $ Per Creator</div>', unsafe_allow_html=True)
    st.markdown("""
    <table class="lb-table">
        <thead>
            <tr>
                <th>Creator</th>
                <th>Channel</th>
                <th>Lurker Signups</th>
                <th>Recovered Rev</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>u/growth_geek</b></td>
                <td>Reddit (r/SaaS)</td>
                <td>54</td>
                <td style="color:#10B981; font-weight:700;">$11,200</td>
            </tr>
            <tr>
                <td><b>@david_saas</b></td>
                <td>X / Twitter</td>
                <td>46</td>
                <td style="color:#10B981; font-weight:700;">$9,450</td>
            </tr>
            <tr>
                <td><b>Sarah Jenkins</b></td>
                <td>LinkedIn</td>
                <td>28</td>
                <td style="color:#10B981; font-weight:700;">$5,100</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    
    creator_df = pd.DataFrame({
        "Creator": ["u/growth_geek", "@david_saas", "Sarah Jenkins"],
        "Revenue ($)": [11200, 9450, 5100]
    }).set_index("Creator")
    st.bar_chart(creator_df, height=160)

st.write("")
st.markdown("---")

# 9. 3-Step Visual Pipeline
st.markdown('<div class="section-header">Lurker Attribution Pipeline State</div>', unsafe_allow_html=True)
pipe1, pipe2, pipe3 = st.columns(3)
with pipe1:
    st.markdown("""
    <div class="pipeline-box">
        <div class="pipeline-step">Step 1</div>
        <div class="pipeline-text"><b>Passive Exposure</b><br>User reads unlinked post on X/Reddit (0 clicks)</div>
    </div>
    """, unsafe_allow_html=True)
with pipe2:
    st.markdown("""
    <div class="pipeline-box">
        <div class="pipeline-step">Step 2</div>
        <div class="pipeline-text"><b>Onboarding Survey</b><br>User types: "Found via saas thread on reddit"</div>
    </div>
    """, unsafe_allow_html=True)
with pipe3:
    st.markdown("""
    <div class="pipeline-box">
        <div class="pipeline-step">Step 3</div>
        <div class="pipeline-text"><b>Recovered Outcome</b><br>Engine attributes signup with 94% confidence</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("---")

# 10. 2-Column Split: Post Feed + Engine Resolution Inspector
col_left, col_right = st.columns([1.1, 1.3], gap="large")

with col_left:
    st.markdown('<div class="section-header">Live Revenue-Driving Posts</div>', unsafe_allow_html=True)
    st.caption("Click any post to inspect engine resolution and passive recovery telemetry.")

    for idx, post in enumerate(posts_db):
        is_selected = (st.session_state.selected_post_idx == idx)
        border_color = "#6366F1" if is_selected else "#27272A"
        bg_color = "#18181B" if is_selected else "#111114"

        col_card, col_action = st.columns([4, 1])
        with col_card:
            st.markdown(f"""
            <div style="background-color: {bg_color}; border: 1px solid {border_color}; padding: 14px; border-radius: 8px; margin-bottom: 10px;">
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#A1A1AA; margin-bottom:4px;">
                    <span><b>{post.platform}</b> • {post.author}</span>
                    <span>{post.timestamp_mins_ago}m ago</span>
                </div>
                <div style="font-size:0.85rem; color:#E4E4E7; margin-bottom:8px;">"{post.post_text}"</div>
                <div style="font-size:0.7rem; color:#10B981; font-weight:600;">⚡ Traffic Spike: {post.current_traffic} visits/hr (Baseline: {post.baseline_traffic})</div>
            </div>
            """, unsafe_allow_html=True)
        with col_action:
            st.write("")
            if st.button("Inspect", key=f"inspect_{idx}", use_container_width=True):
                st.session_state.selected_post_idx = idx
                st.session_state.collision_mode = False
                st.rerun()

with col_right:
    st.markdown('<div class="section-header">Engine Resolution & Signal Breakdown</div>', unsafe_allow_html=True)

    current_post = posts_db[st.session_state.selected_post_idx]
    matched_survey = paired_surveys.get(current_post.post_id, "Saw your product discussed in a saas community post about linkless dark social attribution.")

    if st.session_state.collision_mode:
        res = resolve_attribution(posts_db[:2], matched_survey, current_post.timestamp_mins_ago, has_graph_match=True)
        st.warning("⚡ **Collision Test Active:** Evaluated 2 simultaneous posts within 15-minute window. Anomaly traffic lift isolated the true driver.")
    else:
        res = resolve_attribution([current_post], matched_survey, current_post.timestamp_mins_ago, has_graph_match=True)

    winning = res["winning_post"]
    breakdown = res["signal_breakdown"]

    st.markdown(f"""
    <div style="background-color: #111114; border: 1px solid #27272A; padding: 20px; border-radius: 10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <div>
                <div style="font-size:0.75rem; color:#A1A1AA; text-transform:uppercase;">Attribution Confidence</div>
                <div style="font-size:1.75rem; font-weight:700; color:#10B981;">{res['confidence_score']}% Match</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.75rem; color:#A1A1AA;">Winning Source</div>
                <div style="font-size:0.95rem; font-weight:600; color:#FAFAFA;">{winning.platform if winning else 'N/A'} ({winning.author if winning else ''})</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("**3-Signal Confidence Meters:**")
    st.progress(breakdown["semantic"] / 50, text=f"1. Semantic Intent Overlap (Score: {breakdown['semantic']}/50)")
    st.progress(breakdown["time_decay"] / 35, text=f"2. Temporal Decay & Traffic Lift (Score: {breakdown['time_decay']}/35)")
    st.progress(breakdown["graph_bonus"] / 15, text=f"3. Latent Graph Proximity (Bonus: {breakdown['graph_bonus']}/15)")

    st.markdown("---")
    st.markdown("##### Why This Attribution Was Accepted:")
    for reason in res["acceptance_reasons"]:
        st.markdown(f"✔ {reason}")

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.markdown("---")

# 11. Executive Summary Footer Block
st.markdown('<div class="section-header">Executive Attribution Summary</div>', unsafe_allow_html=True)
lift_exec = st.session_state.coverage_after - 71
st.markdown(f"""
<div class="exec-box">
    <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 16px; text-align:center;">
        <div>
            <div style="font-size:0.75rem; color:#A1A1AA; text-transform:uppercase;">Recovered Revenue</div>
            <div style="font-size:1.35rem; font-weight:700; color:#FFFFFF; margin-top:4px;">${st.session_state.recovered_revenue:,}</div>
        </div>
        <div>
            <div style="font-size:0.75rem; color:#A1A1AA; text-transform:uppercase;">Recovered Signups</div>
            <div style="font-size:1.35rem; font-weight:700; color:#FFFFFF; margin-top:4px;">{st.session_state.recovered_signups}</div>
        </div>
        <div>
            <div style="font-size:0.75rem; color:#A1A1AA; text-transform:uppercase;">Without Social Login</div>
            <div style="font-size:1.35rem; font-weight:700; color:#10B981; margin-top:4px;">{st.session_state.lurker_only_signups}</div>
        </div>
        <div>
            <div style="font-size:0.75rem; color:#A1A1AA; text-transform:uppercase;">Average Confidence</div>
            <div style="font-size:1.35rem; font-weight:700; color:#FFFFFF; margin-top:4px;">{st.session_state.avg_confidence}%</div>
        </div>
        <div>
            <div style="font-size:0.75rem; color:#A1A1AA; text-transform:uppercase;">Coverage Lift</div>
            <div style="font-size:1.35rem; font-weight:700; color:#6366F1; margin-top:4px;">+{lift_exec}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)