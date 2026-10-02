from __future__ import annotations
import html
import streamlit as st

def hero(compact=False):
    if compact:
        st.markdown('<div class="hero" style="padding:22px 24px;"><div class="hero-title" style="font-size:32px;">ScamHunter <span>AI</span></div><div class="hero-description">Evidence-first investigation for suspicious messages, links, offers and documents.</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="hero"><div class="hero-logo">🛡️</div><div class="hero-title">ScamHunter <span>AI</span></div><div class="hero-description">Investigate suspicious messages, offers, links and online claims with AI-powered evidence analysis.</div><div class="hero-badge">● Evidence-first AI investigation</div></div>',unsafe_allow_html=True)

def example_prompts():
    """Render compact, responsive sample-query buttons."""
    prompts = [
        "Is this message a scam?",
        "Check this payment request.",
        "Investigate this link.",
    ]
    st.markdown('<div class="sample-query-title">SAMPLE QUERIES</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for i, prompt in enumerate(prompts):
        with cols[i]:
            if st.button(prompt, use_container_width=True, key=f"example_{i}", help=prompt):
                return prompt
    return None

def setup_banner(groq=False,gemini=False):
    if groq or gemini:
        st.success("AI providers configured: "+", ".join([x for x,y in (("Groq",groq),("Gemini",gemini)) if y]))
    else:
        st.info("No AI API key is configured. Instant heuristic scanning is still available.")

def stat_strip(stats):
    cols = st.columns(len(stats), gap="small")
    for col, (label, value) in zip(cols, stats):
        with col:
            st.markdown(
                f'<div class="stat-card"><div class="stat-label">{html.escape(str(label))}</div>'
                f'<div class="stat-value">{html.escape(str(value))}</div></div>',
                unsafe_allow_html=True,
            )

def risk_meter(scan):
    if not scan:
        return
    level = scan.get("level", "none")
    score = max(0, min(100, int(scan.get("score", 0) or 0)))

    # A non-zero heuristic score means a signal was detected. The old
    # presentation used the threshold label "none" for scores below 10,
    # which made a result such as 8/100 look contradictory.
    if score > 0 and level == "none":
        label = "Low signal"
        tone = "low"
    else:
        labels = {"high": "High signal", "medium": "Moderate signal", "low": "Low signal", "none": "No automatic signals"}
        label = labels.get(level, level.title())
        if score == 0 or level == "none":
            tone = "safe"
        elif score < 40 or level == "low":
            tone = "low"
        elif score < 70 or level == "medium":
            tone = "medium"
        elif score < 85:
            tone = "elevated"
        else:
            tone = "high"

    st.markdown(
        f'<div class="risk-meter-card risk-{tone}"><div class="risk-meter-top"><div><span class="risk-meter-title">⚡ Instant Scan</span><span class="risk-meter-level">{html.escape(label)}</span></div><strong>{score}/100</strong></div><div class="risk-meter-track"><div class="risk-meter-fill" style="width:{score}%;"></div></div><div class="risk-meter-scale"><span>0</span><span>50</span><span>100</span></div><div class="risk-meter-note">{html.escape(scan.get("headline",""))} · Heuristic hint only — not proof of fraud.</div></div>',
        unsafe_allow_html=True,
    )

def scan_details(scan):
    if not scan: return
    flags=scan.get("flags",[])
    if not flags:
        st.caption("No automatic warning signals detected.")
        return
    for f in flags:
        st.markdown(f'<div class="source-card"><b>{html.escape(str(f.get("label","Signal")))}</b><br><span class="muted">{html.escape(str(f.get("advice","")))}</span></div>',unsafe_allow_html=True)

def source_card(item):
    if not isinstance(item,dict): item={"text":str(item)}
    source=item.get("source")
    if isinstance(source,dict):
        merged=dict(source); merged.update({k:v for k,v in item.items() if k!="source" and v not in (None,"")}); item=merged
    source_type=(item.get("source_type") or item.get("type") or "").lower()
    title=item.get("filename") or item.get("title") or item.get("url") or ("Knowledge Base Document" if source_type=="knowledge_base" else "Web source")
    meta=[]
    if item.get("page") is not None: meta.append(f"Page {item.get('page')}")
    if item.get("section"): meta.append(str(item.get("section")))
    if item.get("url") and source_type!="knowledge_base": meta.append(str(item.get("url")))
    excerpt=item.get("excerpt") or item.get("snippet") or item.get("text") or item.get("content") or ""
    icon="📄" if source_type=="knowledge_base" else "🌐"
    st.markdown(f'<div class="source-card"><div class="source-header"><div class="source-icon">{icon}</div><div class="source-heading"><div class="source-title">{html.escape(str(title))}</div><div class="source-meta">{html.escape(" · ".join(meta))}</div></div></div><div class="source-excerpt">{html.escape(str(excerpt)).replace(chr(10),"<br>")}</div></div>',unsafe_allow_html=True)
