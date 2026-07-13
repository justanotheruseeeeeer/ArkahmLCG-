import pandas as pd
import numpy as np
import math
from collections import Counter
import matplotlib.pyplot as plt
import plotly.express as px
from bayes_opt import BayesianOptimization
################################
#Investigators should be classes. To keep their restrictions and passives and stats personal and immediate.
###########################




        
    
metagame=[
    {'Id': 'Cost', 'Label': 'Cost', 'Type': 'cost'},
    {'Id': 'Damage', 'Label': 'Damage', 'Type': 'dm'},
    
    {'Id': 'Evade', 'Label': 'Evade', 'Type': 'evade'},
    {'Id': 'Investigate', 'Label': 'Investigate', 'Type': 'inv'},
    {'Id': 'Resourceful', 'Label': 'Resourceful', 'Type': 'res'},
    {'Id': 'heal_dmg', 'Label': 'heal_dmg', 'Type': 'heal_dmg'},
    {'Id': 'heal_hor', 'Label': 'heal_hor', 'Type': 'heal_hor'}
]#Add horror taken, sanity 
len_met=len(metagame)
####################################
#Decks should be classes in order to breed them comfortably
##############################
deck = [
    {'Id': '0', 'name': 'Arcane initiate',  'search': 3, 'num_sea':4, 'Type':'stre','cost': 1},
    {'Id': '1', 'name': 'Arcane initiate',   'search': 3,'num_sea':4,  'cost': 1, 'Type':'stre'},
    {'Id': '2','name': 'Forbidden kwnoledge ',  'res': 1, 'dm':1 , 'Type':'stre','fix':1,'time':4,'AP+':1},
    {'Id': '3','name': 'Forbidden kwnoledge ',  'res': 1, 'dm':1 , 'Type':'stre','fix':1,'time':4,'AP+':1},
    {'Id': '4','name': 'Emergency cache', 'res': 3,  'draw': 1},
    {'Id': '5','name': 'Emergency cache', 'res': 3,  'draw': 1},
    {'Id': '6','name':'Shrivelling', 'cost':3, 'dm':2, 'time':4,'Type': 'Goal_Card'}
        ,{'Id': '7','name':'Azure Flame','cost':3, 'dm':2, 'time':3,'Type': 'Goal_Card'}
          ,{'Id': '8','name':'Azure Flame','cost':3, 'dm':2, 'time':3,'Type': 'Goal_Card'}
            ,{'Id': '9','name':'Clairvoyance', 'cost':4,'inv':2,'time':3, 'Type': 'Goal_Card'}
              ,{'Id': '10','name':'Clairvoyance', 'cost':4,'inv':2,'time':3,'Type': 'Goal_Card'}
                ,{'Id': '11','name':'Clarity of mind','cost':2,'heal_hor':2, 'time':3,'Type': 'Goal_Card'} 
                  ,{'Id': '12','name':'Clarity of mind','cost':2, 'heal_hor':2,'time':3,'Type': 'Goal_Card'}
                    ,{'Id': '13','name':'Blinding light','cost':2, 'evade':1,'dm':1, 'Type': 'Goal_Card','Add_Q':1}
                      ,{'Id': '14','name':'Shrivelling', 'cost':3, 'dm':2, 'time':4,'Type': 'Goal_Card'}
                        ,{'Id': '15','name':'Ward of protection','cost':1, 'Type': 'Goal_Card', 'dm':1,'fix':1}
                          ,{'Id': '16','name':'Ward of protection','cost':1,'Type': 'Goal_Card', 'dm':1,'fix':1}
                            ,{'Id': '17','name': 'Peter ','perm_A':1, 'cost':3,  'Type':'stre'}
                              ,{'Id': '18','name': 'A test of will', 'cost':1}
                                ,{'Id': '19','name': 'Drawn to the flame', 'inv' :2,'fix':1}
                                  ,{'Id': '20','name':'lucky', 'cost':2,'icons':2, 'Type':'hel'}#not really a way to explain the TEMPO and fast actions....
                                    ,{'Id': '21','name':'lucky', 'cost':2,'icons':2, 'Type':'hel'}
                                      ,{'Id': '22','name':'Holy rosary','perm_A':1,  'Type':'stre','cost':2}
                                        ,{'Id': '23','name':'Holy rosary', 'perm_A':1,  'Type':'stre','cost':2}#perm 1 meaning it gives us a permanent 1 extra icon always.
                                          ,{'Id': '24','name':'guts', 'draw':1,'icons':2, 'Type':'hel'}
                                            ,{'Id': '25','name':'guts','draw':1,'icons':2, 'Type':'hel'}
                                              ,{'Id': '26','name':'fearless','icons':1, 'Type':'hel'}#it heals 1 horror
                                                ,{'Id': '27','name':'fearless','icons':1, 'Type':'hel'}
                                                  ,{'Id': '28','name':'unexpected courage','icons':2, 'Type':'hel'}
                                                    ,{'Id': '29','name':'unexpected courage','icons':2, 'Type':'hel'}
                                                      
    ,{'Id': '30','name': 'Strenght',  'draw': 1,'time':7, 'cost': 3,'res':0, 'Type':'stre'},#actually this draw happens passively but we will "cancel out" the factors and write it directly in the code
    {'Id': '31','name': 'Treachery',  'draw': 0, 'cost': 4,'res':0,'Type': 'Goal_Card', 'dm':-1.25},#if we DO NOT play it then it deals damage passively through agnes. But there's no way to calculate TEMPO so far. Also it gives 1 doom regardless
    {'Id': '32','name': 'Weak'}]
