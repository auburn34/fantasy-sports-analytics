# The Signal: Exploiting the Expected Points Arbitrage

If you are still setting your lineups based on last week’s box scores, you are playing checkers while the rest of the high-stakes community is playing chess. As a top 0.1% Yahoo Diamond-tier manager, my job isn’t to tell you who scored touchdowns yesterday; it’s to tell you who *should* have scored, who is about to inherit a goldmine of volume, and who is currently running on pure, unsustainable hot streaks.

We’ve plugged the latest pipeline data into our local DuckDB analytical model. The results are clear: the market is mispricing opportunity across the board. Here is your weekly blueprint to exploit these inefficiencies before your league mates catch on.

---

### 🔄 Offseason System Shifts & Volume Transfers

When a major weapon changes zip codes, the market frequently struggles to project the transition from raw historical target shares to context-adjusted volume. Let’s break down the actual opportunity shifts for key relocations:

```
+------------+----------+----------+-------------------+--------------------+------------------------+------------------+
| Player     | Old Team | New Team | '25 Target Share | Proj. '26 Share %  | Proj. Pass Attempts/G  | Weekly Targets   |
+------------+----------+----------+-------------------+--------------------+------------------------+------------------+
| A. Brown   | PHI      | NE       | 28.1%             | 24.7%              | 33.5                   | 8.3              |
| J. Waddle  | MIA      | DEN      | 23.7%             | 20.9%              | 33.0                   | 6.9              |
| J. Williams| DET      | DAL      | 18.6%             | 16.4%              | 35.5                   | 5.8              |
| M. Evans   | TB       | SF       | 24.4%             | 21.5%              | 31.5                   | 6.8              |
| R. Doubs   | GB       | NE       | 19.8%             | 17.4%              | 33.5                   | 5.8              |
+------------+----------+----------+-------------------+--------------------+------------------------+------------------+
```

*   **A.J. Brown (NE):** Going from Philly to New England looks like an immediate downgrade on paper, and his projected target share drops from a dominant 28.1% to a still-respectable 24.7%. However, because New England is projected for a surprisingly high 33.5 pass attempts per game, Brown is still slated for **8.3 weekly targets**. The catch? His projected **8.6 xFP per game** suggests these targets will be of a much lower quality than what he enjoyed in Philadelphia. Prepare for a more volatile, floor-heavy profile.
*   **Jaylen Waddle (DEN):** Waddle leaves Miami’s hyper-efficient scheme for Sean Payton's Denver offense. His target share slides to 20.9%, translating to **6.9 weekly targets** on 33.0 projected team pass attempts. With a projected **7.4 xFP/g**, Waddle’s ceiling is heavily capped unless Denver's passing efficiency takes a massive leap forward.
*   **Jameson Williams (DAL):** Williams lands in a highly favorable environment in Dallas. Despite a modest 16.4% projected target share, Dallas’s pass-heavy script (35.5 projected attempts) keeps him relevant with **5.8 weekly targets** and a solid **7.1 xFP/g**. He is a sneaky winner of this cycle.
*   **Mike Evans (SF):** Evans’ transition to Kyle Shanahan’s low-volume passing offense (31.5 projected attempts) drops his target share to 21.5% (**6.8 weekly targets**). This yields a projection of **7.0 xFP/g**. However, as you'll see below, his current opportunity profile makes him a prime target for a trade.
*   **Romeo Doubs (NE):** Doubs accompanies A.J. Brown to New England, holding a 17.4% projected target share. On 33.5 team pass attempts, he will net **5.8 targets per game** with a **6.6 xFP/g** projection. He is a roster-filler, not a difference-maker.

---

### 🔥 Diamond Buy-Low Breakdown

These players are earning elite opportunity, but bad luck, poor quarterback play, or variance has kept them out of the box score spotlight. Acquire them now before their actual output regresses to their stellar underlying metrics.

#### 1. Adonai Mitchell (WR, NYJ)
*   **WOPR:** 0.75 | **Expected FPPG:** 10.6 | **Actual FPPG:** 6.7 | **FPOE/G:** -3.9
*   **The Breakdown:** Mitchell is the ultimate buy-low candidate right now. A WOPR (Weighted Opportunity Rating) of 0.75 is elite—flirting with top-12 wide receiver usage. Yet, he is underperforming his expected output by nearly 4 fantasy points per game. The volume is there; the connection is just slightly off. When that variance flips, he will put up WR1 weeks.

