## A comprehensive example

 I took the liberty of analysing all the decks of my current campaign.
 We chose the following investigators; Father Mateo, Harvey Walters, and Sefina Rousseau. Their DeckIds are kept private de to our personal wishes. 

**Methodology**:

The default settings for a main attribute of 5 and main difficulty of 5 (difficulty=stat), for instance; a guardian with 5 of fight againt enemies with 5 of fight. A normal difficulty on the chaos bag was chosen. By default, I chose around 14 rounds.

I fed the 3 Ids into the public code, without any tampering whatsoever. The Strenghts and weaknesses are as always swapped out for 1 generic Weakness and 1 generic Strength. This impacts Sefina Rousseau the biggest since her 3 strenghts and 1 weakness are quite complicated and rely on a more nontagible mechanic. Additionally, I did tinker with the code in Sefina Rousseau case since she starts with a 8 card hand.

Father Mateo also has his own problems, since his chosen Seal cards are not inside the library. However, I'm certain that this omission doesn't necessarily cause a great variation from real life results.  

The biggest problem with Father Mateo is as always the non-avalability of "free" arcane spots in the code. There are only 2 spots for spells yet there is no way for the game to know this.

**Results**:

The code returned the following visual representations for Harvey Walters.
![[Figure_1Fer.png]]![[Figure_2Fer.png]]![[Figure_3Fer.png]]

The code returned the following visual representations for Father Mateo.

![[Figure_1Pad.png]]
![[Figure_2Pad 1.png]]
![[Figure_3Pad.png]]
The code returned the following visual representations for Sefina Rousseau.
![[Figure_1Sef.png]]
![[Figure_2Sef.png]]
![[Figure_3Sef.png]]
**Analysis of the visual structures**:
The first image shows the ``score`` of individual cards (by starting hand). Second image shows the ressource bottlenecks per ``round``, including extra actions or refunded actions. Finally, third image shows the distribution of fitness by starting hands (it shows a gamma distribution can approximate quite nicely the desired distribution).

- Harvey:
Top cards: Dr Milan, Magnifying Glass, Perception, Strange Solution, No Stone Unturned, Eureka and Shortcut.

A net of 21+ rounds. So the deck consists of a neat amount of AP friendly cards. Additionally, the isn't barely any bottlenecks (good ressource generation). The heatmap shows a debt of 5 ressources around turn 13 out of 21. So in reality, we would expect a bottleneck around 8 or 9 th rounds.

Skewed Gamma (small alpha), long right tail, small offset (bad worst cases). Decent average fitness however.

- Mateo:
Top cards: Pendulum, Rosary, Emergency Cache, Guts, Azure Flame and Drawn to the Flame. (Overall the spells have a pretty good score)

A net of 21+ rounds. So the deck consists of a neat amount of AP friendly cards. Nevertheless, there is a wave of debt surrounding 13 and 14 and propagating in ripples beyond that. In reality, we can expect a high cost around 8 AND 9, and a high cost of maintenance after that. This means we have to be careful when playing costly assets, and maybe even robbing whenever we get the chance instead of drawing a card.

Less skewed Gamma (decent alpha), right tail, good offest (decent worst cases). Good fitness.
- Rousseau:
Top cards: Chuck Fergus, Pickpocketing, Lucky Cigarrete, Leo De Luca, Guts, Sneak Attack, Drawn to the Flame, Sneak By and Manual Dexterity. This gives a comprehensive list of important cards to put under her to duplicate or Draw.

A net of 25+ rounds, heavily AP friendly. With a slight debt bottleneck in round 13. In reality, we expect round 7 or 6 to be more heavy in ressource generation to avoid said bottleneck and have a smooth playthrough. Unlike with father mateo, being mindful and coy when playing cards does not work with Sefina since she uniquely relies on spamming events.

Less skewed Gamma (decent alpha), small right tail, great offset. Pretty good fitness. 

**Interpretations within the statistical context**:

- Harvey:
![[newplot (1).png]]
It's a **Low Curve All Rounders** but with slightly more entropy -that's great!
- Mateo:
 ![[newplot.png]]
