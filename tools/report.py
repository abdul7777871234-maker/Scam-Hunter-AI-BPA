from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = A4
MARGIN = 15 * mm

NAVY = colors.HexColor("#0C2B5E")
TEAL = colors.HexColor("#14A79B")
AMBER = colors.HexColor("#F5A524")
GREEN = colors.HexColor("#16A34A")
YELLOW = colors.HexColor("#EAB308")
RED = colors.HexColor("#DC2626")
TEXT = colors.HexColor("#172033")
MUTED = colors.HexColor("#64748B")
BORDER = colors.HexColor("#D8E0EA")
PANEL = colors.HexColor("#F5F8FC")
PANEL_2 = colors.HexColor("#EEF3F8")
WHITE = colors.white


def _register_fonts():
    regular, bold, italic = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
    arabic_available = False
    base = Path(__file__).with_name("fonts")
    fonts = [
        (base / "DejaVuSans.ttf", "ScamHunterSans"),
        (base / "DejaVuSans-Bold.ttf", "ScamHunterSansBold"),
        (base / "DejaVuSans-Oblique.ttf", "ScamHunterSansItalic"),
    ]
    try:
        if all(path.exists() for path, _ in fonts):
            for path, name in fonts:
                pdfmetrics.registerFont(TTFont(name, str(path)))
            regular, bold, italic = "ScamHunterSans", "ScamHunterSansBold", "ScamHunterSansItalic"
    except Exception:
        pass
    try:
        ar = base / "NotoNaskhArabic-Regular.ttf"
        ab = base / "NotoNaskhArabic-Bold.ttf"
        if ar.exists() and ab.exists():
            pdfmetrics.registerFont(TTFont("ScamHunterArabic", str(ar)))
            pdfmetrics.registerFont(TTFont("ScamHunterArabicBold", str(ab)))
            arabic_available = True
    except Exception:
        pass
    return regular, bold, italic, arabic_available


FONT_REGULAR, FONT_BOLD, FONT_ITALIC, ARABIC_AVAILABLE = _register_fonts()


def _esc(value, quote=False):
    return html.escape(str(value or ""), quote=quote)


def _rtl_text(value):
    text = str(value or "")
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def _font_for_language(language, bold=False):
    lang = str(language or "").lower()
    if ARABIC_AVAILABLE and ("urdu" in lang or "arabic" in lang):
        return "ScamHunterArabicBold" if bold else "ScamHunterArabic"
    return FONT_BOLD if bold else FONT_REGULAR


def _text_markup(value, language="English"):
    text = str(value or "")
    if str(language or "").lower() in {"urdu", "arabic"}:
        text = _rtl_text(text)
    return _esc(text)


def _link_markup(url):
    value = str(url or "").strip()
    if not value:
        return ""
    href = html.escape(value, quote=True)
    display = html.escape(value)
    display = re.sub(r"([/?=&._:-])", r"\1<wbr/>", display)
    return f'<link href="{href}" color="#0C2B5E"><u>{display}</u></link>'


def _risk(level):
    level = str(level or "review").lower()
    if level in {"high", "critical", "red"}:
        return "HIGH", RED
    if level in {"medium", "elevated", "yellow"}:
        return "MEDIUM", YELLOW
    if level in {"low", "green", "safe"}:
        return "LOW", GREEN
    return "REVIEW", TEAL


def _styles(language):
    regular = _font_for_language(language)
    bold = _font_for_language(language, True)
    right = str(language or "").lower() in {"urdu", "arabic"}
    return {
        "body": ParagraphStyle("Body", fontName=regular, fontSize=9.2, leading=13.2, textColor=TEXT, alignment=TA_RIGHT if right else TA_LEFT, spaceAfter=4),
        "small": ParagraphStyle("Small", fontName=regular, fontSize=7.6, leading=10.5, textColor=MUTED, alignment=TA_RIGHT if right else TA_LEFT),
        "label": ParagraphStyle("Label", fontName=bold, fontSize=6.8, leading=8.5, textColor=MUTED, tracking=0.5),
        "h1": ParagraphStyle("H1", fontName=bold, fontSize=23, leading=27, textColor=NAVY, spaceAfter=5),
        "section": ParagraphStyle("Section", fontName=bold, fontSize=8, leading=10, textColor=TEAL, tracking=1.0, spaceBefore=4, spaceAfter=5),
        "quote": ParagraphStyle("Quote", fontName=regular, fontSize=8.7, leading=12.8, textColor=TEXT, leftIndent=2),
        "table": ParagraphStyle("Table", fontName=regular, fontSize=7.2, leading=9.5, textColor=TEXT),
        "table_small": ParagraphStyle("TableSmall", fontName=regular, fontSize=6.7, leading=9, textColor=MUTED),
    }


