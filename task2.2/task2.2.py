from surprise import SVD
from surprise import Dataset
from surprise import KNNWithMeans
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import json
import re


"""из строки вида 'Conspiracy Theory (1997)' достаем год и название
если дано название в неподходящем виде, например 'World of Apu, The (Apur Sansar) (1959)'
то переносим the на место и убираем то, что в скобках (вероятно будет работать не на всех фильмах, но что поделать)"""
def get_name_and_year(movie):
    year=movie[-6:]
    name=movie.replace(year, '')
    name=name[:-1]
    year=year.replace('(', '')
    year=year.replace(')', '')
    i=name.find('(')
    if i!=-1:
        name=name[:i-1]
    i=name.lower().find(', the')
    if i!=-1:
        name=name[:i]
        name="The "+name
    return [name, year]

#ищем по названию и году выхода фильма его id
def get_id(name, year):
    sparql.setQuery("""
    SELECT ?item ?itemLabel
    WHERE { 
      ?item wdt:P31 wd:Q11424.
      ?item rdfs:label ?itemLabel. 
      ?item wdt:P577 ?date.
      FILTER(CONTAINS(LCASE(?itemLabel), LCASE("%s"@en))). 
      FILTER(year(?date)=%s)
    } limit 1
    """%(name, year))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results_df = pd.io.json.json_normalize(results['results']['bindings'])
    res=results_df['item.value'][0].split('/')[-1]
    return [res, name]
    #results_df['itemLabel.value'].to_json("ress.json")

#ищем всех актеров заданного фильма, которым на момент выхода фильма было больше сорока лет с фотографиями
def get_actors(id, name):    
    print(name)
    sparql.setQuery("""
    SELECT distinct ?actor ?actorLabel ?image 
    WHERE 
    {
      wd:%s wdt:P161 ?actor .
      ?actor wdt:P18 ?image;
             wdt:P569 ?born.
      ?actor rdfs:label ?actorLabel.
      wd:Q172241 wdt:P577 ?date.
      BIND(?date - ?born AS ?ageInDays).
      BIND(?ageInDays/365.2425 AS ?ageInYears).       
      FILTER(?ageInYears>40)  
      FILTER(LANGMATCHES(LANG(?actorLabel), "en"))      
      FILTER(!LANGMATCHES(LANG(?actorLabel), "en-gb"))
      FILTER(!LANGMATCHES(LANG(?actorLabel), "en-ca"))
    }
    """%(id))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results_df = pd.io.json.json_normalize(results['results']['bindings'])
    if not results_df.empty:
        print(results_df[['image.value','actorLabel.value']])
    else:
        print("нет подходящих результатов")
        

def get_top_n(predictions, n=5):    
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    return top_n


chosen_uid='7'

data = Dataset.load_builtin('ml-100k')
trainset = data.build_full_trainset()
algo = KNNWithMeans(k=4, min_k=4, sim_options={'name': 'cosine',
               'user_based': True, 'min_support':5 })
algo.fit(trainset)

testset = trainset.build_anti_testset()
predictions = algo.test(testset)

top_n = get_top_n(predictions, n=5)


rec=[]
for uid, user_ratings in top_n.items():
    if uid==chosen_uid:
         ([rec.append((iid, est)) for (iid, est) in user_ratings])



d=[]
i=0
f=open('u.item')
for line in f:
    d.append(line.split('|'))
f.close()
recf=[]
i=0
for line in rec:
    recf.append([])
    recf[i].append(line[0])
    recf[i].append(line[1])
    i=i+1

for row in d:
    for line in recf:
        if line[0]==row[0]:
            line.append(row[1])
            line.append(row[2])
res='User '+str(chosen_uid)+'\n'
list_for_sparql=[]
for line in recf:
    res=res+str(line[0])+' '+str(line[2])+' '+str(line[3])+' '+str(round(line[1], 3))+'\n'
    list_for_sparql.append(str(line[2]))
print(res)
ff=open('res.txt', 'w')
ff.write(res)
ff.close()


sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
for row in list_for_sparql:
    get_actors(get_id(get_name_and_year(row)[0], get_name_and_year(row)[1])[0],get_id(get_name_and_year(row)[0], get_name_and_year(row)[1])[1] )
    
