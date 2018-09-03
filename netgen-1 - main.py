#!/usr/bin/env python3.6
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import sys
import random
from collections import Iterable
#from docplex.cp.model import CpoModel
from sys import stdout
import subprocess
import time
import csv
from itertools import zip_longest
import numpy as np
try:
    import configparser
except:
    from six.moves import configparser
import json
import math
import os
from scipy.stats import poisson
import string
import ast
from itertools import chain
import pickle

fname = ''
def poissongraph(n,mu):
    z= np.zeros(n) #n is number of nodes
    for i in range(n):
        z[i]=poisson.rvs(mu) #mu is the expected value
    G=nx.expected_degree_graph(z)
    H = G.to_directed()
    #print(G.edges())
    #for (fr, to) in list(G.edges()):
    #   G.add_edge(to,fr)
    #   print(to,fr)
    return H

def  writedat_param(dat,tupleInstance):
        dat.write('\r')
        for key, val in tupleInstance.items():
            dat.write(key);
            dat.write('=');
            dat.write(str(val));
            dat.write(';\r');
        dat.write('\r');

def writedat(dat,tupleName,tupleInstance):
        dat.write(tupleName)
        dat.write('={\r')
        ##print(tupleInstance)
        for f in tupleInstance:
          dat.write('<')
          if isinstance(f, Iterable):
              for e in f:
                  if e!='(' and e!=')':
                      if not isinstance(e, str):
                        if isinstance(e, Iterable):
                              for k in e:
                                  dat.write(str(k))
                                  dat.write(',');
                        else:
                              dat.write(str(e));
                              dat.write(',');
                      else:
                          dat.write("\"");
                          dat.write(e);
                          dat.write("\"");
                          dat.write(',');

          else:
                if not isinstance(f, str):
                    dat.write(str(f))
                else:
                    dat.write("\"");
                    dat.write(f);
                    dat.write("\"");
                dat.write(',');
          dat.write('>');
          dat.write('\r');
        dat.write('};\r');

def combine(loc,load):
    first_list = loc
    second_list = load
    combined_list = []
    for i in first_list:
        for j in second_list:
            combined_list.append("["+ str(i) + "," + str(j)+"]")

def removelinks(cnt,H,scenario,edge_,idx):
    G = H.copy()
    fdat = open('failed.dat','a')
    edge = []
    failed = random.sample(G.edges(), cnt)
    for (fr, to) in G.edges():
       edge.append((fr, to))
    for (fr, to) in edge_:
        #print("failed========================")
        #print((fr,to))
        try:
            if  G.degree(fr) > 2 and all(i > 2 for i in  [val for (node, val) in G.degree(G.neighbors(fr))]) and G.degree(to) > 2 and all(i > 2 for i in  [val for (node, val) in G.degree(G.neighbors(to))]):
                fdat.write("\n".join(["scenarios="+str(scenario)+'.'+str(idx)+"-removed="+str(cnt)+"=%s,%s" % (fr, to)]) + "\n")
                edge.remove((fr, to))
                edge.remove((to, fr))
                G.remove_edge(fr,to)
                G.remove_edge(to,fr)

        except:
            pass
    G.clear()
    fdat.close()

    return  edge
def removemorelinks(cnt,H,scenario,lnodes):
    G = H.copy()
    nodes = lnodes
#    nodes = random.sample(G.nodes(), cnt)
    edge = []
    fdat = open('failed.dat','a')
    for (fr, to) in G.edges():
       edge.append((fr, to))

    for node in nodes:
        print(nodes)
        for idx,(fr, to) in zip(range(scenario+1),list(G.edges(node))):
            print(idx)
            if idx <1 and G.degree(node) > 2 and all(i > 2 for i in  [val for (node, val) in G.degree(G.neighbors(node))]):
                try:
                    fdat.write("\n".join(["scenarios="+str(scenario)+"-removed="+str(cnt)+"=%s,%s" % (fr, to)]) + "\n")
                    G.remove_edge(fr,to)
                    G.remove_edge(to,fr)
                    edge.remove((fr, to))
                    edge.remove((to, fr))
                except:
                    pass
    G.clear()
    fdat.close()
    return  edge
def create_graph(test):
    G=nx.DiGraph()
    if test == 0:
        fname = 'topo.txt'
    else:
        fname = 'topo.txt'
    with open(fname,'r') as f:
        firstline = f.readline()
        header = firstline.split()
        data = f.readlines()
        node = int(header[0])
        node_list = range(node-1)
        G.add_nodes_from(node_list)
        for line in data:
            link = line.split()
            G.add_edge(int(link[0])-1,int(link[1])-1)
    return G,node


