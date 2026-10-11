# MHF4U Advanced Functions - Unit 1 Practice Test (Version 1)
## Worked answer key and marking guide

**Total: 60 marks.** Each of the four categories is worth 15 marks. Award equivalent correct methods and reasonable mathematical explanations. For sketches, assess features and endpoint inclusion rather than artistic precision.

## Part A - Knowledge and Understanding (15 marks)

**1. [5]** `6 - x >= 0` gives `x <= 6`; `x + 2 != 0` gives `x != -2`. Domain: `(-infinity, -2) U (-2, 6]`. Award 3 for the domain (including brackets and union) and 2 for the two explained restrictions.

**2. [5]** Vertex `(3, 4)` and opens down [1]. Set `-2|x - 3| + 4 = 0`; then `|x - 3| = 2`, so x-intercepts `(1, 0)` and `(5, 0)` [2]. Domain `(-infinity, infinity)` and range `(-infinity, 4]` [2].

**3. [5]** Vertical asymptote `x = -3`; horizontal asymptote `y = -2` [2]. Domain `(-infinity, -3) U (-3, infinity)`; range `(-infinity, -2) U (-2, infinity)` [2]. `h(0) = 1/3 - 2 = -5/3`, so y-intercept `(0, -5/3)` [1].

## Part B - Thinking (15 marks)

**4. [5]** For input `u = 9`, solve `3(x + 1) = 9`, giving `x = 2`; output `-2(3) + 4 = -2`, so `(2, -2)` [2]. Domain `[-1, infinity)` and range `(-infinity, 4]` [2]. The graph is compressed horizontally by factor `1/3`, shifted left 1, reflected in the x-axis, stretched vertically by factor 2, and shifted up 4 [1 for a complete description].

**5. [5]** Swap x and y in `y = (x - 1)^2 + 2`. With original `x >= 1`, choose the positive root: `f^(-1)(x) = 1 + sqrt(x - 2)` [2]. Inverse domain `[2, infinity)` and range `[1, infinity)` [2]. `f^(-1)(6) = 3`, so `f(3) = 6` [1].

**6. [5]** Sketch: line `y = x + 1` for `x < 0` approaches `(0, 1)` with an open dot on that piece; parabola `y = 1 - x^2` for `0 <= x <= 2` has filled endpoints `(0, 1)` and `(2, -3)`; ray `y = 3` for `x > 2` starts with open dot `(2, 3)` [2]. Range `(-infinity, 1] U {3}` [1]. Continuous at `0` because both sides approach 1 and `p(0)=1`; discontinuous at `2` because the left value/limit is -3 while the right limit is 3 [2].

## Part C - Communication (15 marks)

**7. [5]** The inside `2(x - 3)` makes the horizontal scale `1/2`, not a six-unit shift [1]. The graph shifts **right 3**, not 6, and **up 1** [2]. To map `(4, -1)`, solve `2(x - 3) = 4`, so `x = 5`; the new output is `-1 + 1 = 0`, giving `(5, 0)` [2].

**8. [5]** `[10.00 - 9.79]/0.1 = 2.1 m/s` and `[10.19 - 10.00]/0.1 = 1.9 m/s` [2]. The centred slope is `[10.19 - 9.79]/0.2 = 2.0 m/s` [1]. The earlier secant slope is a little above 2.0 and the later one a little below; they bracket the rate near `t=2`, so `2.0 m/s` is a reasonable instantaneous estimate [2].

**9. [5]** From `y = 2x - 5`, swap variables and solve: `f^(-1)(x) = (x + 5)/2` [2]. The reciprocal is `1/f(x) = 1/(2x - 5)`, which is a different operation [1]. The inverse reverses the input-output mapping; the reciprocal divides 1 by an output [1]. Check: `f(f^(-1)(x)) = 2[(x+5)/2] - 5 = x` [1].

## Part D - Application (15 marks)

**10. [5]** `C(t) = 6` for `0 < t <= 2`, and `C(t) = 6 + 3(t - 2)` for `2 < t <= 8` [2]. `C(4.2) = 6 + 3(2.2) = $12.60` [1]. `C(1) = $6` and `C(5) = $15`, so average rate is `(15 - 6)/(5 - 1) = $2.25 per hour` [1]. This is the average increase in charge per hour over the four-hour interval, despite the rate changing at 2 hours [1].

**11. [5]** `H(1) = 16` and `H(3) = 16`, so average rate is `(16 - 16)/(3 - 1) = 0 m/s` [2]. `H(0.99) = 15.8995` and `H(1.01) = 16.0995`; centred slope is `(16.0995 - 15.8995)/0.02 = 10 m/s` [2]. The average rate describes net height change over two seconds, while the instantaneous estimate describes motion near 1 second; the ball rises and later falls [1].

**12. [5]** `R(9) = R(11) = 198`, so average rate is `(198 - 198)/2 = 0` dollars of revenue per $1 ticket-price increase [2]. `R(9.9) = R(10.1) = 199.98`, so centred rate is `0` in the same units [1]. The parabola opens down with vertex `(10, 200)`, so a $10 ticket price gives maximum modelled daily revenue of $200 [1]. Rates are positive on the left of 10 and negative on the right, while the centred rate at the maximum is zero [1].

## Blueprint and generation notes

- Blueprint: `data/blueprints/math/mhf4u_unit1_functions_rates_researched_v1.json` (schema validated).
- Preserved: Unit 1 topic scope, 12 questions, 60 marks, four 15-mark achievement categories, and progression from direct skills to explanation and application.
- Intentional variation: All contexts, values, and wording are original; no textbook or public sample question was copied.
- Assumptions: 90 minutes and equal category marks are a practice design choice. Ontario curriculum gives expectations and categories, while schools and teachers choose their own unit-test structure.
