"""Verify deck headlines against the reading draft, and scan the deck copy for forbidden content."""
import re, sys, json
sys.path.insert(0, '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/build')
from deck2_content import EN, BM
draft = open('/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/deck-reading-draft.md').read()
keys = ['b01h', 'b02h', 'b03h', 'b03bh', 'b04h', 'b05h', 'b06h', 'b07h', 'b08h', 'b09h', 'b10h', 'b10bh', 'b11h', 'b12h']
def norm(t):
    # Match the builder's final, owner-approved English terminology.
    for old, new in (('pupils', 'students'), ('Pupils', 'Students'), ('pupil', 'student'), ('Pupil', 'Student')):
        t = re.sub(r'(?<![-_\w])' + old + r'(?![-_\w])', new, t)
    return re.sub(r'\s+', ' ', t.replace('’', "'").replace('‘', "'")).strip()
d = norm(draft)
for k in keys:
    for lang, D in (('EN', EN), ('BM', BM)):
        h = norm(D[k])
        print(('OK  ' if h in d else 'MISS'), lang, k, h[:90])
html = open('/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/kota-buku-deck.html').read()
text = re.sub(r'data:image/[^"]+', '', html)
text = re.sub(r'data:[^;\s]+;base64,[A-Za-z0-9+/=]+', '', text)
print('em dashes:', text.count('—'))
print('RM figures:', re.findall(r'RM\s?\d[\d,.]*', text)[:5])
print('DSKP/curriculum codes:', re.findall(r'\bDSKP\b|\b[A-Z]{2,4}\d\.\d', text)[:5])
print('awarded/selected/approved by:', re.findall(r'(?i)awarded to|selected by|approved by (?:kota|kpm)', text)[:5])
print('credits present:', 'not an awarded contract' in text, bool(re.search(r'bukan kontrak yang (?:telah )?dianugerahkan', text)))
print('honest present:', 'people in images are generated' in text, 'orang dalam imej dijana' in text)
# BM strings that are identical to EN (possible untranslated)
same = [k for k in EN if EN[k] == BM[k]]
print('identical EN/BM keys:', same)
