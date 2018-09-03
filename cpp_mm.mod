/*********************************************
 * OPL 12.8.0.0 Model
 * Author: Mamad
 * Creation Date: Apr 19, 2018 at 4:34:04 PM
 *********************************************/

 
int nSwitches =...;
int nLinks =...;
int nControllers =...;
int nNodes =...;
int Number_of_scenario=...;
float k=50;
float DL=100; 
range nodes=0..nNodes-1;
range scenarios=0..Number_of_scenario-1;
 
 
tuple edge{
  
	int scenario; 
 	int source;
 	int dest; 
 }
 tuple switch{
 	int loc;
 	float load;
 }
 tuple controller{
	int id;
 	float capacity;
 }
 
{int} possible_node= ...; 
{edge} links=...;
{switch} switches=...;
{controller} controllers=...;
 
dvar boolean sigma[controllers][nodes];
dvar boolean mu[controllers][controllers][possible_node][possible_node][links];
dvar boolean beta[links]; 
dvar boolean gamma[switches][controllers][scenarios];
dvar boolean  phi[switches][controllers][links][possible_node][scenarios];
dvar boolean  lambda [switches][controllers][possible_node][scenarios];
dvar float+  delta ;
dvar float+  PI;
dvar float+  THETA;
dexpr float cost = delta+k*THETA/DL+k*PI/DL;

minimize cost ;
 
subject to {

	//formula (2)
	forall(c in controllers)
		node_uniqe:
		 sum(n in possible_node)sigma[c][n]==1;

	forall(n in possible_node)
		node_1:
		 sum(c in controllers)sigma[c][n]<=1;
	//formula (3)  	
 	forall(s in scenarios,ci in controllers, cj in controllers,ni in possible_node,nj in possible_node: ci.id!=cj.id && ni!=nj )	  
 	{ 
 		   
 	   	 conservation_law_src:
 	   	  	sum(l in links:l.source == ni && l.scenario==s) mu[ci][cj][ni][nj][l]  == sigma[ci][ni] ;   
	}
 	forall(s in scenarios,ci in controllers, cj in controllers,ni in possible_node,nj in possible_node:  ci.id!=cj.id && ni!=nj )	  
 	{ 
          
 		conservation_law_dst:
 	   	  	sum(l in links:l.dest == nj  && l.scenario==s)  mu[ci][cj][ni][nj][l]   == sigma[cj][nj] ;
	}
 	forall(s in scenarios,n in nodes, ci in controllers, cj in controllers,ni in possible_node,nj in possible_node: ci.id!=cj.id && n!=nj && n!=ni )	  
 	{ 
 	          
 		conservation_law_int:
 	   	  	 sum(l in links:l.source == n  && l.scenario==s) mu[ci][cj][ni][nj][l]  - sum(l in links:l.dest == n  && l.scenario==s ) mu[ci][cj][ni][nj][l] == 0 ;	  		
	}
	 
	//formula (4)  	 
	forall(s in scenarios,ci in controllers,ni in possible_node,nj in possible_node,cj in controllers,l in links:ci!=cj && s==l.scenario)
	  mu[ci][cj][ni][nj][l] <= beta[l];
	  
	
	//formula (5)	
	/*forall(s in scenarios)
	  loacl_flow:
	 	sum(l in links: s==l.scenario) beta[l] * 0.5 <= PI;*/
	//formula (5)	
	  loacl_flow:
	 	sum(s in scenarios,l in links: s==l.scenario) beta[l] == PI;	 
	 
	//formula (6)
	forall(s in switches,sc in scenarios)
	  switch_flow:
	  	sum(c in controllers) gamma[s][c][sc] == 1; 		
	  	
	//formula (7)
	forall(c in controllers,sc in scenarios)
	  controller_load:
	  	sum(s in switches) gamma[s][c][sc]  * s.load <= c.capacity * delta  ;
	 	
	//formula (8)	
	forall(s in switches,n in possible_node,c in controllers,f in scenarios)
	  formula8:
	  	lambda[s][c][n][f]>=gamma[s][c][f]+sigma[c][n]-1;
	
	//formula 9
 	forall(sc in scenarios,nj in possible_node,s in switches, c in controllers) 
 	{ 

 		Switch_controller_latency_src:  
  	   	  	sum(l in links:l.source == s.loc && sc==l.scenario )  phi[s][c][l][nj][sc]    == lambda[s][c][nj][sc]  ;            
     	
	}
 	forall(sc in scenarios,nj in possible_node,s in switches, c in controllers) 	
 	{ 
 		Switch_controller_latency_dst:  
 		 	 sum(l in links:l.dest == nj && sc==l.scenario)  phi[s][c][l][nj][sc]  ==  lambda[s][c][nj][sc]  ;
           
	}
	forall(sc in scenarios,n in nodes,nj in possible_node,s in switches, c in controllers:n!=nj && n!=s.loc ) 	
	{ 
 		Switch_controller_latency_int:  
 	   	  	sum(l in links:l.source == n && sc==l.scenario)  phi[s][c][l][nj][sc]  - sum(l in links:l.dest == n && sc==l.scenario)  phi[s][c][l][nj][sc]  == 0 ;
 	
	}
 	//formula (10
  	/*forall(c in controllers,s in switches,sc in scenarios)
  	  highest_latenacy:
 	 	 sum(l in links:sc==l.scenario,ni in possible_node)  phi[s][c][l][ni][sc]  <= THETA;*/	
 	
 	// formula (10
  	
 		 sum(sc in scenarios,c in controllers,s in switches,ni in possible_node,l in links:sc==l.scenario)  phi[s][c][l][ni][sc]  == THETA;
	
}

 execute
    {
    var f=new IloOplOutputFile("output.txt");
    f.writeln("[vars]");
    f.writeln("Number of Nodes = ",nNodes);
    f.writeln("Number of controllers = ",nControllers);
    f.writeln("Number of Switches = ",nSwitches);
    f.writeln("");    
    f.writeln("cost = ",cost);
    f.writeln("sigma = ",sigma);
    f.writeln("gamma = ",gamma); 
    f.writeln("switches = ",switches);   
    f.writeln("Theta = ",THETA);
    f.writeln("Delta = ",delta);
    f.writeln("PI = ",PI);
    f.writeln("controllers= ",controllers);

    f.close();    
    }