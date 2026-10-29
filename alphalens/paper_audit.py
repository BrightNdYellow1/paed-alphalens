"""Extract reviewable claims from user-supplied plain text without inventing verification."""
import hashlib
import re

CLAIM_PATTERN=re.compile(r"\b(?:sharpe|return|alpha|accuracy|predict|profit|outperform|risk|bias|significant|p.value|forecast|yield|causal)\b",re.I)
NUM_PATTERN=re.compile(r"(?<!\w)(?:\d+(?:\.\d+)?%?|p\s*[<=>]\s*0?\.\d+)(?!\w)",re.I)
def audit_text(text, max_chars=100000):
    if not isinstance(text,str) or not text.strip() or len(text)>max_chars:
        raise ValueError("Supply 1 to 100000 characters of plain text")
    sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+",text) if s.strip()]
    matches=[]
    for idx,sentence in enumerate(sentences):
        if CLAIM_PATTERN.search(sentence):
            matches.append({"source_sentence":idx+1,"claim":sentence[:1500],
                            "numerical_mentions":NUM_PATTERN.findall(sentence),
                            "status":"UNVERIFIED",
                            "recommended_check":"Find primary data, sampling period, timestamp assumptions, statistical test and replication code."})
    return {"source_sha256":hashlib.sha256(text.encode()).hexdigest(),
            "sentences_read":len(sentences),"candidate_claims":matches[:100],
            "limitations":"Keyword based extraction of text only. No PDF parsing, citation verification, independent statistical replication or factual certification."}
