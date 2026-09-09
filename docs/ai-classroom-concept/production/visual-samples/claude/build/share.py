"""Partner share copy of the deck: identical, minus the presenter-only 'R resets the demo' hint."""
import re
D = '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/'
s = open(D + 'kota-buku-deck.html').read()
s2, n = re.subn(r'<span class="sep"></span><span data-i="hintKey">[^<]*</span>', '', s)
assert n == 1, n
open(D + 'kota-buku-deck-share.html', 'w').write(s2)
print('share copy written', len(s2))
