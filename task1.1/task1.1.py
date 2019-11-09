import csv
import json

#импортируем данные
d=[]
cd=[]
cp=[]

with open('data.csv', newline='') as csvfile:
    dreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in dreader:
        d.append(row)	
with open('context_day.csv', newline='') as csvfile:
    dreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in dreader:
        cd.append(row)
with open('context_place.csv', newline='') as csvfile:
    dreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in dreader:
        cp.append(row)

#получаем номер заданного пользователя
#print('Введите номер пользователя')
#uid=int(input())-1
uid=0


#переводим данные об оценках в более удобный формат - индексы от 1 до 30
data_lists=[]
i=0
for row in d:
    data_lists.append([])        
    data_lists[i].append(int(row[''][5:]))
    for r in row:
        if r!='':
            data_lists[i].append(int(row[r]))
    i=i+1
cur_user=data_lists[uid]

#получаем метрику сходства - индекс 31
m=0
while m!=40:
    h=1
    sum1=0
    sum2=0
    sum3=0
    if m!=uid:
        while h!=31:                
            if data_lists[m][h]!=-1 and data_lists[uid][h]!=-1:
                sum1=sum1+data_lists[m][h]*data_lists[uid][h]
                sum2=sum2+data_lists[m][h]**2
                sum3=sum3+data_lists[uid][h]**2        
            h=h+1
        sum2=sum2**.5
        sum3=sum3**.5
        sim=sum1/(sum2*sum3)
        data_lists[m].append(round(sim,3))
    else:
        data_lists[m].append(0)
    m=m+1

#отделяем четырех наиболее похожих пользователей
data_lists.sort(key = lambda row: row[31], reverse=True)
knn=data_lists[:4]

#добавляем средние значения - индекс 32
for i in range(0,4):
    sum=0
    m=0
    for j in range (1,31):
        if knn[i][j]!=-1:
            sum=sum+knn[i][j]
            m=m+1
    knn[i].append(round(sum/m,3))
sum=0
m=0
for j in range (1,31):
    if cur_user[j]!=-1:
        sum=sum+cur_user[j]
        m=m+1
cur_user.append(round(sum/m,3))

new_marks=[]

l=0
for i in range (1, 31):
    sum1=0
    sum2=0
    if cur_user[i]==-1:
        new_marks.append([])
        new_marks[l].append(i)
        for j in range(0, 4):
            if knn[j][i]!=-1:
                sum1=sum1+knn[j][31]*(knn[j][i]-knn[j][32])
                sum2=sum2+knn[j][31]
        new_marks[l].append(round(cur_user[32]+sum1/sum2, 3))
        l=l+1

#переведем данные о днях недели в более удобный формат, сразу разделим выходные и будние дни
day_lists=[]
i=0
for row in cd:
    day_lists.append([])        
    day_lists[i].append(int(row[''][5:]))
    for r in row:
        if r!='':            
            if row[r]==" -1":
                day_lists[i].append(-1)
            else:
                if row[r]==" Sat" or row[r]==" Sun":
                    day_lists[i].append(1)
                else:
                    day_lists[i].append(0)
    i=i+1


#переведем данные о местах просмотра в более удобный формат
place_lists=[]
i=0
for row in cp:
    place_lists.append([])        
    place_lists[i].append(int(row[' '][5:]))
    for r in row:
        if r!='':            
            if row[r]==" h":
                place_lists[i].append(1)
            else:
                place_lists[i].append(0)
    i=i+1

data={}
data['user']=uid+1
data['1']={}
for i in range(0, len(new_marks)):
    data['1'].update({"movie "+str(new_marks[i][0]): new_marks[i][1]})

#отделяем фильмы, не просмотренные заданным пользователем
#для каждого из них считаем, сколько раз другие пользователи смотрели эти фильмы дома
#также считаем, сколько раз другие пользователи смотрели эти фильмы в выходные
#складываем полученные показатели, умножаем на полученную ранее рассчитанную оценку в квадрате (оценка приоритетнее)
#сортируем фильмы в порядке убывания по полученному показателю

for r in new_marks:
    r.append(0)
    for i in range(0, len(day_lists)):
        for ii in range(0, len(day_lists[i])):
            if ii==r[0] and day_lists[i][ii]==1:
                r[2]=r[2]+1
for r in new_marks:
    r.append(0)
    for i in range(0, len(place_lists)):
        for ii in range(0, len(place_lists[i])):
            if ii==r[0]+1 and place_lists[i][ii]==1:
                r[3]=r[3]+1
for i in range(0, len(new_marks)):
    new_marks[i].append((new_marks[i][3]+new_marks[i][2])*(new_marks[i][1]**2))
new_marks.sort(key = lambda row: row[4], reverse=True)
print(new_marks)

data['2']={'movie '+str(new_marks[0][0]): new_marks[0][1]}


with open('task1-1.json', 'w') as outfile:
    json.dump(data, outfile)