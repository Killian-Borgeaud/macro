# Lecture 3a

## Page 1

Macroeconomics III Prof. Guido Cozzi March 1 7 , 202 6

1

## Chapter 6

EDUCATION AND GROWTH: THE SOLOW MODEL WITH HUMAN CAPITAL

## Page 2

## INTRODUCTION

1. The steady state predictions of the Solow model seem quite supported by the data, even though...
2. ...the investment ratio   appears in the data to have a very strong and positive impact on percapita GDP  , while population growth rate    has a very strong negative effect on   . s n y y
3. The empirical results do not contradict convergence, but in reality convergence is much slower than predicted by the Solow model.
- Is there a way to modify the Solow model that can work to rectify both empirical problems?
- Yes: according to Mankiw, Romer, Weil, 1992, 'A Contribution to the Empirics of Economic Growth', QJE, (MRW): considering Human Capital 2

## Page 3

- Human capital : the accumulated stock of what is invested in training of the labour force: education, learning by doing, health, etc.
- Assume that human capital is accumulated in the same way as physical capital : every year a constant share of GDP is used for investment in human capital. Then, accumulation of human capital should affect the rate of convergence i n the same way as accumulation of physical capital.

## Page 4

- Human capital cannot be separated from the workers . One can separate a man from his computer but not from his education. Hence, the return on human capital accrues to the workers . This keeps the 'labour's share' unchanged even though a new kind of capital is being accumulated.
- It looks as if human capital could help solve the problem concerning the rate of convergence in the Solow model.

## Page 5

- What about the problem concerning the steady state prediction of the Solow model?
- Consider an increase in the rate of investmen nt in physical capital (called s until now). This increases capital and income per worker in steady state through the usual well-known channels.
- With a constant rate of investment also in human capital, larger income per worker means more investment in human capital per worker and, in the end, more human capital per worker in steady state. Since human capital is productive, income per worker will increase more than without human capital.

## Page 6

- Seemingly, human capital could also help solve the problem concerning the impact of the investment rate  on GDP per capita
- Hence, incorporating human capital might solve both of the empirical problems of the Solow model.
- Furthermore, it is an aim in itself to improve the model by adding human capital, since, by intuition, the skills of the labour force must be an important input factor.

## Page 7

## THE SOLOW MODEL WITH HUMAN CAPITAL

- More or less the same micro world as in the Solow model
- The same types of agents: one type of (representative) firms and one type of (representative) consumers - and possibly a government sector
- But the firm now uses human capital in its production and
- the consumer also accumulates human capital .
- Output is used for consumption, investment in physical capital or investment in human capital . There is still just one production sector.
- The same markets: output and (services of) physical capital and labour

## Page 8

- No separate market for human capital services since human capital is linked to labour and its services are sold inseparably together with the labour
- The services traded in the labour market are no longer manyears of 'raw labour', but man-years endowed with human capital. The real wage is a mix of compensation for raw labour and return to human capital .
- The number of workers, the labour force, is    . Every worker is endowed with the same amount of human capital, . The total level of human capital in the economy is t L t h t t t H h L . =
- Raw labour input,     , cannot be varied independently of human capital input. The input of human capital,      , is proportional to     because each worker brings her   . Here is an important distinction from physical capital. d t L d t t h L d t L t h
- We can now describe the new elements of the economy.

## Page 9

## THE PRODUCTION FUNCTION WITH HUMAN CAPITAL

<!-- formula-not-decoded -->

- Constant returns to            : the replication argument t t t K ,H ,L
- The per capita production function is:

<!-- formula-not-decoded -->

- When calculating the marginal product of labour, one has to take into account that one additional worker comes with a given amount of human capital,    . Hence,   , not , should be taken as given when we differentiate wrt. t h t h t H t L .

## Page 10

- 1 1 t t t t t Y K h A L α ϕ α ϕ α ---=

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

- t t t r K / Y =α

<!-- formula-not-decoded -->

- 1 3 / α ≅ 1 3 / ϕ ≅

## Page 11

## THE CONSUMERS' ACCUMULATION OF CAPITAL

