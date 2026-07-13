# FSD and Take-The-Best — Theoretical Foundations for the Mulligan Decision

**Date:** 2026-06-21
**Context:** Mathematical foundation for the mulligan decision algorithm (`mulligan_decision.py`), which combines two heuristics — probability of improvement and expected value — without collapsing them into a single weighted number.

---

## TL;DR

- **First-order stochastic dominance (FSD)** compares entire outcome *distributions* using only an ordering relation — it never requires committing to an exact cardinal utility.
- **Take-The-Best** is a lexicographic inference algorithm that picks the single most informative cue and ignores the rest. It is grounded in the **bias-variance tradeoff**: under noisy/small-sample conditions, throwing away information reduces variance more than it increases bias.
- What I built for the mulligan problem is **not a literal instance of either theory**. Section 5 proves, with an explicit numerical counterexample, that comparing two summary statistics (EV, P_better) is mathematically weaker than comparing full cumulative distribution functions — so calling my Pareto-filter "FSD" would be imprecise. I show exactly where the gap is.

---

## 1. First-Order Stochastic Dominance (FSD) — formal development

### 1.1 Origins

The concept was first formalized in welfare economics by Quirk and Saposnik (1962), who linked it to the admissibility of resource allocations under uncertainty using measurable utility functions. The modern, most-cited treatment comes from a cluster of near-simultaneous papers:

- Hadar, J. & Russell, W. (1969). *"Rules for Ordering Uncertain Prospects."* American Economic Review, 59, 25–34.
- Hanoch, G. & Levy, H. (1969). *"The Efficiency Analysis of Choices Involving Risk."* Review of Economic Studies, 36, 335–346.
- Rothschild, M. & Stiglitz, J. (1970) — extended the framework to **second-order** stochastic dominance, relevant to risk-averse agents.

### 1.2 Formal definition

Let $X$ and $Y$ be random variables with cumulative distribution functions $F_X$ and $F_Y$. We say $X$ **first-order stochastically dominates** $Y$ (written $X \succeq_{FSD} Y$) if:

$$F_X(v) \leq F_Y(v) \quad \text{for all } v \in \mathbb{R}$$

with strict inequality for at least one $v$. Intuitively: at *every* threshold, $X$ is at least as likely to exceed that threshold as $Y$ is.

### 1.3 The equivalence theorem — why this is not just a CDF comparison

The result that makes FSD useful as a *decision* criterion (not just a descriptive one) is a theorem jointly established by Hadar & Russell (1969) and Hanoch & Levy (1969):

$$X \succeq_{FSD} Y \iff \mathbb{E}[u(X)] \geq \mathbb{E}[u(Y)] \quad \text{for every non-decreasing } u: \mathbb{R} \to \mathbb{R}$$

with strict inequality in expectation for at least one such $u$. This is the key fact: FSD ordering is **equivalent** to "every decision-maker who simply prefers more to less, regardless of their specific risk attitude, agrees that $X$ is better." You don't need to know the agent's exact utility function — only that it's non-decreasing.

An equivalent formulation, using quantile functions $F_X^{-1}, F_Y^{-1}: (0,1) \to \mathbb{R}$:

$$X \succeq_{FSD} Y \iff F_X^{-1}(p) \geq F_Y^{-1}(p) \quad \text{for all } p \in (0,1)$$

This is the **quantile coupling** formulation: there exist random variables $\tilde{X} \sim X$ and $\tilde{Y} \sim Y$ on a common probability space such that $\tilde{X} \geq \tilde{Y}$ almost surely.

### 1.4 A direct corollary relevant to mulligan ties

Because $u(x) = x$ is itself non-decreasing, the equivalence theorem implies:

$$X \succeq_{FSD} Y \implies \mathbb{E}[X] \geq \mathbb{E}[Y]$$

