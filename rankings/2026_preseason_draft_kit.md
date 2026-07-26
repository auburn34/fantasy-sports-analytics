# THE 2026 YAHOO DIAMOND-TIER PRESEASON DRAFT KIT
## Value-Based Drafting (VBD) Engine & Positional Scarcity Framework

In a competitive 10-team Yahoo Public League (Half-PPR, 1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, 1 K, 1 DEF), drafting by raw projected points is a fast track to mediocrity. To dominate, you must draft based on **Value Over Replacement Player (VORP)**. 

VORP quantifies how much better a player is than a readily available waiver-wire or late-round starter at the exact same position. In a 10-team format, the waiver wire is incredibly rich, which naturally flattens the replacement level for positions with high supply. 

Our local DuckDB analytics pipeline has established the following baseline expected fantasy points (xFP) for replacement players (defined as the starting baseline in a 10-team league):
*   **Quarterback (QB) Baseline:** Streaming level (flat VORP distribution)
*   **Running Back (RB) Baseline:** $81.6\text{ xFP}$
*   **Wide Receiver (WR) Baseline:** $125.8\text{ xFP}$
*   **Tight End (TE) Baseline:** $110.5\text{ xFP}$
*   **Defense (DEF) Baseline:** $127.5\text{ xFP}$
*   **Kicker (K) Baseline:** $136.0\text{ xFP}$

By calculating the delta between a player's projected season xFP and their positional replacement baseline, we isolate their true draft-day value. If a player projected for $150\text{ points}$ plays a position with a $125\text{ baseline}$, their VORP is $+25$. If another player projected for $130\text{ points}$ plays a position with an $80\text{ baseline}$, their VORP is $+50$. The latter is twice as valuable, despite scoring fewer raw points. This draft kit is built entirely on this mathematical truth.

---

## THE OVERALL TOP 30 VBD BIG BOARD

*Note: This board strictly ranks players by their VORP score, representing their true draft-day weight in Yahoo Half-PPR formats.*

| Overall Rank | Player | Position | Team | Season xFP | VORP Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | C. McCaffrey | RB | SF | 183.6 | **102.0** |
| **2** | P. Nacua | WR | LA | 209.1 | **83.3** |
| **3** | B. Robinson | RB | ATL | 163.2 | **81.6** |
| **4** | J. Smith-Njigba | WR | SEA | 207.4 | **81.6** |
| **5** | D. Achane | RB | MIA | 153.0 | **71.4** |
| **6** | J. Chase | WR | CIN | 195.5 | **69.7** |
| **7** | J. Gibbs | RB | DET | 149.6 | **68.0** |
| **8** | A. St. Brown | WR | DET | 185.3 | **59.5** |
| **9** | T. McBride | TE | ARI | 166.6 | **56.1** |
| **10** | R. Rice | WR | KC | 178.5 | **52.7** |
| **11** | J. Taylor | RB | IND | 134.3 | **52.7** |
| **12** | G. Wilson | WR | NYJ | 178.5 | **52.7** |
| **13** | M. Wilson | WR | ARI | 175.1 | **49.3** |
| **14** | D. London | WR | ATL | 175.1 | **49.3** |
| **15** | C. Olave | WR | NO | 170.0 | **44.2** |
| **16** | C. Brown | RB | CIN | 122.4 | **40.8** |
| **17** | C. Skattebo | RB | NYG | 113.9 | **32.3** |
| **18** | A. Jeanty | RB | LV | 112.2 | **30.6** |
| **19** | W. Robinson | WR | NYG | 156.4 | **30.6** |
| **20** | G. Pickens | WR | DAL | 156.4 | **30.6** |
| **21** | C. Lamb | WR | DAL | 156.4 | **30.6** |
| **22** | J. Jefferson | WR | MIN | 154.7 | **28.9** |
| **23** | D. Adams | WR | LA | 154.7 | **28.9** |
| **24** | B. Bowers | TE | LV | 139.4 | **28.9** |
| **25** | J. Cook | RB | BUF | 110.5 | **28.9** |
| **26** | Z. Flowers | WR | BAL | 151.3 | **25.5** |
| **27** | N. Collins | WR | HOU | 149.6 | **23.8** |
| **28** | K. Williams | RB | LA | 105.4 | **23.8** |
| **29** | J. Jacobs | RB | GB | 105.4 | **23.8** |
| **30** | T. Etienne | RB | JAX | 105.4 | **23.8** |

