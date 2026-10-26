# Add after import
from datetime import datetime
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
DATE = datetime.now().strftime("%Y-%m-%d")

# ... teri purani coding same ...

# --- Report save - DATED - Kabhi overwrite nahi hoga!
os.makedirs("reports", exist_ok=True)
os.makedirs("JEEV-Empire/reports", exist_ok=True)

# Purana wala bhi rahega - Email ke liye
with open("JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)

# NAYA - Dated wala - Kabhi nahi urega!
dated_name = f"reports/revert_v4lend_{TIMESTAMP}.md"
dated_name2 = f"JEEV-Empire/reports/revert_v4lend_{TIMESTAMP}.md"

with open(dated_name,"w",encoding="utf-8") as f: f.write(content)
with open(dated_name2,"w",encoding="utf-8") as f: f.write(content)

# Agar JEEV ne 3 bug diye to alag alag split kar de
# Cantina ek report = ek bug mangta hai
if "## Bug" in content or "### Bug" in content:
    bugs = content.split("## Bug")
    for i, bug in enumerate(bugs[1:], 1):
        bug_file = f"reports/revert_v4lend_BUG{i}_{TIMESTAMP}.md"
        with open(bug_file,"w",encoding="utf-8") as f: 
            f.write(f"# Bug {i}\n" + bug)

print(f"✅ REPORT SAVED - DATED - {dated_name} - Kabhi nahi urega!")