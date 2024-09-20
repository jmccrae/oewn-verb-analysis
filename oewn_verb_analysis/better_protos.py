import csv
import yaml
from glob import glob
from collections import defaultdict

hyps = defaultdict(list)

for file in glob('../english-wordnet/src/yaml/verb.*.yaml'):
    with open(file) as f:
        data = yaml.load(f, Loader=yaml.CLoader)
        for ssid, d in data.items():
            hyps[ssid] = d.get('hypernym', [])
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

with open("better_protos.csv", "w") as f:
    better_protos = csv.writer(f)
    for va, bnids in va2bn.items():
        score = defaultdict(int) 
        for bnid in bnids:
            ssid = bn2oewn.get(bnid, '')
            score[bnid] = len([b for b in bnids if ssid in indirect_hyps.get(bn2oewn.get(b, ''), [])])
        current = va_key[va]
        if va == 'va:0003f':
            print(score)
        if max(score.values()) > score[current]:
            better_protos.writerow([va, current, max(score, key=score.get)])
