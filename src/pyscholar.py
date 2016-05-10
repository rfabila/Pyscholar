import matplotlib
from scopus_key import MY_API_KEY
import requests
import networkx as nx
import os
import itertools as it
import math
import pandas as pd 

matplotlib.use('Agg')
import matplotlib.pyplot as plt

search_api_author_url = "http://api.elsevier.com/content/search/author?"
search_api_scopus_url = "http://api.elsevier.com/content/search/scopus?"
search_api_abstract_url = "http://api.elsevier.com/content/abstract/scopus_id/"
search_api_author_id_url="http://api.elsevier.com/content/author/author_id/"
search_api_affiliation_url = "http://api.elsevier.com/content/search/affiliation?"
retrieve_api_affiliation_url="http://api.elsevier.com/content/affiliation/affiliation_id/"



headers = {"Accept":"application/json", "X-ELS-APIKey": MY_API_KEY}

scopus_authors_by_idpapers_cache=dict()
scopus_papers_by_authorid_cache=dict()
scopus_references_by_idpaper_cache=dict()

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
def load_graph_pickle(path=""):
    """Read graph object in Python pickle format.
    """
    return nx.read_gpickle(path)

def save_graph_pickle(G,path="",name_graph=""):
    """
    Save graph in Python pickle format.
    """
    nx.write_gpickle(G,path+name_graph+".gpickle")

def find_affiliation_scopus_id_by_name(organization=""):
    """
    Returns a table which contains all matches found by the search affiliation name.
    """
    searchQuery = "query=affil("+organization+")"
    fields = ""
    resp = requests.get(search_api_affiliation_url+searchQuery+fields, headers=headers)
    if resp.status_code != 200:
            raise Scopus_Exception(resp)
    id_affil=[]
    data = resp.json()
    data = data['search-results']
    if data["opensearch:totalResults"] == '0':
        print "None"
        return None
    affiliation_scopus_id_by_name=dict()
    for entry in data['entry']:
        affiliation_name=entry['affiliation-name']
        identifier=entry['dc:identifier']
        ident=entry['dc:identifier'].split(":")[1]
        #affil_id = entry['dc:identifier'].split(':')
        eid= entry["eid"]
        document_count=entry['document-count']
        if 'country' in entry.keys():
            country =entry['country']
        else:
            country=""
        if 'city' in entry.keys():
            city =entry['city']
        else:
            city=""
        list_names_variants=[]
        if 'name-variant' in entry.keys():
            for name_variant in entry['name-variant']:
                list_names_variants.append(name_variant['$'])

        affiliation_scopus_id_by_name[str(ident)]={'affiliation_name':affiliation_name,'identifier':str(identifier),'eid':str(eid),'document_count':int(document_count),'country':str(country),'city':str(city),'name_variant':list_names_variants}
    table=[]
    for id_affiliation,attributes_affil in affiliation_scopus_id_by_name.items():
        register=[]
        register.append(id_affiliation)
        for key_val,val_affil in attributes_affil.items():
            register.append(val_affil)
        table.append(register)
    headers_table=['id', 'city', 'country', 'name_variant', 'eid', 'affiliation_name', 'identifier', 'document_count']
    affiliation_table=pd.DataFrame(table)
    for i in range(len(headers_table)):
        affiliation_table.rename(index=str, columns={i:headers_table[i]},inplace=True)
    affiliation_table.sort_values(['document_count'],ascending=[False],inplace=True)
    affiliation_table = affiliation_table.reset_index(drop=True)
    
    return affiliation_table

def search_affiliation_by_id(list_scopus_id_affiliation):
    """Returns a dictionary where the key is the ID of the 
    affiliation and the value associated with the key is a dictionary
    with the following keys: date_created, preferred_name, author_count 
    and document_count
    """
    if isinstance(list_scopus_id_affiliation, str):
        list_scopus_id_affiliation=[list_scopus_id_affiliation]
    fields=""
    dict_affiliation_by_id=dict()
    for id_affiliation in list_scopus_id_affiliation:
        searchQuery = str(id_affiliation)
        resp = requests.get(retrieve_api_affiliation_url+searchQuery+fields, headers=headers)
        if resp.status_code != 200:
            raise Scopus_Exception(resp)
        data=resp.json()
        data=data["affiliation-retrieval-response"]
        date_created=str(data["institution-profile"]['date-created']['@day']+"/"+data["institution-profile"]['date-created']['@month']+"/"+data["institution-profile"]['date-created']['@year'])
        preferred_name=str(data["institution-profile"]['preferred-name'])
        author_count=int(data['coredata']['author-count'])
        document_count=int(data['coredata']['document-count'])
        attributes={'date_created':date_created,'preferred_name':preferred_name,'author_count':author_count,'document_count':document_count}
        dict_affiliation_by_id[id_affiliation]=attributes
    return dict_affiliation_by_id

