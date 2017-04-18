#import pyscholar

def homonyms(G):
    D={}
    for i in G.author_info:
        s=""
        
        if G.author_info[i]['name']==None:
            s+="None"
        else:
            s+=G.author_info[i]['name']
        
        if G.author_info[i]['surname']==None:
            s+="None"
        else:
            s+=" "+G.author_info[i]['surname']
        
        if s not in D:
            D[s]=set()
            
        D[s].add(i)
        
    K=D.keys()
    for k in K:
        if len(D[k])<=1:
            D.pop(k)
    
    i=0
    for k in D:
        i+=1
        print str(i)+".- "+k
        print D[k]
                        
    return D

def same_info(G):
    D={}
    for i in G.author_info:
        s=""
        
        if G.author_info[i]['name']==None:
            s+="None"
        else:
            s+=G.author_info[i]['name']
            
        if G.author_info[i]['surname']==None:
            s+=" None\n"
        else:
            s+=" "+G.author_info[i]['surname']+"\n"
        
        if G.author_info[i]['affiliation-id']==None:
            s+=" None\n"
        else:
            s+=" "+G.author_info[i]['affiliation-id']+". \n"
            
        if G.author_info[i]['country']==None:
            s+="None"
        else:
            s+=" "+G.author_info[i]['country']
            
        if s not in D:
            D[s]=set()
            
        D[s].add(i)
        
    K=D.keys()
    for k in K:
        if len(D[k])<=1:
            D.pop(k)
    
    i=0
    for k in D:
        i+=1
        print str(i)+".- "+k
        print D[k]
                        
    
    return D
        
    