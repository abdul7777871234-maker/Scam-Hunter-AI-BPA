import streamlit as st

# Streamlit deployment refresh: working theme source.

ACCENTS = {
    "Cyan": "#22D3EE",
    "Electric Blue": "#3B82F6",
    "Emerald": "#10B981",
    "Violet": "#8B5CF6",
    "Rose": "#F43F5E",
    "Amber": "#F59E0B",
    "Sunset": "#F97316",
}

DARK = {
    "BG": "#050811", "PANEL": "#0B1120", "PANEL2": "#0F172A",
    "INPUT": "#111827", "TEXT": "#F8FAFC", "MUTED": "#A7B3C7",
    "SELECT_BG": "#0F172A", "SELECT_TEXT": "#F8FAFC", "SELECT_BORDER": "#334155", "SELECT_ARROW": "#94A3B8", "SELECT_ICON_BG": "#0F172A",
    "BORDER": "rgba(148,163,184,0.14)", "HOVER": "#141C2E",
    "MENU": "#0B1120", "MENUHOVER": "#172033", "SCHEME": "dark",
}
LIGHT = {
    "BG": "#F8FAFC", "PANEL": "#FFFFFF", "PANEL2": "#F1F5F9",
    "INPUT": "#FFFFFF", "TEXT": "#0F172A", "MUTED": "#64748B",
    "SELECT_BG": "#FFFFFF", "SELECT_TEXT": "#0F172A", "SELECT_ARROW": "#334155", "SELECT_BORDER": "#CBD5E1",
    "BORDER": "rgba(15,23,42,0.14)", "HOVER": "#E8EEF7",
    "MENU": "#FFFFFF", "MENUHOVER": "#EEF4FA", "SCHEME": "light",
}