def get_authors_by_id_affiliatio(list_scopus_id_affiliation):
    """Returns a dictionary where the key is the ID of the 
    paper and the value associated with the key is a set 
    of the ids of the papers cited by the main paper"""
    if isinstance(list_scopus_id_affiliation, str):
        list_scopus_id_affiliation=[list_scopus_id_affiliation]
    authors_by_id_affiliation=dict()
    for id_affiliation in list_scopus_id_affiliation:
        affiliation_attributes=search_affiliation_by_id(id_affiliation)
        author_count=affiliation_attributes[id_affiliation]["author_count"]
        iterations=math.ceil(author_count/200.0)
        chunks=[]
        for size_chunk in range(0,int(iterations)+1):
            if size_chunk==0:
                chunks.append(0)
            else:
                if ((200*size_chunk)+1+200)<=5000:
                    chunks.append((200*size_chunk)+1)
                else:
                    if 4801 not in chunks:
                        chunks.append(4801)
        iterations=len(chunks)
        index_chunk=0
        ids_author=set()
        while(iterations!=0):
            if chunks[index_chunk]!=4801:
                fields = "&field=dc:identifier&count=200"+"&start="+str(chunks[index_chunk])
            else:
                fields = "&field=dc:identifier&count=199"+"&start="+str(chunks[index_chunk])
            searchQuery = "query=AF-ID("+str(id_affiliation)+")"
            #print search_api_author_url+searchQuery+fields
            resp = requests.get(search_api_author_url+searchQuery+fields, headers=headers)
            if resp.status_code != 200:
                raise Scopus_Exception(resp)
            data=resp.json()
            data = data['search-results']
            if data["opensearch:totalResults"] == '0':
                #Check after.
                print "None"
                return None
            for entry in data['entry']:
                authorId = entry['dc:identifier'].split(':')
                ids_author.add(str(authorId[1]))
            iterations-=1
            index_chunk+=1
        authors_by_id_affiliation[id_affiliation]=ids_author

    return authors_by_id_affiliation

def get_references_by_paper(list_scopus_id_paper):
    """Returns a dictionary where the key is the ID of the 
    paper and the value associated with the key is a set 
    of the ids of the papers cited by the main paper"""
    if isinstance(list_scopus_id_paper, str):
        list_scopus_id_paper=[list_scopus_id_paper]
        
    references_by_paper=dict()
    for id_paper in list_scopus_id_paper:
        if id_paper in scopus_references_by_idpaper_cache.keys():
            if len(scopus_references_by_idpaper_cache[id_paper])==0:
                print "I didn't find references for this paper."
            references_by_paper[id_paper]=scopus_references_by_idpaper_cache[id_paper]
        else:
            fields = "?view=REF"
            searchQuery = id_paper
            resp = requests.get(search_api_abstract_url+searchQuery+fields, headers=headers)
            if resp.status_code != 200:
                raise Scopus_Exception(resp)
            data = resp.json()
            if data[u'abstracts-retrieval-response'] is not None:
                data=data[u'abstracts-retrieval-response'][u'references'][u'reference']
                references_ids=set()
                for id_reference in data:
                    references_ids.add(str(id_reference['scopus-id']))
                references_by_paper[id_paper]=references_ids
                scopus_references_by_idpaper_cache.update({id_paper:references_ids})
            else:
                print "I didn't find references for this paper."
                scopus_references_by_idpaper_cache.update({id_paper:set()})

    return references_by_paper

def get_cache_references_by_idpaper():
    """
    Returns the global variable scopus_references_by_idpaper_cache which is 
    a dictionary where the key is the id of the paper and the value associated 
    with the key is a set of the ids of the papers cited by the main paper
    """
    return scopus_references_by_idpaper_cache


def get_common_papers(id_author_1="",id_author_2=""):
    """Returns the intercession of papers between two authors"""
    if id_author_1=="" and id_author_2=="":
        print "Give me the two Authors"
    else:
        papers_author_1=get_papers([id_author_1])[id_author_1]
        papers_author_2=get_papers([id_author_2])[id_author_2]
        papers_in_common=papers_author_1.intersection(papers_author_2)
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
    return (id_paper,str(data['dc:title']),str(data['dc:description']))