---

## POSITIONAL DEEP DIVES

### QUARTERBACK (QB)

#### Tactical QB Roadmap
In a 10-team, 1-QB league, the replacement baseline at quarterback is incredibly high (QB10 baseline). Because the drop-off in projected points from QB3 to QB12 is historically flat, early draft capital spent on a quarterback yields near-zero or even negative VORP relative to the elite flex assets you pass up. Our draft strategy treats QB as a streaming position or late-round target, focusing heavily on Konami-code rushing upside.

*   **Must-Target (Late-Round Rushing Upside):** Streamers or late-round dual-threats. Look for high-volume rushing quarterbacks whose weekly floor mirrors that of a mid-tier RB2, allowing you to maximize roster flexibility in the early rounds.
*   **Fade at Cost (Pocket Passers):** High-cost pocket quarterbacks. Drafting a non-rushing quarterback in the early-to-mid rounds of a 10-team league is a structural error that severely limits your team's ceiling.

---

### RUNNING BACK (RB)
*Replacement Baseline: 81.6 xFP*

| Pos Rank | Player | Team | Expected Vol (xFP/g) | VORP | Key Draft Tag |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | C. McCaffrey | SF | 10.8 | 102.0 | Tier 1 Anchor |
| **2** | B. Robinson | ATL | 9.6 | 81.6 | Elite Workhorse |
| **3** | D. Achane | MIA | 9.0 | 71.4 | High-Efficiency Cheat Code |
| **4** | J. Gibbs | DET | 8.8 | 68.0 | High-Value Touch Monster |
| **5** | J. Taylor | IND | 7.9 | 52.7 | Pure Volume RB1 |
| **6** | C. Brown | CIN | 7.2 | 40.8 | Mid-Round Value |
| **7** | C. Skattebo | NYG | 6.7 | 32.3 | Sleeper Workhorse |
| **8** | A. Jeanty | LV | 6.6 | 30.6 | Rookie Volatility Target |
| **9** | J. Cook | BUF | 6.5 | 28.9 | Stable Floor RB2 |
| **10** | K. Williams | LA | 6.2 | 23.8 | Overdrafted Trap |

#### Diamond Tier Analytical Commentary

```
RB VORP Distribution Curve:
McCaffrey [102.0] ----------------------------------------------------*
B. Robinson [81.6] -----------------------------------------*
D. Achane [71.4]   -------------------------------------*
J. Gibbs [68.0]    ----------------------------------*
J. Taylor [52.7]   ---------------------------*
C. Brown [40.8]    ---------------------*
```

*   **Must-Target (High Scarcity Value): Chase Brown (CIN) — VORP: +40.8**
    Chase Brown is one of the most glaring market inefficiencies in the 2026 data. Projected for a healthy $122.4\text{ xFP}$ with a $14.3\%$ target share in a high-octane Cincinnati offense, Brown delivers $7.2\text{ xFP/g}$. His VORP of $+40.8$ places him as the overall RB6, yet his draft-day cost is typically depressed. He offers an elite blend of receiving volume ($5.1\text{ weekly targets}$) and explosive playmaking ability in a Joe Burrow-led system that has historically sustained elite fantasy assets.