It's a **High-Connectivity Toolbox** much cheaper and less entropy -an objective would be to make it more versatile.
- Rousseau:
![[newplot (2).png]]
We can clearly see it belongs to **Big Decks**. Slightly much more expensive, versatile and smaller -so it balances out.

## Mulligan Behavioralist

Firstly, the initial visual element gives us a rough lexicographic order of the cards. Working with Mulligan.py it would be quite easy to know which cards to mulligan in a certain hand.

However, the starting hands follow gamma distributions, and the following scenario was developped. The starting hand is a random variable, gamma, and the mulliganed hand is the result of redrawing an entire hand (with substitution) if our starting hand falls behind a certain cutoff (Q1, mean, etc).

In reality the optimal mulligan will be better, due to keeping good cards. So this serves as a lower bound of its efficiency.

Maths here: The deduction of the formula f_y(x)=F(q)f(x)+id(x>q)f(x)

Deduction the optimal cutoff to maximise expectancy is q=mean.

Which leaves us the following mulliganed graphs for certain Decks.
![[Figure_2.png]]
![[Figure_1.png]]

Finally, I investigated the relative effect on mulligans, since it is best measured as a ratio that acts upon a base fitness. The following graphs show a series of perspectives of the actual mulligan and its realative effect based off alpha and beta, within a logical deck context.


![[Gamma1.png]]

![[gamma2.png]]

![[gamma3.png]]

![[gammarealtive.png]]

![[gammarelative2.png]]

![[gammarelative3.png]]
As we can see there is a sweet logarithmic curve of maximum fitness beyond which no decks can pass. Additionally, it allows us to put in context the fitness of a deck, which now we know can be no higher than 2.5, and the efficiency of a mulligan which must be lower than 0.3.

## Seal Mechanics

Since seal is not inside the cards library, I decided to put in here a brief abstract of its mathematics and effects. And as a way to explain this side of Father Mateo's deck.

Seal relies on temporarily taking out one chaos token. It is quite easy to see its effect mathematically. If you were to be above or right in the sealed token, you are negatively affected. If you were below, you are positively affected. 

If there are T tokens, B of them make you fail, you seal x tokens, and y of them would make you fail, then your chances of failing are: (B-y)/(T-x) vs B/T.

According to this, it is obvious that you wanna start sealing the worst tokens. Like -8,-6,-5 and obviously the Tentacle token. 

The Tentacle token is the best case scenario of sealing, however only **Seal of the seventh sign** can seal it. It has 7 charges and only **Enraptured** and **Eldritch Inspiration** can give it extra charges. Total, you may be able to consistently get 10 charges on it. Assuming a group of 3 players, each does 3 skill test per round on average (2 in investigator phase, 1 mythos phase). In normal or hard difficulty you encounter around 5 or 6 symbols out of 16 or 18. Which is a third of the chaos bag, meaning that each investigator each phase takes one carge off of **Seal of the seventh sign**. Meaning you get on average a 3-4 turn seal.

Seal is an interesting mechanic in higher difficulty, where the Tentacle sign is way more unlikely to appear, and sealing impossible tokens -such as -6- becomes quite useful. 

``How it impacts the gameplay``

In this particular team, I intend to use the seal to help Sefina take back her events with total certainty, and kill and investigate thrice as much as I do -with total certainty. Wasting an entire broken event becuase you got unliky implies great variance, this can heavily reduce it. Furthermore, Harvey can investigate with **Archaic Glyphs** without a single hiccup and discover a disconcerting amount of clues, synergising with **enraptured**.

Finally, it is my way of giving back to the table, since I use **Shards of the void** and seal the Zero token -bad seal.

Our team doesn't have any more interactions apart from this Bag tinkering. My character also give a free Tentacle pass, by changing it once to an Elder sign. Total, this leaves 11 rounds -> 33 reveals (with Tentacle token eligible), with 17 or 19 tokens -> 2 tentacles -> 1 tentacle thanks to my ability on average. 

This was a concious decision because in the last scenario we got unliky and drew 0 Elder signs, and 4 or 5 Tentacles. This addtion makes the Tentacle distribution change from Binom(1/17,45) to Binom(1/17,33)
and makes **retrievable** cards more impactful for Sefina. (Reduces by 1 the mean and by a ratio of sqrt(33/45) the standard deviation).

