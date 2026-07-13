
import pandas as pd
import numpy as np
import math
# 1. Configuration
deck_size = 0
deck_goal=0
deck_search=0
deck_stre=0
main_att=5
deck_hel=0
#In the deck we could add a few sinks, like horror or dmg taken, clues vs investigates, and actions to complete the effects of a certain 
# cards, this latter requires taking the square root of the action sink and coupling the new system with the new subsystems and 
# internal clocks of the cards, namely the attack spells. and even then the attack spells attack synchronized instead of action by action,
#  so it seems the most  logical way to implement this is by dividing by 5 the actions square root, so a 15 th root controls the firing 
# speed of spells while a square root the progress of a turn.
#Something positive about adding more sinks is a more clear relationship between the internal workings of a character and the context
#however it is extremely intensive to write and doesn't have a clear compacted form or algorithm for the task, it is better to write 
# ourselves whatever changes or synergies result from the initial library of cards unto the character's deck.
#It is true that the icons obtained for test are difficult to account for and are already presumed to exist in the simulation, but the only 
# way to actually account for their real impact is to run a inhomogeneous markov chain process as a "perfect" monte carlo simulation, which will 
#be done in a different code, and then we will compare the results. Tha main disparity between the code and reality is presumed to be the
#rate of firing of the spells or weapons, basically the internal clocks and subsystems of said cards. We will try to account for the real speed by
# dividing  or taking the 11 th root of the subgraphs of goal cards, basically since there are 11 goal cards and they accidentally fire simultaneously we must divide by 11 their
#  impact. Additionally we should put the dm or evade or investigate that results from employing their action completely for one turn.
#Finally, we chose to use the square root of a turn, what is actually an action, but chose to leave out the internal clocks and subsystems of the weapons for sake of simplicity
#This results in something like the search free action of arcane initiate to lose its initial meaning, and we have to find a similar search or draw as an immediate action to correct this oversight,
#given that 0.02 we will be taking the weakness, and 0.85 a spell, and we are supposedly doing this till we get a spell that is not hte weakness, we
# will be doing this maximum thrice, we have a 0.85+0.15*0.85+0.15*0.15*0.85 connection to spells, and a 0.02*0.15*0.02*0.15*0.15*0.02 connection to the weakness. THis way we just have to change the formula. We add the number of times the search is performed.



# REMINDER. WE SHOULD AMP BY AT LEAST 25% THE DMG AND INVE AND EVADE THAT ARE INCONDITIONAL. ONLY INCONDITIONAL!!!!, THIS IS TO
#COUNTERACT THE FACT THAT THEY WILL BE MOST LIKELY MULTIPLIED BY 0.8 LATER ON
#Another option is to use the 'add' feature and make it equal or greater than 32

#I SHOULD ADD A "FREE" LABEL TO TREAT CORRECTLY THE QUICK OR FREE ACTIONS.

