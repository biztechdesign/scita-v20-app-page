"""One-off: increase readable text sizes across the fold HTML/CSS."""
import re
plan = {
 'folds/scita.css': {r'\.lead': '21px', r'\.body': '18px', r'\.h3': '22px'},
 'folds/01-hero.html': {r'\.tile \.lbl': '18px', r'\.why \.sub': '24px', r'\.why \.it h4': '23px', r'\.why \.it p': '17.5px', r'\.headline \.v': '15px'},
 'folds/03-ai-companion.html': {r'\.feat h4': '22px', r'\.feat p': '17.5px'},
 'folds/04-stay-ahead.html': {r'\.copy \.body': '19px', r'\.pills \.chip': '16px'},
 'folds/05-pwa-speed.html': {r'\.feat h4': '22px', r'\.feat p': '17.5px', r'\.g \.l': '16px', r'\.appicon span': '14px', r'\.appicon b': '17px', r'\.speed \.t': '18px'},
 'folds/06-predictive-search.html': {r'\.node b': '17px', r'\.divider span': '25px'},
 'folds/07-b2b.html': {r'\.c h4': '22px', r'\.c p': '17.5px', r'\.ui \.lock': '14px'},
 'folds/08-industry.html': {r'\.lbl': '19px', r'\.inds b': '18px', r'\.more': '17px', r'\.stat \.s': '19px', r'\.ai \.p': '16px'},
 'folds/09-comparison.html': {r'td': '19.5px', r'\.part': '15px'},
 'folds/10-essential-features.html': {r'\.it h4': '22px', r'\.it p': '17.5px', r'\.note p': '20px'},
}
for f, rules in plan.items():
    s = open(f, encoding='utf8').read()
    for sel, size in rules.items():
        pat = re.compile(r'(^|\n)(\s*' + sel + r'\s*\{[^}]*?font-size:\s*)[0-9.]+px', re.M)
        s, n = pat.subn(lambda m: m.group(1) + m.group(2) + size, s, count=1)
        print(f.split('/')[-1], sel.replace(chr(92), ''), '->', size, 'OK' if n else 'NOT FOUND')
    open(f, 'w', encoding='utf8').write(s)
