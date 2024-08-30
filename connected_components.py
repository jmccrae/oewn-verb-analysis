import networkx as nx
import wn

def build_troponymy_graph(lexicon):
    G = nx.Graph()
    for synset in wn.synsets(pos="v", lexicon=lexicon):
        G.add_node(synset.id)
        for hypernym in synset.hypernyms():
            G.add_edge(synset.id, hypernym.id)
    return G

def add_related(G, lexicon):
    for synset in wn.synsets(pos="v", lexicon=lexicon):
        for synset2 in synset.get_related():
            G.add_edge(synset.id, synset2.id)

def add_derivs(G, lexicon):
    for synset in wn.synsets(pos="v", lexicon=lexicon):
        for sense in synset.senses():
            for sense2 in sense.get_related():
                synset2 = sense2.synset()
                if synset2.pos == "n":
                    G.add_edge(synset.id, "nouns")


lexicons = ['omw-en', 'omw-en31', 'ewn:2019', 'ewn:2020', 'oewn:2021',
            'oewn:2022', 'oewn:2023']

for lexicon in lexicons:
    wn.download(lexicon)

wn.add("../../globalwordnet/english-wordnet/wn.xml")
lexicons.append("oewn:2024")

for lexicon in lexicons:
    G = build_troponymy_graph(lexicon)
    print(f"Number of connected components in {lexicon}: {nx.number_connected_components(G)}")
    add_related(G, lexicon)
    print(f"Number of connected components in {lexicon} with related: {nx.number_connected_components(G)}")

    i = 0

    for c in nx.connected_components(G):
        print(len(c), list(c)[:10])
        i += 1
        if i > 10:
            break
    add_derivs(G, lexicon)
    print(f"Number of connected components in {lexicon} with related and derivs: {nx.number_connected_components(G)}")