#DECK CONSTRUCTION THIS IS YOUR INPUT
#I COULD ADD A CATEGORY 2PERMANENT" OR "FAST" TO DENOTE WHEN AN ASSET PERMANENTLY STAYS, THOUGH THIS USSUALLY MEANS WE CAN IMMEDIATELY RIP 
# ITS BENEFITS MATHEMATICALLY IN 1 ACTION. THIS WOULD HELP CALCULATE THE 4/5 PROBABILITY OF NOT PLAYING A CARD BY ADDNG A "HAND CLOCK".
deck_config = [
    {'Id': '0', 'name': 'Arcane initiate',  'search': 3, 'num_sea':4, 'Type':'stre','cost': 1},
    {'Id': '1', 'name': 'Arcane initiate',   'search': 3,'num_sea':4,  'cost': 1, 'Type':'stre'},
    {'Id': '2','name': 'Forbidden kwnoledge ',  'res': 4, 'dm':4 , 'Type':'stre','fix':1},
    {'Id': '3','name': 'Forbidden kwnoledge ',  'res': 4, 'dm':4 , 'Type':'stre','fix':1},
    {'Id': '4','name': 'Emergency cache', 'res': 3}
    ,{'Id': '5','name': 'Shrivelling', 'cost':3,'dm':2,'time':4, 'Type': 'Goal_Card'}
      ,{'Id': '6','name':'Shrivelling', 'cost':3, 'dm':2, 'time':4,'Type': 'Goal_Card'}
        ,{'Id': '7','name':'Azure Flame','cost':3, 'dm':2, 'time':3,'Type': 'Goal_Card'}
          ,{'Id': '8','name':'Azure Flame','cost':3, 'dm':2, 'time':3,'Type': 'Goal_Card'}
            ,{'Id': '9','name':'Clairvoyance', 'cost':4,'inv':2,'time':3, 'Type': 'Goal_Card'}
              ,{'Id': '10','name':'Clairvoyance', 'cost':4,'inv':2,'time':3,'Type': 'Goal_Card'}
                ,{'Id': '11','name':'Clarity of mind','cost':2, 'time':3,'Type': 'Goal_Card'} #because it allows healing we could add a slight budge to the dm
                  ,{'Id': '12','name':'Clarity of mind','cost':2, 'time':3,'Type': 'Goal_Card'}
                    ,{'Id': '13','name':'Blinding light','cost':2, 'evade':1,'dm':1, 'Type': 'Goal_Card'}
                      ,{'Id': '14','name':'Blinding light','cost':2, 'evade':1,'dm':1,  'Type': 'Goal_Card'}#The fighting spells are actually slightly worse because they require en extra action to set up....
                        ,{'Id': '15','name':'Ward of protection','cost':1, 'Type': 'Goal_Card', 'dm':1,'fix':1}
                          ,{'Id': '16','name':'Ward of protection','cost':1,'Type': 'Goal_Card', 'dm':1,'fix':1}
                            ,{'Id': '17','name': 'Peter ', 'cost':3}
                              ,{'Id': '18','name': 'A test of will', 'cost':1}
                                ,{'Id': '19','name': 'Drawn to the flame', 'inv' :2,'fix':1}
                                  ,{'Id': '20','name':'lucky', 'cost':2,'icons':2, 'Type':'hel'}#not really a way to explain the TEMPO and fast actions....
                                    ,{'Id': '21','name':'lucky', 'cost':2,'icons':2, 'Type':'hel'}
                                      ,{'Id': '22','name':'Holy rosary',  'Type':'stre','cost':2}
                                        ,{'Id': '23','name':'Holy rosary',  'Type':'stre','cost':2}
                                          ,{'Id': '24','name':'guts', 'draw':1,'icons':2, 'Type':'hel'}
                                            ,{'Id': '25','name':'guts','draw':1,'icons':2, 'Type':'hel'}
                                              ,{'Id': '26','name':'fearless','icons':1, 'Type':'hel'}#it heals 1 horror
                                                ,{'Id': '27','name':'fearless','icons':1, 'Type':'hel'}
                                                  ,{'Id': '28','name':'unexpected courage','icons':2, 'Type':'hel'}
                                                    ,{'Id': '29','name':'unexpected courage','icons':2, 'Type':'hel'}
                                                      
    ,{'Id': '31','name': 'Strenght',  'draw': 1,'time':7, 'cost': 3,'res':0, 'Type':'stre'},#actually this draw happens passively but we will "cancel out" the factors and write it directly in the code
    {'Id': '32','name': 'Treachery',  'draw': 0, 'cost': 4,'res':0,'Type': 'Goal_Card', 'dm':-1.25},#if we DO NOT play it then it deals damage passively through agnes. But there's no way to calculate TEMPO so far. Also it gives 1 doom regardless
    {'Id': '33','name': 'Rand_Weak'}
]
#don't bother me with more optimal ways to do this:
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
    