class SignalMeter(Flowable):
    def __init__(self, score=0, width=105 * mm, height=8 * mm):
        super().__init__()
        self.score = max(0, min(100, float(score or 0)))
        self.width, self.height = width, height

    def wrap(self, availWidth, availHeight):
        return min(self.width, availWidth), self.height

    def draw(self):
        c = self.canv
        y = self.height / 2 - 2
        c.setFillColor(colors.HexColor("#E5EAF1"))
        c.roundRect(0, y, self.width, 4, 2, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.roundRect(0, y, self.width * self.score / 100, 4, 2, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 7)
        c.drawRightString(self.width, self.height - 1, f"{int(self.score)}/100")


class ShieldMark(Flowable):
    def __init__(self, size=11 * mm):
        super().__init__()
        self.width = self.height = size

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c, s = self.canv, self.width
        c.setFillColor(TEAL)
        p = c.beginPath()
        p.moveTo(s*.5, s); p.lineTo(s*.9, s*.84); p.lineTo(s*.82, s*.37)
        p.curveTo(s*.76, s*.14, s*.57, s*.04, s*.5, 0)
        p.curveTo(s*.43, s*.04, s*.24, s*.14, s*.18, s*.37)
        p.lineTo(s*.1, s*.84); p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setStrokeColor(WHITE); c.setLineWidth(1.4)
        c.line(s*.34, s*.5, s*.46, s*.37); c.line(s*.46, s*.37, s*.7, s*.65)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setStrokeColor(BORDER); self.setLineWidth(.5)
            self.line(MARGIN, 11*mm, PAGE_W-MARGIN, 11*mm)
            self.setFont(FONT_REGULAR, 6.8); self.setFillColor(MUTED)
            self.drawString(MARGIN, 6.7*mm, "SCAMHUNTER AI  •  Investigation support, not a fraud determination")
            self.setFont(FONT_BOLD, 6.8)
            self.drawRightString(PAGE_W-MARGIN, 6.7*mm, f"Page {self._pageNumber} of {total}")
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


def _header_footer(c, doc):
    c.saveState()
    c.setFillColor(WHITE); c.rect(0, PAGE_H-29*mm, PAGE_W, 29*mm, fill=1, stroke=0)
    shield = ShieldMark(); shield.canv = c; shield.drawOn(c, MARGIN, PAGE_H-23*mm)
    c.setFillColor(NAVY); c.setFont(FONT_BOLD, 14)
    c.drawString(MARGIN+15*mm, PAGE_H-14*mm, "SCAMHUNTER AI")
    c.setFillColor(TEAL); c.setFont(FONT_BOLD, 6.6)
    c.drawString(MARGIN+15*mm, PAGE_H-19*mm, "AI-POWERED SCAM INVESTIGATION REPORT")
    c.setFillColor(PANEL_2); c.roundRect(PAGE_W-MARGIN-24*mm, PAGE_H-13*mm, 24*mm, 5*mm, 2.5*mm, fill=1, stroke=0)
    c.setFillColor(NAVY); c.setFont(FONT_BOLD, 6.2)
    c.drawCentredString(PAGE_W-MARGIN-12*mm, PAGE_H-11.3*mm, "CONFIDENTIAL")
    c.setFillColor(MUTED); c.setFont(FONT_REGULAR, 5.8)
    c.drawRightString(PAGE_W-MARGIN, PAGE_H-18.8*mm, str(getattr(doc, "_generated", "")))
    c.drawRightString(PAGE_W-MARGIN, PAGE_H-23*mm, f"{getattr(doc, '_mode', 'Quick Check')}  •  {getattr(doc, '_language', 'English')}")
    c.translate(PAGE_W/2, PAGE_H/2); c.rotate(32); c.setFillColor(colors.HexColor("#E9EEF5"))
    c.setFont(FONT_BOLD, 48); c.drawCentredString(0, 0, "SCAMHUNTER AI")
    c.restoreState()


def _card(flowables):
    t = Table([[flowables]], colWidths=[166*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),PANEL), ("BOX",(0,0),(-1,-1),.6,BORDER),
        ("LEFTPADDING",(0,0),(-1,-1),9), ("RIGHTPADDING",(0,0),(-1,-1),9),
        ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    return t


def _info_cards(data, styles):
    cells = []
    for label, value in (("GENERATED",data.get("generated","")),("MODE",data.get("mode","Quick Check")),("LANGUAGE",data.get("language","English"))):
        cells.append([Paragraph(_esc(label),styles["label"]), Spacer(1,2), Paragraph(_esc(value),styles["body"])])
    t = Table([cells], colWidths=[55*mm,55*mm,56*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),PANEL), ("BOX",(0,0),(-1,-1),.6,BORDER),
        ("INNERGRID",(0,0),(-1,-1),.5,BORDER), ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ]))
    return t