So **if two strategies have exactly equal expected value, neither can strictly FSD-dominate the other** (assuming the distributions aren't literally identical). This is a clean, provable fact — not a heuristic — and it's exactly why a tie on EV *requires* a tie-break rule rather than being resolvable by appeal to dominance.

### 1.5 The contemporary revival: FSD vs. expected-value maximization

Christian Tarsney (2018, revised 2020), *"Exceeding Expectations: Stochastic Dominance as a General Decision Theory,"* arXiv:1807.10895, argues that pure expected-value maximization becomes paradoxical in extreme cases (the St. Petersburg paradox, Pascal's Mugging), and shows that under certain background-uncertainty conditions, stochastic dominance reasoning recovers most of the plausible implications of expected-value reasoning while avoiding these pathologies. His framing of FSD is precise: it formalizes the minimal principle that one should prefer a given probability of a better payoff to the same probability of a worse payoff, all else equal — a much weaker (and therefore much safer) commitment than full expectation maximization.

---

## 2. Take-The-Best (Gigerenzer & Goldstein, 1996)

### 2.1 Citation

Gigerenzer, G. & Goldstein, D.G. (1996). *"Reasoning the Fast and Frugal Way: Models of Bounded Rationality."* Psychological Review, 103(4), 650–669.

### 2.2 The algorithm, formalized

Let $a, b$ be two objects to be compared, each described by a vector of binary cues $c_1, \dots, c_m \in \{0, 1, ?\}$ (where $?$ denotes "cue value unknown"). Each cue $i$ has an empirically estimated **validity**:

$$v_i = \frac{R_i}{R_i + W_i}$$

where $R_i$ is the number of correct pairwise rankings made when cue $i$ discriminates (i.e., $c_i(a) \neq c_i(b)$), and $W_i$ is the number of incorrect ones.

**Algorithm:**
1. Order all cues by decreasing validity: $v_1 \geq v_2 \geq \dots \geq v_m$.
2. For the pair $(a,b)$, scan cues in that order. Stop at the first cue $i^*$ such that $c_{i^*}(a) \neq c_{i^*}(b)$.
3. Predict that the object with the higher value on cue $i^*$ is the better one.
4. If no cue discriminates, guess.

Crucially, step 2 means **all cues after $i^*$ are never consulted, even if they exist and contain information.** This is what "one-reason decision making" means formally.

### 2.3 The empirical result

Gigerenzer & Goldstein ran a computer-simulation competition between Take-The-Best and several "rational" inference procedures (e.g. multiple linear regression, which optimally weights and integrates *all* cues). Take-The-Best matched or outperformed all competitors in both inferential speed and accuracy, despite deliberately ignoring information.

### 2.4 The mathematical explanation: the bias–variance dilemma

The follow-up paper that formalizes *why* this happens is:

Gigerenzer, G. & Brighton, H. (2009). *"Homo Heuristicus: Why Biased Minds Make Better Inferences."* Topics in Cognitive Science, 1, 107–143. DOI: 10.1111/j.1756-8765.2008.01006.x

The argument rests on the standard statistical decomposition of expected squared error for an estimator $\hat{f}$ trained on sample data $D$, estimating a true function $f$ at a point $x$:

$$\mathbb{E}_D\left[(\hat{f}_D(x) - f(x))^2\right] = \underbrace{\left(\mathbb{E}_D[\hat{f}_D(x)] - f(x)\right)^2}_{\text{Bias}^2} + \underbrace{\mathbb{E}_D\left[(\hat{f}_D(x) - \mathbb{E}_D[\hat{f}_D(x)])^2\right]}_{\text{Variance}} + \sigma^2$$

A model that integrates many weighted cues (like multiple regression) has low bias but must *estimate* many parameters from finite, noisy data — each estimated weight contributes variance. A model like Take-The-Best, which uses a single cue and no estimated weights beyond a validity ranking, has higher bias (it ignores real information) but near-zero estimation variance.

**The less-is-more effect occurs precisely when the variance reduction outweighs the bias increase** — which Gigerenzer & Brighton show happens systematically when: (a) the sample size used to estimate cue weights/validities is small, and (b) the underlying criterion is noisy. Both conditions match the mulligan scenario directly: your card-scoring system is acknowledged to be an imprecise, compressed ordinal signal (high "noise" relative to true impact) — exactly the regime where the bias-variance argument favors a lexicographic rule over a fully-weighted linear combination.

---

## 3. Pareto Dominance — formal statement

For a set of alternatives $S$, each described by a vector of $k$ objectives $v_A = (v_{A,1}, \dots, v_{A,k})$ where higher is always better on every axis: $A$ **Pareto-dominates** $B$ (written $A \succeq_P B$) iff:

$$v_{A,i} \geq v_{B,i} \;\; \forall i \in \{1,\dots,k\}, \quad \text{and} \quad v_{A,i} > v_{B,i} \;\; \text{for at least one } i$$

The **Pareto frontier** is the set of non-dominated elements:

$$\mathcal{P} = \{A \in S : \nexists\, B \in S \text{ s.t. } B \succeq_P A\}$$

This concept originates in Pareto's welfare economics (*Manuale di economia politica*, 1906) and is standard in multi-objective optimization. I cite it here only to make its provenance explicit, since it's the piece that mechanically connects FSD-style thinking to the two-heuristic mulligan problem.

---

## 4. What I actually built — the precise gap between literal theory and my synthesis

This section is the most important one. **I did not implement FSD, and I did not implement Take-The-Best.** I built a structure *motivated* by both, and this section proves, with an explicit counterexample, exactly how far my implementation is from the literal theorem.

### 4.1 The claim I am NOT making

I am not claiming that Pareto-dominance over $(\mathbb{E}[V], P_{\text{better}})$ is equivalent to, or even implies, first-order stochastic dominance over the full outcome distribution. **It is not, and I can prove it with a counterexample.**

### 4.2 Counterexample: my Pareto check can rank strategies that FSD cannot rank at all

Let the original hand value be $v_0 = 10$. Consider two mulligan strategies with these discrete outcome distributions:

**Strategy A:** $X_A = 0$ with probability $0.05$; $X_A = 11$ with probability $0.95$.
**Strategy B:** $X_B = 9$ with probability $0.05$; $X_B = 10.5$ with probability $0.95$.

Compute the two summary statistics used by my algorithm:

$$\mathbb{E}[X_A] = 0.05(0) + 0.95(11) = 10.45 \qquad \mathbb{E}[X_B] = 0.05(9) + 0.95(10.5) = 10.425$$
$$P(X_A > 10) = 0.95 \qquad P(X_B > 10) = 0.95$$

By my algorithm's Pareto check, **A weakly dominates B** ($\mathbb{E}[X_A] > \mathbb{E}[X_B]$, $P_{\text{better}}$ tied) — A would be selected (or at least never discarded as dominated).

Now check literal FSD by comparing the full CDFs at every relevant point:

| $v$ | $F_A(v)$ | $F_B(v)$ | Comparison |
|---|---|---|---|
| $0$ | $0.05$ | $0.00$ | $F_A(0) > F_B(0)$ |
| $9$ | $0.05$ | $0.05$ | tied |
| $10$ | $0.05$ | $0.05$ | tied |
| $10.5$ | $0.05$ | $1.00$ | $F_A(10.5) \ll F_B(10.5)$ |
| $11$ | $1.00$ | $1.00$ | tied |

FSD requires $F_A(v) \leq F_B(v)$ for **all** $v$ for $A \succeq_{FSD} B$. At $v=0$, $F_A(0) = 0.05 > F_B(0) = 0$ — **violated**. So $A$ does not FSD-dominate $B$.

Checking the reverse ($B \succeq_{FSD} A$ requires $F_B(v) \leq F_A(v)$ everywhere): at $v=10.5$, $F_B(10.5)=1.00 > F_A(10.5)=0.05$ — **also violated**.

**Conclusion: $A$ and $B$ are FSD-incomparable.** Neither dominates the other once you look at the *full* distribution — because $A$ carries a worse worst-case outcome (a 5% chance of landing on $0$, versus $B$'s worst case of $9$), even though $A$'s expected value and its probability of beating $10$ are both at least as good as $B$'s.

My two-statistic Pareto filter is blind to this: it only checks the mean (one linear functional of the distribution) and one single point on the CDF (the threshold $v_0$). It cannot detect that $A$ has a substantially worse tail at $v=0$, because that information lives at a point on the CDF my algorithm never inspects.

### 4.3 What this means in practice

My Pareto-filter step is a legitimate, self-contained piece of multi-objective optimization (Section 3) — that part needs no caveat. What requires the caveat is calling it *FSD-inspired* in any rigorous sense: it inspects two scalar projections of a distribution, not the distribution itself, and Section 4.2 proves these are not interchangeable. If your mulligan strategies can produce genuinely bimodal or fat-tailed outcomes (which is plausible — a mulligan can draw back the same weak card, or whiff into another weak one), a full CDF comparison would sometimes reveal incomparability or reversed rankings that the two-statistic summary hides.

### 4.4 What I borrowed from Take-The-Best, precisely

Take-The-Best operates on **discrete binary cues** in a **pairwise comparison** setting (does cue $i$ discriminate, yes/no?). My tie-break rule operates on **two continuous statistics** with an **epsilon-tolerance band** substituting for binary discrimination. This is a generalization in spirit — "decide using the strongest signal first; only consult the second signal when the first one hasn't already settled the matter" — but it is not the formal algorithm of Section 2.2. I did not estimate cue validities $v_i$ from any pairwise-correct/incorrect tally, which is the actual empirical core of the original method.

### 4.5 Why the synthesis is still defensible

The justification is not that the two pieces fit into one pre-existing unified framework — they don't; one is normative decision theory under uncertainty, the other is a descriptive/prescriptive model of bounded cognition. The justification is that **both independently converge on the same prescription under the same condition**: when you don't trust the cardinal precision of your numbers but you do trust their relative ordering, prioritize ordering-robust comparisons (dominance, lexicographic rules) over magnitude-sensitive ones (raw expectation, fully-weighted sums). That convergence — from two unrelated literatures solving structurally similar problems — is the actual argument, not a citation of a single unifying theorem.

---

## Full source list

- [Quirk, J.P. & Saposnik, R. (1962) — referenced in Grokipedia, *Stochastic Dominance*](https://grokipedia.com/page/Stochastic_dominance)
- [Hadar, J. & Russell, W. (1969). Citation context — Springer](https://link.springer.com/chapter/10.1007/978-3-030-11590-6_1)
- [Hanoch, G. & Levy, H. (1969). Citation context — Springer](https://link.springer.com/chapter/10.1007/978-3-030-11590-6_1)
- [Extreme Points of First-Order Stochastic Dominance Intervals — Cowles Foundation, Yale](https://cowles.yale.edu/sites/default/files/2023-02/d2355.pdf)
- [Modularity Classes and Boundary Effects in Multivariate Stochastic Dominance — arXiv](https://arxiv.org/pdf/1807.06402)
- [Tarsney, C. (2018, rev. 2020). "Exceeding Expectations." arXiv:1807.10895](https://arxiv.org/abs/1807.10895)
- [Gigerenzer, G. & Goldstein, D.G. (1996). Official PDF](https://www.dangoldstein.com/papers/FastFrugalPsychReview.pdf)
- [Gigerenzer, G. & Brighton, H. (2009). "Homo Heuristicus" — PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3629675/)
- [Gigerenzer & Brighton (2009) — Wiley Online Library, full bias-variance derivation](https://onlinelibrary.wiley.com/doi/10.1111/j.1756-8765.2008.01006.x)

---

## Link to implementation

[[mulligan_decision.py]] — `choose_mulligan()`: Pareto-dominance filter (Section 3) followed by an epsilon-tolerant lexicographic tie-break (Section 2, adapted per Section 4.4).

---

#decision-theory #stochastic-dominance #take-the-best #bias-variance #arkham-miner #research