metagame=[
    {'Id': 'Damage', 'Label': 'Damage', 'Type': 'dm'},
    {'Id': 'Cost', 'Label': 'Cost', 'Type': 'cost'},
    {'Id': 'Evade', 'Label': 'Evade', 'Type': 'evade'},
    {'Id': 'Investigate', 'Label': 'Investigate', 'Type': 'inv'},
    {'Id': 'Resourceful', 'Label': 'Resourceful', 'Type': 'res'}
]
#WE CREATE THE 3 ACTION CLOCK
actioon=[{'Id': 'Action', 'Label': 'Action', 'Type': 'Action'},{'Id': 'Action1', 'Label': 'Action1', 'Type': 'Action'},{'Id': 'Action2', 'Label': 'Action2', 'Type': 'Action'}]

# 2. Build Node Lists 
node_data = []
simple_node_data=[]
for c in deck_config:
    simple_node_data.append({'Id': c['Id'], 'Label': c['Id'], 'Type': 'Card'})
    node_data.append({'Id': c['Id'], 'Label': c['Id'], 'Type': 'Card'})
#We could just do the same for loop
for x in metagame:
    node_data.append(x)
for x in actioon:
    node_data.append(x)
nodes_df = pd.DataFrame(node_data)
simple_nodes=pd.DataFrame(simple_node_data)

# 3. Build Edge List
edges_list = []
simple_edges_list=[]
node_map = {name['Id']: i for i, name in enumerate(node_data)}
simple_node_map = {name['Id']: i for i, name in enumerate(simple_node_data)}
n = len(node_data)
adj_matrix = np.zeros((n, n))

# A. Internal Card-to-Card connections (Drawing)
new_deck_goal=deck_goal
for src in deck_config:
    if src.get('draw', 0) > 0:
        for tgt in deck_config:
            if tgt['Id']!=src['Id']:
                weight = src['draw'] * (1/ (deck_size-1))*1/5#this 1/5 represents the chance of the draw card being played. 5 cards in hand and 1 cards to play per action
                if weight > 0:
                    edges_list.append({'Source': src['Id'], 'Target': tgt['Id'], 'Weight': weight})
                    simple_edges_list.append({'Source': src['Id'], 'Target': tgt['Id'], 'Weight': weight})
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
                        weight+=pro**i*memo*1/5#1/5 is the modal or harmonic geometric average chance of playing that specific card
                    
                    edges_list.append({'Source': src['Id'], 'Target': a['Id'], 'Weight': weight})
                    simple_edges_list.append({'Source': src['Id'], 'Target': a['Id'], 'Weight': weight})
                    adj_matrix[node_map[src['Id']], node_map[a['Id']]] = weight
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
                        weight+=pro**i*g_c*1/5
                    if weight > 0:
                        edges_list.append({'Source': src['Id'], 'Target': tgt['Id'], 'Weight': weight})
                        simple_edges_list.append({'Source': src['Id'], 'Target': tgt['Id'], 'Weight': weight})
                        adj_matrix[node_map[src['Id']], node_map[tgt['Id']]] = weight


#3.5.  define the proficiency of investigate, evade or damage in skill tests too.   
# We always take the proficiency of succeeding in standard difficulty, against a 4 skill test.
# We always take for granted that assets with permanent bonus are in play towards the end of the game, so we take those into account
# We take a chunk of the icons of abilities
# 
#   
bolsa=[2,1,0,0,-1,-1,-1,-1,-1,-2,-2,-2,-2,-3,-4,-26] #the doom sack. This can be easily personalized
def F(a,b):
    c=a-b
    res=0
    tot=0
    for i in bolsa:
        tot+=1
        if c+i>=0:
            res+=1
    return res/tot      