def search_author(list_scopus_id_author):
    """Returns a dictionary where the key is the ID of the 
    author and the value associated with the key is a dictionary
    with the following keys: name, surname, h-index and coauthor-count.
    """
    fields = "?field=dc:identifier,given-name,surname,h-index,coauthor-count,document-count"
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
        attributes={'name':str(data['preferred-name']['given-name']),
        'surname':str(data['preferred-name']['surname']),'h-index':int(data['h-index']),'coauthor-count':int(data['coauthor-count']),'document-count':int(data['coredata']['document-count'])}
        dict_authors[id_author]=attributes
    return dict_authors

def get_coauthors(id_author,min_year="",max_year="",dict_knowledge=dict()):
    """
        Returns a  tuple with the nex elements,
        1.-Id_author
        2.-Set of co-authors associated with an id of an author.
        3.-A dictionary where the key is the ID of the co-authors 
        and the value associated is a set with the ids of the papers between
        the author and co-author.
    """
    scopus_authors_by_idpapers_cache.update(dict_knowledge)
    papers_author=get_papers([id_author],min_year,max_year)[id_author]
    papers_with_coauthors=dict()
    list_authors=set()
    for paper in papers_author:
        if paper in scopus_authors_by_idpapers_cache.keys():
            #print "Here"
            for coauthor in scopus_authors_by_idpapers_cache[paper]:
                if coauthor!=id_author:
                    list_authors.add(coauthor)
                    papers_with_coauthors[coauthor]=papers_with_coauthors.setdefault(coauthor,[])+[paper]
        else:
            authors=get_ids_authors_by_id_paper(paper)
            scopus_authors_by_idpapers_cache.update(authors)
            for author in authors[paper]:
                if author not in list_authors and author!=id_author:
                    list_authors.add(author)
                    papers_with_coauthors[author]=[paper]
                elif author!=id_author:
                    papers_with_coauthors[author].append(paper)


    return (id_author,list_authors,papers_with_coauthors)

def get_cache_papers():
    """
    Returns the scopus_authors_by_idpapers_cache dictionary which 
    is a cache of papers consulted where the key is the id of the paper 
    and the associated value is a set of authors who wrote the article.
    """
    return scopus_authors_by_idpapers_cache


def get_coauthors_graph(list_scopus_id_author,distance,min_year="",max_year="",directory="",name=""):
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
    resource_not_found=[]
    G_coauthors=nx.Graph()
    D=[]
    dist_count=0
    dict_knowledge_papers=dict()
    while(iteration!=0):
        new_search=set()
        #print "Nivel: "+str(distance)
        #print len(list_scopus_id_author)
        #print list_scopus_id_author
        for id_author in list_scopus_id_author:
            #print id_author
            if id_author not in nodes:
                nodes.add(id_author)
                G_coauthors.add_node(str(id_author),color=node_colors[index_color%5],distance=dist_count)
            if(iteration==1):
                continue
            else:
                coauthors=get_coauthors(str(id_author),min_year,max_year,dict_knowledge_papers)
                print coauthors
                dict_knowledge_papers.update(coauthors[2])
                for coauthor in coauthors[1]:
                    edge_list.append((id_author,str(coauthor)))
                    attribute_edge.append((id_author,str(coauthor),coauthors[2][coauthor]))
                    new_search.add(str(coauthor))
        if (iteration==1):
            print list_scopus_id_author
            dict_last_authors=dict()
            list_scopus_id_author_found=set()
            for id_author in list_scopus_id_author:
                try:
                    coauthors_of_author=get_coauthors(id_author,min_year,max_year,dict_knowledge_papers)
                    dict_knowledge_papers.update(coauthors_of_author[2])
                    dict_last_authors[id_author]=coauthors_of_author[1]
                    list_scopus_id_author_found.add(id_author)
                except:
                    resource_not_found.append(id_author)
                    continue
            check_edge=it.combinations(list_scopus_id_author_found,2)
            for edge in check_edge:
                #print edge[0],edge[1]
                intersection_papers=get_common_papers(edge[0],edge[1])
                if len(intersection_papers)>0:
                    edge_list.append((edge[0],edge[1]))
                    attribute_edge.append((edge[0],edge[1],intersection_papers))
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
        #print list_scopus_id_paper
        #print len(list_scopus_id_paper)
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
                    continue
        if(iteration==1):
            dict_last_nodes=dict()
            for id_paper in list_scopus_id_paper:
                try:
                    #print id_paper
                    cites=get_references_by_paper(str(id_paper))
                    dict_last_nodes[id_paper]=cites[str(id_paper)]
                except:
                    paper_not_found.add(str(id_paper))
                    continue
            check_edge=it.permutations(dict_last_nodes.keys(),2)
            for edge in check_edge:
                if edge[1] in dict_last_nodes[edge[0]]:
                    edge_list.append((str(edge[0]),str(edge[1])))
                    edge_list.append((str(edge[0]),str(edge[1])))
        list_scopus_id_paper=new_search.copy()
        iteration-=1
        dist_count+=1
    G_citation.add_edges_from(edge_list)
    for node_to_remove in paper_not_found:
        G_citation.remove_node(node_to_remove)
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
            id_authors.append(str(author["@auid"]))     
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