def mainf(*m_args):
    # Overrides argv when testing (interactive or below)
    if m_args:
        sys.argv = ["testing mainf"] + list(m_args)
    labels={}
    controller= int(sys.argv[1] )
    switches= int(sys.argv[2] )
    nodes=int( sys.argv[3])
    iterate=int( sys.argv[4])
    plan=int( sys.argv[5])
    test = int( sys.argv[6])
    #G=nx.DiGraph()
    #G=poissongraph(nodes,2)
    G,nodes = create_graph(test)
    node_list = range(nodes)
    #print(G)
    # G.add_nodes_from(node_list)
    # for n in G.nodes:
    #     tmp = list(node_list[:])
    #     tmp.remove(n)
    #     nbr = random.sample(set(tmp), 2)
    #     G.add_edges_from([(n,nbr[0]),(n,nbr[1])])
    #     G.add_edges_from([(nbr[0],n),(nbr[1],n)])

        #nbr = random.sample(set(tmp), 1)
        #G.add_edges_from([(n,nbr[0]),(nbr[0],n)])



    controller_pos = random.sample(node_list, controller+2)
    #print(controller_pos)

    nodetmp = list(node_list[:])
    nodetmp = np.delete(nodetmp,controller_pos).tolist()
    loc_switch = random.sample(set(nodetmp), switches)
    #print(loc_switch)
    controller_data = []
    controller_data.extend([list(a) for a in zip(range(controller), [random.randint(500,600) for r in range(controller)])])
    load = [None] * (iterate)

    for i in range(iterate):
        load[i] = [random.randint(5*i+30,50+5*i) for r in range(switches)]
    if test ==0 :
        with open('param.txt','wb') as w:
            pickle.dump(controller_pos,w)
            pickle.dump(loc_switch,w)
            pickle.dump(load,w)
            pickle.dump(controller_data,w)
    else:
        with open('param.txt','rb') as w:
            controller_pos1=pickle.load(w)
            loc_switch=pickle.load(w)
            load=pickle.load(w)
            controller_data1=pickle.load(w)
    #print(controller_pos)
    #print(loc_switch)



    percent = [0.05,0.15,0.05,0.15]
    fdat = open('failed.dat','w')
    fdat.close()
    for scenario in range(plan):
        inp={'Number_of_scenario':scenario+1,'nSwitches':switches,'nControllers':controller,'nNodes':nodes,'nLinks':G.number_of_edges(),'possible_node':set(controller_pos)}
        failure=[]
        edge = []
        delta_list = []
        theta_list = []
        cost_list = []
        pi_list = []
        rm_links = []
        ug = G.to_undirected()
        remove_ = random.sample(ug.edges(),math.ceil(ug.number_of_edges()*2*percent[scenario]))
        #len_remove = len(remove_)
        len_remove = 3
        #print(remove_)
        inp={'Number_of_scenario':len_remove,'nSwitches':switches,'nControllers':controller,'nNodes':nodes,'nLinks':G.number_of_edges(),'possible_node':set(controller_pos)}
        if scenario < 2:
            inp={'Number_of_scenario':len_remove,'nSwitches':switches,'nControllers':controller,'nNodes':nodes,'nLinks':G.number_of_edges(),'possible_node':set(controller_pos)}
            for idx in range(3):
                #rm_links = removemorelinks(len(rnodes),G,scenario,[fl])
                #rm_links = removelinks(len(remove_),G,scenario,[fl],idx)
                if (len(remove_)>3 and idx ==2):
                    rm_links = removelinks(len(remove_),G,scenario,remove_[idx:],idx)
                    failure = [idx] * len(rm_links)
                    edge.extend([list(a) for a in zip(failure,rm_links)])
                else:
                    rm_links = removelinks(len(remove_),G,scenario,[remove_[idx]],idx)
                    failure = [idx] * len(rm_links)
                    edge.extend([list(a) for a in zip(failure,rm_links)])

        else:
            #len_remove = 1
            inp={'Number_of_scenario':len_remove,'nSwitches':switches,'nControllers':controller,'nNodes':nodes,'nLinks':G.number_of_edges(),'possible_node':set(controller_pos)}
            #random.shuffle(remove_)
            for idx in range(3):
                #random.shuffle(remove_)
                if idx < 111:
                    # cut = random.randint(1, len(remove_))
                    # list_1 = remove_[:cut]
                    # list_2 = remove_[cut:]
                    #rm_links = removemorelinks(len(rnodes),G,scenario,[fl])
                    if (len(remove_)>3 and idx ==2):
                        rm_links = removelinks(len(remove_),G,scenario,remove_[idx:],idx)
                        failure = [idx] * len(rm_links)
                        edge.extend([list(a) for a in zip(failure,rm_links)])
                    else:
                        rm_links = removelinks(len(remove_),G,scenario,[remove_[idx]],idx)
                        failure = [idx] * len(rm_links)
                        edge.extend([list(a) for a in zip(failure,rm_links)])



        for i in range(iterate):
            l=[]
            l.extend([list(a) for a in zip(loc_switch, load[i])])
            dat = open('input.dat','w')
            writedat_param(dat,inp);
            writedat(dat,'links',edge);
            writedat(dat,'switches',l);
            writedat(dat,'controllers',controller_data)
            dat.close()
            with open(os.devnull, "w") as f:
                subprocess.check_call(["C://Program Files//IBM//ILOG//CPLEX_Studio128//opl//bin//x64_win64//oplrun.exe" ,"cpp_mm.mod", "input.dat"],stdout=f)
            config = configparser.ConfigParser()
            config.read("output.txt", encoding = "ISO-8859-1")
            cost = config.get("vars", "cost")
            sigma = config.get("vars", "sigma")
            delta = config.get("vars", "delta")
            theta = config.get("vars", "THETA")
            gamma = config.get("vars", "gamma")
            switch_loc = config.get("vars", "switches")
            controller_loc = config.get("vars", "controllers")
            pi  = config.get("vars", "PI")
            cost_list.append(cost)
            theta_list.append(theta)
            delta_list.append(delta)
            pi_list.append(pi)
            sigma = sigma.replace(' ',',')
            sigma = sigma.replace('\n',',')
            t = json.loads(sigma)
        print("delta=" ,delta_list)
        print("theta=",theta_list)
        #print(gamma)
        d3 = [ np.mean(load, axis=1), delta_list,theta_list, pi_list,cost_list]
        export_data = zip_longest(*d3, fillvalue = '')
        with open(fname+'numbers'+str(scenario)+'.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
          wr = csv.writer(myfile)
          wr.writerow(("x", "Scenario"+str(scenario)))
          wr.writerows(export_data)
        myfile.close()
        a=switch_loc.replace("<","(")
        b=a.replace(">",")").replace("}","]").replace(" ",",").replace("{","[").replace("\n","")
        #print(b)
        #swloc,swload = zip(*ast.literal_eval(b))
        cp = controller_loc.replace("<","(").replace(">",")").replace("}","]").replace(" ",",").replace("{","[").replace("\n","")
        cloc,cload = zip(*ast.literal_eval(cp))
        #print(gamma)
        g = gamma.replace("]","").replace("[","").replace("\n","").replace(" ","")
        #print(g)
        tg = [g[i::len_remove] for i in range(len_remove)]
        #print(tg)
        gg = [0] * len_remove
        for j in range(len_remove):
            #print(t[j])
            gg[j] = [tg[j][i*controller:controller*(i+1)] for i in range(len(loc_switch))]
        #print(gg)
        colors = ['yellow','orange','yellow','black','brown','orange']
        color_map =  ['orange'] * nodes
        control_set=[]
        node_sizes = [70] * nodes

        for conidx,con  in enumerate(t):
            #print(con)
            for nodeidx,node in enumerate(con):
                if node == 1 :
                    labels[nodeidx] = "Controller"
                    color_map[nodeidx]=colors[conidx]
                    control_set.append(nodeidx)
                    node_sizes[nodeidx] = 700
                elif loc_switch.count(nodeidx) == 1 and control_set.count(nodeidx)!=1:
                    idxsw =loc_switch.index(nodeidx)
                    #print(colors[gg[idxsw].index("1")])
                    #labels[nodeidx] = "SW" + str(nodeidx)
                    #print(gg[scenario])
                    #print(gg[scenario][idxsw].index("1"))
                    #print(gg)
                    color_map[nodeidx]=colors[gg[0][idxsw].index("1")]
                    node_sizes[nodeidx] = 250
                elif  control_set.count(nodeidx)!=1 :
                    labels[nodeidx] = nodeidx
                    color_map[nodeidx]='green'
        #nx.draw(G,labels=labels,node_color = color_map,font_size=10,with_labels = True)
        #print(color_map)
        #print(node_sizes)
        nx.draw(G,node_size = node_sizes,node_color = color_map,font_size=10,with_labels = True)
        plt.suptitle(r'# Controllers='+str(controller)+" # Switches="+str(switches), fontsize=8, fontweight='bold')
        plt.savefig("Graph"+str(scenario)+".png", format="PNG")
        plt.show(block=True)

if __name__ == "__main__":
    if False: # not testing?
        sys.exit(mainf())
    else:
        mainf("2", "9","21","10","4","0")
        #mainf("3", "1","20")
