import csv
import yaml
from glob import glob
from collections import defaultdict

hyps = defaultdict(list)
members = defaultdict(list)
defns = defaultdict(str)

for file in glob('../english-wordnet/src/yaml/verb.*.yaml'):
    with open(file) as f:
        data = yaml.load(f, Loader=yaml.CLoader)
        for ssid, d in data.items():
            hyps[ssid] = d.get('hypernym', [])
            members[ssid] = d.get('members', [])
            defns[ssid] = d.get('definition', [''])[0]
print("HYP", len(hyps))

indirect_hyps = {k: v.copy() for k, v in hyps.items()}

changed = True
while changed:
    changed = False
    for ssid, hyp in indirect_hyps.items():
        for h in hyp:
            for h2 in hyps[h]:
                if h2 not in indirect_hyps[ssid]:
                    indirect_hyps[ssid].append(h2)
                    changed = True
    print("CHANGED", changed)

wn2bn = {}

with open('VerbAtlas-1.1.0/bn2wn.tsv') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for row in reader:
        wnid = row[1][3:-1] + '-' + row[1][-1]
        wn2bn[wnid] = row[0]

print("BN2WN", len(wn2bn))

ili2bn = {}

with open('../cili/ili-map-pwn30.tab') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for row in reader:
        if row[1] in wn2bn:
            ili2bn[row[0]] = wn2bn[row[1]]

print("ILI2BN", len(ili2bn))

oewn2bn = {}

with open('../cili/ili-map-pwn31.tab') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for row in reader:
        if row[0] in ili2bn:
            oewn2bn[row[1]] = ili2bn[row[0]]

print("OEWN2BN", len(oewn2bn))

bn2oewn = {v: k for k, v in oewn2bn.items()}

va2bn = defaultdict(list)

with open('VerbAtlas-1.1.0/VA_bn2va.tsv') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for row in reader:
        va2bn[row[1]].append(row[0])

va_key = {}

with open('VerbAtlas-1.1.0/VA_frame_info.tsv') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for row in reader:
        bnid = row[3][:12]
        if not bnid.endswith('v'):
            bnid = bnid + 'v'
        va_key[row[0]] = bnid

print("VA2BN", len(va2bn))

hyp_agree = 0
hyp_disagree = 0
hyp_new = 0

with open('disagreement.csv', 'w') as f, open('new.csv', 'w') as g:
    disagreements = csv.writer(f)
    disagreements.writerow(['Members', 'Definition', 'Hyp Members', 'Hyp Definition', 'VerbAtlas Key', 'VerbAtlas Key Definition'])
    new = csv.writer(g)
    new.writerow(['Members', 'Definition', 'VerbAtlas Key', 'VerbAtlas Key Definition'])
    for va, bns in va2bn.items():
        key_bn = va_key[va]
        if key_bn not in bn2oewn:
            print("KEY", va, key_bn)
            continue
        key_ssid = bn2oewn[key_bn]
        for bn in bns:
            if bn in bn2oewn:
                ssid = bn2oewn[bn]
                if bn != key_bn:
                    # We propose the link bn -> key_bn
                    if ssid not in indirect_hyps or not indirect_hyps[ssid]:
                        hyp_new += 1
                        new.writerow([", ".join(members[ssid]), defns[ssid].replace(";", ""), 
                            ", ".join(members[key_ssid]), defns[key_ssid].replace(";", "")])
                    elif key_ssid in indirect_hyps[ssid]:
                        hyp_agree += 1
                    else:
                        disagreements.writerow([", ".join(members[ssid]), defns[ssid].replace(";", ""), 
                            ", ".join(members[hyps[ssid][0]]), defns[hyps[ssid][0]].replace(";", ""),
                            ", ".join(members[key_ssid]), defns[key_ssid].replace(";", "")])
                        hyp_disagree += 1

print("AGREE", hyp_agree)
print("DISAGREE", hyp_disagree)
print("NEW", hyp_new)