def chance(x,y):
    #A is the "mass" matrix.
    if y== {'Id': 'Resourceful', 'Label': 'Resourceful', 'Type': 'res'}:
            return 1
    if y== {'Id': 'Cost', 'Label': 'Cost', 'Type': 'cost'}:
            return 1
    if x.get('fix')==1:
            return 1
    j=0
    ad=0#so we need to also do a thing with "permanent" additions with like the rosary for example. I can only think of a BIG clock.
    red=0#We still should make the clock
    #MAKE THE CLOCK....................
    ad+=x.get('add',0)#the add means a literal addition to your roll because of card properties
    red+=x.get('red',0)#the reductions
    for h in deck_config:#unfortunately we don't have really have a way to actually couple this with the firing of "help" cards... But we can put the same chance (4/5) and actually connect this to the chance of each card...
        if h.get('icons',0)>0:
            j+=(F(main_att+ad+h.get('icons',0),5-red)/5+F(main_att+ad,5-red)*4/5)#kinda a fifth chance to use any help card. This is by far the worst heuristic in the game but it seems to give some reasonable numbers
            #doesnt take into account correctly the using various cards simultaneously but its quite unlikely so it probably doesnt matter.
        else:
            j+=(F(main_att+ad,5-red))
    return (j/deck_size)#if we take into account the "mass" it should be 5. This is a "chance" vector.
# B. Card-to-Costlike_Sinks connections 
#Problem with the spells firing simultaneously and their internal clocks. Correct the cost per action based on the recurrence simplification

for x in metagame:
    for src in deck_config:
        if src.get(x['Type'],0) > 0:
            clock=src.get('time',0)
            a=1
            if x['Type']=='cost':
                a=clock+1#we add the "prepare" action of the spells. We only pay the spell once however it's the only thing that will only be "fired" once. So we divide over all actions.
            weight = src[x['Type']]*chance(src,x)*1/5 #we take the total effect of a card per action, and make them "equiprobable"
            edges_list.append({'Source': src['Id'], 'Target': x['Id'], 'Weight': weight/a})
            adj_matrix[node_map[src['Id']], node_map[x['Id']]] = weight/a
            #The above occurs when "firing the spells". So now we have to maintain the mass of the system, there's a 4/5 of not firing sad spell, meaning that amount of mass stays.
            
            if clock>1:
                
                clock=1-1/(clock+1)#it includes the preparing of the card
                #this is the ratio of the geometric progression that sums up to a.
                #So we prepare the spell and fire it "infinitely" to take a actions total, this is 1+clock+clock^2+...=a
                #The problem is that this is assuming the spell is firing, in actuality it fires with 1/5 chance so. 1/5*1(chance prepare) and 1/5*clock(chance of firing)
                #Some simple maths show that treating the spell node like this, with an 4/5 autoloop for not playing the card and a 1/5clock autoloop correctly accounts for the limit of actions while keeping the actual
                #memory value of the card, total damage for example.
                clock=1/5*clock
                simple_edges_list.append({'Source': src['Id'], 'Target': src['Id'], 'Weight': clock})
                edges_list.append({'Source': src['Id'], 'Target': src['Id'], 'Weight': clock})
                adj_matrix[node_map[src['Id']], node_map[src['Id']]] = clock
#This clock correctly accounts for the costs and damage and every value of the card and its limited uses.
#This means that now we can justify adding an 4/5 autoloop for each and every single card except some fringe cases.
################################
#4/5 autoloop heuristic clock:
##################################
for src in deck_config:
    clock=4/5
    simple_edges_list.append({'Source': src['Id'], 'Target': src['Id'], 'Weight': clock})
    edges_list.append({'Source': src['Id'], 'Target': src['Id'], 'Weight': clock})
    adj_matrix[node_map[src['Id']], node_map[src['Id']]] += clock
#This previous line of code describes the current randomness of playing cards per action
# C. Cost_Sink Self-Loop (The "Memory" edge)
#add the action clock. 

for x in metagame:
    edges_list.append({'Source': x['Id'], 'Target': x['Id'], 'Weight': 1.0})
    adj_matrix[node_map[x['Id']], node_map[x['Id']]] = 1.0