deck_size_out=len(deck)
#WE CREATE THE 3 ACTION CLOCK
actioon=[{'Id': 'Action', 'Label': 'Action', 'Type': 'Action'},{'Id': 'Action1', 'Label': 'Action1', 'Type': 'Action'},{'Id': 'Action2', 'Label': 'Action2', 'Type': 'Action'}]
bolsa=[2,1,0,0,-1,-1,-1,-1,-1,-2,-2,-2,-2,-3,-4] #the doom sack. This can be easily personalized
main_att=5
#3.5.  define the proficiency of investigate, evade or damage in skill tests too.   
# We always take the proficiency of succeeding in standard difficulty, against a 4 skill test.
# We always take for granted that assets with permanent bonus are in play towards the end of the game, so we take those into account
# We take a chunk of the icons of abilities
# 
#   
bolsa=[2,1,0,0,-1,-1,-1,-1,-1,-2,-2,-2,-2,-3,-4] #the doom sack. This can be easily personalized

def V(x_query,bolsaaa):
    counts = Counter(bolsaaa)
    
    # 1. Sort ascending so we build the area from left to right
    values = sorted(counts.keys())   # [-4, -3, -2, -1, 0, 1, 2]
    
    total = 0.0
    
    for v in values:
        lower_edge = v - 1
        
        # 2. If the query is completely past this bin, add the full bin count
        if x_query >= v:
            total += counts[v]
            
        # 3. If the query falls inside this bin, add the fraction and stop
        elif lower_edge < x_query < v:
            fraction = x_query - lower_edge
            total += fraction * counts[v]
            break
            
        # 4. If the query is completely below this bin, we are done
        else:
            break
            
    return total
def G(x,bolsa):
    return (V(3,bolsa)+1-V(-x-1,bolsa))/(V(3,bolsa)+2)#2 because +1 in denominator for immediate succes and +1 for immediate failure.
def F(x,y,bolsa):
    if y<=0:
        return 1
    else:
        return G(x-y,bolsa)  

#############
#We create a class for the perm_add
#############

class ClockAdd:
    """This represents the clock of Adds, like blessed tokens or just encyclopedia.
    """
    def __init__(self, quant, clock, prob, vessel):
        self.mod=quant*prob
        self.time=clock
        self.place=vessel
        self.place.append(self)
        if self.time>=1:
            self.time+=1
    def pass_time(self):
        if self.time<1:
            if self in self.place:
                self.place.remove(self)
            return False#must erase
        else:
            self.time-=1
            return True

