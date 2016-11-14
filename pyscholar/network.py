import scopus
import networkx
import pickle

def load(filename):
    G_file=open(filename,"r")
    G=pickle.load(G_file)
    G_file.close()
    return G
    

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

def load_collaboration_network(filename):
    file_G=open(filename,"r")
    G=pickle.load(file_G)
    return G

class CollaborationNetwork():
    def __init__(self,core_names=[],distance=0,core_ids=[]):
        self.core_ids=core_ids
        self.core_names=core_names
        self.paper_info={}
        self.author_info={}
        self.distance=distance
        self.network_computed=False
        self.computed_distance=-1
        self.nodes_by_distance=[set() for i in range(self.distance+2)]
        
        self.current_paper=0
        self.current_author=0
        
        splitted_names=[n.split(',') for n in self.core_names]
        self.core_name_IDS={self.core_names[i]:scopus.find_author_scopus_id_by_name(splitted_names[i][0],splitted_names[i][1]) for i in range(len(self.core_names))}
        print self.core_name_IDS
        for lst in self.core_name_IDS.values():
            self.core_ids.extend(lst)
        
        [self.nodes_by_distance[0].add(str(x)) for x in self.core_ids]
        self.G=networkx.graph.Graph()
        [self.G.add_node(str(x)) for x in self.core_ids]
        
        
        #self.create_network()
        #self.get_paper_info()
        #self.get_author_info()
    
    def copy_from_other(self,G):
        self.core_ids=G.core_ids
        self.core_names=G.core_names
        self.paper_info=G.paper_info
        self.author_info=G.author_info
        self.distance=G.distance
        self.network_computed=G.network_computed
        self.computed_distance=G.computed_distance
        self.nodes_by_distance=G.nodes_by_distance
        self.current_author=G.current_author
        self.current_paper=G.current_paper
        self.core_name_IDS=G.core_name_IDS
        self.G=G.G
    
    def get_paper_info(self):
        for e in self.G.edges():
            papers=self.G[e[0]][e[1]]["papers"]
            for paper_id in papers:
                if paper_id not in self.paper_info:
                    print paper_id
                    self.paper_info[paper_id]=scopus.paper_info(paper_id)
                    
    def get_author_info(self):
        for author_id in self.G.nodes():
            if  author_id not in self.author_info:
                self.author_info[author_id]=scopus.author_info(author_id)
                
    def save(self,file_name):
        file_G=open(file_name,'w')
        pickle.dump(self,file_G)
        file_G.close()
        
    
        
    
        
    def create_network(self,heuristic=None):
        """Creates the collaboration network."""
        
        distance_start=self.computed_distance+1
        for d in range(distance_start,self.distance+1):
            Q=list(self.nodes_by_distance[d])
            start=self.current_author
            for i in range(start,len(Q)):
                self.current_author=i
                print "current_author", self.current_author
                print "Author_id", Q[i]
                papers=scopus.get_publications(Q[i])
                print Q[i]
                papers=list(papers)
                start_paper=self.current_paper
                for paper_id in range(start_paper,len(papers)):
                    self.current_paper=paper_id
                    print "current paper ", papers[paper_id]
                    paper_id=papers[paper_id]
                    authors=scopus.get_authors_from_paper(str(paper_id))
                    for y in authors:
                        y=str(y)
                        if not self.G.has_node(y):
                            self.nodes_by_distance[d+1].add(y)
                        if Q[i]!=y:
                            if self.G.has_edge(Q[i],y):
                                self.G[Q[i]][y]["papers"].add(str(paper_id))
                            else:
                                self.G.add_edge(Q[i],y)
                                self.G[Q[i]][y]["papers"]=set()
                                self.G[Q[i]][y]["papers"].add(str(paper_id))
                self.current_paper=0
                                
            self.current_author=0
            self.computed_distance=d
        self.network_computed=True
                
        
        
        
        
    #def update_paper_info(self):
     #   for e in self.G.edges():
      #      for p in self.G[e[0]][e[1]]["papers"]:
       #         if p not in self.paper_info:
        #            self.paper_info[p]=scopus.paper_info(p)
    
    
    
