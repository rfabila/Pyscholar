import scopus
import networkx
import pickle
import datetime
import dateutil.parser

def load(filename):
    G_file=open(filename,"r")
    G=pickle.load(G_file)
    G_file.close()
    return G


def save_graphml(G,filename):
    """Saves a network created get_network to graphml file"""
    
    if "paper" in G.edges()[0]:
        H=networkx.graph.Graph()
        for e in G.edges():
            H.add_edge(e[0],e[1])
            H[e[0]][e[1]]['weight']=len(G[e[0]][e[1]]['papers'])
        G=H
    networkx.write_graphml(G,filename)
    

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
        self.Q_by_distance=[[] for i in range(self.distance+2)]
        
        self.current_paper=0
        self.current_author=0
        
        splitted_names=[n.split(',') for n in self.core_names]
        self.core_name_IDS={self.core_names[i]:scopus.find_author_scopus_id_by_name(splitted_names[i][0],splitted_names[i][1]) for i in range(len(self.core_names))}
        print self.core_name_IDS
        for lst in self.core_name_IDS.values():
            self.core_ids.extend(lst)
        
        
        self.G=networkx.graph.Graph()
        
        self.alias={}
        for x in self.core_ids:
            if isinstance(x,list):
                y=min(x)
                for z in x:
                    self.alias[str(z)]=str(y)
                    self.Q_by_distance[0].append(str(z))
                self.G.add_node(str(y))
                self.nodes_by_distance[0].add(str(y))
            else:
                self.Q_by_distance[0].append(str(x))
                self.alias[str(x)]=str(x)
                self.G.add_node(str(x))
                self.nodes_by_distance[0].add(str(x))
                
        
        
        #[self.G.add_node(str(x)) for x in self.core_ids]
        
        
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
        
     
    def create_network(self):
        """Creates the collaboration network."""
        
        for current_dist in range(self.distance+2):
            if len(self.Q_by_distance[current_dist])>0:
                break
        while current_dist<=self.distance:
            while len(self.Q_by_distance[current_dist])>0:
                print "current distance",current_dist
                
                author=self.Q_by_distance[current_dist][-1]
                if author in self.alias:
                    x=self.alias[author]
                else:
                    x=author
                
                print "current_author",author
                papers=scopus.get_publications(author)
                papers=list(papers)
                start_paper=self.current_paper
                for paper_id in range(start_paper,len(papers)):
                    self.current_paper=paper_id
                    print "current paper ", papers[paper_id]
                    paper_id=papers[paper_id]
                    authors=scopus.get_authors_from_paper(str(paper_id))
                    for y in authors:
                        
                        if str(y) in self.alias:
                            y=self.alias[str(y)]
                        else:
                            y=str(y)
                            self.alias[y]=y
                              
                        if not self.G.has_node(y):
                            self.nodes_by_distance[current_dist+1].add(y)
                            if current_dist<self.distance:
                                self.Q_by_distance[current_dist+1].append(y)
                            
                        if x!=y:
                            if self.G.has_edge(x,y):
                                self.G[x][y]["papers"].add(str(paper_id))
                            else:
                                self.G.add_edge(x,y)
                                self.G[x][y]["papers"]=set()
                                self.G[x][y]["papers"].add(str(paper_id))
                self.Q_by_distance[current_dist].pop()
                self.current_paper=0
            current_dist+=1
        self.network_computed=True
    
    def add_alias(self,author,author_alias):
        """Add an alias to an author, note that the author must be already part of the network."""
        author_alias=str(author_alias)
        if author_alias not in self.alias:
            author=self.alias[str(author)]
            self.alias[author_alias]=author
            self.network_computed=False
            for d in range(self.distance+1):
                if author in self.nodes_by_distance[d]:
                    break
            self.Q_by_distance[d].append(author_alias)
            
                                  
    def get_network(self,start_year=None,end_year=None,start_date=None,end_date=None,use_names=True,use_paper_id=False):
        """Returns a networkX graph with the given parameters."""
        if not self.network_computed:
            self.create_network()
        self.get_paper_info()
        
        if start_year!=None:
            start_date=datetime.date(int(start_year),1,1)
        if end_year!=None:
            end_date=datetime.date(int(start_year),1,1)
            
        if start_date==None:
            start_date=datetime.date.min
        
        if end_date==None:
            end_date=datetime.date.max
             
        H=networkx.graph.Graph()
        
        for x in self.G.nodes():
            H.add_node(x)
        
        for e in self.G.edges():
            for paper_id in self.G[e[0]][e[1]]['papers']:
                paper_date=dateutil.parser.parse(self.paper_info[paper_id]['date']).date()
                if paper_date>=start_date and paper_date<=end_date:
                    if H.has_edge(e[0],e[1]):
                        if use_paper_id:
                            H[e[0]][e[1]]['papers'].add(str(paper_id))
                        else:
                            H[e[0]][e[1]]['weight']+=1
                    else:
                        H.add_edge(e[0],e[1])
                        if use_paper_id:
                            H[e[0]][e[1]]['papers']=set()
                            H[e[0]][e[1]]['papers'].add(str(paper_id))
                        else:
                            H[e[0]][e[1]]['weight']=1
                            
        if use_names:
            F=networkx.graph.Graph()
            for e in H.edges():
                print e
                n1=""
                n2=""
                
                if self.author_info[e[0]]['name']!=None:
                    n1+=self.author_info[e[0]]['name']
                    n1+=" "
                    
                if self.author_info[e[0]]['surname']!=None:
                    n1+=self.author_info[e[0]]['surname']
                    
                if self.author_info[e[1]]['name']!=None:
                    n2+=self.author_info[e[1]]['name']
                    n2+=" "
                    
                if self.author_info[e[1]]['surname']!=None:
                    n2+=self.author_info[e[1]]['surname']
                    
                F.add_edge(n1,n2)
                print n1
                print n2
                F[n1][n2]=H[e[0]][e[1]]
            H=F
        
        return H
    

    
                        
                
                
                
            
        
    
    
