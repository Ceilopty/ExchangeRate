def load():
    import time
    with open("./JPY.csv",encoding="utf-8") as f:
        k=f.read()
    l=k.splitlines()
    data=[]
    for j in l:
        data.append(j.split(','))
        data[-1][-1]=time.strptime(data[-1][-1],"%Y-%m-%d %H:%M:%S")
    return data

def save(data):
    with open("./OUT.csv","w",encoding="utf-8") as f:
        for line in data:
            f.write(",".join(line)+"\n")
import time,datetime
a = load()
temp = [a[0][4],a[0][4],a[0][4],a[0][4],datetime.date(*a[0][7][:3])]
data = []
for line in a[1:]:
    if datetime.date(*line[7][:3]) == temp[4]:
        temp[1] = temp[1] if float(temp[1]) > float(line[4]) else line[4]
        temp[2] = temp[2] if float(temp[2]) < float(line[4]) else line[4]
    else:
        temp[0] = line[4]
        temp[4] = temp[4].strftime("%Y/%m/%d")
        data.append(tuple(temp))
        temp = [0,line[4],line[4],line[4],datetime.date(*line[7][:3])]
temp[0] = a[-1][4]
temp[4] = temp[4].strftime("%Y/%m/%d")
data.append(tuple(temp))

save(data)
