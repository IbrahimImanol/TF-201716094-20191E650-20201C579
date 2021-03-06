from collections import defaultdict, deque
from pathlib import Path
import perlin_noise
import heapq as hp
import json
import numpy as np
from sympy import sqrt
import math

def generateGraph():
    with open('Data/nyc-streets.geojson') as f:
        data = json.load(f)
    i=0
    ind=0
    ncount=0
    data=data['features']
    relations={}
    posInd={}
    def haversine(lat1, lon1, lat2, lon2):
        dlat=lat2-lat1
        dlon=lon2-lon1
        distancia= sqrt(np.double((dlon)**2)+np.double((dlat)**2))
        return np.double(distancia*100000)

    for elem in data:
        if elem['geometry']['type']=='MultiLineString':
            for coord in elem['geometry']['coordinates']:
                for a in range(len(coord)-1):
                    cad1=str(coord[a][0])+' '+str(coord[a][1]) 
                    cad2=str(coord[a+1][0])+' '+str(coord[a+1][1]) 

                    if cad1 not in relations.keys():
                        relations[cad1]=[[cad2,haversine(coord[a][1],coord[a][0],coord[a+1][1],coord[a+1][0])]]
                    else:
                        relations[cad1].append([cad2,haversine(coord[a][1],coord[a][0],coord[a+1][1],coord[a+1][0])])
                    
                    if cad2 not in relations.keys():
                        relations[cad2]=[[cad1,haversine(coord[a][1],coord[a][0],coord[a+1][1],coord[a+1][0])]]
                    else:
                        relations[cad2].append([cad1,haversine(coord[a][1],coord[a][0],coord[a+1][1],coord[a+1][0])])
                    
                    if cad1 not in posInd.keys():
                        posInd[cad1]=ind
                        posInd[ind]=cad1
                        ind+=1
                    
                    if cad2 not in posInd.keys():
                        posInd[cad2]=ind
                        posInd[ind]=cad2
                        ind+=1
        else :
            for a in range(len(elem['geometry']['coordinates'])-1): 
                cad1=str(elem['geometry']['coordinates'][a][0])+' '+str(elem['geometry']['coordinates'][a][1]) 
                cad2=str(elem['geometry']['coordinates'][a+1][0])+' '+str(elem['geometry']['coordinates'][a+1][1])         
                if cad1 not in relations.keys():
                    relations[cad1]=[[cad2,haversine(elem['geometry']['coordinates'][a][1],elem['geometry']['coordinates'][a][0],elem['geometry']['coordinates'][a+1][1],elem['geometry']['coordinates'][a+1][0])]]
                else:
                    relations[cad1].append([cad2,haversine(elem['geometry']['coordinates'][a][1],elem['geometry']['coordinates'][a][0],elem['geometry']['coordinates'][a+1][1],elem['geometry']['coordinates'][a+1][0])])

                if cad2 not in relations.keys():
                    relations[cad2]=[[cad1,haversine(elem['geometry']['coordinates'][a][1],elem['geometry']['coordinates'][a][0],elem['geometry']['coordinates'][a+1][1],elem['geometry']['coordinates'][a+1][0])]]
                else:
                    relations[cad2].append([cad1,haversine(elem['geometry']['coordinates'][a][1],elem['geometry']['coordinates'][a][0],elem['geometry']['coordinates'][a+1][1],elem['geometry']['coordinates'][a+1][0])])
                
                if cad1 not in posInd.keys():
                        posInd[cad1]=ind
                        posInd[ind]=cad1;
                        ind+=1
                if cad2 not in posInd.keys():
                        posInd[cad2]=ind
                        posInd[ind]=cad2
                        ind+=1   
        i+=1
    array=[[]]*(len(posInd)//2);
    for i in relations.keys():
        if len(relations[i])==1:
            array[posInd[i]]=[(posInd[relations[i][0][0]],relations[i][0][1])]
        else:
            array[posInd[i]]=[(posInd[relations[i][0][0]],relations[i][0][1])]
            for j in range(1,len(relations[i])):
                array[posInd[i]].append((posInd[relations[i][j][0]],relations[i][j][1]))
    pushInfo_Text(array,"grafoGeneratedText.txt");
    pushInfo_Text2(posInd,"dictPosText.txt");
    
    return array,posInd

def pushInfo_Text2(posInd,s:str):
    with open(s,'w+',newline='\n') as f:
        for i in posInd.keys():
            try: 
                int(i)
                f.write(f"{i}: "+ str(posInd.get(i))+"\n")
            except:
                continue
    
def pushInfo_Text(graph:list(list()),s:str):
    with open(s,'w+',newline='\n') as f:
        for i in range(len(graph)):
            f.write(str(i)+": "+str(graph[i])+"\n");

def convertidorNodeToPos(dicPosId,node):
    pos=dicPosId.get(node);
    pos=pos.split(' ');
    return [np.double(pos[0]),np.double(pos[1])];

def getLoc(G,dictPosId:dict()):
    n=len(G)
    L=[]
    minPosX=float('inf')
    # for node in range(n):
    #     if node==None: continue
    #     _ ,posx=convertidorNodeToPos(dictPosId,node)
    #     minPosX=min(minPosX,posx)
    
    for node in range(n):
        if node==None: continue;
        posy,posx=convertidorNodeToPos(dictPosId,int(node))
        L.append((posy,posx));
        #L.update({node:(posy,posx)});
    return L;


def bfs(G, s):
    n = len(G)
    visited = [False]*n
    path = [-1]*n # parent
    queue = [s]
    visited[s] = True

    while queue:
        u = queue.pop(0)
        for v, _,_,_ in G[u]:
            if not visited[v]:
                visited[v] = True
                path[v] = u
                queue.append(v)

    return path


def caminoAlternativo(graph,start,end):
    n=len(graph);
    cost=[math.inf for _ in range(n)];
    q=[];
    cola=deque();
    visiDict={};
    visited=[False]*n;
    path=[-1]*n;
    cola.append((start,0,-1));
    print(start);
    print(end);
    while cola:
        at,c,prev=cola.popleft();
        path[at]=prev;
        #drawG_al(G, weighted=True, path=path);
        if at==end:
            return path,cost;
        else:
            for nei,_,_,newD in graph[at]:
                if path[at]==nei or visited[nei]:continue;
                f=newD+c;
                if f<=cost[nei]:
                    cost[nei]=min(f,cost[nei]);
                    hp.heappush(q,(f,nei,at));
        while q:    
            w,at,prev=hp.heappop(q);
            if (at,prev) in visiDict or (prev,at) in visiDict or visited[at]:
                continue;
            visited[at]=True;
            visiDict[(at,prev)]=1;
            visiDict[(prev,at)]=1;
            cola.append((at,w,prev));
    return path,cost;

def dijkstra(G, start,end):
    n = len(G)
    visited = [False]*n
    path = [-1]*n
    cost = [float('inf')]*n
    path[start]=-1;
    cost[start] = 0;
    pqueue = [(0, start,-1)];
    caminos=[];
    while pqueue:
        g, u,prev = hp.heappop(pqueue)
        if not visited[u]:
            if end==u:
                return path,cost;
            visited[u] = True;
        for v,w,tr,newd in G[u]:
            if not visited[v]:
                f = g + newd
                if f < cost[v]:
                    cost[v] = f
                    path[v] = u
                    hp.heappush(pqueue, (f, v, u))
    return path,cost;




def addTrafic(graph,dicPosId):
    n=len(graph);
    noise = perlin_noise.PerlinNoise(octaves=5, seed=1981);
    #trafico:    12:00am - 2am -    4am-   6am-     8am   -10am
    traficoHora=[3.2,      3.1,     4.2,   6.60,   8.82,   8.954
                #12:00pm- 2pm-   4pm -   6pm -   8pm - 10pm
                ,7.806   ,7.355, 7.6005, 5.7544, 4.52, 3.34];
    #hora=input('Inserte hora(24 format): ');
    hora=18;
    for node1 in range(n):
        for idnode2 in range(len(graph[node1])):
            node2,dist=graph[node1][idnode2];
            pos1=dicPosId.get(node1);
            pos2=dicPosId.get(node2);
            pos1=pos1.split(' ');
            pos2=pos2.split(' ');
            x1=np.double(pos1[0]);
            y1=np.double(pos1[1]);
            x2=np.double(pos2[0]);
            y2=np.double(pos2[1]);
            traf=calcularTrafico(x1,y1,x2,y2,traficoHora,hora,noise)
            newDist=dist*traf;
            graph[node1][idnode2]=(node2,dist,traf,newDist);

def calcularTrafico(x1,y1,x2,y2,traficoHora,hora,noise):
    hora=int(hora);
    xm=(x1+x2)/2; ym=(y1+y2)/2;
    traf=abs(noise([xm,ym]));
    traf*=traficoHora[hora//2];
    return traf

def main():
    dictPosInd={};
    dictStretNodestoPos={};
    graph,dictPosInd=generateGraph();

    addTrafic(graph,dictPosInd);
    #print(graph)
    
    

if __name__=="__main__":
    main();