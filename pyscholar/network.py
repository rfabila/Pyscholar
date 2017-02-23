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
        self.affiliation_info={}
        
        self.current_paper=0
        self.current_author=0
        
        splitted_names=[n.split(',') for n in self.core_names]
        self.core_name_IDS={self.core_names[i]:scopus.find_author_scopus_id_by_name(splitted_names[i][0],splitted_names[i][1]) for i in range(len(self.core_names))}
        print self.core_name_IDS
        for lst in self.core_name_IDS.values():
            self.core_ids.extend(lst)
        
        self.paper_ids_set=set()
        
        #self.G=networkx.graph.Graph()
        
        self.alias={}
        
        for x in core_ids:
            if isinstance(x,list):
                for y in x:
                    self.author_info[str(y)]=False
                    self.alias[str(y)]=str(x[0])
                    self.Q_by_distance[0].append(str(y))
                    self.nodes_by_distance[0].add(str(y))
            else:
                self.author_info[str(x)]=False
                self.Q_by_distance[0].append(str(x))
                self.alias[str(x)]=str(x)
                self.nodes_by_distance[0].add(str(x))
                
                
        
    
    #needs updating
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
    
    def get_paper_info(self):
        Papers=set()
        for paper_id in self.paper_ids_set:
            if paper_id not in self.paper_info:
                    Papers.add(paper_id)
        scopus.download_paper_info(list(Papers))
        
        for paper_id in self.paper_ids_set:
            if paper_id not in self.paper_info:
                self.paper_info[paper_id]=scopus.paper_info(paper_id)
    
    
    def get_author_info(self):
        Q=[]
        for x in self.author_info:
            if  not self.author_info[x]:
                Q.append(x)
        print "Downloading info"
        scopus.download_author_info(Q)
        print "Adding info"
        for x in self.author_info:
            if not self.author_info[x]:
                try:
                    D=scopus.author_info(x,strict=True)
                    self.author_info[x]=D
                except scopus.Alias_Exception as e:
                    #Whait if the alias has an alias!???
                    self.author_info[x]=e
                    self.alias[e.author_id]=e.alias
                    D=scopus.author_info(e.alias,strict=True)
                    self.author_info[e.alias]=D
    
    def get_affiliation_info(self):
        """Get information about the author affiliations. get_author_info
        should have been called prior to call this function."""
        Q=set()
        for x in self.author_info:
            print x
            s=self.author_info[x]['affiliation-id']
            if s!='':
                Q.add(s)
        Q=list(Q)
        print Q
        scopus.download_affiliation_info(Q)
        for x in Q:
            print x
            self.affiliation_info[x]=scopus.affiliation_info(x)
    
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
            
            scopus.download_publications(self.Q_by_distance[current_dist])
            
            while len(self.Q_by_distance[current_dist])>0:
                print "current distance",current_dist
                
                author=self.Q_by_distance[current_dist][-1]
                
                if author not in self.author_info:
                    self.author_info[author]=False
                # 
                # if author in self.alias:
                #     x=self.alias[author]
                # else:
                #     x=author
                
                print "current_author",author
                papers=scopus.get_publications(author)
                
                scopus.download_authors_from_papers(papers)
                
                start_paper=self.current_paper
                for paper_id in range(start_paper,len(papers)):
                    self.current_paper=paper_id
                    print "current paper ", papers[paper_id]
                    paper_id=papers[paper_id]
                    self.paper_ids_set.add(str(paper_id))
                    authors=scopus.get_authors_from_paper(str(paper_id))
                    for y in authors:
                        
                        if y not in self.author_info:
                            self.author_info[y]=False
                            self.nodes_by_distance[current_dist+1].add(y)
                            if current_dist<self.distance:
                                self.Q_by_distance[current_dist+1].append(y)
                        
                        if not str(y) in self.alias:
                            y=str(y)
                            self.alias[y]=y
                         
                             
                        # if not self.G.has_node(y):
                        #     self.nodes_by_distance[current_dist+1].add(y)
                        #     if current_dist<self.distance:
                        #         self.Q_by_distance[current_dist+1].append(y)
                            
                        #if author!=y:
                         #   if self.G.has_edge(author,y):
                          #      self.G[author][y]["papers"].add(str(paper_id))
                           # else:
                            #    self.G.add_edge(author,y)
                             #   self.G[author][y]["papers"]=set()
                             #   self.G[author][y]["papers"].add(str(paper_id))
                self.Q_by_distance[current_dist].pop()
                self.current_paper=0
            current_dist+=1
        self.network_computed=True
        
    def get_alias(self,x):
        if self.alias[x]==x:
            return x
        return self.get_alias(self.alias[x])
    
    
    # def add_alias(self,author,author_alias):
    #     """Add an alias to an author, note that the author must be already part of the network."""
    #     author_alias=str(author_alias)
    #     if author_alias not in self.alias:
    #         author=self.alias[str(author)]
    #         self.alias[author_alias]=author
    #         self.network_computed=False
    #         for d in range(self.distance+1):
    #             if author in self.nodes_by_distance[d]:
    #                 break
    #         self.Q_by_distance[d].append(author_alias)
            
    
    def get_info(self):
        self.get_author_info()
        self.get_paper_info()
        self.get_affiliation_info()
    
    # def get_core_network(self):
    #     H=networkx.graph.Graph()
    #     for v in self.G.nodes():
    #         H.add_node(v)
    #     for e in self.G.edges():
    #         H.add_edge(e[0],e[1])
    #         H[e[0]][e[1]]['weight']=len(G[e[0]][e[1]]['papers'])
    #     
    #     return H
    
    def get_network2(self,start_year=None,end_year=None,start_date=None,end_date=None,label_function=None):
        """Returns a networkX graph with the given parameters."""
        #if not self.network_computed:
         #   self.create_network()
        #self.get_paper_info()
        
        if start_year!=None:
            start_date=datetime.date(int(start_year),1,1)
        if end_year!=None:
            end_date=datetime.date(int(start_year),1,1)
            
        if start_date==None:
            start_date=datetime.date.min
        
        if end_date==None:
            end_date=datetime.date.max
             
        H=networkx.graph.Graph()
        author_dict={}
        for x in self.author_info:
            x=self.get_alias(x)
            if x not in author_dict:
                author_dict[x]=label_function(x)
        #Cuidado!!! tal cual esta agrupa homonimos
        
        for paper_id in self.paper_info:
            
            try:
                paper_date=dateutil.parser.parse(self.paper_info[paper_id]['date']).date()
            except ValueError as ex:
                print ex
                paper_date=datetime.date.min
            
            if paper_date>=start_date and paper_date<=end_date:
                    print "paper_id",paper_id
                    paper_authors=self.paper_info[paper_id]['authors']
                    print "authors",paper_authors
                    for i in range(len(paper_authors)):
                        for j in range(i+1,len(paper_authors)):
                            x=author_dict[self.get_alias(str(paper_authors[i]))]
                            y=author_dict[self.get_alias(str(paper_authors[j]))]
                            print x,y
                            if H.has_edge(x,y):
                                H[x][y]['weight']+=1
                            else:
                                H.add_edge(x,y)
                                H[x][y]['weight']=1            
        
        return H
    
    def affiliation_label(self,x):
        af_id=self.author_info[x]['affiliation-id']
        if af_id=='':
            return "UNKWON AFFILIATION"
        af_name=self.affiliation_info[af_id][u'affiliation-name']
        return af_name
    
    def name_label(self,x):
        name=""
        if self.author_info[x]['name']!=None:
            name+=self.author_info[x]['name']
            name+=" "
        if self.author_info[x]['surname']!=None:
            name+=self.author_info[x]['surname']
        return name
     
    def country_label(self,x):
        country=self.author_info[x]["country"]
        if country==None:
            return "UNKNOWN COUNTRY"
        return country
        
    def get_network_by_names(self,start_year=None,end_year=None,start_date=None,end_date=None):
        H=self.get_network2(start_year=start_year,end_year=end_year,start_date=start_date,end_date=end_date,label_function=self.name_label)
        return H
    
    def get_network_by_affiliation(self,start_year=None,end_year=None,start_date=None,end_date=None):
        H=self.get_network2(start_year=start_year,end_year=end_year,start_date=start_date,end_date=end_date,label_function=self.affiliation_label)
        return H
    
    def get_network_by_country(self,start_year=None,end_year=None,start_date=None,end_date=None):
        H=self.get_network2(start_year=start_year,end_year=end_year,start_date=start_date,end_date=end_date,label_function=self.country_label)
        return H
    
    def get_info(self):
        self.get_author_info()
        self.get_paper_info()
        self.get_affiliation_info()
    
    def get_network(self,start_year=None,end_year=None,start_date=None,end_date=None,use_names=True,):
        """Returns a networkX graph with the given parameters."""
        #if not self.network_computed:
         #   self.create_network()
        #self.get_paper_info()
        
        if start_year!=None:
            start_date=datetime.date(int(start_year),1,1)
        if end_year!=None:
            end_date=datetime.date(int(start_year),1,1)
            
        if start_date==None:
            start_date=datetime.date.min
        
        if end_date==None:
            end_date=datetime.date.max
             
        H=networkx.graph.Graph()
        names_dict={}
        for x in self.author_info:
            x=self.get_alias(x)
            if x not in names_dict:
                names_dict[x]=None
                
        for x in names_dict:
            name=""
            print x, self.author_info[x]
            if self.author_info[x]['name']!=None:
                name+=self.author_info[x]['name']
                name+=" "
            if self.author_info[x]['surname']!=None:
                name+=self.author_info[x]['surname']
            print name            
            i=1
            tname=name[:]
            while tname in H.nodes():
                tname=name+"_"+str(i)
                i=i+1
            H.add_node(tname)
            names_dict[x]=tname
        
        for paper_id in self.paper_info:
            
            try:
                paper_date=dateutil.parser.parse(self.paper_info[paper_id]['date']).date()
            except ValueError as ex:
                print ex
                paper_date=datetime.date.min
            
            if paper_date>=start_date and paper_date<=end_date:
                    print "paper_id",paper_id
                    paper_authors=self.paper_info[paper_id]['authors']
                    print "authors",paper_authors
                    for i in range(len(paper_authors)):
                        for j in range(i+1,len(paper_authors)):
                            x=names_dict[self.get_alias(str(paper_authors[i]))]
                            y=names_dict[self.get_alias(str(paper_authors[j]))]
                            print x,y
                            if H.has_edge(x,y):
                                H[x][y]['weight']+=1
                            else:
                                H.add_edge(x,y)
                                H[x][y]['weight']=1            
        
        return H
    


    
                        
                
                
                
            
        
    
    
