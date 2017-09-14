import xml.etree.ElementTree as ET


def get_node_dict_layout_from_graphml_file(filename):
    """Reads the given graphml file an extracts the nodes attributes. The idea is that the graphml was
    probably modified in gephi."""
    D={}
    tree = ET.parse(filename)
    root=tree.getroot()
    for v in root.iter("{http://graphml.graphdrawing.org/xmlns}node"):
        name=v.attrib['id']
        #print name
        d={}
        for ch in v:
            d[ch.attrib['key']]=ch.text
        D[name]=d
    return D

def apply_layout(H,D):
    for v in H.nodes():
        if v in D:
            for key in D[v]:
                H.node[v][key]=D[v][key]
