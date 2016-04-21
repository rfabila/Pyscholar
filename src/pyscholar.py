import matplotlib
from scopus_key import MY_API_KEY
import requests
import networkx as nx
import os
import itertools as it

matplotlib.use('Agg')

import matplotlib.pyplot as plt

search_api_author_url = "http://api.elsevier.com/content/search/author?"
search_api_scopus_url = "http://api.elsevier.com/content/search/scopus?"
search_api_abstract_url = "http://api.elsevier.com/content/abstract/scopus_id/"
search_api_author_id_url="http://api.elsevier.com/content/author/author_id/"

headers = {"Accept":"application/json", "X-ELS-APIKey": MY_API_KEY}

#Un diccionario con las listas 
Scopus_ids_merged_rep={}
Scopus_ids_merged_lists={}

#Voy a poner aqui lo que falta por hacer (TODO list) 

#Funciones para manejar las ids, hago implementaciones ingenuas que
#despues mejoraremos
#Vean https://en.wikipedia.org/wiki/Disjoint-set_data_structure

class Scopus_Exception(Exception):
    def __init__(self, resp):
        self.code = resp.status_code
        resp = resp.json()
        resp = resp[u'service-error'][u'status']
        self.statusCode=resp[u'statusCode']
        self.statusText=resp[u'statusText']
    def __str__(self):
        return "%s: %s"%(self.statusCode, self.statusText)


def load_authors_from_file(directory=""):
    """
    Returns a list of the authors who were in a file.
    """
    try:
        with open(directory, 'r') as f: 
            return [line.strip() for line in f]
    except IOError :
        print "Could not read file:", directory


def load_papers_from_file(directory=""):
    """
    Returns a list of the papers who were in a file.
    """
    try:
        with open(directory, 'r') as f: 
            return [line.strip() for line in f]
    except IOError :
        print "Could not read file:", directory


def _add_scopus_id(scopus_id):
    """Adds a scopus id to the merged list. Returns False if the ID
    is already in the merged list and false otherwise"""
    
    #Buscamos a ver si ya estaba en algunas lista, de ser
    #asi no hacemos nada
    for x in Scopus_ids_merged_lists:
        if scopus_id in D[x]:
            return False
    
    
    #No tiene "padre" y por tanto es la raiz
    Scopus_ids_merged_rep[scopus_id]=None
    
    #De momento el es el unico de la lista
    Scopus_ids_merged_lists[scopus_id]=[scopus_id]
    
    return list


def _get_root_id(scopus_id):
    """Follows the path of parents until it finds the root"""
    
    #Si no esta en la lista de representantes pues no hay nada que hacer
    if scopus_id not in Scopus_ids_merged_rep:
        return scopus_id
    
    
    root_scopus_id=scopus_id
    parent_scopus_id=t_scopus_id
    
    #seguimos los apuntadores hasta llegar a la raiz
    while Scopus_ids_merged_rep[root_scopus_id]!=None:
        root_scopus_id=Scopus_ids_merged_rep[root_scopus_id]
    
    return root_scopus_id

def _get_alias_list_id(scopus_id):
    """returns the list of alias id"""
    #En Scopus_ids_merged_lists[root_id] se van a guardar la lista
    #de alias
    
def _union_alias_id(scopus_id_1,scopus_id_2):
    #Junta a la lista de scopus_id_1 y scopus_id_2
    pass
        
    
def _get_alias_id(scopus_id):
    pass
    



###FIN DE FUNCIONES de IDs
def get_references_by_paper(list_scopus_id_paper):
    """Returns a dictionary where the key is the ID of the 
    paper and the value associated with the key is a set 
    of the ids of the papers cited by the main paper"""
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]
        
    references_by_paper=dict()
    for id_paper in list_scopus_id_paper:
        fields = "?view=REF"
        searchQuery = id_paper
        resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)
        data = resp.json()
        data=data[u'abstracts-retrieval-response'][u'references'][u'reference']
        references_ids=set()
        for id_reference in data:
            references_ids.add(id_reference['scopus-id'])
        references_by_paper[id_paper]=references_ids
    return references_by_paper


def get_common_papers(id_author_1="",id_author_2=""):
    """Returns the intercession of papers between two authors"""
    if id_author_1=="" and id_author_2=="":
        print "Give me the two Authors"
    else:
        papers_author_1=get_papers([id_author_1])
        papers_author_2=get_papers([id_author_2])
        papers_in_common=papers_author_1[id_author_1].intersection(papers_author_2[id_author_2])
    return papers_in_common    


def get_title_abstract_by_idpaper(id_paper=""):
    """Returns a tuple with the id_paper,title and abstract of each paper """
    
    fields = "?field=dc:description,title"
    
    searchQuery = (id_paper)
    resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
    if resp.status_code != 200:
        raise Scopus_Exception(resp)
    
    data=resp.json()
    data=data["abstracts-retrieval-response"]["coredata"]
    return (id_paper,data['dc:title'],data['dc:description'])