#### 2. Jerry Jeudy (WR, CLE)
*   **WOPR:** 0.58 | **Expected FPPG:** 8.5 | **Actual FPPG:** 5.7 | **FPOE/G:** -2.8
*   **The Breakdown:** Jeudy is quietly dominating Cleveland's target share with a 0.58 WOPR. He's leaving 2.8 points per game on the table relative to his expected volume. He is a cheap depth piece with a rock-solid floor that the fantasy public is completely ignoring.

#### 3. Mike Evans (WR, SF)
*   **WOPR:** 0.61 | **Expected FPPG:** 11.2 | **Actual FPPG:** 8.7 | **FPOE/G:** -2.5
*   **The Breakdown:** Evans is adjusting to San Francisco, but his underlying usage is highly encouraging. A 0.61 WOPR and 11.2 Expected FPPG indicate he is still being heavily utilized in high-value areas (deep targets and red-zone looks). His -2.5 FPOE suggests he’s just a touchdown or two away from a massive breakout. Buy the dip.

#### 4. Justin Jefferson (WR, MIN)
*   **WOPR:** 0.74 | **Expected FPPG:** 11.1 | **Actual FPPG:** 9.4 | **FPOE/G:** -1.7
*   **The Breakdown:** Yes, even the king can be a buy-low. Jefferson is commanding a monster 0.74 WOPR, but he's underperforming his expected output of 11.1 FPPG. If a frustrated manager in your league is worried about Minnesota's passing game caps, send an offer immediately. 

#### 5. Rashid Shaheed (WR, NO)
*   **WOPR:** 0.56 | **Expected FPPG:** 10.6 | **Actual FPPG:** 9.4 | **FPOE/G:** -1.3
*   **The Breakdown:** Shaheed is usually pinned as a volatile "boom-or-bust" deep threat. However, his 0.56 WOPR and 10.6 Expected FPPG prove his role is far more consistent and valuable than the public realizes. He has a stable floor to go with his game-winning ceiling.

---

### ⚠️ Regression Red Flags

The players below are currently printing fantasy points, but they are doing so on borrow-time efficiency. They are heavily outperforming their actual volume, making them prime "sell-high" candidates.

*   **Tucker Kraft (TE, GB):** Kraft is averaging **12.7 FPPG** on a meager **7.1 Expected FPPG** (a massive **+5.5 FPOE/G**). His WOPR is a microscopic **0.35**. He is entirely dependent on outlier efficiency and touchdown variance. Sell him to a tight-end-needy manager for a premium before the Packers' target distribution normalizes.
*   **Jonathan Taylor (RB, IND):** Taylor is running hot with **20.0 FPPG** against an expected **15.8 xFPPG** (**+4.1 FPOE/G**). With a **0.16 WOPR**, he isn't heavily involved in the passing game, meaning his production is entirely tied to elite rushing efficiency. While he's great, this is his absolute ceiling. If you can swap him for an elite tier-1 receiver, do it.
*   **Jahmyr Gibbs (RB, DET):** Much like Taylor, Gibbs is outrunning his volume. He is averaging **19.4 FPPG** on **15.3 Expected FPPG** (**+4.1 FPOE/G**). His **0.25 WOPR** is solid for a back, but Detroit's committee cap will eventually pull his actual production back down to earth.
*   **Puka Nacua (WR, LA):** Nacua's **0.71 WOPR** is spectacular, but his **19.9 FPPG** is pacing ahead of an already sky-high **16.4 Expected FPPG** (**+3.5 FPOE/G**). Don’t sell him for pennies, but recognize that he is playing at his absolute peak right now.
*   **Rashee Rice (WR, KC):** Rice is turning a **0.54 WOPR** into **15.2 FPPG**, outperforming his **11.9 Expected FPPG** by **+3.4 points per game**. Patrick Mahomes' efficiency is elevating him, but his actual volume profile is that of a high-end WR2 rather than the untouchable WR1 he's currently priced as.

---

### 💎 Closing Diamond Takeaway

In fantasy football, **volume is the only currency that matters**, and **WOPR is the exchange rate**. Efficiency (FPOE) is highly volatile and regresses to the mean over a multi-week sample size. 

If you want to win championships, build your rosters around players with high WOPRs and negative FPOE (like **Adonai Mitchell** and **Mike Evans**), while aggressively liquidating players with low WOPRs and high positive FPOE (like **Tucker Kraft**). Let your league mates chase yesterday's touchdowns while you corner the market on tomorrow's volume.