for x in range(len(actioon)):
    
    y=actioon[x]
    z=actioon[((x+1)%len(actioon))]
    
    edges_list.append({'Source': y['Id'], 'Target': z['Id'], 'Weight': 1.0})
    adj_matrix[node_map[y['Id']], node_map[z['Id']]] = 1.0
    
for y in deck_config:
        edges_list.append({'Source': 'Action2', 'Target': y['Id'], 'Weight': 1.0*(1/deck_size)}) #times 2 with harvey walters
        adj_matrix[node_map['Action2'], node_map[y['Id']]] = 1.0*(1/(deck_size))



# 4. Export
#np.set_printoptions(threshold=np.inf)
nodes_df.to_csv('deck_nodes_final.csv', index=False)
simple_nodes.to_csv('deck_simple_nodes_final.csv', index=False)
pd.DataFrame(edges_list).to_csv('deck_edges_final.csv', index=False)
pd.DataFrame(simple_edges_list).to_csv('deck_simple_edges_final.csv', index=False)

print("--- Adjacency Matrix (Rows/Cols order: " + ", ".join(nodes_df['Id']) + ") ---")

matrixxx=np.array(adj_matrix)
#print(matrixxx)



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
    if i['name']=='Treachery':
        break
    if i.get('Type',0)==0:
        mulligan.append(norma)
    if i.get('Type',0)=='hel':
        mulligan.append(norma)
    if i.get('Type',0)=='stre':
        mulligan.append(atr)
    if i.get('Type',0)=='Goal_Card':
        mulligan.append(goa)
    #print(i)
    randgene.append(5/(deck_size-2))
    perfect.append(0)
    one_z.append(0)
mulligan.append(0)
mulligan.append(0)
randgene.append(0)
randgene.append(0)
perfect.append(0)
perfect.append(0)
one_z.append(0)
one_z.append(0)
for i in metagame:
    mulligan.append(0)
    randgene.append(0)
    if i =={'Id': 'Cost', 'Label': 'Cost', 'Type': 'cost'}:
        perfect.append(-1/3)
        one_z.append(0)
    else:
        
        perfect.append(1.1)
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
mull=np.array(mulligan)
ra=np.array(randgene)
per=np.array(perfect)
oo=np.array(one_z)
#print(mull)
#Now we have the whole mulligan starting hand defined
#6. Matrix multiplication for final states averaged and idealized, repeating nodes gives max +10% based on initial mulligan, we have also relieved the cost so we will add a 10% there too, but that is also a +10% for final product by defnition

#So now we will get a vector, whose last elements will give us an approximation (10% off) to the elements of play and effectiveness f the deck, 
# this in turn means that we can singlehandedly COMPARE decks with this code

A_15 = np.linalg.matrix_power(matrixxx.T, 45)#15 turns... 45 actions
fianl=A_15@mull#this is the final state, which has recorded in the "sinks" the dmg, cost, resource generated etc:
#print(matrixxx.T@mull)
print("Our final state with our preferred strategy and deck is: ")
print(fianl)


#We can see that the mulliganed state is around 33% better, this could be alleviated by a inhomogeneous markov chain
#Importantly we can see that it is way more important to have a good strategy in the mulligan, to the point where our
# play could be immediately ameliorated from the beginning by 33%. This 33% takes into account the improvement of the starting hand whithin a play
#and a number of plays where we will have a better starting hand. So it's both a a global improvement and a local one (inter and intra-play)
#Finally we can see the effect of certain "strategies", like the number of times we search with arcane initiate, 3 times is more than enough more than that
#and on an average run we will not get positive feedback, in fact we are risking our progress with "arcane initiate".

#We ran the numbers and we can avoid spending around 1/3 of the total estimated cost by using a good playing strategy.
#And we multiply everything else by 1.1. Due to the errors of "truncating" the more reals inhomogenous markov chain.
#We sum everything up :
print(per)
print(mull)
print(ra)
print("Our score with our preferred strategy and deck is:  ")
print(A_15@mull@per)
print("The same deck but with a random mulligan has the following score: ")
print(A_15@ra@per)