- As before, each of the     consumers supplies one unit of labour inelastically and t L
- the number of consumers grows at a constant rate,         , 1 n &gt; -
- and all physical capital,     , is supplied as long as        . t K 0 t r &gt;
- As in the general Solow model, the representative consumer has to decide     given    , which in turn determines              . t Y t C t t t S Y C = -
- But now the consumer also has to decide how to divide gross savings,     , into gross investment in physical capital, , and gross investment in human capital,    . t S K t I H t I

## Page 12

- Given     and     : K t I H t I

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where we have assumed the same rate of depreciation, , for physical and human capital. 0 1 &lt;δ &lt;

- The restriction that     and     have to fulfill is: K t I H t I

<!-- formula-not-decoded -->

- We assume that the consumer's considerations result in the standard Solow assumptions:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

- Hence ( ) t K H t S s s Y = + ⇒

<!-- formula-not-decoded -->

## Page 13

## THE COMPLETE SOLOW MODEL WITH HUMAN CAPITAL

<!-- formula-not-decoded -->

- Parameters: K H , ,s ,s , ,n,g. α ϕ δ
- Given                  the model determines the sequences 0 0 0 0 K ,H ,L ,A ( ) ( ) ( ) ( ) ( ) ( ) ( ) ( ) t t t t t t t t K , H , L , A , Y , r , w , S . 13

## Page 14

## 1. Define:

<!-- formula-not-decoded -->

2. From                            we get that ( ) 1 t t t t t Y K H AL α ϕ α ϕ --=

<!-- formula-not-decoded -->

3. Restatement of the capital accumulation equations:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

4. Dividing on both sides by           gives: 1 1 t t A L + +

<!-- formula-not-decoded -->

## THE LAW OF MOTION

<!-- formula-not-decoded -->

## Page 15

## 5. Inserting             gives the transition equations : t t t y k h α ϕ =  

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

- The law of motion: two coupled, first-order difference equations in     and    . Given     and     they determine and      . t k  t h  0 k  0 h  ( ) t k  ( ) t h 
- There is no easy diagrammatic way to show convergence towards a steady state. We will show:
1. There is a well-defined steady state.
2. Numerical simulations suggest convergence towards a steady state for reasonable parameter values.
3. Convergence holds for a linear approximation around a steady state.

## Page 16

6. Subtracting     and     , respectively, on both sides of the transition equations gives the Solow equations : t k  t h 

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

- From these we found in the previous lecture a welldefined steady state:    ,     , implying also a steady state growth path,    , for income per worker. * k  * h  * t y
- From the Solow equations also follow:

<!-- formula-not-decoded -->

- We use these to construct:

## Page 17

*[high visual content — prefer .pages/p017.png]*

## The Phase diagram for the Solow model with human capital

<!-- image -->

## Page 18

## STEADY STATE

- 0 k k h h -= -=    

<!-- formula-not-decoded -->

- Solving for          and          gives the steady state values: * t k k =   * t h h =  

<!-- formula-not-decoded -->

- Inserting these into              gives: t t t y k h α ϕ =  

<!-- formula-not-decoded -->

## Page 19

and then, from            , the steady state growth path: t t t y y A = 

<!-- formula-not-decoded -->

- Taking logs gives:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

- The elasticity of    with respect to: * t y
- -is now                  , where in the Solow model it was             . It is now around 1, where before it was around ½. K s ( ) 1 / α α ϕ --( ) 1 / α -α
- -is                  , that is, around one. ( ) 1 / ϕ α ϕ --H s
- -is now                            , where in the Solow model it was , that is, now around -2, where before it was around -½. ( ) n g δ + + ( ) ( ) 1 / α ϕ α ϕ -+ --( ) 1 / α α --

These features are much more realistic.

## Page 20

## STRUCTURAL POLICIES FOR STEADY STATE

<!-- formula-not-decoded -->

.

1. The effects of     and             on    are qualitatively as in the Solow model, but the quantitative effects are now much stronger and much more plausible. And has a stronger effect than    ! K s n g δ + + K s n g δ + + * t y
2. The effect of     is of the same size as the effect of    . Golden rule: K s H s