*   **Fade at Cost: Kyren Williams (LA) — VORP: +23.8**
    At a VORP of just $+23.8$, Kyren Williams is an easy fade at his current ADP. Williams' projection is heavily dragged down by a meager $8.0\%$ target share ($2.8\text{ weekly targets}$) in Sean McVay's passing tree. With LA projecting $34.5\text{ pass attempts per game}$, Williams is almost entirely dependent on rushing volume and touchdown efficiency. If the Rams split goal-line work or regress in offensive efficiency, Williams has a dangerously low floor for an early-round selection.

---

### WIDE RECEIVER (WR)
*Replacement Baseline: 125.8 xFP*

| Pos Rank | Player | Team | Expected Vol (xFP/g) | VORP | Key Draft Tag |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | P. Nacua | LA | 12.3 | 83.3 | Alpha WR1 |
| **2** | J. Smith-Njigba | SEA | 12.2 | 81.6 | Elite Target Earner |
| **3** | J. Chase | CIN | 11.5 | 69.7 | Tier 1 Foundation |
| **4** | A. St. Brown | DET | 10.9 | 59.5 | Slot Machine Alpha |
| **5** | R. Rice | KC | 10.5 | 52.7 | Mahomes' Preferred Read |
| **6** | G. Wilson | NYJ | 10.5 | 52.7 | High-WOPR Target |
| **7** | M. Wilson | ARI | 10.3 | 49.3 | Deep-Threat Value |
| **8** | D. London | ATL | 10.3 | 49.3 | Post-Hype Breakout |
| **9** | C. Olave | NO | 10.0 | 44.2 | High-Share WR2 |
| **10** | W. Robinson | NYG | 9.2 | 30.6 | PPR Machine |

#### Diamond Tier Analytical Commentary

```
WR Elite Tier Target Share Projections:
G. Wilson (NYJ):       [====================================] 36.0%
J. Smith-Njigba (SEA): [===================================] 35.7%
J. Chase (CIN):        [==================================] 32.1%
A. St. Brown (DET):    [=================================] 31.7%
P. Nacua (LA):         [==============================] 31.1%
```

*   **Must-Target (High Scarcity Value): Jaxon Smith-Njigba (SEA) — VORP: +81.6**
    The analytical models are screaming to draft Jaxon Smith-Njigba. He boasts a massive $35.7\%$ projected target share, translating to $12.0\text{ weekly targets}$—the highest volume projection in the entire dataset. This translates to an elite $12.2\text{ xFP/g}$ and a VORP score of $+81.6$, virtually tied with Puka Nacua for the positional crown. JSN has officially graduated to a hyper-targeted alpha role in Seattle, commanding an elite Weighted Opportunity Rating (WOPR) that makes him a lock to smash his ADP.
*   **Fade at Cost: A.J. Brown (NE) — VORP: +20.4**
    With a changed team flag of $1.0$ following his high-profile transfer to New England, A.J. Brown is a highly risky pick. The Patriots' low-volume passing environment (projecting just $33.5\text{ pass attempts per game}$) drops Brown's projected target share to $24.7\%$ and his weekly targets to $8.3$. This results in a season projection of $146.2\text{ xFP}$ and a VORP of only $+20.4$. Avoid paying for his past Philadelphia production; he is now trapped in an inefficient, run-heavy offense.

---

### TIGHT END (TE)
*Replacement Baseline: 110.5 xFP*

| Pos Rank | Player | Team | Expected Vol (xFP/g) | VORP | Key Draft Tag |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | T. McBride | ARI | 9.8 | 56.1 | Positional Cheat Code |
| **2** | B. Bowers | LV | 8.2 | 28.9 | Elite Sophomore |
| **3** | T. Kraft | GB | 7.6 | 18.7 | Deep Value Sleeper |
| **4** | K. Pitts | ATL | 7.5 | 17.0 | Post-Hype Option |
| **5** | G. Kittle | SF | 7.4 | 15.3 | Volatile Veteran |
| **6** | D. Goedert | PHI | 7.1 | 10.2 | Steady Floor |

