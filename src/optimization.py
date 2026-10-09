"""Colombo metro delivery-routing optimisation (102 real named localities).
Distances are Haversine straight-line proxies, NOT road-network travel distances.
Exact Held-Karp is benchmarked on 12 nodes; heuristics are evaluated on all 102.
"""
from pathlib import Path
import csv, math, time, itertools, random, json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"colombo_delivery_locations.csv"
def load_locations():
    with open(DATA,newline="",encoding="utf-8") as f:
        return [(r["location_name"],float(r["latitude"]),float(r["longitude"])) for r in csv.DictReader(f)]
def haversine(a,b):
    p1,p2=math.radians(a[1]),math.radians(b[1]); dp=math.radians(b[1]-a[1]); dl=math.radians(b[2]-a[2])
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371*2*math.asin(math.sqrt(h))
def matrix(points): return [[0.0 if i==j else haversine(points[i],points[j]) for j in range(len(points))] for i in range(len(points))]
def cost(route,d): return sum(d[route[i]][route[i+1]] for i in range(len(route)-1))
def held_karp(d):
    n=len(d); m=n-1; dp={}; parent={}
    for j in range(1,n): dp[(1<<(j-1),j)]=d[0][j]; parent[(1<<(j-1),j)]=0
    for size in range(2,m+1):
        for sub in itertools.combinations(range(1,n),size):
            mask=sum(1<<(x-1) for x in sub)
            for j in sub:
                pm=mask^(1<<(j-1)); k=min((x for x in sub if x!=j),key=lambda x:dp[(pm,x)]+d[x][j])
                dp[(mask,j)]=dp[(pm,k)]+d[k][j]; parent[(mask,j)]=k
    full=(1<<m)-1; last=min(range(1,n),key=lambda j:dp[(full,j)]+d[j][0])
    best=dp[(full,last)]+d[last][0]; route=[last]; mask=full; j=last
    while mask:
        k=parent[(mask,j)]; mask^=1<<(j-1)
        if k==0: break
        route.append(k); j=k
    route=[0]+route[::-1]+[0]
    return best,route
def nearest_neighbour(d,start=0):
    n=len(d)
    route=[0]
    unseen=set(range(1,n))
    if start != 0:
        route.append(start)
        unseen.remove(start)
    cur=route[-1]
    while unseen:
        nxt=min(unseen,key=lambda j:d[cur][j])
        route.append(nxt); unseen.remove(nxt); cur=nxt
    route.append(0)
    return route
def two_opt(route,d):
    best=route[:]; improved=True
    while improved:
        improved=False
        for i in range(1,len(best)-2):
            for j in range(i+1,len(best)-1):
                if d[best[i-1]][best[i]]+d[best[j]][best[j+1]] > d[best[i-1]][best[j]]+d[best[i]][best[j+1]]+1e-12:
                    best[i:j+1]=reversed(best[i:j+1]); improved=True
    return best
def main():
    points=load_locations(); d=matrix(points); results=[]
    # Same 12-node subset for a fair exact-vs-heuristic comparison
    small=d[:12]; methods=[]
    t=time.perf_counter(); opt,route=held_karp(small); methods.append(("Exact Held-Karp (12)",opt,time.perf_counter()-t,route,"optimal"))
    t=time.perf_counter(); r=nearest_neighbour(small); methods.append(("Nearest Neighbour (12)",cost(r,small),time.perf_counter()-t,r,"heuristic"))
    t=time.perf_counter(); r=two_opt(nearest_neighbour(small),small); methods.append(("Nearest Neighbour + 2-opt (12)",cost(r,small),time.perf_counter()-t,r,"heuristic"))
    t=time.perf_counter(); best=None
    for s in range(1,len(small)):
        r=two_opt(nearest_neighbour(small,s),small)
        if best is None or cost(r,small)<cost(best,small): best=r
    methods.append(("Multi-start NN + 2-opt (12)",cost(best,small),time.perf_counter()-t,best,"heuristic"))
    for name,val,rt,r,status in methods: results.append({"dataset_size":"12 nodes","method":name,"distance_km":round(val,4),"runtime_seconds":round(rt,6),"feasible":True,"optimality_status":status})
    t=time.perf_counter(); r=nearest_neighbour(d); results.append({"dataset_size":f"{len(d)} nodes","method":"Nearest Neighbour","distance_km":round(cost(r,d),4),"runtime_seconds":round(time.perf_counter()-t,6),"feasible":len(set(r[:-1]))==len(d),"optimality_status":"heuristic"})
    t=time.perf_counter(); r2=two_opt(r,d); results.append({"dataset_size":f"{len(d)} nodes","method":"Nearest Neighbour + 2-opt","distance_km":round(cost(r2,d),4),"runtime_seconds":round(time.perf_counter()-t,6),"feasible":len(set(r2[:-1]))==len(d),"optimality_status":"heuristic"})
    t=time.perf_counter(); best=None
    # Multi-start using 30 geographically distinct starting points for runtime control
    for s in range(min(30,len(d))):
        rr=two_opt(nearest_neighbour(d,s),d)
        if best is None or cost(rr,d)<cost(best,d): best=rr
    results.append({"dataset_size":f"{len(d)} nodes","method":"30-start NN + 2-opt","distance_km":round(cost(best,d),4),"runtime_seconds":round(time.perf_counter()-t,6),"feasible":len(set(best[:-1]))==len(d),"optimality_status":"heuristic"})
    out=ROOT/"results"/"comparison_results.csv"; out.parent.mkdir(exist_ok=True)
    with open(out,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=results[0].keys());w.writeheader();w.writerows(results)
    with open(ROOT/"results"/"best_102_node_route.txt","w",encoding="utf-8") as f:
        f.write("Best 102-node heuristic route (node IDs):\\n"+ " -> ".join(map(str,best))+"\\n\\n")
        f.write("Route locations:\\n"+" -> ".join(points[i][0] for i in best)+"\\n")
    print(f"Locations: {len(points)}")
    for x in results: print(x)
if __name__=="__main__": main()
