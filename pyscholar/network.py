import scopus
import networkx

def collaboration_network_by_ids(author_ids,distance=0):
    """Creates a collaboration network with the given list of scopus
    author ids.  The distance parameter specifies at what distance from the authors in names will other nodes by included.
       For example, if distance=0 only those authors in names will be part of the network. If distance=1 then
       any author who is a coauthor with someone in author_ids will be included."""
    N=[]
    C=[]
    G=networkx.graph.Graph()
    for x in author_ids:
        N.append(str(x))
    #Ver lo de la distancia. Una opcion es calcular las aristas entre vertices
    #a distancia d o bien dejarlos como hojas.
    for i in range(distance+1):
        C=N
        N=[]
        for x in C:
            G.add_node(x)
        for x in C:
            #print x
            papers=scopus.get_publications(x)
            #print papers
            for paper_id in papers:
                #print paper_id
                authors=scopus.get_authors_from_paper(str(paper_id))
                for y in authors:
                    if not G.has_node(y):
                        N.append(y)
                    else:
                        if x!=y:
                            if G.has_edge(x,y):
                                G[x][y]["papers"].append(paper_id)
                            else:
                                G.add_edge(x,y)
                                G[x][y]["papers"]=[paper_id]
    H=CollaborationNetwork(G)
    return H

def collaboration_network_by_names(names,distance=0):
    """Creates a collaboration network with a given list of names.
       The first and last names should be sperated by comma.
       The distance parameter specifies at what distance from the authors in names will other nodes by included.
       For example if distance=0 only those authors in names will be part of the network. If distance=1 then
       any author who is a coauthor with someone in names will be included."""
    splitted_names=[n.split(',') for n in names]
    IDS={names[i]:scopus.find_author_scopus_id_by_name(splitted_names[i][0],splitted_names[i][1]) for i in range(len(names))}
    author_ids=[]
    for lst in IDS.values():
        for x in lst:
            author_ids.append(str(x))
    G=collaboration_network_by_ids(author_ids,distance=distance)
    G.core_names=IDS
    return G

class CollaborationNetwork():
    def __init__(self,G=None,core_names=None):
        self.G=G
        self.core_names=core_names
        self.paper_info={}
        #self.update_paper_info()
        
    def update_paper_info(self):
        for e in self.G.edges():
            for p in self.G[e[0]][e[1]]["papers"]:
                if p not in self.paper_info:
                    self.paper_info[p]=scopus.paper_info(p)
    
    
    