def search_author(list_scopus_id_author):
    """Returns a dictionary where the key is the ID of the 
    author and the value associated with the key is a dictionary
    with the following keys: name, surname, h-index and coauthor-count.
    """
    fields = "?field=dc:identifier,given-name,surname,h-index,coauthor-count"
    dict_authors=dict()
    if isinstance(list_scopus_id_author, str):
        list_scopus_id_author=[list_scopus_id_author]
    for id_author in list_scopus_id_author:
        attributes=dict()
        searchQuery = str(id_author)
        resp = requests.get(search_api_author_id_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)
        data=resp.json()
        data=data['author-retrieval-response'][0]
        attributes={'name':data['preferred-name']['given-name'],
        'surname':data['preferred-name']['surname'],'h-index':int(data['h-index']),'coauthor-count':int(data['coauthor-count'])}
        dict_authors[id_author]=attributes
    return dict_authors

def get_coauthors(id_author=""):
    """
    Returns a  tuple with the nex elements,
    1.-Id_author
    2.-Set of co-authors associated with an id of an author.
    3.-A dictionary where the key is the ID of the co-authors 
     and the value associated is a set with the ids of the papers between
     the author and co-author.
    """
    papers_author=get_papers(id_author)
    list_authors=set()
    papers_with_coauthors=dict()
    for paper in papers_author[id_author]:
        paper_list=[paper]
        authors=get_ids_authors_by_id_paper(paper_list)
        for author in authors[paper]:
            if author not in list_authors and author!=id_author:
                list_authors.add(author)
                papers_with_coauthors[author]=[paper]
            elif author!=id_author:
                papers_with_coauthors[author].append(paper)


    return (id_author,list_authors,papers_with_coauthors)



def get_coauthors_graph(list_scopus_id_author,distance,directory="",name=""):
    """
    Returns a tuple where the first element is the graph induced by several authors 
    and the second element is a list of sets where each set is a set of authors to distance d.
    """
    node_colors=["red","blue","green","yellow","brown"]
    node_distance=distance
    iteration=distance+1
    if isinstance(list_scopus_id_author, str):
        list_scopus_id_author=[list_scopus_id_author]
    nodes=set()
    index_color=0
    edge_list=[]
    attribute_edge=[]
    G_coauthors=nx.Graph()
    D=[]
    dist_count=0
    while(iteration!=0):
        new_search=set()
        #print "Nivel: "+str(distance)
        #print len(list_scopus_id_author)
        #print list_scopus_id_author
        for id_author in list_scopus_id_author:
            if id_author not in nodes:
                nodes.add(id_author)
                G_coauthors.add_node(str(id_author),color=node_colors[index_color%5],distance=dist_count)
            if(iteration==1):
                continue
            else:
                coauthors=get_coauthors(str(id_author))
                for coauthor in coauthors[1]:
                    edge_list.append((id_author,str(coauthor)))
                    attribute_edge.append((id_author,str(coauthor),coauthors[2][coauthor]))
                    new_search.add(str(coauthor))
        if (iteration==1):
            check_edge=it.combinations(list_scopus_id_author,2)
            for edge in check_edge:
                number_paper=get_common_papers(edge[0],edge[1])
                if len(number_paper)>0:
                    #print number_paper
                    edge_list.append((edge[0],edge[1]))
                    attribute_edge.append((edge[0],edge[1],number_paper))
        list_scopus_id_author=new_search.copy()
        iteration-=1
        index_color+=1
        dist_count+=1
    G_coauthors.add_edges_from(edge_list)
    for dis in range(node_distance+1):
        D.append([])
    for id_node in G_coauthors.nodes():
        D[G_coauthors.node[id_node]['distance']].append(id_node)
    """
    custom_node_color={}
    pos = nx.spring_layout(G_coauthors,k=0.15,iterations=200)
    for id_node in G_coauthors.nodes():
        custom_node_color[id_node]=G_coauthors.node[id_node]['color']
    nx.draw(G_coauthors,pos,node_list = custom_node_color.keys(), node_color=custom_node_color.values())
    """
    nx.draw(G_coauthors)
    if  os.path.exists(directory):
        plt.savefig(directory+name+".png")
    for atribute in attribute_edge:
        if 'papers' in G_coauthors[atribute[0]][atribute[1]]:
            G_coauthors[atribute[0]][atribute[1]]['papers']+=atribute[2]
        else:
            G_coauthors[atribute[0]][atribute[1]]['papers']=[]
            G_coauthors[atribute[0]][atribute[1]]['papers']+=atribute[2]
    return (G_coauthors,D)

