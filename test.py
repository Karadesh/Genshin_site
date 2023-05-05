from datetime import datetime

c=datetime.strptime('9:00:00', '%H:%M:%S')
k=datetime.utcnow()
g=datetime.utcnow()
s =str((g-c)).split(" ")[0]
print((str(g-c)).split(" "))
print(s)
k=int(s)
a=k/365
a=str(a).split(".")[0]
if int(a)>=1:
    print("365!")
else:
    k/30
    k=str(k).split(".")[0]



"""j=("%.2f" % float(365/65))
print(j)
k= j.split(".")
print(k[1][0])"""