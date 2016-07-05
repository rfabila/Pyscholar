.. _scopus:

================
scopus module
================

.. currentmodule:: scopus

Scopus Author/Co-Authors
==========================
.. autofunction:: find_author_scopus_id_by_name
.. autofunction:: get_authors_by_id_affiliation

.. autofunction:: get_coauthors (id_author,min_year="",max_year="")

.. autofunction:: get_ids_authors_by_id_paper
.. autofunction:: load_authors_from_file

    :param path: The directory where the file is located.
    :type path: :class:`str`
    :returns: A list with the authors ids.
    :rtype: :class:`list`

    :Example:

    >>> import pyscholar
    >>> pyscholar.load_authors_from_file("/home/dir/authors.txt")
    >>> ['56013555800', '12645109800', '12645615700', '12646275800', '15740951000', '23388216300', '23398643600', '24171073600', '24512697200', '26032291700', '34870304900', '35566511400', '36117667600', '36117782600', '36118513000', '36141027800', '37107692000', '37111010900', '54792735300', '55439178900', '55468916100', '55669785100', '55918277800', '55943170800', '55993686500', '56002701400', '56013629200', '56013731100', '56013734400', '56240672400', '56263920000', '56279187000']
    >>>

.. autofunction:: search_author


Scopus Paper
==============
.. autofunction:: count_citations_by_id_paper
.. autofunction:: get_common_papers
.. autofunction:: get_papers
.. autofunction:: get_references_by_paper
.. autofunction:: get_title_abstract_by_idpaper
.. autofunction:: get_title_abstract_by_idpaper
.. autofunction:: load_papers_from_file

    :param path: The directory where the file is located.
    :type path: :class:`str`
    :returns: A list with the papers ids.
    :rtype: :class:`list`

    :Example:

    >>> import pyscholar
    >>> pyscholar.load_papers_from_file("/home/dir/papers.txt")
    >>> ['78149425675', '79959254005', '84883029526', '84887837079', '84892691931', '84893836569', '84897620666', '84904102369', '84908190310', '84919922003', '84924004559', '84925067887', '84928486421', '84928490197', '84928742486', '84939945186', '84939973084', '84945466401', '84961373040']



Scopus Affiliation
====================
.. autofunction:: find_affiliation_scopus_id_by_name

    :param organization: The name of the affiliation to search.
    :type organization: :class:`str`
    :returns: A data frame with the following attributes: id,city,country,name_variant,eid,affiliation_name,identifier,document_count.
    :rtype: :class:`pandas.DataFrame`

    :Example:

    >>> import pyscholar
    >>> pyscholar.find_affiliation_scopus_id_by_name("CINVESTAV")
               id                 city      country                 name_variant                        eid                   affiliation_name                              identifier          document_count
        0    60017323          Mexico City  Mexico        [CINVESTAV-IPN, CINVESTAV]             10-s2.0-60017323  Centro de Investigacion y de Estudios Avanzados    AFFILIATION_ID:60017323       19254  
        1    60010531        M&eacute;rida  Mexico              [CINVESTAV-IPN]                  10-s2.0-60010531           CINVESTAV Unidad Merida                   AFFILIATION_ID:60010531        1811
        2    60018216          Guadalajara  Mexico  [CINVESTAV, CINVESTAV Unidad Guadalajara]    10-s2.0-60018216           CINVESTAV Unidad Guadalajara              AFFILIATION_ID:60018216        1010  
        .
        .
        .
        .

.. autofunction:: search_affiliation_by_id


Graph Generators
===================
.. autofunction:: get_citation_graph
.. autofunction:: get_coauthors_graph


Reading and Writing Graphs
=============================
.. autofunction:: save_graph_pickle

    :param G: The graph object to be saved.
    :param path: The directory where the graph will be saved.
    :param name_graph: The name of the graph.
    :type G: :ref:`networkx.graph <networkx:Graph>`
    :type path: :class:`str`
    :type name_graph:  :class:`str`
    :returns: :class:`NoneType`

    :Example:

    >>> import pyscholar
    >>> psycholar.save_graph_pickle(G,"~/dir/","my_graph")

.. autofunction:: load_graph_pickle

    :param path: The directory where the pickle object is located.
    :type path: :class:`str`
    :returns: A graph G.
    :rtype: :ref:`networkx.graph <networkx:Graph>`

    :Example:

    >>> import pyscholar
    >>> my_graph = psycholar.load_graph_pickle("~/dir/graph.pickle")
    >>> my_graph


Other Functions
=================
.. autofunction:: disable_graphical_interface
.. autofunction:: enable_graphical_interface
