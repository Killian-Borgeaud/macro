# Lecture Rules — Full Bad/Good Examples

Worked examples for each rule R1-R10 from `SKILL.md`. Subject-agnostic — patterns apply to any technical lecture. Read on first lecture of a session.

## Contents
- R1: Intuition before formalism
- R2: Symbol-to-meaning bridge
- R3: Comparison tables for related concepts
- R4: Narrate every derivation step
- R5: Worked examples with realistic numbers
- R6: Key concepts in callout boxes
- R7: Assumptions explain what breaks
- R8: Supplement sparse slides
- R9: Source citations
- R10: Length and depth

---

## R1: Intuition before formalism — always

Before ANY formula, explain what the mathematical object IS. What does it represent? What would it look like if you could see it?

**Bad:**
> The OLS estimator is $\hat{\beta}_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}$.

**Good:**
> We need a number that captures "how much does Y change when X changes by one unit?" The OLS slope is exactly this: it measures the average co-movement between X and Y, scaled by how spread out X is.
>
> Formally: $\hat{\beta}_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}$
>
> Symbol by symbol: the numerator is empirical covariance (unnormalized); the denominator is the total variation in X. So $\hat{\beta}_1$ = "co-movement divided by X-spread."

---

## R2: Symbol-to-meaning bridge for every formula

Every symbol gets a plain-words reading immediately after. Use the "reading this" pattern.

**Good:**
> $Var(\hat{\beta}_1 \mid x_1, \ldots, x_n) = \frac{\sigma^2}{\sum (x_i - \bar{x})^2}$
>
> Reading this: precision of the slope depends on two things. The numerator $\sigma^2$ is error variance — how noisy the data is (more noise → less precise slope). The denominator is total variation in X (more spread in X → more precise slope). This is why "variance in X is good."

---

## R3: Comparison tables for related concepts

When two or more concepts are related or easily confused, use a table.

**Good (HTML):**
```html
<table>
<tr><th>Symbol</th><th>Name</th><th>What it is</th><th>Observable?</th></tr>
<tr><td>$u_i$</td><td>Error</td><td>True unobservable deviation from population line</td><td>No</td></tr>
<tr><td>$\hat{u}_i$</td><td>Residual</td><td>$y_i - \hat{y}_i$</td><td>Yes</td></tr>
<tr><td>$\beta_1$</td><td>True slope</td><td>Population parameter</td><td>No</td></tr>
<tr><td>$\hat{\beta}_1$</td><td>OLS slope</td><td>Sample estimate of $\beta_1$</td><td>Yes</td></tr>
</table>
```

---

## R4: Derivations must be narrated

Each transition gets a short sentence on WHY, not just WHAT.

**Bad:**
> $\sum y_i(x_i - \bar{x}) = \sum(\beta_0 + \beta_1 x_i + u_i)(x_i - \bar{x}) = \ldots$
> But $\sum(x_i-\bar{x})=0$, so $\hat{\beta}_1 = \beta_1 + B$.

**Good:**
> Start from the estimator and substitute the true model $y_i = \beta_0 + \beta_1 x_i + u_i$:
> $$\sum y_i(x_i - \bar{x}) = \sum(\beta_0 + \beta_1 x_i + u_i)(x_i - \bar{x})$$
> Distribute across the three terms:
> $$= \beta_0 \underbrace{\sum(x_i - \bar{x})}_{=\,0} + \beta_1 \underbrace{\sum x_i(x_i - \bar{x})}_{=\,\sum(x_i-\bar{x})^2} + \sum u_i(x_i - \bar{x})$$
> The first sum vanishes because deviations from the mean always sum to zero. The second simplifies algebraically. We're left with:
> $$\hat{\beta}_1 = \beta_1 + \underbrace{\frac{\sum u_i(x_i - \bar{x})}{\sum(x_i - \bar{x})^2}}_{B}$$
> The estimator equals the true value PLUS a bias term that depends on how errors correlate with X.

---

## R5: Worked examples with realistic, non-round numbers

```html
<div class='example'>
<strong>Example: Computing OLS estimates</strong>
<p>From 321 observations on house prices: $\bar{x} = 2106.73$, $\bar{y} = 96100.7$, $\hat{\beta}_1 = 40.14$.</p>
<p>Find $\hat{\beta}_0$:</p>
<p>$$\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x} = 96100.7 - 40.14 \times 2106.73 = 11536.57$$</p>
<p>Each additional square foot adds $40.14 to the price.</p>
</div>
```

Use realistic non-round numbers (40.14, 2106.73). Never `x=2, y=5`.

---

## R6: Key concepts in callout boxes

```html
<div class='key-concept'>
<strong>Unbiasedness of OLS:</strong> Under assumptions SLR.1–SLR.4, $E[\hat{\beta}_0] = \beta_0$ and $E[\hat{\beta}_1] = \beta_1$. If we could repeat sampling infinitely, the average estimate equals the truth.
</div>
```

Every theorem, definition, or named result the reader might want to find later.

---

## R7: Assumptions explain what breaks when violated

Never just state — always: (1) plain meaning, (2) scenario where it holds, (3) scenario where it fails, (4) what breaks.

**Bad:** "SLR.4: $E[u|X] = 0$."

**Good:**
> SLR.4 (zero conditional mean): $E[u|X] = 0$.
>
> **Plain meaning:** the unobserved factors $u$ have no systematic relationship with X. Knowing X tells you nothing about the average error.
> **Holds:** randomized experiments where X is assigned by coin flip — by design, $u$ is uncorrelated with X.
> **Fails:** observational wage regressions, where $X$ = years of schooling and $u$ contains ability. People with high ability both school more AND earn more, so $E[u|X]$ rises with X.
> **What breaks:** OLS becomes biased. $\hat{\beta}_1$ no longer estimates the causal effect — it conflates schooling with ability.

---

## R8: Supplement sparse slides, flag out-of-scope

If slides say "SLR.4: $E[u|X]=0$" with one bullet, the lecture should spend 2-3 paragraphs unpacking it.

Out-of-scope content gets flagged:
```html
<p><em>Beyond exam scope, but useful:</em> The reason homoskedasticity matters is that...</p>
```

---

## R9: Source citations parenthetically

End a paragraph or formula with the source page in parens: "(Lecture 1a p7)" or "(textbook ch3 p82)". Don't over-cite — once per major concept is enough.

---

## R10: Length and depth

A lecture is LONG. 4000-8000 words for a multi-module topic. The user wants a complete reference, not a summary. Every proof in slides → reproduced and narrated. Every formula → at least one worked example or figure.

When in doubt: longer.
