import os

key = raw_input("Your scopus api key:")
s = "MY_API_KEY="+'\"'+str(key)+"\""
file_scopus=open("src/scopus_key.py","w")
file_scopus.write(s)