#We assume that 1 dmg =2 res=1Evad=1Clue, it seems a fine equation.IMPORTANT. An the cost is usually around 30 but you get 20 total, so its -1/3.




#print(A_15@per-per)
#print((A_15@(A_15@per)@per))#We are not taking into account the normal regeneration of ressources.
#Funnily enough our decision happens to be a steady eigenvector because it's exclusively related to metaplay, 
#but this is at its core the equation that describes the "total score" of our game. A simple score that is. 

#WHAT'S THE VALUE OF EACH CARD???=>
print("Our value vector is: ")
print(A_15.T@per)#we take the maximum of the vector and take the corresponding dual vectors, in this case e_3 and e_4,
#which correspond to the vault of knowledge, this is simply due to agnes making huge progress with this card. 
#This allows us to develop a way to order the cards in a kind of priority list.
#We proceed to make some new rules:
#1) We will use said list to identify other 'stre' cards. It seems obvious that we should add vault of knowledge to our stre cards.
# 2)We will follow said list to, whithin a type, break the ties between cards objectively. in this case it is obvious that we should choose vault of knowledge 
#over arcane initiate (all the more obvious during play due to the fact that arcane initiate gives us 1 doom, only during withching hours is this ok)
#3) We will follow the previous rules we made, specifically the whole mulligan. 
# Aditionally we will keep at least one goal card or one stre card if they land in our initial hand.
#4)Finally in order to identify which partial mulligan to use we will use this list. First we follow the previous rules here stated
#Secondly we identify the value of each card in our initial hand.As said before we will keep at least one stre and one goal.
# IN case of ties, aka having various cards of each type, the values of the cards will secure their spots in our hand if the are the best.
# Finally, we calculate the average value left in the deck, we will potentially "discard" all other non-secured cards with worse value than the deck average.
#Aditionally, in case of duplicity of cards we will use experience to determine whether it's better to return said copy to the deck
#or if it's a good idea to keep it. THis will barely happen and make barely any impact.
#Once we have identified the "improvable" parts of our deck we will effectively "redraw" to "improve" (on average) said hand.
#It might be wise to employ other "averages" and "distances", like for example a kind of hamming distance that COUNTS the number or chance
#of actually improving the deck and acting accordingly so. 
#Say we draw 'str' and 'normal' cards, we take the best 'str' and mulligan everything else as per the rules to get goals.
# Say we got "goals", then we secure the best goal, we aditionally secure the cards whose value is better than the deck average. And to 
#see what kind of mulligan is necessary we look at the below average value cards (except the best 'stre' card if in hand).
# We proceed to calculate the "improvement chance/distance" if it is strictly bigger than 50% we proceed and choose that card for a mulligan. 
# Then we continue the process with the following low value cards, treating them as a set, and we choose the mulliganed cards when we have
#no more viable cards to choose(stre,goal, and average rules), or when the distance stops being over 50% ("improvement" rule)

#The idea is that by implementing both the average and the "improvement distance" we can avoid any skewness of the values.
#In conclusion this list allows for a better approach and decisively improves the "mulligans". Namely when we said we wouldn't mulligan once we had a goal card.
#Finally, the list tells us that mathematically 7 is the value of the vault of knowledge, and the highest value among cards.
print("This is our preferred mulligan strategy (improvement partial mulligans are unaccounted for): ")
print(mull)
#However in this case scenario ths strategy seems to be actually worse than randomly choosing cards. This is due to high value cards not being goal_cards.

#We cold think of another mulligan where we mulligan till we get the both vault of knowledge.
avvvv=(math.comb(29,4)*2*((math.comb(25,3)*2/math.comb(26,4))+(math.comb(25,4)*1/math.comb(26,4)))+math.comb(29,3)*2+math.comb(29,5)*(math.comb(24,4)*2+0+math.comb(24,3)*2)/math.comb(26,5))/math.comb(31,5)#on average how many vault of knowledge?

