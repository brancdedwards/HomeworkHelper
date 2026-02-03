import re, string

def normalize_answer(ans: str, topic: str = "") -> str:
    ans = ans.strip().lower()
    if topic and any(p in topic for p in ["mark", "exclamation", "period"]):
        return ans
    return re.sub(rf"[{re.escape(string.punctuation)}]", "", ans)