def get_citation_graph(list_scopus_id_paper,distance,directory="",name=""):
    """
    Returns a tuple where the first element is the graph induced by papers
    and the second element is a list of sets where each set is a set of papers to distance d.
    and the last element is a set of papers not found.
    """
    node_distance=distance
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]
    iteration=distance+1
    G_citation=nx.DiGraph()
    nodes=set()
    edge_list=[]
    paper_not_found=set()
    dist_count=0
    D=[]
    while(iteration!=0):
        new_search=set()
        for paper in list_scopus_id_paper:
            if paper not in nodes:
                nodes.add(paper)
                G_citation.add_node(str(paper),distance=dist_count)
            if(iteration==1):
                continue
            else:
                try:
                    cites=get_references_by_paper(str(paper))
                    for cite in cites[str(paper)]:
                        edge_list.append((str(paper),str(cite)))
                        new_search.add(str(cite))
                except:
                    paper_not_found.add(str(paper))
        if(iteration==1):
            check_edge=it.permutations(list_scopus_id_paper,2)
            for edge in check_edge:
                try:
                    check_cite=get_references_by_paper(edge[0])
                    if edge[1] in check_cite[edge[0]]:
                        edge_list.append((edge[0],edge[1]))
                except:
                    paper_not_found.add(edge[0])
        list_scopus_id_paper=new_search.copy()
        iteration-=1
        dist_count+=1
    G_citation.add_edges_from(edge_list)
    nx.draw(G_citation)
    if  os.path.exists(directory):
        plt.savefig(directory+name+".png")
    for dis in range(node_distance+1):
        D.append([])
    for id_node in G_citation.nodes():
        D[G_citation.node[id_node]['distance']].append(id_node)
    return (G_citation,D,paper_not_found)

def get_ids_authors_by_id_paper(list_scopus_id_paper):
    """Returns a dictionary where the key is the ID of the 
    paper and the value associated with the key is a list 
    of the ids of the authors who wrote the paper"""
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]

    fields = "?field=dc:description,authors"
    authors_by_id_paper=dict()
    
    for id_paper in list_scopus_id_paper:
        searchQuery = str(id_paper)
        resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)
            
        id_authors=[]
        data=resp.json()
        data=data["abstracts-retrieval-response"]["authors"]["author"]
        for author in data:
            id_authors.append(author["@auid"])     
        authors_by_id_paper[id_paper]=id_authors
    return authors_by_id_paper

def count_citations_by_id_paper(list_scopus_id_paper):
    """Returns a dictionary where the key is the ID of the 
    paper and the value associated with the key is the 
    number citations """

    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]
    
    fields = "?field=dc:description,citedby-count"
    cited_by_count=dict()
        
    for id_paper in list_scopus_id_paper:
        searchQuery = str(id_paper)
        resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp) 
        
        number_citations=0
        data=resp.json()
        data=data["abstracts-retrieval-response"]["coredata"]
        number_citations=int(data['citedby-count'])
        cited_by_count[id_paper]=number_citations
    return cited_by_count


def get_papers(list_scopus_id_author):
    """Returns a dictionary where the key is the ID of the 
    author and the value associated with the key 
    is a set of the ids of the papers that belong to the author."""

    if isinstance(list_scopus_id_author, str):
        list_scopus_id_author=[list_scopus_id_author]
    
    fields = "&field=identifier"
    papers_by_author=dict()
    
    for id_author in list_scopus_id_author:
        searchQuery = "query=AU-ID("+str(id_author)+")"
        resp = requests.get(search_api_scopus_url+searchQuery+fields, headers=headers)
        
        if resp.status_code != 200:
            raise Scopus_Exception(resp)
            
        id_papers=set()
        data = resp.json()
        data = data['search-results']
        if data["opensearch:totalResults"] == '0':
            return None
        else:
            for entry in data['entry']:
                paperId = entry['dc:identifier'].split(':')
                id_papers.add(paperId[1])
            papers_by_author[id_author]=id_papers
    return papers_by_author
    
    #Hay que considerar que pudieran tener aliases

#FIN DE TODO LIST

def find_author_scopus_id_by_name(firstName="", lastName=""):
    """Searches for an author scopus id given its name."""

    searchQuery = "query="

    if firstName:
        searchQuery += "AUTHFIRST(%s)" % (firstName)
    if lastName:
        if firstName:
            searchQuery += " AND "
        searchQuery += "AUTHLASTNAME(%s)" % (lastName)
    
    #print searchQuery 
    
    fields = "&field=identifier"
    resp = requests.get(search_api_author_url+searchQuery+fields, headers=headers)
    
    if resp.status_code != 200:
       raise Scopus_Exception(resp)
    
    data = resp.json()
    #print "-----------JSON----------"
    #print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': '))
    
    #print "----------DATA----------"
    data = data['search-results']
    #print data
    
    if data["opensearch:totalResults"] == '0':
        print "None"
        return None
                                                                                           
    ids = []
                                                                                           
    for entry in data['entry']:
        authorId = entry['dc:identifier'].split(':')
        ids.append(authorId[1])
                                                                                                                       
    return ids
