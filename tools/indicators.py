from __future__ import annotations
import re
from urllib.parse import urlparse

PATTERNS = {
    "urgency": [r"\burgent\b", r"\bimmediately\b", r"\bact now\b", r"\blimited slots?\b", r"\bexpires?\b", r"\blast chance\b", r"\bcontact.{0,20}\bnow\b"],
    "payment": [r"\bpay\b", r"\bpayment\b", r"\btransfer\b", r"\bdeposit\b", r"\bfee\b", r"\bwire transfer\b", r"\bgift card\b", r"\bpersonal account\b", r"\bcrypto(?:currency)?\b", r"\busdt\b"],
    "credentials": [r"\bpassword\b", r"\bpasscode\b", r"\botp\b", r"\bverification code\b", r"\bsecurity code\b", r"\bpin\b", r"\blogin\b", r"\busername\b"],
    "personal": [r"\bcnic\b", r"\bpassport\b", r"\bid card\b", r"\bdate of birth\b", r"\baccount number\b", r"\bcard number\b", r"\bcredit card\b", r"\bdebit card\b"],
    "threat": [r"\barrest\b", r"\bpolice\b", r"\blawsuit\b", r"\blegal action\b", r"\baccount.{0,30}\b(?:suspend|suspended|blocked|terminate)\b"],
    "reward": [r"\bwon\b", r"\bwinner\b", r"\bprize\b", r"\breward\b", r"\blottery\b", r"\bgiveaway\b", r"\bfree money\b", r"\bcongratulations\b"],
    "investment": [r"\binvest(?:ment|ing)?\b", r"\btrading system\b", r"\bai trading\b", r"\bprofit(?:s)?\b", r"\breturns?\b", r"\b20\s*%\b", r"\bguarantee(?:d)?\b", r"\bzero[- ]risk\b", r"\bno risk\b"],
    "external_contact": [r"\bwhatsapp\b", r"\btelegram\b", r"\bsignal\b", r"\bcontact me\b", r"\bmessage me\b"],
}
URL_PATTERN=re.compile(r"(https?://[^\s<>\"]+|www\.[^\s<>\"]+)",re.I)
PHONE_PATTERN = [r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"]
WALLET_PATTERN = [r"(?<![A-Za-z0-9])0x[a-fA-F0-9]{40}(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])(?:bc1[a-zA-Z0-9]{25,87}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})(?![A-Za-z0-9])"]

def _count(text, key):
    return sum(len(re.findall(p,text,re.I)) for p in PATTERNS[key])

def _urls(text):
    return [x.rstrip(".,!?;:)]}") for x in URL_PATTERN.findall(text)]

def _url_flags(url):
    flags=[]
    candidate=url if url.lower().startswith(("http://","https://")) else "https://"+url
    try:
        host=(urlparse(candidate).hostname or "").lower()
        if not host: flags.append("URL has no recognizable hostname.")
        if any(x in host for x in ("verify","secure","account","login","claim","reward","wallet")):
            flags.append("Hostname contains an account, verification, reward, or wallet keyword.")
        if len(host.split("."))>4: flags.append("Unusually deep hostname.")
    except Exception:
        flags.append("URL could not be parsed normally.")
    return flags

def _flag(label,advice,severity,count=1):
    return {"label":label,"advice":advice,"severity":severity,"count":count}

def scan_text(text):
    text=str(text or "").strip()
    if not text:
        return {"level":"none","score":0,"headline":"No content was provided.","flags":[],"urls":[],"categories":[]}
    counts={k:_count(text,k) for k in PATTERNS}
    counts["phone"] = sum(len(re.findall(p, text)) for p in PHONE_PATTERN)
    counts["wallet"] = sum(len(re.findall(p, text)) for p in WALLET_PATTERN)
    urls=_urls(text)
    flags=[]; categories=[]
    def add(key,label,advice,severity,category=None):
        n=counts[key]
        if n:
            flags.append(_flag(label,advice,severity,n))
            if category: categories.append(category)
    add("urgency","Urgency or pressure","Do not act immediately. Verify the request independently first.","medium","Urgency")
    add("payment","Money or payment request","Do not transfer money until the recipient and request are independently verified.","high","Payment")
    add("credentials","Credential or verification request","Never share passwords, OTPs, PINs, or verification codes with an unverified contact.","high","Credential theft")
    add("personal","Sensitive personal information","Verify why the information is required and use an official channel.","high","Identity information")
    add("threat","Threat or consequence language","Verify the claim through the organization's official contact information.","high","Threat")
    add("reward","Unexpected prize or reward","Do not pay a fee or provide sensitive information to claim an unexpected reward.","medium","Reward")
    add("investment","Investment or guaranteed-return language","Do not send funds based on guaranteed returns or zero-risk claims. Verify licensing and the firm independently.","high","Investment")
    add("external_contact","External messaging request","Verify the sender before moving the conversation to another messaging platform.","low","External contact")
    add("phone","Phone number detected","A phone number is not proof of legitimacy. Verify it through an official source before calling or sending information.","low","Phone number")
    add("wallet","Crypto wallet address detected","A wallet address alone does not prove fraud, but irreversible transfers should be independently verified before sending funds.","high","Crypto wallet")
    if urls:
        flags.append(_flag("Link detected","Inspect and independently verify the destination before opening it.","medium",len(urls)))
        categories.append("Link")
    url_items=[{"url":u,"flags":_url_flags(u)} for u in urls]

    score=0
    score += min(counts["urgency"]*8,20)
    score += min(counts["payment"]*12,30)
    score += min(counts["credentials"]*18,35)
    score += min(counts["personal"]*14,25)
    score += min(counts["threat"]*16,30)
    score += min(counts["reward"]*10,25)
    score += min(counts["investment"]*14,40)
    score += min(counts["external_contact"]*4,8)
    score += min(counts["phone"]*4,8)
    score += min(counts["wallet"]*18,36)
    score += min(len(urls)*8,20)
    score=min(score,100)

    if score>=60: level,headline="high","Multiple strong warning signals were detected."
    elif score>=30: level,headline="medium","Several warning signals were detected."
    elif score>=10: level,headline="low","A small number of warning signals were detected."
    else: level,headline="none","No automatic warning signals were detected."
    return {"level":level,"score":score,"headline":headline,"flags":flags,"urls":url_items,"categories":list(dict.fromkeys(categories))}

def format_signals(scan):
    if not scan: return "No instant scan was performed."
    lines=[f"Instant heuristic scan level: {scan.get('level','none')}",f"Heuristic signal score: {scan.get('score',0)}/100",f"Summary: {scan.get('headline','')}", "This score is a heuristic hint only; it is not proof of fraud."]
    for f in scan.get("flags",[])[:10]: lines.append(f"- {f.get('label','Signal')}: {f.get('advice','')}")
    for u in scan.get("urls",[])[:10]:
        if u.get("flags"): lines.append(f"- URL {u.get('url')}: "+"; ".join(u["flags"]))
    return "\n".join(lines)