# Tokens are written @@NAME@@ so one token can never be a substring of another
# (the old .replace("HOVER") also rewrote the inside of "MENUHOVER").
CSS = """
<style>
:root{
  --sh-accent:@@ACCENT@@; --sh-bg:@@BG@@; --sh-panel:@@PANEL@@; --sh-panel2:@@PANEL2@@;
  --sh-input:@@INPUT@@; --sh-text:@@TEXT@@; --sh-muted:@@MUTED@@; --sh-border:@@BORDER@@;
  --sh-hover:@@HOVER@@; --sh-menu:@@MENU@@; --sh-menu-hover:@@MENUHOVER@@;
  --sh-input-bg:@@INPUT@@; --sh-input-text:@@TEXT@@; --sh-input-arrow:@@MUTED@@;
  --sh-select-bg:@@SELECT_BG@@; --sh-select-text:@@SELECT_TEXT@@; --sh-select-arrow:@@SELECT_ARROW@@; --sh-select-border:@@SELECT_BORDER@@;
  --sh-scheme:@@SCHEME@@;\n  color-scheme:var(--sh-scheme);
}


/* Delete-history confirmation dialog: keep text and surface theme-aware. */
div[role="dialog"],
div[role="dialog"] > div,
div[role="dialog"] [data-testid="stModal"],
div[role="dialog"] [data-testid="stModal"] > div {
  background:var(--sh-panel)!important;
  background-color:var(--sh-panel)!important;
  color:var(--sh-text)!important;
  border-color:var(--sh-border)!important;
  color-scheme:var(--sh-scheme)!important;
}
div[role="dialog"] p,
div[role="dialog"] span,
div[role="dialog"] label,
div[role="dialog"] [data-testid="stMarkdownContainer"],
div[role="dialog"] [data-testid="stMarkdownContainer"] * {
  color:var(--sh-text)!important;
  -webkit-text-fill-color:var(--sh-text)!important;
}
div[role="dialog"] button {
  color:var(--sh-text)!important;
  border-color:var(--sh-border)!important;
}

/* GLOBAL */
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
  background:var(--sh-bg)!important; color:var(--sh-text)!important; color-scheme:var(--sh-scheme)!important;}
.stApp{background:radial-gradient(circle at 50% -10%,@@ACCENT@@18 0,transparent 32%),var(--sh-bg)!important;}
.block-container{max-width:1320px!important;padding-top:4.5rem!important;padding-bottom:8rem!important;}
* {box-sizing:border-box;}

/* HEADER */
header,[data-testid="stHeader"]{background:var(--sh-bg)!important;background-color:var(--sh-bg)!important;
  border-bottom:1px solid var(--sh-border)!important;box-shadow:none!important;}
[data-testid="stHeader"] *,[data-testid="stToolbar"] *{color:var(--sh-text)!important;}
[data-testid="stHeader"] button,[data-testid="stToolbar"] button,[data-testid="stMainMenu"] button{
  background:transparent!important;border:0!important;box-shadow:none!important;color:var(--sh-text)!important;}
[data-testid="stHeader"] button:hover,[data-testid="stToolbar"] button:hover{
  background:var(--sh-hover)!important;color:var(--sh-accent)!important;border-radius:10px!important;}
[data-testid="stHeader"] svg,[data-testid="stToolbar"] svg{color:var(--sh-text)!important;fill:currentColor!important;}
[data-testid="stDecoration"]{display:none!important;}

/* SIDEBAR */
section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div,section[data-testid="stSidebar"]>div>div{
  background:var(--sh-panel)!important;color:var(--sh-text)!important;}
section[data-testid="stSidebar"]{border-right:1px solid var(--sh-border)!important;}
section[data-testid="stSidebar"] *{color:var(--sh-text);}
section[data-testid="stSidebar"] hr{border-color:var(--sh-border)!important;}
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *{color:var(--sh-muted)!important;}

.sidebar-brand{width:100%;display:flex;align-items:center;gap:12px;padding:8px 2px 14px;}
.sidebar-brand-logo{width:48px;height:48px;min-width:48px;display:flex;align-items:center;justify-content:center;
  border-radius:14px;background:@@ACCENT@@18;border:1px solid @@ACCENT@@66;color:var(--sh-accent)!important;
  font-size:23px;line-height:1;box-shadow:0 0 24px @@ACCENT@@20;}
.sidebar-brand-text{min-width:0;flex:1;}
.sidebar-brand-name{color:var(--sh-text)!important;font-size:18px;line-height:1.1;font-weight:800;white-space:nowrap;}
.sidebar-brand-name span{color:var(--sh-accent)!important;}
.sidebar-brand-subtitle{margin-top:4px;color:var(--sh-muted)!important;font-size:10px;white-space:nowrap;}
.sidebar-section-title{color:var(--sh-muted)!important;font-size:10px;font-weight:800;letter-spacing:1.4px;
  text-transform:uppercase;margin:8px 0;}

[data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebarCollapsedControl"] button{
  background:var(--sh-panel)!important;color:var(--sh-text)!important;border:1px solid var(--sh-border)!important;
  box-shadow:none!important;border-radius:10px!important;}
[data-testid="stSidebarCollapseButton"] svg,[data-testid="stSidebarCollapsedControl"] svg{
  color:var(--sh-text)!important;fill:currentColor!important;}
[data-testid="stSidebarCollapseButton"] button:hover,[data-testid="stSidebarCollapsedControl"] button:hover{
  background:var(--sh-hover)!important;color:var(--sh-accent)!important;border-color:var(--sh-accent)!important;}

/* SELECTBOX LABELS */
[data-testid="stSelectbox"] label,[data-testid="stSelectbox"] label p{color:var(--sh-text)!important;font-weight:700!important;}

/* BUTTONS + POPOVERS */
div.stButton>button,[data-testid="stPopover"] button,button[data-testid="stPopoverButton"]{
  min-height:40px;background:var(--sh-panel)!important;color:var(--sh-text)!important;
  border:1px solid var(--sh-border)!important;border-radius:11px!important;box-shadow:none!important;}
div.stButton>button:hover,[data-testid="stPopover"] button:hover,button[data-testid="stPopoverButton"]:hover{
  background:var(--sh-hover)!important;color:var(--sh-accent)!important;border-color:var(--sh-accent)!important;}
div.stButton>button p{color:inherit!important;}

/* CHAT INPUT */
[data-testid="stBottom"],[data-testid="stBottom"]>div,[data-testid="stBottomBlockContainer"]{background:var(--sh-bg)!important;}
[data-testid="stChatInput"]>div{background:var(--sh-panel)!important;border:1px solid var(--sh-border)!important;border-radius:18px!important;}
[data-testid="stChatInput"] textarea{background:transparent!important;color:var(--sh-text)!important;
  -webkit-text-fill-color:var(--sh-text)!important;caret-color:var(--sh-accent)!important;}
[data-testid="stChatInput"] textarea::placeholder{color:var(--sh-muted)!important;-webkit-text-fill-color:var(--sh-muted)!important;}
[data-testid="stChatInput"] button{background:var(--sh-panel2)!important;color:var(--sh-muted)!important;border:0!important;}
[data-testid="stChatInput"] svg{color:inherit!important;fill:currentColor!important;}
[data-testid="stChatInput"] button:hover{color:var(--sh-accent)!important;}

/* CHAT MESSAGES */
[data-testid="stChatMessage"]{background:transparent!important;}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li{color:var(--sh-text)!important;}

/* HERO */
.hero{border:1px solid var(--sh-border);border-radius:24px;padding:28px 24px;text-align:center;
  background:linear-gradient(145deg,var(--sh-panel),@@ACCENT@@0D);box-shadow:0 20px 60px rgba(0,0,0,.08);}
.hero-logo{width:54px;height:54px;margin:0 auto;display:flex;align-items:center;justify-content:center;
  border:1px solid var(--sh-accent);border-radius:20px;font-size:25px;line-height:1;box-shadow:0 0 28px @@ACCENT@@44;}
.hero-title{margin-top:12px;font-size:38px;line-height:1.02;font-weight:800;letter-spacing:-2px;color:var(--sh-text)!important;}
.hero-title span{color:var(--sh-accent)!important;}
.hero-description{max-width:760px;margin:9px auto 0;color:var(--sh-muted)!important;font-size:14px;line-height:1.45;}
.hero-badge{display:inline-flex;align-items:center;gap:7px;margin-top:11px;padding:6px 12px;border:1px solid var(--sh-accent);
  border-radius:999px;color:var(--sh-accent)!important;font-size:11px;font-weight:700;background:@@ACCENT@@0F;}

/* SOURCE CARDS */
.source-card,.source{border:1px solid var(--sh-border);border-left:3px solid var(--sh-accent);border-radius:12px;
  padding:15px;margin:10px 0;background:var(--sh-panel)!important;color:var(--sh-text)!important;}
.source-header{display:flex;align-items:flex-start;gap:11px;}
.source-icon{width:34px;height:34px;min-width:34px;display:flex;align-items:center;justify-content:center;
  border-radius:9px;background:@@ACCENT@@12;color:var(--sh-accent)!important;}
.source-title{color:var(--sh-text)!important;font-weight:750;font-size:14px;}
.source-meta{margin-top:3px;color:var(--sh-muted)!important;font-size:11px;}
.source-excerpt{margin-top:12px;padding-top:11px;border-top:1px solid var(--sh-border);
  color:var(--sh-muted)!important;font-size:13px;line-height:1.65;}

/* PIPELINE */
.pipeline-card{padding:16px;margin:8px 0;border:1px solid var(--sh-border);border-radius:16px;background:var(--sh-panel);}
.pipeline-step{display:flex;align-items:center;gap:12px;padding:10px 12px;margin:6px 0;border:1px solid var(--sh-border);
  border-radius:12px;background:var(--sh-panel2);}
.pipeline-icon{width:30px;height:30px;min-width:30px;display:flex;align-items:center;justify-content:center;border-radius:9px;
  background:@@ACCENT@@18;border:1px solid @@ACCENT@@44;color:var(--sh-accent)!important;}
.pipeline-text{flex:1;}
.pipeline-name{color:var(--sh-text)!important;font-weight:700;font-size:13px;}
.pipeline-status{color:var(--sh-muted)!important;font-size:11px;}
.pipeline-arrow{text-align:center;color:var(--sh-muted)!important;}

/* VERDICT */
.verdict-card{display:flex;align-items:center;gap:14px;padding:14px 16px;margin-bottom:12px;
  border:1px solid var(--verdict-color);border-left:4px solid var(--verdict-color);border-radius:14px;
  background:var(--sh-panel)!important;color:var(--sh-text)!important;}
.verdict-dot{width:15px;height:15px;min-width:15px;border-radius:50%;background:var(--verdict-color);box-shadow:0 0 14px var(--verdict-color);}
.verdict-title{color:var(--sh-text)!important;font-weight:700;}
.verdict-note{margin-top:3px;color:var(--sh-muted)!important;font-size:13px;}

/* MISC */
.muted{color:var(--sh-muted)!important;}
.footer-card,.card{width:100%;margin-top:28px;padding:18px 20px;text-align:center;border:1px solid var(--sh-border);
  border-radius:16px;background:var(--sh-panel)!important;color:var(--sh-muted)!important;}
.footer-card *{color:var(--sh-muted)!important;}
.footer-title{color:var(--sh-text)!important;font-size:12px;font-weight:700;}
.footer-description{margin-top:6px;color:var(--sh-muted)!important;font-size:11px;line-height:1.55;}
.sidebar-status-card{display:flex;align-items:center;gap:8px;padding:9px 10px;border:1px solid var(--sh-border);
  border-radius:10px;background:var(--sh-panel2);color:var(--sh-muted)!important;font-size:11px;}
.sidebar-status-dot{width:7px;height:7px;min-width:7px;border-radius:50%;background:var(--sh-accent);box-shadow:0 0 10px var(--sh-accent);}

[data-testid="stExpander"]{background:var(--sh-panel)!important;border:1px solid var(--sh-border)!important;border-radius:14px!important;}
[data-testid="stExpander"] summary{background:var(--sh-panel)!important;color:var(--sh-text)!important;}
[data-testid="stExpander"] summary *{color:var(--sh-text)!important;}
section[data-testid="stFileUploaderDropzone"]{background:var(--sh-input)!important;border:1px dashed var(--sh-border)!important;border-radius:14px!important;}
section[data-testid="stFileUploaderDropzone"] *{color:var(--sh-text)!important;}

::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:var(--sh-bg);}
::-webkit-scrollbar-thumb{background:var(--sh-border);border-radius:999px;}
::-webkit-scrollbar-thumb:hover{background:var(--sh-accent);}

/* =====================================================================
   
/* CLEAN THEME CONTROL LOCK
   Streamlit/BaseWeb native controls are bound to the active palette. */
html body .stApp input,
html body .stApp textarea,
html body .stApp [data-baseweb="input"],
html body .stApp [data-baseweb="base-input"],
html body .stApp [data-baseweb="textarea"],
html body .stApp [data-baseweb="textarea"] > div,
html body .stApp [data-testid="stTextInput"] input,
html body .stApp [data-testid="stTextArea"] textarea,
html body .stApp [data-testid="stNumberInput"] input,
html body .stApp [data-testid="stDateInput"] input,
html body .stApp [data-testid="stTimeInput"] input {
  background:var(--sh-input)!important;
  background-color:var(--sh-input)!important;
  color:var(--sh-text)!important;
  -webkit-text-fill-color:var(--sh-text)!important;
  border-color:var(--sh-border)!important;
  color-scheme:var(--sh-scheme)!important;
}
html body .stApp [data-testid="stTextInput"] > div,
html body .stApp [data-testid="stTextArea"] > div,
html body .stApp [data-testid="stNumberInput"] > div,
html body .stApp [data-testid="stDateInput"] > div,
html body .stApp [data-testid="stTimeInput"] > div {
  background:var(--sh-input)!important;
  background-color:var(--sh-input)!important;
  border-color:var(--sh-border)!important;
}
html body .stApp section[data-testid="stFileUploaderDropzone"],
html body .stApp [data-testid="stFileUploaderDropzone"] {
  background:var(--sh-input)!important;
  background-color:var(--sh-input)!important;
  color:var(--sh-text)!important;
  border-color:var(--sh-border)!important;
}
html body .stApp [data-testid="stFileUploaderDropzone"] * {
  color:var(--sh-text)!important;
}

/* Sidebar action buttons follow the active palette. */
html body .stApp section[data-testid="stSidebar"] button {
  color:var(--sh-text)!important;
}
html body .stApp section[data-testid="stSidebar"] button:hover {
  color:var(--sh-accent)!important;
}

/* Preserve hero spacing without transforms or negative offsets. */
.hero {
  position:relative!important;
  height:auto!important;
  min-height:0!important;
  margin-top:0!important;
  margin-bottom:1.5rem!important;
  padding-bottom:42px!important;
  overflow:visible!important;
  transform:none!important;
}
.hero + div { margin-top:0!important; }
.stat-card {
  position:relative!important;
  transform:none!important;
  margin-top:0!important;
  overflow:hidden!important;
}
@media (max-width:900px) {
  .hero { margin-bottom:1.25rem!important; padding:30px 20px!important; }
  .hero-title { font-size:36px!important; letter-spacing:-1.5px!important; }
}

/* =====================================================================
   PREMIUM UI POLISH — visual only
   No layout/state/backend behavior is changed.
   ===================================================================== */

/* Page rhythm + typography */
html body .stApp {
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif!important;
  letter-spacing: -0.01em;
}
html body .stApp [data-testid="stMain"] {
  padding-left: 0!important;
  padding-right: 0!important;
}
.block-container {
  max-width: 1380px!important;
  padding-left: 28px!important;
  padding-right: 28px!important;
}

/* Softer global text hierarchy */
.stMarkdown p, .stMarkdown li {
  line-height: 1.68;
}
h1, h2, h3 {
  color:var(--sh-text)!important;
  letter-spacing:-0.025em!important;
}
hr {
  border-color:var(--sh-border)!important;
}

/* Premium sidebar */
section[data-testid="stSidebar"] > div {
  padding: 1rem .9rem 1.25rem!important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  gap: .55rem!important;
}
.sidebar-brand {
  padding: 7px 4px 18px!important;
  margin-bottom: 4px!important;
}
.sidebar-brand-logo {
  width:50px!important;
  height:50px!important;
  border-radius:16px!important;
  background:linear-gradient(145deg, @@ACCENT@@22, @@ACCENT@@08)!important;
  box-shadow:0 8px 28px @@ACCENT@@18!important;
}
.sidebar-section-title {
  margin:15px 2px 7px!important;
  font-size:9px!important;
  letter-spacing:1.8px!important;
}

/* Sidebar controls — cleaner spacing and tactile hover */
html body .stApp section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
  margin-bottom:4px!important;
}
html body .stApp section[data-testid="stSidebar"] [data-testid="stSelectbox"] label {
  margin-bottom:5px!important;
  font-size:11px!important;
  letter-spacing:.01em!important;
}
html body .stApp section[data-testid="stSidebar"] [data-baseweb="select"] {
  transition:background .16s ease,border-color .16s ease,box-shadow .16s ease,transform .16s ease!important;
}
html body .stApp section[data-testid="stSidebar"] [data-baseweb="select"]:hover {
  box-shadow:0 0 0 3px @@ACCENT@@10!important;
}
html body .stApp section[data-testid="stSidebar"] button {
  transition:background .16s ease,border-color .16s ease,color .16s ease,transform .16s ease!important;
}
html body .stApp section[data-testid="stSidebar"] button:hover {
  transform:translateY(-1px)!important;
}

/* Stat strip */
.stat-card {
  background:linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  border:1px solid var(--sh-border)!important;
  border-radius:16px!important;
  box-shadow:0 10px 30px rgba(15,23,42,.06)!important;
  transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease!important;
}
.stat-card:hover {
  transform:translateY(-2px)!important;
  border-color:@@ACCENT@@55!important;
  box-shadow:0 14px 36px rgba(15,23,42,.10)!important;
}

/* Hero refinement */
.hero {
  border-radius:26px!important;
  background:
    radial-gradient(circle at 50% 0%,@@ACCENT@@18 0,transparent 42%),
    linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 18px 55px rgba(15,23,42,.08)!important;
}
.hero-logo {
  background:linear-gradient(145deg,@@ACCENT@@22,transparent)!important;
}
.hero-title {
  font-size:42px!important;
  letter-spacing:-2.4px!important;
}
.hero-description {
  max-width:820px!important;
  font-size:14px!important;
  line-height:1.65!important;
}

/* Chat surfaces */
html body .stApp [data-testid="stChatMessage"] {
  padding:12px 4px!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
  border:1px solid var(--sh-border)!important;
  border-radius:18px!important;
  padding:13px 17px!important;
  background:var(--sh-panel)!important;
  box-shadow:0 8px 28px rgba(15,23,42,.045)!important;
}
html body .stApp [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
  background:linear-gradient(145deg,var(--sh-panel),@@ACCENT@@08)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
  border:1px solid var(--sh-border)!important;
  border-radius:12px!important;
  background:var(--sh-panel2)!important;
}
html body .stApp [data-testid="stChatMessage"] p:last-child {
  margin-bottom:0!important;
}

/* Risk / verdict / evidence cards */
.verdict-card {
  border-radius:17px!important;
  padding:16px 18px!important;
  background:linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 10px 30px rgba(15,23,42,.06)!important;
}
.source-card,.source {
  border-radius:15px!important;
  background:linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 7px 24px rgba(15,23,42,.045)!important;
  transition:transform .16s ease,border-color .16s ease!important;
}
.source-card:hover,.source:hover {
  transform:translateY(-1px)!important;
  border-color:@@ACCENT@@55!important;
}

/* Investigation pipeline */
.pipeline-card {
  padding:12px!important;
  border-radius:18px!important;
  background:linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
}
.pipeline-step {
  min-height:52px!important;
  margin:5px 0!important;
  border-radius:13px!important;
  background:var(--sh-panel)!important;
  transition:border-color .16s ease,transform .16s ease!important;
}
.pipeline-step:hover {
  border-color:@@ACCENT@@55!important;
  transform:translateX(2px)!important;
}
.pipeline-arrow {
  opacity:.65!important;
  font-size:12px!important;
}

/* Expanders */
html body .stApp [data-testid="stExpander"] {
  overflow:hidden!important;
  border-radius:16px!important;
  background:var(--sh-panel)!important;
  box-shadow:0 7px 24px rgba(15,23,42,.035)!important;
}
html body .stApp [data-testid="stExpander"] summary {
  min-height:48px!important;
  padding:0 15px!important;
  transition:background .16s ease!important;
}
html body .stApp [data-testid="stExpander"] summary:hover {
  background:var(--sh-hover)!important;
}

/* Chat input — primary interaction */
html body .stApp [data-testid="stChatInput"] {
  padding-left:0!important;
  padding-right:0!important;
}
html body .stApp [data-testid="stChatInput"] > div {
  min-height:58px!important;
  border-radius:20px!important;
  background:linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 12px 36px rgba(15,23,42,.10)!important;
  transition:border-color .16s ease,box-shadow .16s ease!important;
}
html body .stApp [data-testid="stChatInput"] > div:focus-within {
  border-color:@@ACCENT@@88!important;
  box-shadow:0 0 0 3px @@ACCENT@@12,0 14px 38px rgba(15,23,42,.12)!important;
}
html body .stApp [data-testid="stChatInput"] textarea {
  font-size:14px!important;
  line-height:1.5!important;
}

/* Buttons */
html body .stApp div.stButton > button,
html body .stApp [data-testid="stDownloadButton"] button {
  border-radius:11px!important;
  font-weight:650!important;
  transition:transform .16s ease,background .16s ease,border-color .16s ease,box-shadow .16s ease!important;
}
html body .stApp div.stButton > button:hover,
html body .stApp [data-testid="stDownloadButton"] button:hover {
  transform:translateY(-1px)!important;
  box-shadow:0 7px 20px @@ACCENT@@14!important;
}

/* File uploader */
html body .stApp [data-testid="stFileUploaderDropzone"] {
  min-height:100px!important;
  border-radius:16px!important;
  background:linear-gradient(145deg,var(--sh-input),var(--sh-panel2))!important;
  transition:border-color .16s ease,background .16s ease!important;
}
html body .stApp [data-testid="stFileUploaderDropzone"]:hover {
  border-color:@@ACCENT@@77!important;
  background:var(--sh-hover)!important;
}

/* Warning/info/success messages */
html body .stApp [data-testid="stAlert"] {
  border-radius:15px!important;
  border:1px solid var(--sh-border)!important;
  box-shadow:0 7px 24px rgba(15,23,42,.045)!important;
}

/* Download/report control */
html body .stApp [data-testid="stDownloadButton"] button {
  background:var(--sh-panel)!important;
  color:var(--sh-text)!important;
  border:1px solid var(--sh-border)!important;
}
html body .stApp [data-testid="stDownloadButton"] button:hover {
  color:var(--sh-accent)!important;
  border-color:@@ACCENT@@66!important;
}

/* Mobile */
@media (max-width:900px) {
  .block-container {
    padding-left:14px!important;
    padding-right:14px!important;
  }
  .hero-title {
    font-size:34px!important;
    letter-spacing:-1.7px!important;
  }
  html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    padding:11px 13px!important;
    border-radius:15px!important;
  }
}


/* =====================================================================
   3D WORLD-CLASS VISUAL LAYER — visual only
   Premium motion, depth, glass, ambient lighting and 3D interaction.
   No application logic/state/API/RAG behavior is changed.
   ===================================================================== */

/* Animated ambient canvas */
html body .stApp {
  background:
    radial-gradient(circle at 8% 12%, @@ACCENT@@12 0, transparent 25%),
    radial-gradient(circle at 92% 8%, #7C3AED10 0, transparent 24%),
    radial-gradient(circle at 50% 100%, @@ACCENT@@0B 0, transparent 32%),
    var(--sh-bg)!important;
  background-size:140% 140%,130% 130%,150% 150%,100% 100%!important;
  animation:shAmbient 18s ease-in-out infinite alternate!important;
}
@keyframes shAmbient {
  0% { background-position:0% 0%,100% 0%,50% 100%,0 0; }
  50% { background-position:18% 12%,82% 18%,42% 82%,0 0; }
  100% { background-position:5% 22%,96% 5%,58% 92%,0 0; }
}

/* Subtle futuristic grid */
html body .stApp [data-testid="stMain"] {
  position:relative!important;
}
html body .stApp [data-testid="stMain"]::before {
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  z-index:0;
  opacity:.18;
  background-image:
    linear-gradient(@@ACCENT@@08 1px,transparent 1px),
    linear-gradient(90deg,@@ACCENT@@08 1px,transparent 1px);
  background-size:52px 52px;
  mask-image:linear-gradient(to bottom,black,transparent 78%);
  -webkit-mask-image:linear-gradient(to bottom,black,transparent 78%);
}
html body .stApp [data-testid="stMain"] > div {
  position:relative;
  z-index:1;
}

/* Hero becomes the visual centerpiece */
.hero {
  position:relative!important;
  isolation:isolate!important;
  min-height:300px!important;
  overflow:hidden!important;
  border:1px solid @@ACCENT@@35!important;
  background:
    radial-gradient(circle at 50% 18%,@@ACCENT@@18 0,transparent 30%),
    radial-gradient(circle at 12% 90%,#7C3AED10 0,transparent 30%),
    linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:
    0 30px 90px rgba(0,0,0,.18),
    inset 0 1px 0 rgba(255,255,255,.07),
    0 0 70px @@ACCENT@@0B!important;
  transform-style:preserve-3d!important;
  perspective:1000px!important;
}
.hero::before {
  content:"";
  position:absolute;
  width:360px;
  height:360px;
  left:50%;
  top:-190px;
  transform:translateX(-50%);
  border-radius:50%;
  border:1px solid @@ACCENT@@25;
  box-shadow:
    0 0 0 35px @@ACCENT@@05,
    0 0 0 70px @@ACCENT@@04,
    0 0 90px @@ACCENT@@14;
  animation:shOrbit 9s linear infinite!important;
  pointer-events:none;
}
.hero::after {
  content:"";
  position:absolute;
  width:110px;
  height:110px;
  right:8%;
  top:18%;
  border-radius:32px;
  background:
    radial-gradient(circle at 30% 25%,rgba(255,255,255,.30),transparent 22%),
    linear-gradient(145deg,@@ACCENT@@42,@@ACCENT@@08);
  border:1px solid @@ACCENT@@55;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.22),
    0 25px 60px @@ACCENT@@18,
    0 0 45px @@ACCENT@@12;
  transform:rotateX(58deg) rotateZ(38deg);
  animation:shFloat3D 6s ease-in-out infinite!important;
  pointer-events:none;
}
@keyframes shOrbit {
  from { transform:translateX(-50%) rotate(0deg); }
  to { transform:translateX(-50%) rotate(360deg); }
}
@keyframes shFloat3D {
  0%,100% { margin-top:0; transform:rotateX(58deg) rotateZ(38deg) translateZ(0); }
  50% { margin-top:18px; transform:rotateX(70deg) rotateZ(52deg) translateZ(18px); }
}
.hero > * { position:relative!important; z-index:2!important; }
.hero-logo {
  position:relative!important;
  width:76px!important;
  height:76px!important;
  border-radius:24px!important;
  border:1px solid @@ACCENT@@70!important;
  background:
    radial-gradient(circle at 35% 25%,rgba(255,255,255,.24),transparent 22%),
    linear-gradient(145deg,@@ACCENT@@32,@@ACCENT@@08)!important;
  box-shadow:
    0 18px 50px @@ACCENT@@25,
    inset 0 1px 0 rgba(255,255,255,.20)!important;
  transform:translateZ(35px) rotateX(8deg)!important;
  animation:shLogoFloat 4s ease-in-out infinite!important;
}
@keyframes shLogoFloat {
  0%,100% { transform:translateY(0) translateZ(35px) rotateX(8deg) rotateY(-4deg); }
  50% { transform:translateY(-8px) translateZ(48px) rotateX(12deg) rotateY(5deg); }
}
.hero-title {
  text-shadow:0 0 32px @@ACCENT@@18!important;
  transform:translateZ(24px)!important;
}
.hero-description { transform:translateZ(16px)!important; }
.hero-badge {
  box-shadow:0 0 24px @@ACCENT@@18,inset 0 1px 0 rgba(255,255,255,.08)!important;
  backdrop-filter:blur(12px)!important;
}

/* Premium glass stat deck */
.stat-card {
  position:relative!important;
  overflow:hidden!important;
  background:
    linear-gradient(145deg,rgba(255,255,255,.055),transparent 55%),
    linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  backdrop-filter:blur(18px)!important;
  -webkit-backdrop-filter:blur(18px)!important;
  border:1px solid rgba(255,255,255,.09)!important;
  box-shadow:
    0 18px 45px rgba(0,0,0,.13),
    inset 0 1px 0 rgba(255,255,255,.08)!important;
  transform-style:preserve-3d!important;
}
.stat-card::before {
  content:"";
  position:absolute;
  width:120px;
  height:120px;
  right:-55px;
  top:-55px;
  border-radius:50%;
  background:@@ACCENT@@16;
  filter:blur(5px);
  animation:shPulse 4s ease-in-out infinite alternate;
}
@keyframes shPulse {
  from { transform:scale(.85); opacity:.45; }
  to { transform:scale(1.15); opacity:.85; }
}
.stat-card:hover {
  transform:translateY(-7px) rotateX(2deg) rotateY(-1deg)!important;
  border-color:@@ACCENT@@55!important;
  box-shadow:0 26px 60px rgba(0,0,0,.20),0 0 35px @@ACCENT@@10!important;
}

/* Glassmorphism chat */
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
  position:relative!important;
  overflow:hidden!important;
  background:
    linear-gradient(145deg,rgba(255,255,255,.045),transparent 60%),
    var(--sh-panel)!important;
  backdrop-filter:blur(16px)!important;
  -webkit-backdrop-filter:blur(16px)!important;
  border:1px solid rgba(255,255,255,.08)!important;
  box-shadow:
    0 16px 42px rgba(0,0,0,.11),
    inset 0 1px 0 rgba(255,255,255,.06)!important;
}
html body .stApp [data-testid="stChatMessage"]:hover [data-testid="stChatMessageContent"] {
  transform:translateY(-2px)!important;
  border-color:@@ACCENT@@35!important;
  box-shadow:0 20px 48px rgba(0,0,0,.15),0 0 28px @@ACCENT@@08!important;
  transition:all .22s ease!important;
}

/* 3D pipeline */
.pipeline-card {
  position:relative!important;
  overflow:hidden!important;
  background:
    radial-gradient(circle at 0% 0%,@@ACCENT@@0C,transparent 28%),
    linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 22px 55px rgba(0,0,0,.14),inset 0 1px 0 rgba(255,255,255,.06)!important;
}
.pipeline-step {
  position:relative!important;
  overflow:hidden!important;
  background:linear-gradient(145deg,rgba(255,255,255,.04),var(--sh-panel))!important;
  box-shadow:0 8px 24px rgba(0,0,0,.08),inset 0 1px 0 rgba(255,255,255,.05)!important;
  transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease!important;
}
.pipeline-step::after {
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(110deg,transparent 20%,@@ACCENT@@12 48%,transparent 72%);
  transform:translateX(-110%);
  animation:shScan 4.5s ease-in-out infinite;
  pointer-events:none;
}
@keyframes shScan {
  0%,35% { transform:translateX(-110%); }
  65%,100% { transform:translateX(110%); }
}
.pipeline-step:hover {
  transform:translateX(5px) translateZ(8px)!important;
  border-color:@@ACCENT@@55!important;
  box-shadow:0 14px 30px rgba(0,0,0,.13),0 0 22px @@ACCENT@@08!important;
}

/* Verdict / risk card gets a cinematic glow */
.verdict-card {
  position:relative!important;
  overflow:hidden!important;
  background:
    linear-gradient(145deg,rgba(255,255,255,.045),transparent 60%),
    linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 20px 48px rgba(0,0,0,.14),inset 0 1px 0 rgba(255,255,255,.06)!important;
}
.verdict-card::after {
  content:"";
  position:absolute;
  inset:auto -15% -65% 30%;
  height:180px;
  background:radial-gradient(circle,@@ACCENT@@16,transparent 68%);
  pointer-events:none;
  animation:shGlow 5s ease-in-out infinite alternate;
}
@keyframes shGlow {
  from { transform:translateX(-4%); opacity:.35; }
  to { transform:translateX(8%); opacity:.85; }
}

/* Source cards feel like floating evidence tiles */
.source-card,.source {
  background:
    linear-gradient(145deg,rgba(255,255,255,.04),transparent 58%),
    var(--sh-panel)!important;
  box-shadow:0 15px 36px rgba(0,0,0,.10),inset 0 1px 0 rgba(255,255,255,.05)!important;
  backdrop-filter:blur(12px)!important;
  transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease!important;
}
.source-card:hover,.source:hover {
  transform:translateY(-4px) translateX(2px)!important;
  box-shadow:0 22px 48px rgba(0,0,0,.15),0 0 25px @@ACCENT@@09!important;
}

/* Sidebar becomes a premium control cockpit */
section[data-testid="stSidebar"] {
  box-shadow:12px 0 45px rgba(0,0,0,.08)!important;
}
.sidebar-brand-logo {
  position:relative!important;
  overflow:hidden!important;
  box-shadow:0 12px 35px @@ACCENT@@20,inset 0 1px 0 rgba(255,255,255,.12)!important;
  animation:shLogoFloat 5s ease-in-out infinite!important;
}
.sidebar-brand-logo::after {
  content:"";
  position:absolute;
  width:140%;
  height:30%;
  left:-20%;
  top:35%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.22),transparent);
  transform:rotate(-35deg);
  animation:shShimmer 3.8s linear infinite;
}
@keyframes shShimmer {
  from { transform:translateX(-80%) rotate(-35deg); }
  to { transform:translateX(120%) rotate(-35deg); }
}
.sidebar-status-card {
  background:linear-gradient(145deg,rgba(255,255,255,.05),var(--sh-panel2))!important;
  box-shadow:0 10px 28px rgba(0,0,0,.09)!important;
}

/* Chat composer as a floating command bar */
html body .stApp [data-testid="stChatInput"] > div {
  background:
    linear-gradient(145deg,rgba(255,255,255,.055),transparent 65%),
    linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  backdrop-filter:blur(22px)!important;
  -webkit-backdrop-filter:blur(22px)!important;
  border:1px solid @@ACCENT@@30!important;
  box-shadow:
    0 20px 55px rgba(0,0,0,.18),
    0 0 35px @@ACCENT@@08,
    inset 0 1px 0 rgba(255,255,255,.09)!important;
}
html body .stApp [data-testid="stChatInput"] > div:focus-within {
  transform:translateY(-2px)!important;
  border-color:@@ACCENT@@88!important;
  box-shadow:
    0 24px 65px rgba(0,0,0,.20),
    0 0 0 4px @@ACCENT@@0D,
    0 0 45px @@ACCENT@@12,
    inset 0 1px 0 rgba(255,255,255,.12)!important;
}

/* Buttons become tactile premium controls */
html body .stApp div.stButton > button,
html body .stApp [data-testid="stDownloadButton"] button {
  position:relative!important;
  overflow:hidden!important;
  background:linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 9px 25px rgba(0,0,0,.10),inset 0 1px 0 rgba(255,255,255,.07)!important;
}
html body .stApp div.stButton > button::after,
html body .stApp [data-testid="stDownloadButton"] button::after {
  content:"";
  position:absolute;
  top:0;
  left:-120%;
  width:80%;
  height:100%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.14),transparent);
  transform:skewX(-18deg);
  transition:left .55s ease;
  pointer-events:none;
}
html body .stApp div.stButton > button:hover::after,
html body .stApp [data-testid="stDownloadButton"] button:hover::after {
  left:140%;
}

/* Expanders become glass panels */
html body .stApp [data-testid="stExpander"] {
  background:linear-gradient(145deg,rgba(255,255,255,.035),var(--sh-panel))!important;
  box-shadow:0 14px 35px rgba(0,0,0,.09),inset 0 1px 0 rgba(255,255,255,.05)!important;
  backdrop-filter:blur(12px)!important;
}

/* Respect reduced-motion accessibility */
@media (prefers-reduced-motion:reduce) {
  html body .stApp,
  .hero::before,.hero::after,.hero-logo,
  .stat-card::before,.pipeline-step::after,.verdict-card::after,
  .sidebar-brand-logo,.sidebar-brand-logo::after {
    animation:none!important;
  }
  .hero-logo,.stat-card,.pipeline-step { transform:none!important; }
}

/* Premium stat alignment + sidebar cockpit */
.stat-card{min-height:112px!important;height:112px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important;gap:7px!important;padding:18px 14px!important;border-radius:18px!important;background:radial-gradient(circle at 50% 0%,@@ACCENT@@13,transparent 48%),linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;}
.stat-label{width:100%!important;color:var(--sh-muted)!important;font-size:10px!important;line-height:1.2!important;font-weight:800!important;letter-spacing:1.05px!important;text-transform:uppercase!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;}
.stat-value{width:100%!important;color:var(--sh-text)!important;font-size:18px!important;line-height:1.15!important;font-weight:800!important;letter-spacing:-.35px!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;}
section[data-testid="stSidebar"]>div{padding:18px 14px 22px!important;}
section[data-testid="stSidebar"] .sidebar-brand{min-height:68px!important;margin-bottom:5px!important;padding:8px!important;border-radius:18px!important;background:radial-gradient(circle at 10% 0%,@@ACCENT@@13,transparent 55%),linear-gradient(145deg,rgba(255,255,255,.035),transparent 75%)!important;}
section[data-testid="stSidebar"] .sidebar-brand-name{font-size:19px!important;letter-spacing:-.45px!important;}
section[data-testid="stSidebar"] .sidebar-section-title{display:flex!important;align-items:center!important;gap:8px!important;margin:16px 3px 8px!important;font-size:9px!important;letter-spacing:1.6px!important;}
section[data-testid="stSidebar"] .sidebar-section-title:before{content:"";width:18px;height:1px;background:linear-gradient(90deg,var(--sh-accent),transparent)!important;box-shadow:0 0 8px @@ACCENT@@55!important;}
section[data-testid="stSidebar"] .sidebar-section-title:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--sh-border),transparent)!important;}
section[data-testid="stSidebar"] [data-testid="stSelectbox"]{margin-bottom:11px!important;}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] label{margin-bottom:5px!important;padding-left:3px!important;font-size:10px!important;letter-spacing:.65px!important;text-transform:uppercase!important;color:var(--sh-muted)!important;}

section[data-testid="stSidebar"] .sidebar-active-theme{margin:8px 1px 2px!important;padding:9px 11px!important;border:1px solid var(--sh-border)!important;border-radius:11px!important;background:linear-gradient(145deg,@@ACCENT@@09,var(--sh-panel2))!important;color:var(--sh-muted)!important;font-size:10px!important;text-align:center!important;}
section[data-testid="stSidebar"] .sidebar-provider-card,section[data-testid="stSidebar"] .sidebar-status-card{min-height:58px!important;padding:11px 12px!important;border-radius:15px!important;border:1px solid var(--sh-border)!important;background:radial-gradient(circle at 0% 0%,@@ACCENT@@10,transparent 45%),linear-gradient(145deg,var(--sh-panel2),var(--sh-panel))!important;box-shadow:0 12px 28px rgba(0,0,0,.09),inset 0 1px 0 rgba(255,255,255,.06)!important;}

section[data-testid="stSidebar"] .sidebar-provider-card.sidebar-provider-online .sidebar-provider-dot{background:#22C55E!important;box-shadow:0 0 0 3px rgba(34,197,94,.14),0 0 14px rgba(34,197,94,.65)!important;animation:providerPulse 2s ease-in-out infinite!important;}
section[data-testid="stSidebar"] .sidebar-provider-card.sidebar-provider-partial .sidebar-provider-dot{background:#F59E0B!important;box-shadow:0 0 0 3px rgba(245,158,11,.14),0 0 14px rgba(245,158,11,.58)!important;animation:providerPulse 2s ease-in-out infinite!important;}
section[data-testid="stSidebar"] .sidebar-provider-card.sidebar-provider-offline .sidebar-provider-dot{background:#EF4444!important;box-shadow:0 0 0 3px rgba(239,68,68,.14),0 0 14px rgba(239,68,68,.55)!important;animation:none!important;}
section[data-testid="stSidebar"] .sidebar-provider-card .sidebar-provider-dot{display:inline-block!important;width:8px!important;height:8px!important;min-width:8px!important;margin:4px 10px 0 0!important;border-radius:50%!important;background:#22C55E!important;box-shadow:0 0 0 3px rgba(34,197,94,.14),0 0 14px rgba(34,197,94,.65)!important;vertical-align:top!important;animation:providerPulse 2s ease-in-out infinite!important;} 
section[data-testid="stSidebar"] .sidebar-provider-card.sidebar-provider-offline .sidebar-provider-dot{background:#EF4444!important;box-shadow:0 0 0 3px rgba(239,68,68,.14),0 0 14px rgba(239,68,68,.55)!important;animation:none!important;}
section[data-testid="stSidebar"] .sidebar-provider-card{display:flex!important;align-items:flex-start!important;gap:0!important;}
section[data-testid="stSidebar"] .sidebar-provider-title{color:var(--sh-text)!important;font-weight:800!important;}
section[data-testid="stSidebar"] .sidebar-provider-list{color:var(--sh-muted)!important;margin-top:2px!important;}
@keyframes providerPulse{0%,100%{transform:scale(1);opacity:.95;}50%{transform:scale(1.18);opacity:1;}}
section[data-testid="stSidebar"] button[key^="open_"]{min-height:42px!important;margin:3px 0!important;padding:8px 11px!important;border-radius:12px!important;text-align:left!important;font-size:11px!important;background:linear-gradient(145deg,var(--sh-panel2),var(--sh-panel))!important;box-shadow:0 6px 18px rgba(0,0,0,.06)!important;}
section[data-testid="stSidebar"] button[key^="open_"]:hover{transform:translateX(3px)!important;border-color:@@ACCENT@@60!important;color:var(--sh-accent)!important;}
section[data-testid="stSidebar"] button[key="btn_clear"],section[data-testid="stSidebar"] button[key="btn_delete_all"]{min-height:40px!important;border-radius:12px!important;margin-top:5px!important;}
section[data-testid="stSidebar"] button[key="btn_clear"]{color:var(--sh-accent)!important;border-color:@@ACCENT@@40!important;background:@@ACCENT@@08!important;}
section[data-testid="stSidebar"] hr{margin:13px 0!important;border:0!important;border-top:1px solid var(--sh-border)!important;opacity:.75!important;}
@media(max-width:900px){.stat-card{min-height:100px!important;height:100px!important;}}

/* Risk meter — green / yellow / orange / red */
.risk-meter-card {
  --risk:#22C55E;
  position:relative!important;
  overflow:hidden!important;
  margin:12px 0 16px!important;
  padding:16px 18px!important;
  border:1px solid color-mix(in srgb,var(--risk) 42%,var(--sh-border))!important;
  border-left:4px solid var(--risk)!important;
  border-radius:17px!important;
  background:linear-gradient(145deg,var(--sh-panel),var(--sh-panel2))!important;
  box-shadow:0 14px 36px color-mix(in srgb,var(--risk) 9%,transparent)!important;
}
.risk-meter-card.risk-safe{--risk:#22C55E!important;}
.risk-meter-card.risk-low{--risk:#EAB308!important;}
.risk-meter-card.risk-medium{--risk:#F59E0B!important;}
.risk-meter-card.risk-elevated{--risk:#F97316!important;}
.risk-meter-card.risk-high{--risk:#EF4444!important;}
.risk-meter-top{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:14px!important;}
.risk-meter-title{color:var(--sh-text)!important;font-weight:800!important;font-size:13px!important;}
.risk-meter-level{display:inline-flex!important;margin-left:8px!important;padding:3px 8px!important;border-radius:999px!important;background:color-mix(in srgb,var(--risk) 12%,transparent)!important;color:var(--risk)!important;border:1px solid color-mix(in srgb,var(--risk) 30%,transparent)!important;font-size:10px!important;font-weight:750!important;}
.risk-meter-top strong{color:var(--risk)!important;font-size:18px!important;}
.risk-meter-track{height:10px!important;margin-top:12px!important;overflow:hidden!important;border-radius:999px!important;background:color-mix(in srgb,var(--sh-muted) 18%,transparent)!important;border:1px solid var(--sh-border)!important;}
.risk-meter-fill{height:100%!important;border-radius:inherit!important;background:linear-gradient(90deg,#22C55E 0%,#EAB308 38%,#F59E0B 62%,#F97316 78%,#EF4444 100%)!important;box-shadow:0 0 14px color-mix(in srgb,var(--risk) 45%,transparent)!important;transition:width .55s ease!important;}
.risk-meter-scale{display:flex!important;justify-content:space-between!important;margin-top:5px!important;color:var(--sh-muted)!important;font-size:9px!important;}
.risk-meter-note{margin-top:9px!important;color:var(--sh-muted)!important;font-size:11px!important;line-height:1.45!important;}

/* Balanced response text for both themes */
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] p,
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] li,
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] span,
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] strong,
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] em {
  color:var(--sh-text)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] code {
  color:var(--sh-accent)!important;
  background:var(--sh-panel2)!important;
  border:1px solid var(--sh-border)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] a {
  color:var(--sh-accent)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] blockquote {
  color:var(--sh-muted)!important;
  border-left-color:var(--sh-accent)!important;
  background:var(--sh-panel2)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] hr {
  border-color:var(--sh-border)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] table {
  color:var(--sh-text)!important;
  background:var(--sh-panel)!important;
  border-color:var(--sh-border)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] th {
  color:var(--sh-text)!important;
  background:var(--sh-panel2)!important;
  border-color:var(--sh-border)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] td {
  color:var(--sh-text)!important;
  border-color:var(--sh-border)!important;
}
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] p,
html body .stApp [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] li {
  line-height:1.65!important;
}



/* SELECTBOX DROPDOWN — force the entire opened popup surface to follow the active theme.
   Streamlit/BaseWeb renders this menu in a portal outside the sidebar, so target
   every relevant popup/listbox layer rather than relying on the sidebar scope. */
html body div[data-baseweb="popover"],
html body div[data-baseweb="popover"] > div,
html body div[data-baseweb="popover"] > div > div,
html body div[data-baseweb="popover"] > div > div > div,
html body div[data-baseweb="menu"],
html body div[data-baseweb="menu"] > div,
html body div[data-baseweb="menu"] > div > div,
html body div[data-baseweb="menu"] > ul,
html body ul[role="listbox"],
html body div[role="listbox"],
html body div[role="listbox"] > div,
html body div[role="listbox"] > ul,
html body div[role="listbox"] > div > div {
  background:var(--sh-menu)!important;
  background-color:var(--sh-menu)!important;
  color:var(--sh-text)!important;
  color-scheme:var(--sh-scheme)!important;
}

/* BaseWeb option rows can paint their own white surface over the menu. */
html body div[data-baseweb="menu"] [role="option"],
html body ul[role="listbox"] [role="option"],
html body div[role="listbox"] [role="option"] {
  background:var(--sh-menu)!important;
  background-color:var(--sh-menu)!important;
  color:var(--sh-text)!important;
}

html body div[data-baseweb="menu"] [role="option"]:hover,
html body ul[role="listbox"] [role="option"]:hover,
html body div[role="listbox"] [role="option"]:hover,
html body div[data-baseweb="menu"] [role="option"][aria-selected="true"],
html body ul[role="listbox"] [role="option"][aria-selected="true"],
html body div[role="listbox"] [role="option"][aria-selected="true"] {
  background:var(--sh-menu-hover)!important;
  background-color:var(--sh-menu-hover)!important;
  color:var(--sh-text)!important;
}

/* MODERN STREAMLIT SELECTBOX POPUP — current Streamlit uses a portaled
   stSelectboxVirtualDropdown instead of the older BaseWeb menu. */
html body [data-testid="stSelectboxVirtualDropdown"],
html body [data-testid="stSelectboxVirtualDropdown"] > div,
html body [data-testid="stSelectboxVirtualDropdown"] > div > div,
html body [data-testid="stSelectboxVirtualDropdown"] ul,
html body [data-testid="stSelectboxVirtualDropdown"] li,
html body [data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
html body [data-testid="stSelectboxVirtualDropdown"] [role="option"] {
  background:var(--sh-menu)!important;
  background-color:var(--sh-menu)!important;
  color:var(--sh-text)!important;
  color-scheme:var(--sh-scheme)!important;
}

html body [data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
html body [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"] {
  background:var(--sh-menu-hover)!important;
  background-color:var(--sh-menu-hover)!important;
  color:var(--sh-text)!important;
}

/* FINAL SELECTBOX OUTER CONTROL — outer box only. Inner content and dropdown stay native. */
html body .stApp section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  min-height:44px!important;
  box-sizing:border-box!important;
  background:var(--sh-select-bg)!important;
  background-color:var(--sh-select-bg)!important;
  border:1px solid var(--sh-select-border)!important;
  border-radius:14px!important;
  outline:none!important;
  box-shadow:none!important;
}
html body .stApp section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  background:var(--sh-hover)!important;
  background-color:var(--sh-hover)!important;
  border-color:var(--sh-accent)!important;
}
html body .stApp section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus,
html body .stApp section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  outline:none!important;
  box-shadow:0 0 0 1px var(--sh-select-border)!important;
  border-color:var(--sh-select-border)!important;
}</style>
"""


