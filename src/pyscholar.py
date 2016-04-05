from scopus_key import MY_API_KEY
import json
import requests

search_api_author_url = "http://api.elsevier.com/content/search/author?"

def find_author_scopus_id_by_name(firstName="", lastName=""):
    """Searches for an author scopus id given its name."""
    
    
    headers = {"Accept":"application/json", "X-ELS-APIKey": MY_API_KEY}
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
        print json.dumps(resp.json(), sort_keys=True, indent=4, separators=(',', ': '))
        return None
    
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
