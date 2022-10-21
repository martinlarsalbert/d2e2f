# Introduction
The operation of two sister ferries Tycho Brahe and Aurora as seen in {numref}`forsea-fig` is investigated with historical data collected from the online [Blueflow](https://www.blueflow.se/) monitoring systems installed on the ships. This kind of analysis is important for the *Energy management* of ships: monitoring, analyzing and controlling. Only energy consumption that is related to the propulsion of the ships, the energy that moves the ships from A to B is analyzed. The energy consumption from the "hotel" of the ships is thereby not included in this analysis.   

```{figure} vitaskär.jpg
---
height: 200px
name: forsea-fig
---
ForSea ferries Tycho Brahe and Aurora
```
The energy consumption of these ships depend on:
1. *Loading condition* : weight of the cargo (trains, trucks and cars.).
2. *Operation* : trajectory of the route as a function of how the crew operated the thrusters controlling the ship.  
3. *Environment* : wind, waves and current.
4. *Energy efficiency of ships*: ship design, propulsion, engines and ship hull condition with fouling.

Only energy saving potential related to the *operation* of the ships is addressed in this project. It is not possible to change the *loading condition* or the environmental conditions. The energy potential of improved energy efficiency from ship's overhaul: cleaning ship hull, repair or rebuild the ships, is also not addressed here. 

The energy consumption from the operation should be estimated. Only the total propulsion energy can be measured however. 
The additional energy consumptions from the *loading condition*, *environment* and the *energy efficiency of the ships* does therefore make this more complicated. An increase in total energy consumption can originate from either of mentioned components. It is therefore hard to say if a trip with high energy consumption was due to suboptimal operation or bad weather. When analyzing the energy consumption for longer times, it is also hard to say if an increased energy consumption originates from worse operation or that resistance of the ships have increased due to fouling, or the engines have aged etc.
The influence from the operation therefore needs to be filtered out from the rest. 

One way to do this is to assume that the changes in the other components changes much slower, so that within a small time window they can be assumed to be constant. The energy potential is analysed in this way in the [Following-trips section](following_trips.ipynb).
