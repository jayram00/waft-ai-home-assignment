import re, ipaddress, phonenumbers, tldextract
from typing import Dict, Iterable, List

RE_URL = re.compile(r"https?://[\w\-\._~:/?#\[\]@!$&'()*+,;=%]+", re.I)
RE_EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
RE_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_GA = re.compile(r"\bUA-\d{4,}-\d+\b", re.I)
RE_ADSENSE = re.compile(r"\bpub-\d{16}\b", re.I)

SOCIAL_PATTERNS = {
    'twitter': re.compile(r"(?:twitter|x)\.com/(?:#!/)?([A-Za-z0-9_]{1,15})", re.I),
    'facebook': re.compile(r"facebook\.com/([A-Za-z0-9\.\-_]{3,})", re.I),
    'instagram': re.compile(r"instagram\.com/([A-Za-z0-9\._]{1,30})", re.I),
    'youtube': re.compile(r"youtube\.com/(?:c/|channel/|@)?([A-Za-z0-9_\-]{1,})", re.I),
    'linkedin': re.compile(r"linkedin\.com/(?:in|company)/([A-Za-z0-9\-_%]+)", re.I),
    'tiktok': re.compile(r"tiktok\.com/@([A-Za-z0-9\._]{2,24})", re.I),
    'telegram': re.compile(r"t\.me/([A-Za-z0-9_]{3,64})", re.I),
    'vk': re.compile(r"vk\.com/([A-Za-z0-9_\.]+)", re.I),
    'reddit': re.compile(r"reddit\.com/(?:u|user)/([A-Za-z0-9_\-]{3,20})", re.I),
    'truthsocial': re.compile(r"truthsocial\.com/@([A-Za-z0-9_\.]+)", re.I),
    'parler': re.compile(r"parler\.com/profile/([A-Za-z0-9_\.]+)", re.I),
}

DOMAIN_RE = re.compile(r"\b(?:(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,})\b", re.I)

def normalize_domain(d: str) -> str:
    ext = tldextract.extract(d)
    parts = [p for p in [ext.domain, ext.suffix] if p]
    return ".".join(parts)

def extract_indicators(text: str) -> List[Dict]:
    found: List[Dict] = []
    # URLs
    for m in RE_URL.finditer(text):
        url = m.group(0).rstrip(').,;')
        found.append({"type":"url","value":url,"normalized":url.lower(),"platform":None,"confidence":0.95})
        dom = normalize_domain(url)
        if dom:
            found.append({"type":"domain","value":dom,"normalized":dom.lower(),"platform":None,"confidence":0.9})

    # Domains
    for m in DOMAIN_RE.finditer(text):
        dom = normalize_domain(m.group(0))
        if dom:
            found.append({"type":"domain","value":dom,"normalized":dom.lower(),"platform":None,"confidence":0.85})

    # Emails
    for m in RE_EMAIL.finditer(text):
        v = m.group(0)
        found.append({"type":"email","value":v,"normalized":v.lower(),"platform":None,"confidence":0.95})

    # IPs
    for m in RE_IP.finditer(text):
        ip = m.group(0)
        try:
            ipaddress.ip_address(ip)
            found.append({"type":"ip","value":ip,"normalized":ip,"platform":None,"confidence":0.9})
        except Exception:
            pass

    # Phones
    for m in re.finditer(r"[+\(]?[0-9][0-9\s\-\(\)]{6,}[0-9]", text):
        raw = m.group(0)
        for cc in ["FR", "DE", "GB", "US"]:
            try:
                num = phonenumbers.parse(raw, cc)
                if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
                    e164 = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
                    found.append({"type":"phone","value":raw,"normalized":e164,"platform":None,"confidence":0.7})
                    break
            except Exception:
                continue

    # Socials
    for platform, regex in SOCIAL_PATTERNS.items():
        for m in regex.finditer(text):
            handle = m.group(1)
            norm = f"{platform}:{handle.lower()}"
            found.append({"type":"social","value":handle,"normalized":norm,"platform":platform,"confidence":0.9})

    # Trackers
    for m in RE_GA.finditer(text):
        found.append({"type":"ga","value":m.group(0),"normalized":m.group(0).upper(),"platform":None,"confidence":0.95})
    for m in RE_ADSENSE.finditer(text):
        found.append({"type":"adsense","value":m.group(0),"normalized":m.group(0).lower(),"platform":None,"confidence":0.95})

    return found