# ---------------------------------------------------------------------------
# HTML safety net
# Markdown turns indented lines / blank lines inside HTML into a code block,
# which is why raw <div ...> text appeared in the hero and sidebar. Any
# st.markdown(..., unsafe_allow_html=True) whose content starts with "<" is
# flattened (indentation + blank lines removed) before rendering.
# ---------------------------------------------------------------------------
def _flatten_html(body):
    if isinstance(body, str) and body.lstrip().startswith("<"):
        return "\n".join(line.strip() for line in body.splitlines() if line.strip())
    return body


def _install_html_fix():
    from streamlit.delta_generator import DeltaGenerator

    if getattr(DeltaGenerator.markdown, "_sh_patched", False):
        return

    original = DeltaGenerator.markdown

    def markdown(self, body, *args, **kwargs):
        unsafe = kwargs.get("unsafe_allow_html", args[0] if args else False)
        if unsafe:
            body = _flatten_html(body)
        return original(self, body, *args, **kwargs)

    markdown._sh_patched = True
    DeltaGenerator.markdown = markdown

    original_top = st.markdown

    def top_markdown(body, *args, **kwargs):
        unsafe = kwargs.get("unsafe_allow_html", args[0] if args else False)
        if unsafe:
            body = _flatten_html(body)
        return original_top(body, *args, **kwargs)

    st.markdown = top_markdown


_install_html_fix()


def apply_theme(dark: bool, accent: str):
    palette = dict(DARK if dark else LIGHT)
    palette["ACCENT"] = ACCENTS.get(accent, ACCENTS["Cyan"])

    css = CSS
    for key, value in palette.items():
        css = css.replace(f"@@{key}@@", value)

    st.markdown(css, unsafe_allow_html=True)
