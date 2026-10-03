import re

BANNED_WORDS = [
    "in summary", "in conclusion", "delve", "testament to", "furthermore",
    "moreover", "crucial", "vital", "ensure seamless", "it is important to remember",
    "let's dive into", "lets dive into", "dive into", "scientifically correct diagram as i told you to edit it"
]

def audit_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().lower()
    
    found = []
    for word in BANNED_WORDS:
        matches = re.findall(rf"\b{re.escape(word)}\b", content)
        if matches:
            found.append((word, len(matches)))
    return found

print("JOURNAL.md banned words:", audit_file("JOURNAL.md"))
print("README.md banned words:", audit_file("README.md"))
