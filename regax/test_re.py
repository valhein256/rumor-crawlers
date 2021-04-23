import re


r_str = r'，外交部[\s\S]*(說明|如下(:|：))'
# r_str = r'外交部.[\s\S*]|澄清|說明|如下|說明如下:|：*?'

with open("./mofa_test", "r") as f:
    lines = f.readlines()

matchs = list()
not_matchs = list()
for i, s in enumerate(lines):
    match = re.search(r_str, s)
    if match:
        matchs.append(s)
        print(i, s, bool(re.search(r_str, s)), match.group())
    else:
        not_matchs.append(s)
        print(i, s, bool(re.search(r_str, s)))

print("Match")
for i, m in enumerate(matchs):
    print(i, m)

print("Not Match")
for i, m in enumerate(not_matchs):
    print(i, m)

for i, s in enumerate(lines):
    match = re.search(r_str, s)
    newstr = re.sub(r_str, "", s)
    print(i, newstr)
    print(i, s)
    if match:
        print(i, match.group(), "\n")
    else:
        print(i, "\n")
