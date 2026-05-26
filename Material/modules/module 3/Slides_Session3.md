# Slides_Session3

## Page 1

## 4,212,2 Macroeconomics III Exercises and Independent Studies

Maria Bolboaca

March 2026

## Page 2

## Outline

- The Solow Model with Human Capital (Exercise 3.1)
- The Solow Model with Oil (Exercise 3.2)

## Page 3

## The Solow Model with Human Capital: Motivation

- Remember Exercise 1.3.
- The Solow model predicts that there should be a linear relationship between ln( y ∗ ) and ln( s ) -ln( n + δ ) , and that the slope should be α 1 -α , which is equal to 0 . 5 if α = 1 / 3 :

<!-- formula-not-decoded -->

## Page 4

## The Solow Model with Human Capital: Motivation

<!-- image -->

The slope estimate is significantly larger than 1 / 2 and we can conclude that in the real world, the structural parameters s and n seem to have a stronger influence on y than predicted by the theory.

## Page 5

## The Solow Model with Human Capital: Motivation

- The slope estimate is α 1 -α = 1 . 63, which implies that α = 0 . 62 ∼ 2 / 3.
- α = 2 / 3 is too large to be attributable to physical capital.
- If we are confident that α = 1 / 3, it follows that our OLS estimate is biased, meaning it is different than the 'true value' .
- Note: If we do not add all relevant variables in the empirical model, these will be left in the error term (residuals). And they could be correlated with s and n .
- Ideally, we should add something which is positively correlated with s , and negatively correlated with n .
- What about human capital (skills)?

## Page 6

## The Solow Model with Human Capital: Motivation

- Human capital can be defined as the accumulated stock of what is invested in the training of the labor force: education, learning by doing, health, etc.
- Schooling tends to rise when fertility declines, hence it is negatively correlated with n .
- Countries with high investment rates in capital tend also to invest in schooling, hence human capital is positively correlated with s .
- Mass education and sustained growth took off around the same time (19th century).
- Thus, including human capital in the model seems worthwhile, as it might 'solve' some of our problems.

## Page 7

## The Solow Model with Human Capital

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## Page 8

## The Solow Model with Human Capital

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

7 Parameters: g , α , s K , s H , n , ϕ and δ . 8 Endogenous variables: Y , K , L , r , w , C , A , and H of which K t , H t , A t and L t are state (predetermined) variables.

## Page 9

## Transformations in per 'Efficiency Unit of Labor' Terms

Define: ˜ k t = kt At = Kt AtLt , ˜ y t = yt At = Yt AtLt , ˜ h t = ht At = Ht AtLt . Then:

<!-- formula-not-decoded -->

which is equivalent to

<!-- formula-not-decoded -->

## Page 10

## Transformations in per 'Efficiency Unit of Labor' Terms

The set of equations with transformed variables in per efficiency unit of labor terms is:

<!-- formula-not-decoded -->

where ˜ w t = At

<!-- formula-not-decoded -->

## Page 11

## The Transition Equations

Replacing the production function: ˜ y t = ( ˜ k t ) α ( ˜ h t ) ϕ in the physical and human capital accumulation equations, we obtain the transition equations:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## Page 12

## The Solow Equations

Subtracting ˜ k t and ˜ h t , respectively, on both sides of the transition equations gives the Solow equations:

<!-- formula-not-decoded -->

which is equivalent to:

<!-- formula-not-decoded -->

Similarly,

<!-- formula-not-decoded -->

## Page 13

## Steady State

Set ˜ k t + 1 = ˜ k t = ˜ k ∗ and ˜ h t + 1 = ˜ h t = ˜ h ∗ . This implies:

<!-- formula-not-decoded -->

which in the Solow equations is equivalent to:

<!-- formula-not-decoded -->

## Page 14

## Steady State

We can re-write these equations as:

<!-- formula-not-decoded -->

These are the two lines along which k and h are constant and which we plot in the phase diagram. Solving the two equations gives:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## Page 15

## Steady State

Having found the steady state value of human and physical capital stock, we can solve for the steady state of the other variables in the model:

<!-- formula-not-decoded -->

## Page 16

## Variables in per 'Worker' Terms

<!-- formula-not-decoded -->

## Page 17