def _assessment(data, styles):
    level, risk_color = _risk(data.get("level"))
    score = data.get("score",0); category = data.get("category") or "Not specified"
    headline = data.get("headline") or "Signal assessment generated from available evidence."
    badge_style = ParagraphStyle("Badge", parent=styles["body"], fontName=FONT_BOLD, fontSize=8, textColor=WHITE)
    badge = Table([[Paragraph(level,badge_style)]], colWidths=[23*mm], rowHeights=[7*mm])
    badge.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),risk_color),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1)]))
    left = [Paragraph("ASSESSMENT SIGNAL",styles["label"]),Spacer(1,3),badge,Spacer(1,4),Paragraph(f"<b>Category:</b> {_esc(category)}",styles["table_small"])]
    right = [Paragraph("SIGNAL SCORE",styles["label"]),SignalMeter(score),Paragraph(_esc(headline),styles["table_small"]),Spacer(1,2),Paragraph("Signal only — not proof of fraud.",styles["table_small"])]
    t = Table([[left,right]], colWidths=[55*mm,111*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PANEL),("BOX",(0,0),(-1,-1),.7,risk_color),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    return t


def _user_content(text, styles, language):
    flow = [Paragraph(_text_markup(line,language) or " ",styles["quote"]) for line in str(text or "(No text provided.)").replace("\r","").split("\n")]
    t = Table([[flow]], colWidths=[166*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PANEL_2),("BOX",(0,0),(-1,-1),.6,BORDER),("LINEBEFORE",(0,0),(0,0),3,TEAL),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    return t


def _markdown_inline(text, language):
    value = _text_markup(text,language)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"__(.+?)__", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r"<i>\1</i>", value)
    return value


def _investigation_sections(answer, styles, language):
    headings = {"assessment":"Assessment","key signals":"Key Signals","verified vs uncertain":"Verified vs Uncertain","what to do":"What To Do","what to do next":"What To Do"}
    sections=[]; current=None
    for raw in str(answer or "").replace("\r","").split("\n"):
        line=raw.strip()
        normalized=re.sub(r"^[#*\-\s]+", "", line).rstrip(":").strip().lower()
        if normalized in headings:
            current=headings[normalized]; sections.append((current,[])); continue
        if current is None:
            if line: sections.append(("Assessment",[line])); current="Assessment"
        else:
            sections[-1][1].append(raw)
    if not sections: sections=[("Assessment",[str(answer or "(No investigation generated.)")])]
    output=[]
    for heading, lines in sections:
        cleaned=[]
        for line in lines:
            s=line.strip()
            if not s: continue
            m=re.match(r"^(?:[-*•]|\d+[.)])\s+(.*)$", s)
            cleaned.append(("• "+m.group(1)) if m else s)
        if not cleaned: continue
        flow=[Paragraph(_esc(heading.upper()),styles["section"])]
        flow.extend(Paragraph(_markdown_inline(line,language),styles["body"]) for line in cleaned)
        output.append(KeepTogether(flow))
    return output


def _scan_details(scan, styles):
    flags=scan.get("flags") or []
    if not flags: return [Paragraph("No automatic signals were recorded.",styles["table_small"])]
    output=[]
    for flag in flags[:12]:
        if not isinstance(flag,dict): continue
        output.append(_card([Paragraph(_esc(flag.get("label") or "Detected signal"),ParagraphStyle("SignalLabel",parent=styles["body"],fontName=FONT_BOLD,textColor=NAVY)),Paragraph(_esc(flag.get("advice") or ""),styles["table_small"])]))
        output.append(Spacer(1,3))
    return output


def _source_rows(sources, source_type, styles):
    rows=[]
    for source in sources or []:
        if not isinstance(source,dict) or source.get("source_type")!=source_type: continue
        title=source.get("title") or source.get("filename") or "Untitled source"
        if source_type=="knowledge_base":
            loc=[]
            if source.get("page"): loc.append(f"Page {source['page']}")
            if source.get("paragraph"): loc.append(f"Paragraph {source['paragraph']}")
            rows.append([Paragraph(_esc(title),styles["table"]),Paragraph(_esc(" • ".join(loc) or "Internal knowledge base"),styles["table_small"])])
        else:
            rows.append([Paragraph(_esc(title),styles["table"]),Paragraph(_link_markup(source.get("url")) or "No URL",styles["table_small"])])
    return rows


def _source_table(title, rows, styles):
    output=[Paragraph(_esc(title.upper()),styles["section"])]
    if not rows:
        output.append(Paragraph("No evidence retrieved.",styles["table_small"])); return output
    t=Table([[Paragraph("SOURCE",styles["label"]),Paragraph("LOCATION / LINK",styles["label"])]]+rows,colWidths=[78*mm,88*mm],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),PANEL_2),("GRID",(0,0),(-1,-1),.45,BORDER),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    output.append(t); return output


