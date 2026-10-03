import json
import re

with open("portal_entries_dump.json", "r", encoding="utf-8") as f:
    portal = json.load(f)

with open("JOURNAL.md", "r", encoding="utf-8") as f:
    journal_text = f.read()

BANNED_WORDS = [
    "in summary", "in conclusion", "delve", "testament to", "furthermore",
    "moreover", "crucial", "vital", "ensure seamless", "it is important to remember",
    "let's dive into", "lets dive into", "dive into", "scientifically correct diagram as i told you to edit it"
]

REQUIRED_MAKER_ELEMENTS = [
    ("breadboard_bench_testing", ["breadboard", "multimeter", "i2c", "ssd1306"]),
    ("soldering_flush_trimming", ["flush", "cutter", "lipo", "puncture", "kapton"]),
    ("battery_management_resistor", ["tp4056", "resistor", "200ma", "400mah"]),
    ("firmware_displayio_optimization", ["displayio", "tilegrid", "30fps", "animation"])
]

print("=== AUDIT REPORT ===")
for entry_name, data in portal.items():
    val = data["val"].lower()
    imgs = data["images"]
    print(f"\n--- {entry_name} ---")
    print(f"Total length: {len(data['val'])} chars")
    print(f"Images count: {len(imgs)}")
    
    # Check banned words
    banned_found = [w for w in BANNED_WORDS if w in val]
    print(f"Banned words found: {banned_found}")
    
# Check overall repository / entries for maker elements
combined_text = (journal_text + " " + " ".join([d["val"] for d in portal.values()])).lower()

print("\n--- Genuine Maker Elements Check ---")
for elem_name, keywords in REQUIRED_MAKER_ELEMENTS:
    found_kw = [k for k in keywords if k in combined_text]
    print(f"{elem_name}: {len(found_kw)}/{len(keywords)} matches ({found_kw})")

# Banned words across full JOURNAL.md
journal_banned = [w for w in BANNED_WORDS if w in journal_text.lower()]
print(f"\nBanned words in JOURNAL.md: {journal_banned}")