<!-- formula-not-decoded -->

An interesting new question is:

## Page 21

3. Should the government promote investment in education (up to golden rule) by subsidizing education?
- Note: this happens to a large extent in many Western countries.
- Also note: the empirics suggest that investment in human capital is (at least) as important as investment in physical capital.
- Does this make investment subsidies in physical and human capital equally-well or equally-badly motivated?
- A general view of welfare economics: intervene if (and only if) private decisions cannot be expected to lead to socially optimal outcomes.
- Government subsidies have to be motivated by specific market imperfections.

## Page 22

- Some imperfections that specifically point to education subsidies:
- -Imperfect credit markets (adverse selection problem)
- -Imperfect insurance markets (moral hazard problem)
- -Externalities
- -Imperfect private knowledge
- Another motive for education subsidies lies in distributive concerns.
- If inequality is high, the poor may not invest in education . Underinvestment by the many poor cannot be compensated by over-investment by the few rich.
- Decreasing returns to education: can one rich study 100 years? Can this ever compensate 5 poor not studying 20 years each?

## Page 23

## STABILITY OF STEADY STATE

- t y  t t k ,h   g
- ( ) 1 t t t t t w k h A w α ϕ α = -⇒   g
- 1 t t t t t r k h A r α ϕ α -= ⇒  

## Page 24

## SIMULATION

- Let                                                             and . 1 3 0 2 0 15 0 06 0 K H / , s . , s . , . , n α ϕ δ = = = = = = 0 015 g . =
- In steady state:               and             . 14 22 * k . =  10 67 * h . = 
- Start in          and         , and simulate using the transition equations: 0 16 k =  0 2 h = 

<!-- formula-not-decoded -->

- The result is shown in the phase diagram:

## Page 25

*[high visual content — prefer .pages/p025.png]*

<!-- image -->

## Page 26

## Comparative analysis in the phase diagram

- An increase in     shifts             upwards. At first, only increases, but then     begins to increase as well. H s t h  0 t h   ∆ =    t k 
- What happens to     and to          ? The growth rates jump! t y  t t y y A = 

<!-- image -->

## Page 27

## SOCIAL INFRASTRUCTURE

- Why do some countries invest so much more than others? And why are some countries much more productive?
- An explanation could be found (partly) in differences in social infrastructure or institutions:
- -Presence and quality of a financial system
- -Quality of government rules and regulations
- -Well-functioning systems of laws and courts
- -Sound fiscal policy with an uncorrupted expenditure side
- -Good educational system
- Plotting a constructed index of social infrastructure against GDP per worker unveils a clear positive correlation:

## Page 28

<!-- image -->

- Correcting for reversed causality results in an even stronger effect of institutions on economic performance.
- This suggests that institutions certainly are important when considering structural policy.

## Page 29

## SUMMING UP

With the Solow model with human capital we have:

- Explained intuitively why incorporating human capital into the Solow model should work to overcome both of its empirical problems
- Set up explicitly a Solow model with accumulation of both physical and human capital
- Derived the model's law of motion
- Found its steady state and realised that indeed it conforms with our intuitions
- Tested the model's steady state prediction empirically and found it to perform remarkably well

## Page 30

- Discussed the model's implications for structural policy:
- Traditional policies for saving and investment in physical capital and for population growth are qualitatively supported as in the Solow model, but with stronger and more plausible qualitative effects.
- Policies for investment in human capital are supported as strongly as policies for investment in physical capital. Given the imperfections related to educational decisions, public subsidies to education seem to be well-motivated.

## Page 31

## CONCLUSIONS

1. The Solow model with human capital performs very well empirically, both wrt. its steady state prediction and wrt. its convergence prediction, even under the assumption of 'same technology' in all countries.
2. This is reassuring for policy implications!
3. However, important parameters are unexplained, e.g., and    . K s H s
4. The quality of 'institutions' may provide explanation of otherwise unexplained parameters.
5. The rate of technological growth that determines the longrun rate of growth in GDP per worker, is unexplained in the Solow model with human capital: 'we have understood almost everything, and yet almost nothing!'.
6. Points towards theories of endogenous technological progress. 31
