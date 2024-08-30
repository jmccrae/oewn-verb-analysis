import wn
from wn.similarity import path, lch, wup, res, jcn, lin
from scipy.stats import pearsonr, spearmanr, kendalltau
from collections import defaultdict
import csv
from tqdm import tqdm

def load_simverb():
    simverb = {}
    with open("SimVerb-3500.txt") as f:
        lines = f.readlines()
        for line in lines:
            word1, word2, _, score, rel = line.split('\t')
            if rel != "ANTONYMS":
                simverb[(word1, word2)] = float(score)
    return simverb
        

simverb = load_simverb()

def find_sim(word1, word2, sim_fn, ewn):
    best = 0
    for synset1 in ewn.synsets(word1, pos="v"):
        for synset2 in ewn.synsets(word2, pos="v"):
            try:
                score = sim_fn(synset1, synset2)
            except wn.Error:
                continue
            if score > best:
                best = score
    return best

def load_ic():
    ic = wn.ic.load('~/nltk_data/corpora/wordnet_ic/ic-brown.dat', ewn)
    for k,vs in ic.items():
        for s, v in vs.items():
            if v == 0:
                vs[s] = 0.1    
    return {
            k: defaultdict(lambda: 0.1, v) for k, v in ic.items()
            }
    

for lexicon in ['omw-en', 'oewn:2024']:
    ewn = wn.Wordnet(lexicon)
    path_sims = []
    lch_sims = []
    wup_sims = []
    res_sims = []
    jcn_sims = []
    lin_sims = []
    sims = []
    ic = load_ic()
    with open(f"similarity_{lexicon}.txt", "w") as f:
        out = csv.writer(f)
        out.writerow(["word1", "word2", "path", "lch", "wup", 
                      "res", "jcn", "lin", "simverb"])
        for (word1, word2), sim in tqdm(simverb.items()):
            if not ewn.synsets(word1, pos="v") or not ewn.synsets(word2, pos="v"):
                continue
            path_sims.append(find_sim(word1, word2, path, ewn))
            lch_sims.append(find_sim(word1, word2, 
                                     lambda s1, s2: lch(s1, s2, 20, True), ewn))
            wup_sims.append(find_sim(word1, word2, wup, ewn))
            res_sims.append(find_sim(word1, word2, 
                                     lambda s1, s2: res(s1, s2, ic), ewn))
            jcn_sims.append(find_sim(word1, word2, 
                                     lambda s1, s2: jcn(s1, s2, ic), ewn))
            lin_sims.append(find_sim(word1, word2,
                                     lambda s1, s2: lin(s1, s2, ic), ewn))
            sims.append(sim)
            out.writerow([word1, word2, path_sims[-1], 0, wup_sims[-1],
                          0, 0, 0, sim])
    print("Lexicon:", lexicon)
    print("----------------")
    print("")
    print("Similarity wup Pearson:", pearsonr(wup_sims, sims).statistic)
    print("Similarity wup Spearman:", spearmanr(wup_sims, sims).statistic)
    print("Similarity wup Kendall:", kendalltau(wup_sims, sims).statistic)
    print("Similarity path Pearson:", pearsonr(path_sims, sims).statistic)
    print("Similarity path Spearman:", spearmanr(path_sims, sims).statistic)
    print("Similarity path Kendall:", kendalltau(path_sims, sims).statistic)
    #print("Similarity lch Pearson:", pearsonr(lch_sims, sims).statistic)
    #print("Similarity lch Spearman:", spearmanr(lch_sims, sims).statistic)
    #print("Similarity lch Kendall:", kendalltau(lch_sims, sims).statistic)
    print("Similarity res Pearson:", pearsonr(res_sims, sims).statistic)
    print("Similarity res Spearman:", spearmanr(res_sims, sims).statistic)
    print("Similarity res Kendall:", kendalltau(res_sims, sims).statistic)
    print("Similarity jcn Pearson:", pearsonr(jcn_sims, sims).statistic)
    print("Similarity jcn Spearman:", spearmanr(jcn_sims, sims).statistic)
    print("Similarity jcn Kendall:", kendalltau(jcn_sims, sims).statistic)
    print("Similarity lin Pearson:", pearsonr(lin_sims, sims).statistic)
    print("Similarity lin Spearman:", spearmanr(lin_sims, sims).statistic)
    print("Similarity lin Kendall:", kendalltau(lin_sims, sims).statistic)
    print("")

