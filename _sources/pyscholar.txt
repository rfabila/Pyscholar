.. _pyscholar:

================
pyscholar module
================

.. currentmodule:: pyscholar

Scopus Author/Co-Authors
==========================
.. autofunction:: find_author_scopus_id_by_name
.. autofunction:: get_authors_by_id_affiliation

.. autofunction:: get_coauthors (id_author,min_year="",max_year="")

.. autofunction:: get_ids_authors_by_id_paper
.. autofunction:: load_authors_from_file
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



Scopus Affiliation
====================
.. autofunction:: find_affiliation_scopus_id_by_name
.. autofunction:: search_affiliation_by_id


Graph Generators
===================
.. autofunction:: get_citation_graph
.. autofunction:: get_coauthors_graph


Reading and Writing Graphs
=============================
.. autofunction:: save_graph_pickle
.. autofunction:: load_graph_pickle


Other Functions
=================
.. autofunction:: disable_graphical_interface
.. autofunction:: enable_graphical_interface