def build_report_pdf(report_data):
    data=dict(report_data or {})
    generated=data.get("generated_at")
    if isinstance(generated,datetime): generated=generated.astimezone(timezone.utc)
    else: generated=datetime.now(timezone.utc)
    language=str(data.get("language") or "English")
    data["generated"]=generated.strftime("%Y-%m-%d %H:%M UTC")
    data["mode"]=str(data.get("mode") or "Quick Check")
    styles=_styles(language)

    output=BytesIO()
    doc=BaseDocTemplate(output,pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=33*mm,bottomMargin=17*mm,title="ScamHunter AI Investigation Report",author="ScamHunter AI")
    doc._generated=data["generated"]; doc._mode=data["mode"]; doc._language=language
    frame=Frame(MARGIN,17*mm,PAGE_W-2*MARGIN,PAGE_H-50*mm,id="normal",leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="report",frames=[frame],onPage=_header_footer)])

    story=[Spacer(1,2*mm),Paragraph("INVESTIGATION SUMMARY",styles["section"]),Paragraph("ScamHunter AI Investigation Report",styles["h1"]),Paragraph("A structured, printable snapshot of the investigation performed by the application.",styles["table_small"]),Spacer(1,5*mm),_info_cards(data,styles),Spacer(1,5*mm),_assessment(data.get("assessment") or {},styles),Spacer(1,5*mm),Paragraph("USER CONTENT",styles["section"]),_user_content(data.get("user_content",""),styles,language),Spacer(1,4*mm),Paragraph("AI INVESTIGATION",styles["section"])]
    story.extend(_investigation_sections(data.get("ai_investigation",""),styles,language))
    scan=data.get("instant_scan") or {}
    story.extend([Spacer(1,3*mm),Paragraph("INSTANT SCAN DETAILS",styles["section"]),Paragraph("Automatically detected signals are heuristic indicators and should not be treated as proof.",styles["table_small"]),Spacer(1,2*mm)])
    story.extend(_scan_details(scan,styles))
    sources=data.get("sources") or []
    story.extend([Spacer(1,3*mm),*_source_table("Knowledge Base Evidence",_source_rows(sources,"knowledge_base",styles),styles),Spacer(1,4*mm),*_source_table("Web Evidence",_source_rows(sources,"web",styles),styles)])
    doc.build(story,canvasmaker=NumberedCanvas)
    return output.getvalue()


def build_report(question,answer,verdict=None,scan=None,sources=None,mode="Quick Check",language="English"):
    verdict=verdict or {}; scan=scan or {}
    level,_=_risk(verdict.get("level") or scan.get("level") or "review")
    return build_report_pdf({
        "generated_at":datetime.now(timezone.utc),
        "mode":mode,
        "language":language,
        "user_content":question or "",
        "ai_investigation":answer or "",
        "assessment":{"level":level.lower(),"score":scan.get("score",0),"category":verdict.get("category") or "Not specified","headline":scan.get("headline") or verdict.get("reason") or "Signal assessment generated from the available evidence."},
        "instant_scan":scan,
        "sources":sources or [],
    })


def build_report_markdown(report_data):
    data=dict(report_data or {}); a=data.get("assessment") or {}
    lines=["# ScamHunter AI Investigation Report","",f"**Generated:** {data.get('generated','')}",f"**Mode:** {data.get('mode','Quick Check')}",f"**Language:** {data.get('language','English')}","","## Assessment Signal",f"- Level: **{str(a.get('level','review')).upper()}**",f"- Score: **{a.get('score',0)}/100**",f"- Category: {a.get('category','Not specified')}",f"- Signal: {a.get('headline','')}","","## User Content",data.get("user_content",""),"","## AI Investigation",data.get("ai_investigation",""),"","## Instant Scan Details"]
    for flag in (data.get("instant_scan") or {}).get("flags",[]) or []:
        lines.append(f"- **{flag.get('label','Signal')}**: {flag.get('advice','')}")
    lines.extend(["","## Sources"])
    for source in data.get("sources",[]) or []:
        title=source.get("title") or source.get("filename") or "Untitled source"; url=source.get("url")
        lines.append(f"- **{title}**"+(f" — {url}" if url else ""))
    lines.extend(["","---","ScamHunter AI provides investigation support and does not guarantee authenticity or safety."])
    return "\n".join(lines)