## Teamwork

As mentioned before there isn't much teamwork happening. In fact, I love when different people synergise, indeed there are many guardian cards to help the entire team but I rarely see this kind of setup.

In our case Sefina is quite balanced and selfish. She is a strong flex so we support her. Me with Bag tampering, Harvey with **Anatomical Designs**. 

Harvey is a strong ``Seeker`` so my Bag tampering also helps.

Finally, Mateo or me, is quite damage oriented, has to be played carefully so as to not exhaust too many ressources and end up in a bottleneck, has lacking but useful flex capabilities, intangible supporting capabilities and **Scrying**-like abilities. 

My strategy is mostly **strategic**, rely on my teammates to take out the big guns, and be able to defend myself when necessary, deny certain game effects and ``come in clutch``. Since I have to be careful with what cards to play, I like to use Harvey's ability and **No stoned unturned** on myself to have a wider pool of cards to choose from, and use my own scrying to help with Sefina's weakness and strenghts. 

Finally, Sefina's weakness is quite frustrating, last game she drew it 5 times even after using **Quantum flux** and having help from me and Harvey.

## Closing Remarks

When helping in the Deck Building of this campaign I didn't resort to the code at all. And I had a different idea of what each deck did, its strenghts and shortcomings.

When reviewieng the actual visual structures I realised my biases and was humby reminded that the human eye can only see so much without being hijacked by whishes and comparisons.

Firstly, I was conviced my own deck (Mateo) was a **Extreme Card-Advantage Engine** with more versatility. Instead it is now clear and obvious how precise **High-Connectivity Toolbox** is. Furthermore, it has a shade of **Low-Curve All-Rounders** due to its low cost curve.

Additionally, without this labelling I wouldn't be able to devise a plan of amelioration, such as  upping the versatility. Finally, I genuinely wasn't aware of how costly it is to mantain, now I will play this deck with far greater care and won't jump right into paying cards, but rather hoard ressources. My playstyle will reflect the more necessary strategy aspects from here on out, and I will look into the future as much as possible to adapt my play to what I think the board WILL need. In summary, my playstyle will become more conservative, attentive, strategic and ``future proof``. In the future I will add ressource generation hopefully.

Secondly, Sefina really struck me as the **AFK** or **Turret** playstyle. Since she just plays whatever she draws and doesn't have much problem with ressources. Or she sets up and frontloads periodically.

Nevertheless, her stats couldn't be father away from those two playstyles. She is quite versatile, and has a high cost curve, even if she does generates enough ressources consistently.

If her deck was smaller she could pass for a **Curve-Heavy Generalists**. However there isn't much consistency with such a big deck to be exploited for a **Curve-Heavy**.

Instead she relies on specific interactions and various combos to periodically flex and hypercarry, with hopefully enough downtime to ``restock``. Leo de Luca or Chuck Fergus are clear examples, or illicit events of experience which ``return to you hand``. It's randomized and with external help can be easily set up for sucess. Additionally, her specific ability makes the ``event combos`` so much easier to set up.

Still it is clear that fortunately the cost isn't a problem in the playstyle, however I would encourage lowering the cost curve. In conclusion, Sefina's Deck is mostly **Big Deck**, with shades of **Curve-Heavy**.  The strategy doen't change much, but it is surely not **AFK**, just combo and random heavy.

Last but not least, Walter's deck is mostly **Low-Curve All-Rounders**. Both Mateo's and Harvey's deck are quite curve cost free, though with different ressource generating capabilities. I thought his deck would have much more connectivity and turn into **High-Connectivity Toolbox**. Once again I didn't guess right!

This analysis can inform our decisions to add new cards, open our eyes to shortcomings and allow us to exploit the strenghts. It also helps see who should get what mythos cards or trigger certain special location actions.

Honestly, the results are surprising and have changed my mind as to how to play the decks and change them over time.

## Outliers

The **Big Deck** DeckId 50346 has a stunning 3.14 fitness (yes even pi has a place here).

It turns out that it is possible to have a fitness higher than 2.5 though highly unlikely. 

![[outlier1.png]]

![[outlier2.png]]

Additionally, with such a big alpha there is simply not much effect for a mulligan.