class ArkhamSimulator:
    def __init__(self, deck_configg, bolsaa, alphaa):
        # All your global variables go here
        
        self.deck_config = deck_configg
        self.bolsa = bolsaa
        self.alpha = alphaa
        self.perm_Add = 0
        self.perm_Red = 0
        self.rect=0
        self.deck_size =0
        self.perm_Add = 0
        self.perm_Red = 0
        #unwrapping
        deck_config=self.deck_config
        bolsa=self.bolsa
        alpha=self.alpha
        deck_size = self.deck_size
        deck_search=0
        deck_hel=0
        deck_goal=0
        deck_stre=0
        for x in deck_config:
            deck_size+=1
            if x.get('Type',0)=='Goal_Card':
                deck_goal+=1
            if x.get('search',0)>0:
                deck_search+=1
            if x.get('Type',0)=='stre':
                deck_stre+=1
            if x.get('Type',0)=='hel':
                deck_hel+=1
        self.deck_size=deck_size
        self.chacha=1-deck_hel/deck_size
        chacha=self.chacha
        NN=5*chacha
        self.rect=0.3*(1.7*NN/(NN-1)+0.4*(NN*(NN-2)/((NN-1)*(NN-1))))
        # 2. Build Node Lists 
        node_data = []
        for c in deck_config:
            
            node_data.append({'Id': c['Id'], 'Label': c['Id'], 'Type': 'Card'})
        #We could just do the same for loop
        for x in metagame:
            node_data.append(x)
        for x in actioon:
            node_data.append(x)
        nodes_df = pd.DataFrame(node_data)


        # 3. Build Edge List
        edges_list = []
        simple_edges_list=[]
        node_map = {name['Id']: i for i, name in enumerate(node_data)}
        self.node_map=node_map
        n = len(node_data)
        adj_matrix = np.zeros((n, n))

        # A. Internal Card-to-Card connections (Drawing)
        new_deck_goal=deck_goal
        for src in deck_config:
            if src.get('draw', 0) > 0:#this we can later eliminate
                for tgt in deck_config:
                    if tgt['Id']==src['Id']:
                        continue
                    weight = src['draw'] * (1/ (deck_size-1))/(chacha*5)*self.rect #this chacha5^-1 represents the chance of the draw card being played. 5 cards in hand and 1 cards to play per action
                    if weight > 0:
                        edges_list.append({'Source': src['Id'], 'Target': tgt['Id'], 'Weight': weight})
                        adj_matrix[node_map[src['Id']], node_map[tgt['Id']]] = weight
            if src.get('search', 0) > 0:
                x=src['search']
                
                memo=0
                ttt=src['num_sea']
                for tgt in deck_config:
                    if tgt.get('Type',0)=='Goal_Card':
                        if tgt.get('name',0)=='Treachery':
                            new_deck_goal-=1
                            a=tgt
                            weight=math.comb(deck_size-1-deck_goal,x-1 )/math.comb(deck_size-1,x)*3/5#3/5 because we assume 5 cards in hand, so 5 possible actions and 3 actions per turn.
                            memo+=weight*5/3#we want the probability here assuming we did use the search, not the full bayesian probability
                            #we search a total of ttt times, so:
                            pro=math.comb(deck_size-1-deck_goal,x)/math.comb(deck_size-1,x)#chance of getting nothing
                            
                            weight=0
                            for i in range(ttt):
                                weight+=pro**i*memo*1/5/chacha#1/5 is the modal or harmonic geometric average chance of playing that specific card
                            edges_list.append({'Source': src['Id'], 'Target': a['Id'], 'Weight': weight})
                            
                            adj_matrix[node_map[src['Id']], node_map[a['Id']]] = weight*self.rect
                        if tgt.get('name',0)!='Treachery':
                        #3.21. define the proficiency of the searches with a function.
                        ####################################### Supposing we have all 32 other cards, we have deck_goal cards to get. And the connection will be as follows:
                        #If we search X cards, then the chance of getting no searches is (deck-deck_goal-1) chooses x/deck-1 chooses x, so getting only normals over all possible outcomes.
                        # Then if we have a treachery that can be searched, we only draw it if it is the only searched one, so we have x-1 holes to fill up with normal cards:
                        #so deck-1-deck_goal chooses x-1 / deck-1 chooses /deck_goal.
                        #Finally, the chance we have left is the chance to draw some non treachery cards, it is equiprobable among the goal-1 cards.
                            pro=math.comb(deck_size-1-deck_goal,x)/math.comb(deck_size-1,x)#chance of not getting anything
                            #print(new_deck_goal)
                            g_c=(1-memo-pro)
                            weight =0
                            for i in range(ttt):
                                weight+=pro**i*g_c*1/5/chacha
                            if weight > 0:
                                edges_list.append({'Source': src['Id'], 'Target': tgt['Id'], 'Weight': weight})
                                
                                adj_matrix[node_map[src['Id']], node_map[tgt['Id']]] = weight*self.rect
        #5. Mulligan initial state


        #We will attend to the following mulligan strategy:
        #1) If in our starting 5 hand we have at least 1 'stre' we will keep one 'stre'
        #2)If we have no goal cards we will mulligan everything allowed (not one stre)
        #3)If we have at least one goal card, we will only mulligan surreptitiously to avoid duplicity of cards, or tendencies towards one aspect like evading. This is barely strategic 
        # and only depends on the amount of cards of each type, evade, dmg, cost etc. We assume similar sizes of the sub strategies and thus avoid any 
        # significant change on the probabilities given this rule

        #We have to take three scenarios and their probabilities into account:1)Good nitial hand 2)Necessary whole mulligan 3)Partial mulligan
        #Then in each scenario given that we must have 5 cards, we take the aerage of each cards and know full weell  their sum mst give 5.
        # Then we take the weighted average given the probabilities of each scenario.
        p=[0,0,0]
        Goal=[0,0,0]
        Stre=[0,0,0]
        Normal=[0,0,0]
        #1)Chance to get goal cards. (iff no mulligan)
        p[0]=1-math.comb(deck_size-2-new_deck_goal, 5)/math.comb(deck_size-2, 5)#opposite of chance of having the 5 chosen cards to be normal
        #We have 1 goal card and 4 other possible cards, all equally likely, so :
        Tot=deck_size-2-1
        Goal[0]=1+4*(new_deck_goal-1)/Tot
        Stre[0]=4*deck_stre/Tot
        Normal[0]=5-Goal[0]-Stre[0]
        #Is 5 cards total
        #2)Chance to get none stre nor goal (iff whole mulligan)
        p[1]=math.comb(deck_size-2-new_deck_goal-deck_stre, 5)/math.comb(deck_size-2, 5)
        #So now we have 5 less noraml cards and all the other cards
        Tot=deck_size-2-5
        Goal[1]=5*(new_deck_goal)/Tot
        Stre[1]=5*deck_stre/Tot
        Normal[1]=5-Goal[1]-Stre[1]#less cahnce overall
        #3)Partial mulligan (iff chance to get no goal but stre yes)
        p[2]=1-p[0]-p[1]
        #So now we now we have kept 1 stre, and have all the goal available
        Tot=deck_size-2-5
        Goal[2]=4*(new_deck_goal)/Tot
        L=(Tot-new_deck_goal)/(Tot)*(1/(Tot+5-new_deck_goal-1))
        #print(L)
        Stre[2]=1+4*(deck_stre-1)*L
        Normal[2]=5-Goal[2]-Stre[2]#=Av*4*L And L is the solution to the equations
        vectorGoa = np.array(Goal)
        vectorStre= np.array(Stre)
        vectorNorm = np.array(Normal)
        proba=np.array(p)
        #
        #This results in the average of cards per faction, if we dividw each element by the cardinality of the faction we get the density per card in the starting hand.
        norma=vectorNorm@proba/(deck_size-2-new_deck_goal-deck_stre)
        goa=vectorGoa@proba/(new_deck_goal)
        atr=vectorStre@proba/(deck_stre)
        #
        randgene=[]
        mulligan=[]
        perfect=[]
        one_z=[]
        for i in deck_config:
            perfect.append(0)
            if i['name']=='Treachery' or i['name']=='Weak':
                mulligan.append(0)
                randgene.append(0)
                
                continue
            if i.get('Type',0)==0:
                mulligan.append(norma)
            if i.get('Type',0)=='hel':
                mulligan.append(norma)
            if i.get('Type',0)=='stre':
                mulligan.append(atr)
            if i.get('Type',0)=='Goal_Card':
                mulligan.append(goa)
            #print(i)
            randgene.append(5/(deck_size-2))#2 weaknesses generally
        one_z.append(0)
        one_z.append(0)
        for i in metagame:
            mulligan.append(0)
            randgene.append(0)
            if i =={'Id': 'Cost', 'Label': 'Cost', 'Type': 'cost'}:
                perfect.append(-2/5)#heuristics...
                one_z.append(0)
            else:
                
                perfect.append(1)
                one_z.append(1)
            
        for i in actioon:
            perfect.append(0)
            one_z.append(0)
            if i=={'Id': 'Action', 'Label': 'Action', 'Type': 'Action'}:
                mulligan.append(1)
                randgene.append(1)
            else:
                mulligan.append(0)
                randgene.append(0)
        #print(mulligan)
        self.mull=np.array(mulligan)
        self.ra=np.array(randgene)
        self.per=np.array(perfect)
        self.oo=np.array(one_z)
        #print(mull)
        #Now we have the whole mulligan starting hand defined
        #6. Matrix multiplication for final states averaged and idealized
