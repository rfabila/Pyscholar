def homonyms(G):
    D=[]
    for i in G.author_info:
        for j in G.author_info:
            if i != j:
                if G.author_info[i]['surname'] == G.author_info[j]['surname']:
                     if G.author_info[i]['name'] == G.author_info[j]['name']:
                        print G.author_info[i], G.author_info[j]
                        D.append((i,j))
    return D

def same_info(G):
    D=[]
    for i in G.author_info:
        for j in G.author_info:
            if i != j:
                if (G.author_info[i]['surname'] == G.author_info[j]['surname'] and
                    G.author_info[i]['name'] == G.author_info[j]['name'] and
                    G.author_info[i]['country'] == G.author_info[j]['country'] and
                    G.author_info[i]['affiliation-id'] == G.author_info[j]['affiliation-id']):
                    print G.author_info[i], G.author_info[j]
                    D.append((i,j))
    return D
        
    