#on average 0.61 of these guys when starting

fixated=[]
for i in range(deck_size-2):
    if i in [2,3]:#put the first most valuable card in these positions
        fixated.append(avvvv/2)
    else:
        fixated.append((5-avvvv)/(deck_size-4))
fixated.append(0)
fixated.append(0)#as before 2 zeroes for zero interaction with the 2 weaknesses. It's very importnat to only have 2 weaknesses.
for i in metagame:
    fixated.append(0)
for i in actioon:
    
    if i=={'Id': 'Action', 'Label': 'Action', 'Type': 'Action'}:
        fixated.append(1)
        
    else:
        fixated.append(0)
fixx=np.array(fixated)
print("The most realistic 'fixated' mulligan will have the following value: ")
print(A_15@fixx@per)
#now for the arcane...
fixat=[]
for i in range(deck_size-2):
    if i in [0,1]:#put the second most valuable card in these positions
        fixat.append(avvvv/2)
    else:
        fixat.append((5-avvvv)/(deck_size-4))
fixat.append(0)
fixat.append(0)#as before 2 zeroes for zero interaction with the 2 weaknesses. It's very importnat to only have 2 weaknesses.
for i in metagame:
    fixat.append(0)
for i in actioon:
    
    if i=={'Id': 'Action', 'Label': 'Action', 'Type': 'Action'}:
        fixat.append(1)
        
    else:
        fixat.append(0)
fixxx=np.array(fixat)
print("The most realistic 'fixated' arcane draw mulligan will have the following value: ")
print(A_15@fixxx@per)
#This seems to point at an even better strategy, "just mulligan for your best card". This is potentially the best strategy given the
#prior stochastic process to which we must be subjected, and it's not far from our preferred strategy. In fact they are only 16% apart.
#This is probably the best strategy since it prioritizes the bigest pivot in our value vector.
# It also goes without saying that the "best" strategy is quite rude and situational, only available due to an interesting synergy with agnes baker,
# and even then it's quite risky in many aspects, due to the fact that survivality is unaccounted for in this calculations.

#As a general rule to calculate the maximum basic power of a mulligan (not realistic but rather a surreally and imposibly good strategy)  ,
# we list the 2 best "kinds" of cards, which must come in pairs.
# and multiply their value by 0.61. Then we add 3.78*average(other cards). And voilá, that's an upper limit that will serve to compare
#mulligans and decks intraplayer-wise.

#Finally, adjustments can be made adding other memory sinks like healing, and survivality. But the fact remains 
# that the strategy can shift wildly depending on the context, and thus the weights given to cost,dmg,evade, clues, 
# survivality in a certain scenario remain the most contested values of this simulation.

print("the ratio of dmg and cost is: Mulligan Prefferred:",(A_15@mull)[deck_size+3+5-8]/ (A_15@mull)[deck_size+3+5-7])
print("the ratio of dmg and cost is: Random:",(A_15@ra)[deck_size+3+5-8]/ (A_15@ra)[deck_size+3+5-7])
print("the ratio of dmg and cost is: Fix Vault:",(A_15@fixx)[deck_size+3+5-8]/ (A_15@fixx)[deck_size+3+5-7])
print("the ratio of dmg and cost is: Fix Arcane:",(A_15@fixxx)[deck_size+3+5-8]/ (A_15@fixxx)[deck_size+3+5-7])
#END
print("Tha fixed strategy have better ratios and scores. However the mulligan strategy migh still be contending when higher and more diverse card are added to the collection. So far the mulligan offers a diversity and balanced not yet achieved by this specific deck")
print("This is the reason why we should pay attention not only to the cards and their traits, but to our overall deck. Understanding its purpose whithin a game and interacting with it, like in mulligans, correctly is a huge boost to our gameplay")