#################################
#MAYBE DEBUG THIS AND PUT IT IN THE DECK PUT IT IS HONESTLY NOT NECESASARY SINCE WE HAVE TO RECALCULATE IT ALWAYS ANYWAYS
############################################3
            #The following clock correctly accounts for the costs and damage and every value of the card and its limited uses.
            #This means that now we can justify adding an 4/5 autoloop for each and every single card except some fringe cases.
            ################################
            #4/5 autoloop heuristic clock:
            ##################################
        for src in deck_config:
            clock=1-1/(5*chacha)
            if src.get('Type',0)=='hel':
                clock=alpha
            adj_matrix[node_map[src['Id']], node_map[src['Id']]] = clock
        #This previous line of code describes the current randomness of playing cards per action
        # C. Cost_Sink Self-Loop (The "Memory" edge)
        #add the action clock. 

        for x in metagame:
            adj_matrix[node_map[x['Id']], node_map[x['Id']]] = 1.0
        for x in range(len(actioon)):
            
            y=actioon[x]
            z=actioon[((x+1)%len(actioon))]
            
            edges_list.append({'Source': y['Id'], 'Target': z['Id'], 'Weight': 1.0})
            adj_matrix[node_map[y['Id']], node_map[z['Id']]] = 1.0
            
        for y in deck_config:
                edges_list.append({'Source': 'Action2', 'Target': y['Id'], 'Weight': 1.0*(1/deck_size)}) #times 2 with harvey walters
                adj_matrix[node_map['Action2'], node_map[y['Id']]] = 1.0*(1/(deck_size)) 
        for src in deck_config:
                clock=src.get('time',0)
                if clock>1:
                                
                                clock=1-1/(clock+1)#it includes the preparing of the card
                                #this is the ratio of the geometric progression that sums up to a.
                                #So we prepare the spell and fire it "infinitely" to take a actions total, this is 1+clock+clock^2+...=a
                                #The problem is that this is assuming the spell is firing, in actuality it fires with 1/5 chance so. 1/5*1(chance prepare) and 1/5*clock(chance of firing)
                                #Some simple maths show that treating the spell node like this, with an 4/5 autoloop for not playing the card and a 1/5clock autoloop correctly accounts for the limit of actions while keeping the actual
                                #memory value of the card, total damage for example.
                                clock=1/5*clock/chacha
                                if src.get('Type',0)=='hel':#icons you can use repeatedly mainly for rogues. But also the old pages of -2 reduction for 3 actions from the librarians.
                                    clock=src.get('time',0)
                                    clock=1-1/(clock+1)
                                    clock=clock*alpha
                                adj_matrix[node_map[src['Id']], node_map[src['Id']]] += clock
        self.adj=adj_matrix[:]
    #def chance(self, card, test, state):
        # Your math for success goes here
        # Notice we use self.bolsa instead of just bolsa
        #v_val = self.V(test['value']) 
        #return v_val / len(self.bolsa)
    #def matr45(self, initial_hand):
        # Your Markov chain logic
        # Instead of returning just a vector, we can return a dictionary 
        # of metrics for the Radar Chart
        #final_state = ... # (the result of the matrix multiplication)
        #remember the spider graphs
        #return final_state
    
    def chance(self,x,y,A,add=0,redd=0):
        #A is the "mass" matrix.
        if y== {'Id': 'Resourceful', 'Label': 'Resourceful', 'Type': 'res'}:
                return 1
        if y== {'Id': 'Cost', 'Label': 'Cost', 'Type': 'cost'}:
                return 1
        if x.get('fix')==1:
            
            return 1
        bolsa=self.bolsa
        j=[]
        l=[]
        ad=0#so we need to also do a thing with "permanent" additions with like the rosary for example. I can only think of a BIG clock.
        red=0#We still should make the clock
        ad+=add
        red+=redd
        perm_Add=self.perm_Add
        perm_Red=self.perm_Red
        #We still need to do one about the ad and red permanently. Just put them outside and whenever a "permanent" one fires add it. And then use interpolation
        ###########################
        #INTERPOLATION AND PERMANET BUFS/DEBUFFS
        #############################
        ad+=x.get('add',0)#the add means a literal addition to your roll because of card properties
        red+=x.get('red',0)#the reductions
        ad+=perm_Add
        red+=perm_Red
        deck_config=self.deck_config
        alpha=self.alpha
        for h in deck_config:#unfortunately we don't have really have a way to actually couple this with the firing of "help" cards... But we can put the same chance (4/5) and actually connect this to the chance of each card...
            if h.get('Type',0)=='hel':
                j.append(F(main_att+ad+h.get('icons',0)+h.get('loser_icon',0),5-red-h.get('red',0),bolsa)*(alpha)+F(main_att+ad,5-red,bolsa)*(1-alpha))#kinda a fifth chance to use any help card. This is by far the worst heuristic in the game but it seems to give some reasonable numbers
                #doesnt take into account correctly the using various cards simultaneously but its quite unlikely so it probably doesnt matter.
                
            else:
                j.append(F(main_att+ad,5-red,bolsa))
            l.append(1)
        for i in metagame:
            j.append(0)
            l.append(0)
        for i in actioon:
            j.append(0)
            l.append(0)
        
        return (A@j)/(A@l)#if we take into account the "mass" it should be 5 that is our playable mass. This is a "chance" vector.
    # B. Card-to-Costlike_Sinks connections 
    #Problem with the spells firing simultaneously and their internal clocks. Correct the cost per action based on the recurrence simplification

    def matr45(self,t):#This turns our program into a kind of markov chain.
        ooo=t[:]
        #wrapping
        self.perm_Add=0
        self.perm_Red=0
        deck_config=self.deck_config
        chacha=self.chacha
        rect=self.rect
        adj_matrix=self.adj
        node_map = self.node_map
        actions_remaining = 39+1 # Total actions in the simulation. =Turns*3+1. 13 turns because under 15 turns 6 whole actions WILL be spent on movement, here it's unaccounted for.
        res_gen_bad=0
        array_add_clock=[]#the add clock
        #while actions_remaining>1:
        robb=[]
        addd=0
        for i in range(actions_remaining+7):
            actions_remaining-=1
            j=-1
            ############################# lets see if ths will work
            k=1.29*ooo[node_map['Cost']]-(ooo[node_map['Resourceful']]+res_gen_bad+(0.34*i)+5)
            if k>0:
                res_gen_bad+=1
                robb.append(min(1,k))
                #print("robbed")
                continue
            robb.append(0)
            if actions_remaining<-0.1:
                break
            ################################ well it works!!!!!!!!!!!!!!!!!
            array_add_clock=[r for r in array_add_clock if r.pass_time()]
            addd=sum(r.mod for r in array_add_clock)
            for src in deck_config:
                j+=1
                actions_remaining+=src.get('AP+',0)*1/5/chacha*rect*ooo[j]#Action Points economy. If the result is movement and/or fast it will be +1 AP. This cards are indeed in the normal cards pool, unlike skills.
                actions_remaining-=src.get('AP-',0)*1/5/chacha*rect*ooo[j]
                # The code snippet is checking if the dictionary `src` contains keys 'perm_A' and
                # 'perm_R' with values greater than 0. If the condition is met, it calculates and
                # updates the values of `self.perm_Add` and `self.perm_Red` respectively based on the
                # formula provided. The formula involves multiplying the value of 'perm_A' or 'perm_R'
                # with the corresponding value in the list `ooo`, then dividing by 5, `chacha`, and 3.
                # The comment in the code suggests that the division by 3 is due to limited slots.
                
                        #print(perm_Add)
                self.perm_Add+= src.get('perm_A',0)*ooo[j]*1/(8*chacha)#we divide by approx 2 due to the limited slot
                self.perm_Red+= src.get('perm_R',0)*ooo[j]*1/(8*chacha)
                
                
                for x in metagame:   #this is another heuristic, once again we find it uncoupled from the actual system. Kinda a tensor decomposition
                    if src.get(x['Type'],0) > 0:
                        
                        clock=src.get('time',0)
                        a=1
                        if x['Type']=='cost':
                            a=clock+1#we add the "prepare" action of the spells. We only pay the spell once however it's the only thing that will only be "fired" once. So we divide over all actions.
                        weight = src[x['Type']]*self.chance(src,x,ooo,addd+src.get('Add',0))*1/5/chacha*rect
                        #print(chance(src,x,ooo),src,x)
                        #we take the total effect of a card per action, and make them "equiprobable"
                        adj_matrix[node_map[src['Id']], node_map[x['Id']]] = weight/a
                        #The above occurs when "firing the spells". So now we have to maintain the mass of the system, there's a 4/5 of not firing sad spell, meaning that amount of mass stays.
            for src in deck_config:
                ClockAdd(src.get('Add_Q',0),src.get('Add_Clock',0),rect*ooo[j]*1/(5*chacha),array_add_clock) #creation of various instances of adds
            ooo=(np.array(adj_matrix).T)@ooo
            #print(self.perm_Add)
            #print("adj;",adj_matrix)
            #print(res_gen_bad)
            #print(self.perm_Add)
        return ooo, robb
    def result(self,mull,spid=0):
        print("Our final state with our preferred strategy and deck is: ")
        
        aa, data =self.matr45(mull)
        print(aa)
        print(  "Our score with our preferred strategy and deck is:  ")
        
        print(aa@self.per)
        metagame_stats = list(aa[self.deck_size+1 : self.deck_size+len_met] / (aa[self.deck_size] + 1e-9))

        # Calculate the 'durability' (total progress / total mulligan)
        durability = (np.sum(aa[:self.deck_size]) / (np.sum(mull[:self.deck_size]) + 1e-9)-1)/2

        # Combine them into one list
        r_values = metagame_stats + [durability]
        theta_labels = [item['Id'] for item in metagame[1:]] + ['durability']
        if spid==1:
            df = pd.DataFrame(dict(
                r=r_values, 
                theta=theta_labels))
            fig = px.line_polar(df, r='r', theta='theta', line_close=True)
            fig.update_traces(fill='toself')
            fig.show()#spiderchart
            # 1. Split the array into chunks using list slicing
            
            chunks = [data[i:i + 3] for i in range(0, len(data), 3)]
            
            # 2. Calculate the value for each chunk (e.g., the sum)
            chunk_values = [sum(chunk) for chunk in chunks]
            #3 Heatmap of robbing, where is the bottleneck of our economy.
            
            plt.imshow(np.atleast_2d(chunk_values), cmap='RdBu_r', aspect='auto', vmin=0, vmax=3)
            plt.show()
    def ranres(self):
        self.result(self.ra,1)