## Golden Rule

The growth path for consumption per worker in the steady state is:

<!-- formula-not-decoded -->

Since the natural logarithm is an increasing function, we may as well maximize the altitude of the path for ln( c ∗ t ) :

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## Page 18

## Golden Rule

The first-order conditions are:

<!-- formula-not-decoded -->

Solving this system of equations with two unknowns gives s K = α and s H = ϕ .

## Page 19

*[high visual content — prefer .pages/p019.png]*

## Phase Diagram

Calibration (Lecture 3a, slide 24): α = ϕ = 1 3 , n = 0, δ = 0 . 06, g = 0 . 015, s i K = 0 . 2, s i H = 0 . 15.

<!-- image -->

## Page 20

*[high visual content — prefer .pages/p020.png]*

## Phase Diagram

<!-- formula-not-decoded -->

<!-- image -->

## Page 21

*[high visual content — prefer .pages/p021.png]*

## Phase Diagram

<!-- formula-not-decoded -->

<!-- image -->

## Page 22

## Comment

In the general Solow model: only one factor can be accumulated; share α = 1 3 . Here: 2 factors, with combined share α + ϕ = 2 .

3

## Page 23

## Exercise 3.1:Simulations

<!-- formula-not-decoded -->

- ˜ k ∗ , ˜ y ∗ increase if either s K or s H increases.
- The effect of the policy on ˜ c ∗ depends on where s K and s H were initially and where they end up relative to the Golden Rule.

## Page 24

## Increase in the Savings Rate

## Economy 1:

What happens if the savings rate s K increases from 0.25 to 0.33? Economy 2:

What happens if the savings rate s H increases from 0.25 to 0.33?

## Page 25

*[high visual content — prefer .pages/p025.png]*

## Increase in the Savings Rate

<!-- image -->

## Page 26

*[high visual content — prefer .pages/p026.png]*

## Increase in the Savings Rate

<!-- image -->

## Page 27

*[high visual content — prefer .pages/p027.png]*

## Increase in the Savings Rate

<!-- image -->

## Page 28

*[high visual content — prefer .pages/p028.png]*

## Increase in the Savings Rate

<!-- image -->

## Page 29

*[high visual content — prefer .pages/p029.png]*

## Increase in the Savings Rate

<!-- image -->

## Page 30

*[high visual content — prefer .pages/p030.png]*

## Increase in the Savings Rate

<!-- image -->

## Page 31

## More Realistic Calibration

<!-- formula-not-decoded -->

- ˜ k ∗ , ˜ y ∗ increase if either s K or s H increases.
- The effect of the policy on ˜ c ∗ depends on where s K and s H were initially and where they end up relative to the Golden Rule.

## Page 32

## Increase in the Savings Rate

## Economy 1:

What happens if the savings rate s K increases from 0.25 to 0.33? Economy 2:

What happens if the savings rate s H increases from 0.25 to 0.33?

## Page 33

*[high visual content — prefer .pages/p033.png]*

## Increase in the Savings Rate

<!-- image -->

$$Note:$$

$$α = 1 4 & ϕ = 1 6 (left), α = ϕ = 1 3 (right)$$

## Page 34

*[high visual content — prefer .pages/p034.png]*

## Increase in the Savings Rate

<!-- image -->

$$Note:$$

$$α = 1 4 & ϕ = 1 6 (left), α = ϕ = 1 3 (right)$$

## Page 35

*[high visual content — prefer .pages/p035.png]*

## Increase in the Savings Rate

<!-- image -->

$$Note:$$

$$α = 1 4 & ϕ = 1 6 (left), α = ϕ = 1 3 (right)$$

## Page 36

*[empty text — see .pages/p036.png]*

## Page 37

*[empty text — see .pages/p037.png]*

## Page 38

*[empty text — see .pages/p038.png]*

## Page 39

*[empty text — see .pages/p039.png]*

## Page 40

*[empty text — see .pages/p040.png]*

## Page 41

*[empty text — see .pages/p041.png]*

## Page 42

*[empty text — see .pages/p042.png]*

## Page 43

*[empty text — see .pages/p043.png]*

## Page 44

*[empty text — see .pages/p044.png]*

## Page 45

*[empty text — see .pages/p045.png]*
