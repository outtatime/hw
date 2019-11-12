from surprise import SVD
from surprise import Dataset
from surprise import KNNWithMeans
from collections import defaultdict

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
for line in recf:
    res=res+str(line[0])+' '+str(line[2])+' '+str(line[3])+' '+str(round(line[1], 3))+'\n'
print(res)
ff=open('res.txt', 'w')
ff.write(res)
ff.close()


