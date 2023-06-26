        # 0 1 2 3 4 5 6 7 8  9 0 1 2 3 4 5 6 7 
eyemap= [[1,1,0,0,0,0,0,1,1, 1,1,0,0,0,0,0,1,1], # 0
         [1,0,0,0,0,0,0,0,1, 1,0,0,0,0,0,0,0,1], # 1
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 2
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 3
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 4 
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 5
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 6
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 7
         [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0], # 8
         [0,0,0,0,0,0,0,0,1, 1,0,0,0,0,0,0,0,0], # 9
         [1,0,0,0,0,0,0,0,1, 1,0,0,0,0,0,0,0,1], # 10
         [1,1,0,0,0,0,0,1,1, 1,1,0,0,0,0,0,1,1]] # 11

columndirection=-1
counter=1000
y=12

for x in range(0, 18):
    for y_counter in range(0, 12):
        y+=columndirection
        #print (x,y)
        if eyemap[y][17-x] == 0:
            eyemap[y][17-x]=counter
            counter+=1
        else:
            eyemap[y][17-x]=1191 #(1 past the end)
    y+=columndirection
    if(columndirection==1):
        columndirection=-1
    else:
        columndirection=1


        
    #for y_count in range(0,12):
    #    y+=columndirection
    #    print(17-x, y)
    #    eyemap[y][17-x]=counter
    #    counter+=1
    #y+=columndirection
 
for r in eyemap:
   for c in r:
      print(c,end = " ")
   print()  