def evaluation_function(alpha, deck=deck, bolsa=bolsa):
    # Create the sim with the current deck and the alpha suggested by AI
    sim = ArkhamSimulator(deck, bolsa, alpha)
    ooo, rob = sim.matr45(sim.ra)
    
    # Return the 'Fitness' (e.g., Damage / Cost). 
    # TODO Add up to 0.5 based off of how many archetypes are shared.
    
    # Debug print
    #score = ooo[deck_size_out+1] # Or whatever your score is
    #print(f"Testing Alpha: {alpha:.4f} | Resulting Score: {score}")
    #print(ooo)
    deck_size_out=len(deck)
    print("fitness calculated")
    return (ooo[deck_size_out+1]+ooo[deck_size_out+2]+ooo[deck_size_out+3]+ooo[deck_size_out+5]+ooo[deck_size_out+6]) / (ooo[deck_size_out]-ooo[deck_size_out+4] + 0.1) 
if __name__=="__main__":
    example=ArkhamSimulator(deck,bolsa,0.78)
    example.result(example.ra)
    print(evaluation_function(0.784))
# This is the function the AI will 'watch'
def new_function_for_passing(deck1, bolsa=bolsa,alpha=0.78):
    example=ArkhamSimulator(deck1,bolsa,alpha)
    example.result(example.ra,1)
    print(evaluation_function(alpha, deck1, bolsa))