#### Diamond Tier Analytical Commentary
*   **Must-Target (High Scarcity Value): Trey McBride (ARI) — VORP: +56.1**
    McBride is the ultimate positional differentiator in 2026. Commanding a staggering $27.9\%$ target share ($9.1\text{ weekly targets}$) in Arizona's passing attack, his $9.8\text{ xFP/g}$ projection results in a $+56.1\text{ VORP}$ score. To put this in perspective, McBride's VORP is nearly double that of the TE2 (Brock Bowers, $+28.9$) and lightyears ahead of Travis Kelce ($+6.8$) or Sam LaPorta ($+1.7$). McBride is a true wide receiver masquerading as a tight end.
*   **Fade at Cost: Sam LaPorta (DET) — VORP: +1.7**
    LaPorta is a massive landmine at his current market price. While he remains a highly talented real-life tight end, his projected target share of $18.5\%$ in Detroit's crowded offense (featuring Amon-Ra St. Brown and Jahmyr Gibbs) limits him to $6.3\text{ weekly targets}$ and $6.6\text{ xFP/g}$. With a season projection of $112.2\text{ xFP}$, he sits barely above the 10-team replacement baseline of $110.5$, yielding a nearly useless $+1.7\text{ VORP}$. 

---

### DEFENSE/SPECIAL TEAMS (DEF)
*Replacement Baseline: 127.5 xFP*

| Pos Rank | Team | Season xFP | VORP | Key Draft Tag |
| :--- | :--- | :--- | :--- | :--- |
| **1** | San Francisco 49ers | 144.5 | **17.0** | Elite DST1 |
| **2** | Baltimore Ravens | 139.4 | **11.9** | High Floor |
| **3** | Dallas Cowboys | 136.0 | **8.5** | Big Play Dependent |
| **4** | Buffalo Bills | 132.6 | **5.1** | Streamer Core |
| **5** | Philadelphia Eagles | 127.5 | **0.0** | Replacement Level |

#### Diamond Tier Analytical Commentary
*   **Must-Target: San Francisco 49ers — VORP: +17.0**
    In 10-team leagues, streaming defenses is a highly viable strategy, but if you want to lock and leave a premium unit, the 49ers are the only defense worth paying any premium for. Projecting for $8.5\text{ xFP/g}$ and a season-long $144.5\text{ xFP}$, they offer a $+17.0\text{ VORP}$ over replacement. Their elite pass-rush win rate and defensive scheme keep their weekly floor incredibly safe.
*   **Fade at Cost: Philadelphia Eagles — VORP: 0.0**
    The Eagles project exactly at the $127.5\text{ xFP}$ replacement level. Drafting them or holding them through tough matchups is a negative-EV play. Treat them strictly as a streaming option rather than a roster fixture.

---

### KICKER (K)
*Replacement Baseline: 136.0 xFP*

| Pos Rank | Player | Team | Season xFP | VORP | Key Draft Tag |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Justin Tucker | BAL | 149.6 | **13.6** | Premium Leg |
| **2** | Harrison Butker | KC | 144.5 | **8.5** | High-Volume Offense |
| **3** | Brandon Aubrey | DAL | 142.8 | **6.8** | Elite Range |
| **4** | Evan McPherson | CIN | 137.7 | **1.7** | Neutral Value |
| **5** | Jake Elliott | PHI | 136.0 | **0.0** | Replacement Level |

#### Diamond Tier Analytical Commentary
*   **Must-Target: Justin Tucker (BAL) — VORP: +13.6**
    Tucker remains the gold standard of kicking assets, projecting for $8.8\text{ xFP/g}$ in a Baltimore offense that consistently moves the ball but occasionally stalls in the red zone. With a VORP of $+13.6$, he represents a legitimate weekly advantage at a position most managers ignore.
*   **Fade at Cost: Jake Elliott (PHI) — VORP: 0.0**
    Elliott sits exactly at the replacement level of $136.0\text{ xFP}$. In a highly aggressive Philadelphia offense that routinely goes for it on fourth down, Elliott's field goal volume is capped, making him a generic streamer rather than a draftable asset.