def check_years(min_year="",max_year=""):
    """
    Return the filter if the given interval is correct 
    otherwise returns None
    """
    filtr=""
    if min_year =="":
        if max_year=="":
            filtr=""
            return filtr
        else:
            if max_year.isdigit():
               filtr+="AND (PUBYEAR < "+ str(int(max_year)+1) +")"
               return filtr
            else:
                print "max_year must be a number"
                return None
    else:
        if min_year.isdigit():
            if max_year=="":
                filtr+="AND (PUBYEAR > "+ str(int(min_year)-1) +")"
                return filtr
            else:
                if max_year.isdigit():
                    if int(max_year)<int(min_year):
                        print "Max_year must be greater than min_year"
                        return None
                    else:
                        filtr+="AND (PUBYEAR > "+ str(int(min_year)-1) +") AND (PUBYEAR < "+ str(int(max_year)+1)+")"
                        return filtr
                else:
                    print "max_year must be a number"
                    return None
        else:
            if max_year.isdigit():
                print "min_year must be a number"
                return None
            else:
                print "min_year and max_year must be numbers"
                return None                



def get_papers(list_scopus_id_author,min_year="",max_year=""):
    """Returns a dictionary where the key is the ID of the 
    author and the value associated with the key 
    is a set of the ids of the papers that belong to 
    the author in certain time interval."""

    if isinstance(list_scopus_id_author, str):
        list_scopus_id_author=[list_scopus_id_author]
    
    papers_by_author=dict()
    filter_year=""
    filter_year=check_years(min_year,max_year)
    if filter_year==None:
        return None
    
    for id_author in list_scopus_id_author:
        if (id_author in scopus_papers_by_authorid_cache.keys()) and (min_year+"-"+max_year in scopus_papers_by_authorid_cache[id_author].keys()):
            papers_by_author[id_author]=set()
            papers_by_author[id_author]=papers_by_author[id_author].union(scopus_papers_by_authorid_cache[id_author][min_year+"-"+max_year])
        else:
            author_attributes=search_author(id_author)
            document_count=author_attributes[id_author]['document-count']
            iterations=math.ceil(document_count/200.0)
            chunks=[]
            for size_chunk in range(0,int(iterations)+1):
                if size_chunk==0:
                    chunks.append(0)
                else:
                    chunks.append((200*size_chunk)+1)
            index_chunk=0
            id_papers=set()
            while (iterations!=0):
                #print iterations
                fields = "&field=dc:identifier&count=200"+"&start="+str(chunks[index_chunk])
                searchQuery = "query=AU-ID("+str(id_author)+") "+filter_year
                #print searchQuery
                resp = requests.get(search_api_scopus_url+searchQuery+fields, headers=headers)
                data = resp.json()
                if resp.status_code != 200:
                    raise Scopus_Exception(resp)
                data = resp.json()
                data = data['search-results']
                if data["opensearch:totalResults"] == '0':
                    papers_by_author[id_author]=dict()
                    papers_by_author[id_author].update({min_year+"-"+max_year:id_papers})
                else:
                    for entry in data['entry']:
                        paperId = entry['dc:identifier'].split(':')
                        id_papers.add(str(paperId[1]))
                iterations-=1
                index_chunk+=1
            papers_by_author[id_author]=set()
            papers_by_author[id_author]=papers_by_author[id_author].union(id_papers)
            if id_author not in scopus_papers_by_authorid_cache.keys():
                scopus_papers_by_authorid_cache[id_author]=dict()
                scopus_papers_by_authorid_cache[id_author].update({min_year+"-"+max_year:id_papers})
            else:
                scopus_papers_by_authorid_cache[id_author].update({min_year+"-"+max_year:id_papers})
    return papers_by_author
    
def get_cache_papers_by_authorid():
    """
    Returns the global variable scopus_papers_by_authorid_cache which is 
    a dictionary of dictionaries where the first dictionary key is 
    the id of the author and the key to the second dictionary is 
    the time interval whose associated value is a set of papers.
    """
    return scopus_papers_by_authorid_cache

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