# Configure the Optimizer
optimizer = BayesianOptimization(
    f=evaluation_function,
    pbounds={'alpha': (0.4, 0.925)}, # Alpha can't be 0 or 1 usually
    random_state=42,
    verbose=0
)

#optimizer.maximize(n_iter=5)
# 1. Get the dictionary containing the best score and the best parameters
#res = optimizer.max

#best_alpha = res['params']['alpha']
#best_score = res['target']

#print(f"--- OPTIMIZATION COMPLETE ---")
#print(f"Best Alpha found: {best_alpha:.6f}")
#print(f"Highest Score: {best_score:.6f}")

# 2. Now you can use that best_alpha to run one final "Master Simulation"
#final_sim = ArkhamSimulator(deck, bolsa, best_alpha)
#final_sim.ranres()

###########################
#CONCLUSIONS:
####################


####################
#The resulting vector is quite aligned with reality but i feel pretty confidently the following:
#-The cost will end up being around 85% of the end value, simply because of the randomness of playing. However it is a great heuristic to showcase just how hard certain mechanincs or obstacles the game will throw at you thus i won't change it.
#- The dmg seems fine, although maybe slightly off by 1 or 2. To be fair, we are assuming the max difficulty for the test. If anything maybe it should be lower, but most of the successes actually come from having 3 assets to boost 1 will. 
# - Also a big chunk of damage comes fom the passsive and fixed dmg of her kit, thus it actually doesn't reduce as much as expected when changing the number of actions or parts of her kit.
#-The investigate and evade seem fine.
# -In reality we would generate around 10% more resources.
# -I'm inclined to agree with the resulting vector when it comes to the probabilities of the cards.
#Overall the result is probably 10% off of the average of plays, however this is mostly negative and thus would coincide more realistically 
#with the overall structure and objectives of the game and its mythos components when it comes to an holistic appraisal of decks.
#However, a 10% tweaking would be recommended to find out the true possible values of your plays in advamce.
#This code also presents the chanve to diagnose potential problems with the decks, not just by this "holistic appraisal" but by having markov-like components
#like the perm_add, cost-total resource=rob instead of play, and the alpha. Specifically, it tells you how importatn playing guts really is, and 
# you can extract information as to how many times you would maybe have to steal resources, thus making you more aware of an invisible future neckbottle
#This premature diagnosis, even if 10% off, still provides enough clear evidence to alter your playstyle, by making you aware of blottlenecks (cost vs resource),
#and it allows for more fluid deckbuilding, by taking care fo synergies like the skills that allow you to steal for example. (alpha)
#Finally, it provides a solid representation and framework with which to work with decks. It can represent visually, numerically, and progressively the evolution of many
#key characteristics of decks. Thus allowing for a more dynamic visualization and diagnosis, which makes the task of comapring and bettering deck all the more easy.
#This final point is the subject of further coding,  with this code we can easily compare most aspects between two decks, from their results (dmf,evd,dur,...) to their optimal playstyles,
# draw their many weaknesses and strenghts, alter, modify and 
#evolve them into better decks, and then choose the one that aligns more with our personal playstyles, scenarios and teamcomps.
##########