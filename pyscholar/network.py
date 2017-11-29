import datetime
import pickle

import scopus
import networkx
import dateutil.parser


def load(filename):
    G_file = open(filename, "r")
    G = pickle.load(G_file)
    G_file.close()
    return G


def save_graphml(G, filename):
    """Saves a network created get_network to graphml file"""

    if "paper" in G.edges()[0]:
        H = networkx.graph.Graph()
        for e in G.edges():
            H.add_edge(e[0], e[1])
            H[e[0]][e[1]]['weight'] = len(G[e[0]][e[1]]['papers'])
        G = H
    networkx.write_graphml(G, filename)


class CollaborationNetwork():
    def __init__(self, distance=0, core_ids=[]):
        self.core_ids = core_ids
        # self.core_names=core_names
        self.paper_info = {}
        self.author_info = {}
        self.distance = distance
        self.network_computed = False
        self.computed_distance = -1
        self.nodes_by_distance = [set() for i in range(self.distance + 2)]
        self.Q_by_distance = [[] for i in range(self.distance + 2)]
        self.affiliation_info = {}
        self.extra_ids = {}
        self.authors_searched_for_extra_ids = set()
        self.current_paper = 0
        self.current_author = 0

        # splitted_names=[n.split(',') for n in self.core_names]
        # self.core_name_IDS={self.core_names[i]:scopus.find_author_scopus_id_by_name(splitted_names[i][0],splitted_names[i][1]) for i in range(len(self.core_names))}
        # print self.core_name_IDS
        # for lst in self.core_name_IDS.values():
        #    self.core_ids.extend(lst)

        self.paper_ids_set = set()

        self.alias = {}

        for x in core_ids:
            if isinstance(x, list):
                for y in x:
                    self.author_info[str(y)] = False
                    self.alias[str(y)] = str(x[0])
                    self.Q_by_distance[0].append(str(y))
                    self.nodes_by_distance[0].add(str(y))
            else:
                self.author_info[str(x)] = False
                self.Q_by_distance[0].append(str(x))
                self.alias[str(x)] = str(x)
                self.nodes_by_distance[0].add(str(x))

    # Needs updating
    def copy_from_other(self, G):
        self.core_ids = G.core_ids
        self.paper_info = G.paper_info
        self.author_info = G.author_info
        self.distance = G.distance
        self.network_computed = G.network_computed
        self.computed_distance = G.computed_distance
        self.nodes_by_distance = G.nodes_by_distance
        self.Q_by_distance = G.Q_by_distance
        self.affiliation_info = G.affiliation_info
        self.extra_ids = G.extra_ids
        self.authors_searched_for_extra_ids = G.authors_searched_for_extra_ids
        self.current_author = G.current_author
        self.current_paper = G.current_paper
        self.paper_ids_set = G.paper_ids_set
        self.alias = G.alias

    def get_paper_info(self, parallel_download=True):
        Papers = set()
        for paper_id in self.paper_ids_set:
            if paper_id not in self.paper_info:
                Papers.add(paper_id)

        if parallel_download:
            scopus.download_paper_info(list(Papers))

        for paper_id in self.paper_ids_set:
            if paper_id not in self.paper_info:
                self.paper_info[paper_id] = scopus.paper_info(paper_id)

    def get_author_info(self, parallel_download=True, distance=0):
        Q = []

        IDS = self.author_info.keys()

        for x in IDS:
            if not self.author_info[x] and self.get_distance(x) <= distance:
                Q.append(x)

        if parallel_download:
            print "Downloading info"
            scopus.download_author_info(Q)

        print "Adding info"

        for x in Q:
            if not self.author_info[x]:
                print x
                try:
                    D = scopus.author_info(x, strict=True)
                    self.author_info[x] = D
                except scopus.Alias_Exception as e:
                    # What if the alias has an alias!???
                    self.author_info[x] = None
                    root = self.get_alias(x)
                    # root = e.alias[0]
                    print "alias", e.alias

                    for d in range(len(self.nodes_by_distance)):
                        if x in self.nodes_by_distance[d]:
                            break

                    for y in e.alias:
                        print root, y
                        if y not in self.author_info:
                            D = scopus.author_info(y, strict=True)
                            self.author_info[y] = D
                            self.nodes_by_distance[d].add(y)
                            if d <= self.distance:
                                self.Q_by_distance[d].append(y)
                                self.network_computed = False
                            if d == 0:
                                self.core_ids.append(y)
                                self.network_computed = False
                            self.alias[y] = root
                    if not self.author_info[root]:
                        self.author_info[root] = self.author_info[e.alias[0]].copy()

                except scopus.Scopus_Exception as e:
                    print "Scopus Exception"
                except:
                    print "General Exception"

    def get_affiliation_info(self, parallel_download=True, distance=0):
        """
        Get information about the author affiliations.
        get_author_info should have been called prior to call this function.
        """

        Q = set()
        for x in self.author_info:
            print x
            if self.get_distance(x) <= distance:
                s = self.author_info[x]['affiliation-id']
                if (s != '' and ((s not in self.affiliation_info) or self.affiliation_info[s] == None)):
                    Q.add(s)
        Q = list(Q)
        print Q

        if parallel_download:
            scopus.download_affiliation_info(Q, strict=False)

        for x in Q:
            print x
            try:
                self.affiliation_info[x] = scopus.affiliation_info(x, strict=True)
            except scopus.Scopus_Exception as e:
                print "Scopus Exception for ", x
                print e
                for y in self.author_info:
                    if self.get_distance(y) <= distance:
                        if self.author_info[y]['affiliation-id'] == x:
                            self.author_info[y]['affiliation-id'] = ''

    def save(self, file_name):
        file_G = open(file_name, 'w')
        pickle.dump(self, file_G)
        file_G.close()

    def create_network(self, parallel_download=True):
        """Creates the collaboration network."""

        for current_dist in range(self.distance+2):
            if len(self.Q_by_distance[current_dist]) > 0:
                break

        while current_dist <= self.distance:
            if parallel_download:
                scopus.download_publications(self.Q_by_distance[current_dist])

            while len(self.Q_by_distance[current_dist]) > 0:
                print "current distance", current_dist

                author = self.Q_by_distance[current_dist][-1]

                #
                # if author in self.alias:
                #     x=self.alias[author]
                # else:
                #     x=author

                print "current_author", author
                papers = scopus.get_publications(author)

                if parallel_download:
                    scopus.download_authors_from_papers(papers)

                start_paper = self.current_paper
                for paper_id in range(start_paper, len(papers)):
                    self.current_paper = paper_id
                    print "current paper ", papers[paper_id]
                    paper_id = papers[paper_id]
                    self.paper_ids_set.add(str(paper_id))
                    authors = scopus.get_authors_from_paper(str(paper_id))
                    for y in authors:

                        if y not in self.author_info:
                            self.author_info[y] = False
                            self.nodes_by_distance[current_dist+1].add(y)
                            if current_dist < self.distance:
                                self.Q_by_distance[current_dist+1].append(y)
                        
                        if not str(y) in self.alias:
                            y = str(y)
                            self.alias[y] = y
                             
                        # if not self.G.has_node(y):
                        #     self.nodes_by_distance[current_dist+1].add(y)
                        #     if current_dist<self.distance:
                        #         self.Q_by_distance[current_dist+1].append(y)
                            
                        # if author!=y:
                        #     if self.G.has_edge(author,y):
                        #        self.G[author][y]["papers"].add(str(paper_id))
                        # else:
                        #     self.G.add_edge(author,y)
                        #     self.G[author][y]["papers"]=set()
                        #     self.G[author][y]["papers"].add(str(paper_id))
                self.Q_by_distance[current_dist].pop()
                self.current_paper = 0
            current_dist += 1
        self.network_computed = True
        
    def get_alias(self, x):
        if x not in self.alias:
            return None
        
        if self.alias[x] == x:
            return x
        return self.get_alias(self.alias[x])
   
    def construct_first_publication_dict(self):
        """Constructs a dictionary that for each author, stores
        the date of his/her fist publication."""
        
        self.first_publication = {}
        
        for paper in self.paper_info:
            
            try:
                paper_date = dateutil.parser.parse(self.paper_info[paper]['date']).date()
            except ValueError as ex:
                print ex
                paper_date = datetime.date.max
            
            for aid in self.paper_info[paper]['authors']:
                aid = self.get_alias(aid)
                if (aid not in self.first_publication or self.first_publication[aid] > paper_date):
                    self.first_publication[aid] = paper_date

            
    
    def get_network(self, start_year=None, end_year=None, start_date=None, end_date=None,
                    label_function=None, distance=0, loops=False, author_filter=lambda x: True):
        """Returns a networkX graph with the given parameters."""
        # if not self.network_computed:
        #     self.create_network()
        # self.get_paper_info()
        
        if label_function == None:
            label_function = self.name_label
        
        if start_year != None:
            start_date = datetime.date(int(start_year), 1, 1)
            print start_date
        if end_year != None:
            end_date = datetime.date(int(end_year), 12, 31)
            print end_date
            
        if start_date == None:
            start_date = datetime.date.min
        
        if end_date == None:
            end_date = datetime.date.max
             
        H = networkx.graph.Graph()
        author_dict = {}
        
        for x in self.author_info:
            x = self.get_alias(x)
            if(x not in author_dict and self.get_distance(x) <= distance
               and author_filter(self.get_alias(x))):

                author_dict[x] = label_function(x)
        
        S = [set(x) for x in self.nodes_by_distance]
        
        for x in author_dict:
            for i in range(len(S)):
                if x in S[i] and i <= distance:
                    H.add_node(author_dict[x])
        
        for paper_id in self.paper_info:
            
            try:
                paper_date = dateutil.parser.parse(self.paper_info[paper_id]['date']).date()
            except ValueError as ex:
                print ex
                paper_date = datetime.date.min
            
            if paper_date >= start_date and paper_date <= end_date:
                #print "paper_id",paper_id
                paper_authors = self.paper_info[paper_id]['authors']
                #print "authors",paper_authors
                for i in range(len(paper_authors)):
                    for j in range(i+1, len(paper_authors)):
                        alias_i = self.get_alias(str(paper_authors[i]))
                        alias_j = self.get_alias(str(paper_authors[j]))
                        
                        found_x = False
                        found_y = False
                            
                        if alias_i != None:
                            for dx in range(distance+1):
                                if alias_i in self.nodes_by_distance[dx]:
                                    #print "found"
                                    found_x = True                                    
                                    break
                            if alias_j != None:
                                for dy in range(distance+1):
                                    if alias_j in self.nodes_by_distance[dy]:
                                        #print "found"
                                        found_y = True
                                        break
                                
                            
                            #print x,y
                            if found_x and found_y and author_filter(alias_i) and author_filter(alias_j):
                                x = author_dict[self.get_alias(str(paper_authors[i]))]
                                y = author_dict[self.get_alias(str(paper_authors[j]))]
                                if x != y or loops:
                                    if H.has_edge(x, y):
                                        H[x][y]['weight'] += 1
                                    else:
                                        H.add_edge(x, y)
                                        H[x][y]['weight'] = 1

        return H
    
    def construct_affiliation_labels(self):
        self.affiliation_label_dict = {}
        for afid in self.affiliation_info:
            if afid != '' and self.affiliation_info[afid] != None:
                s = self.affiliation_info[afid][u'affiliation-name']+"."
                
                afp = self.parent_aff_id(afid)
                if afp != None and afp in self.affiliation_info:
                    s += " \n"+self.affiliation_info[afp][u'affiliation-name']
                
                self.affiliation_label_dict[afid] = s
                
    
    def affiliation_label(self, x):
        y = self.author_info[x]['affiliation-id']
        if y in self.affiliation_label_dict:
            return self.affiliation_label_dict[y]
        return "UNKNOWN AFFILIATION"
        # af_id=self.author_info[x]['affiliation-id']
        # if af_id=='':
        #     return "UNKWON AFFILIATION"
        # if self.affiliation_info[af_id]==None:
        #     return "UNKWON AFFILIATION"
        # af_name=self.affiliation_info[af_id][u'affiliation-name']
        # return af_name
    
    
    def parent_aff_id(self, afid):
        if type(self.affiliation_info[afid]) == dict:
            if 'coredata' in self.affiliation_info[afid]:
                if 'parent-affiliation-id' in self.affiliation_info[afid]['coredata']:
                    return self.affiliation_info[afid]['coredata']['parent-affiliation-id']
        return None
    
    def download_parent_aff_info(self):
        Q = set()
        for afid in self.affiliation_info:
            x = self.parent_aff_id(afid)
            if x != None and x not in self.affiliation_info:
                Q.add(x)
        
        Q = list(Q)
        for x in Q:
            print x
            try:
                self.affiliation_info[x] = scopus.affiliation_info(x, strict=True)
            except scopus.Scopus_Exception as e:
                print "Scopus Exception for ", x
                print e
                for y in self.author_info:
                    if self.author_info[y]['affiliation-id'] == x:
                        self.author_info[y]['affiliation-id'] = ''
                
    
    def construct_name_labels(self, first_name_first=False, distance=0):
        self.names = {}
        N = set()
        for x in self.author_info:
            if self.get_distance(x) <= distance:
                x = self.get_alias(x)
                if x not in self.names:
                    name = ""
                    if first_name_first:
                        if self.author_info[x]['name'] != None:
                            name += self.author_info[x]['name']
                            name += " "
                        if self.author_info[x]['surname'] != None:
                            name += self.author_info[x]['surname']
                    else:
                        if self.author_info[x]['surname'] != None:
                            name += self.author_info[x]['surname']
                            name += " "
                        if self.author_info[x]['name'] != None:
                            name += self.author_info[x]['name']
                                
                    tname = name[:]
                    i = 2
                    tname = name[:]
                    while tname in N:
                        tname = name+"_"+str(i)
                        i = i+1
                
                    self.names[x] = tname
                    N.add(tname)
            
            
    
    def name_label(self, x):
        x = self.get_alias(x)
        return self.names[x]
    
    def country_label(self, x):
        country = self.author_info[x]["country"]
        if country == None:
            return "UNKNOWN COUNTRY"
        return country
    
    def get_network_by_ids(self, start_year=None, end_year=None, start_date=None,
                           end_date=None, distance=0, loops=False, author_filter=lambda x: True):
        H = self.get_network(start_year=start_year, end_year=end_year, start_date=start_date,
                             end_date=end_date, label_function=self.get_alias, distance=distance,
                             loops=loops, author_filter=author_filter)
        return H
    
    def get_network_by_names(self, start_year=None, end_year=None, start_date=None,
                             end_date=None, distance=0, loops=False, author_filter=lambda x: True):
        H = self.get_network(start_year=start_year, end_year=end_year, start_date=start_date,
                             end_date=end_date, label_function=self.name_label, distance=distance,
                             loops=loops, author_filter=author_filter)
        return H
    
    def get_network_by_affiliation(self, start_year=None, end_year=None, start_date=None,
                                   end_date=None, distance=0, loops=False, author_filter=lambda x: True): 
        H = self.get_network(start_year=start_year, end_year=end_year, start_date=start_date,
                             end_date=end_date, label_function=self.affiliation_label, distance=0,
                             loops=loops, author_filter=author_filter)
        return H
    
    def get_network_by_country(self, start_year=None, end_year=None, start_date=None,
                               end_date=None, loops=False, author_filter=lambda x: True):
        H = self.get_network(start_year=start_year, end_year=end_year, start_date=start_date,
                             end_date=end_date, label_function=self.country_label, distance=0,
                             loops=loops, author_filter=author_filter)
        return H
    
    def get_network_by_dict(self, D, start_year=None, end_year=None, start_date=None,
                            end_date=None, loops=False, author_filter=lambda x: True):
        def f(aid):
            print aid
            aid = self.get_alias(aid)
            print aid
            return D[aid]
        H = self.get_network(start_year=start_year, end_year=end_year, start_date=start_date,
                             end_date=end_date, label_function=f, distance=0,
                             loops=loops, author_filter=author_filter)
        return H
    
    def first_publication_filter_funct(self, date=None, year=None):
        """It returns a function that filters the authors whose
        first publication is no later than the given dates."""
        if not hasattr(self, "first_publication"):
            self.construct_first_publication_dict()
        if year != None:
            date = datetime.date(int(year), 1, 1)    
        if date == None:
            date = datetime.date.max
        
        def f(aid):
            aid = self.get_alias(aid)
            if self.first_publication[aid] <= date:
                return True
            return False
        
        return f
    
    def get_info(self, parallel_download=True, distance=0):
        self.get_author_info(parallel_download=parallel_download, distance=distance)
        self.get_paper_info(parallel_download=parallel_download)
        self.get_affiliation_info(parallel_download=parallel_download, distance=distance)
        self.download_parent_aff_info()
        self.construct_name_labels(distance=distance)
        self.construct_affiliation_labels()
    
    def _get_id_from_internal_id(self, i):
        for x in self.author_info:
            if self.author_info[x]['internal_id'] == i:
                return x
        return None
    
    def show_authors(self, distance=0):
        N = {}
        for x in self.author_info:
            author_within_distance = False
            for d in range(distance+1):
                if x in self.nodes_by_distance[d]:
                    author_within_distance = True
            if author_within_distance:
                name = self.name_label(x)
                if name not in N:
                    N[name] = [x]
                else:
                    N[name].append(x)
        Names = N.keys()
        Names.sort()
        for name in Names:
            x = self.get_alias(N[name][0])
            print str(self.author_info[x]['internal_id'])+".- "+name
            print "Scopus_ids", N[name]
            print ""
        
    def merge_authors(self, i, j):
        """Merge author with internal_id i with author with internal_id j. j becomes
        an alias of i."""
        
        for author in self.author_info:
            if i == self.author_info[author]['internal_id']:
                x = author
                break
        
        for author in self.author_info:
            if j == self.author_info[author]['internal_id']:
                y = author
                break
        
        x = self.get_alias(x)
        y = self.get_alias(y)
        
        if x == y:
            return None
        
        for dx in range(self.distance+1):
            if x in self.nodes_by_distance[dx]:
                break
        
        for dy in range(self.distance+1):
            if y in self.nodes_by_distance[dy]:
                break
        
        if dx < dy:
            self.nodes_by_distance[dy].remove(y)
            self.nodes_by_distance[dx].append(y)
        
        if dy < dx:
            self.nodes_by_distance[dx].remove(x)
            self.nodes_by_distance[dy].append(x)
        
        print x, y
        
        self.alias[x] = y
        
    def compute_possible_extra_ids(self):
        
        for author in self.author_info:
            if author not in self.authors_searched_for_extra_ids:
                print author
                alias = self.get_alias(author)
                if type(self.author_info[author]) != str:
                    author = alias
                first_name = self.author_info[author]['name']
                last_name = self.author_info[author]['surname']
            
                print last_name
                print first_name
                
                if first_name != None and "(" in first_name:
                    idx = first_name.index("(")
                    first_name = first_name[:idx]
                
                print first_name, last_name
                
                lst_tmp = scopus.find_author_scopus_id_by_name(firstName=first_name, lastName=last_name)
                lst = []
                if lst_tmp == None:
                    lst_tmp = []
                for x in lst_tmp:
                    if x not in self.author_info:
                        lst.append(x)
                if len(lst) > 0:
                    if alias not in self.extra_ids:
                        self.extra_ids[alias] = set()
                    for x in lst:
                        self.extra_ids[alias].add(x)
                
                self.authors_searched_for_extra_ids.add(author)
            else:
                print "author computed already"
                
        for author in self.extra_ids:
            self.extra_ids[author] = list(self.extra_ids[author])
    
    def show_possible_extra_ids(self, distance=0):
        for author in self.extra_ids:
            author_in_distance = False
            for dx in range(distance+1):
                if author in self.nodes_by_distance[dx]:
                    author_in_distance = True
                    break
            if author_in_distance:
                name = self.names[author]
                alias = self.get_alias(author)
                print ""
                print str(self.author_info[alias]["internal_id"])+".-"+name
                print "Possible ids"
                lst = self.extra_ids[alias]
                for i in range(len(lst)):
                    print str(i)+".-"+lst[i]
    
    def add_id(self, author_id):
        """Adds a new author_id. You should rerun create_network
        and get_info afterwards"""
        
        for S in self.nodes_by_distance:
            try:
                if author_id in S:
                    print "found"
                    S.remove(author_id)
            except:
                pass
        
        self.core_ids.append(author_id)
        self.nodes_by_distance[0].add(author_id)
        self.Q_by_distance[0].append(author_id)
        self.current_paper = 0
        self.current_author = 0
        self.network_computed = False
        self.author_info[author_id] = False
        self.alias[author_id] = str(author_id)

    def add_alias(self, author_id, alias_id):
        """Adds and alias to and author_id. You should run
        create_network and add_info afterwards."""

        if alias_id in self.author_info:
            self.merge_authors(self.author_info[author_id]["internal_id"],
                               self.author_info[alias_id]["internal_id"])
            return None
        
        root = self.get_alias(author_id)
        d = self.get_distance(root)
        self.author_info[alias_id] = False
        self.alias[alias_id] = root
        self.Q_by_distance[d].append(alias_id)
        self.network_computed = False
        self.current_paper = 0
        self.current_author = 0
        
    def add_aliases(self, author_id, alias_list):
        for alias_id in alias_list:
            self.add_alias(author_id, alias_id)


    def add_new_id(self, internal_id, idx):
        """Adds the scopus_id stored in extra_ids with index_id. You should have run
        compute_possible_ids first!"""
    
        for author in self.author_info:
            if self.author_info[author]['internal_id'] == internal_id:
                break

        author = self.get_alias(author)
        print author
        for d in range(self.distance+2):
            if author in self.nodes_by_distance[d]:
                break
    
        scopus_id = self.extra_ids[author][idx]
        if scopus_id not in self.author_info:
            self.author_info[scopus_id] = False
            self.alias[scopus_id] = author
            if d <= self.distance:
                self.Q_by_distance[d].append(scopus_id)
                self.network_computed = False
                self.current_paper = 0
    
    def delete_id(self, aid):
        if aid in self.core_ids:
            self.core_ids.remove(aid)
        
        for d in range(len(self.nodes_by_distance)):
        
            if aid in self.nodes_by_distance[d]:
                self.nodes_by_distance[d].remove(aid)
        
        for d in range(len(self.Q_by_distance)):
            if aid in self.Q_by_distance[d]:
                self.Q_by_distance[d].remove(aid)
                
        if aid in self.author_info:
            self.author_info.pop(aid)
        
        if aid in self.alias:
            self.alias.pop(aid)
            
    #Edit functions
    def replace_id(self, old_id, new_id):
        """
        Mistakes when writing the core_ids of G are common. This function
        enable us to fix these errors by replacing the mistken id with the correct one."""
        for i in range(len(self.core_ids)):
            if self.core_ids[i] == old_id:
                self.core_ids[i] = new_id
                
            if type(self.core_ids[i]) == list:
                if old_id in self.core_ids[i]:
                    self.core_ids[i][self.core_ids[i].index(old_id)] = new_id
                    
        for S in self.nodes_by_distance:
            if old_id in S:
                S.remove(old_id)    
        
        for S in self.Q_by_distance:
            if old_id in S:
                S.remove(old_id)
        
        if old_id in self.author_info:
            self.author_info.pop(old_id)
        
        self.nodes_by_distance[0].add(new_id)
        self.Q_by_distance[0].append(new_id)
        self.network_computed = False
        self.current_author = 0
        self.current_paper = 0


    def get_ids_with_missing_info(self):
        """Returns a list of which author's ids we still need to get their info."""
        
        lst = []
        for x in self.author_info:
            if not self.author_info[x]:
                lst.append(x)
                
        return lst
            
    def set_author_info(self, author_id, affiliation_id=None, city=None, country=None,
                        name=None, document_count=None, surname=None):
        
        """
        Manually set the information on an author.
        The author must have been discovered by now.
        Take care to use Unicode encoding.
        """

        if not self.author_info[author_id]:
            self.author_info[author_id] = dict()
        
        if ("affiliation-id" not in self.author_info[author_id] or affiliation_id != None):
            if affiliation_id not in self.affiliation_info:
                self.affiliation_info[affiliation_id] = None
            self.author_info[author_id]["affiliation_id"] = affiliation_id

        if ("city" not in self.author_info[author_id] or city != None):
            self.author_info[author_id]["city"] = city
            
        if ("name" not in self.author_info[author_id] or name != None):
            self.author_info[author_id]["name"] = name
            
        if ("country" not in self.author_info[author_id] or country != None):
            self.author_info[author_id]["country"] = country
        
        if ("document-count" not in self.author_info[author_id] or document_count != None):
            self.author_info[author_id]["document-count"] = document_count
        
        if ("surname" not in self.author_info[author_id] or surname != None):
            self.author_info[author_id]["surname"] = surname
            
    def compute_internal_ids(self):
        i = 1
        for x in self.author_info:
            self.author_info[x]['internal_id'] = i
            i += 1
    

    def get_distance(self, aid):

        for i in range(len(self.nodes_by_distance)):
            if aid in self.nodes_by_distance[i]:
                return i
        return len(self.nodes_by_distance)



