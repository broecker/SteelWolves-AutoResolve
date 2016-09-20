# SteelWolves-AutoResolve
A combat auto-resolver for the board game 'Steel Wolves' -- Markus Broecker 
<mbrckr@gmail.com>

![U-87](U_87_Kriegsmarine.jpg "U-87")
---

## Introduction
Steel Wolves has a very detailed tactical sub vs convoy attack simulation built
in. However, there were few decision points and lots of die rolling as well as 
drawing chits from up to 14 different cups. The focus of the game was on also 
on the strategic side of the campaing and resolving the tactical combat was 
taking _a lot_ of time. While the previous game 'Silent War' had an optional 
quick resolve rule for combat, there was no such thing for 'Steel Wolves'.

This program tries to implement an auto-resolver for the tactical combat in 
'Steel Wolves'. It is built upon a few assumptions and simplifications of how 
this pogram will behave in during the combat phase (call it 'doctrine' or 
'rules of engagment' if you will). It can be either used stand-alone to resolve 
a single combat or used repeatedly to build engagement statistics which, in 
turn, can be compiled into easy-to-use tables. The focus of this project is on 
the creation of these tables.

The basic idea is then to run the combat resolution hundreds of times with a 
specific configuration, record the result (and its statistical properties, such
as mean, median, standard deviation and so on) and do this for many different
configurations. These results will then be compiled into an abbreviated combat 
table. 

## Performance
First runs indicate that a run of 500 combat resolutions can be easily computed
on a lower-end laptop in less than a second. 

## Assumptions
The following assumptions are made:
- Only small and large (C1/C2) convoys are currently supported
- All merchants are modeled on the british merchant fleet, especially concerning 
tonnage and defense values
- Destroyer values are randomly generated; while their tonnage is either 1 or 2
, their defense and asw values are uniformly distributed between 1 and 3
- Submarines will disengange as soon as they are either spotted or damaged
- Submarines will attack highest-value targets (sorted by tonnage, then defense
) first and parcel out their attack value in '4's
- Submarines will never engage undetected targets
- Wolfpacks are currently unsupported


## Building and Running
The script is currently a single-file python script. Run it using your normal 
way of executing python scripts on your system (eg `python ./ccomputer.py`).

There are no command-line parameters yet. Changing the values of combat 
resolution and parameters is currently achieved by hacking the code. 

To create the table 3 steps are involved:
1. The combat result statistics must be created
2. These statistics are analyzed and interpreted into linear tables
3. These tables must be manually aligned to create DRMs 

### Running the Combat Simulation
`ccomputer.py` simulates the combat between a single submarine and a convoy 
thousands of times and writes the output to a file. Important parameters for 
the simulation include:
- Parameters of the submarine (attack, defense, tac)
- Skipper rating (from 0 to +2)
- Convoy size (C1 or C2)
- War period, global ASW level and torpedo quality

The output is a single csv file that contains the result each combat. The 
submarines in this combat are named consecutively, not historically. Each line/
result contains the number of ships sunk and damaged, total tonnage sunk, 
whether the sub got sunk, damaged, spotted or is returning to base. These files
can either be loaded into an external program, such as Excel, or be processed 
in the next step.

If the `globals.verbose_combat` variable is set to `True` there will be a ton
of output describing the combat, such as:
```
Placed sub U-932.0 in column Outer Starboard  [ roll: 5 > None ]
Warning, sub U-932.1(2-1-2) could not be placed
Placed sub U-932.1 in column Outer Starboard  [ roll: 7 > None ]
Revealing 2 counters in column Outer Starboard
Sub U-932.0 has 2 potential targets, placing 2 TDC markers, tactical rating: 2
Target/TDC: M5t (1-0) -1
Target/TDC: M2t (0-0) -1
[M5t (1-0), M2t (0-0)]
Updated target priority: [M5t (1-0), M2t (0-0)]
Combat vs M5t (1-0)
Attack : 2 [ 2 attack 0 skipper -1  torp rating 1 convoy straggle]
Defense: 0 [ 0 ASW -2 TDC 0 column mod 0  damaged]
Diff: 4 Roll: 3 Target hit
Rolling damage for M5t (1-0) : 2 ( -1 torp value) -> damage
Counterattack, red boxes: 0 global asw: 0
Total ASW 0 defense 1 diff -1
No counterattack, diff: -1
Revealing 2 counters in column Outer Starboard
Sub U-932.1 has 4 potential targets, placing 2 TDC markers, tactical rating: 2
Target/TDC: M5t (1-0) 1
Target/TDC: M5t (3-0) 0
[M5t (1-0), M5t (3-0)]
Updated target priority: [M5t (1-0), M5t (3-0)]
Combat vs M5t (1-0)
Attack : 2 [ 2 attack 0 skipper -1  torp rating 1 convoy straggle]
Defense: 0 [ 0 ASW -1 TDC 0 column mod -1  damaged]
Diff: 4 Roll: 0 Target hit
Rolling damage for M5t (1-0) : 3 ( -1 torp value) -> sunk
Sub U-932.1 is claiming target M5t (1-0)
Counterattack, red boxes: 0 global asw: 0
Total ASW 0 defense 1 diff -1
No counterattack, diff: -1
```

### Analyzing the Data

We are looking into different aspects of the output data; mostly we are 
interested in tons and ships sunk, subs spotted, damaged or sunk. The data from
the previous step often exhibits a close to normal distribution, eg the 
following tonnage data (which compares the effect of having an elite skipper):

```
  +********* 1315 00  865 *********+
           *   15 01   14 
        ****   66 02   55 **
          **   29 03   39 *
       *****   90 04  116 ****
  **********  186 05  299 **********
          **   42 06   76 ***
        ****   70 07  114 ****
          **   44 08   79 ***
         ***   55 09  100 ***
          **   33 10   84 ***
           *   15 11   33 *
           *   13 12   28 *
                9 13   18 *
           *   10 14   23 *
                1 15   11 
                2 16   10 
                1 17   16 *
                1 18    6 
                1 19    6 
                0 20    7 
                0 21    0 
```

Note: the format is [histoA] [countA] [tons] [countB] [histoB] with the stars 
acting as a histogram of the data. In this example, the two data sets are both
of a small convoy ('C1') attacked by a single (3-3-2) sub with the left data
having no elite skipper and the right data having a +1 elite skipper. The data
shows a small effect on tonnage sunk and a large reduction of 0 tons sunk (all
misses during the attack). Note that this is not a rigorous statistical 
analysis but rather looking at the data and seeing what happens and how the 
distribution changes. 

### Aligning the Tables
From the distribution calculated above, tables with even spacing and ten 
entries are created. The tables are aligned by shifting them left and right to
each other with each shift counting as a single +/-DRM. As needed, the tables 
are either padded with zeros on the left or the last value on the right. The 
sum of absolute differences between the tables gives a good estimate of how 
close these tables are. 

Finally, based on the best DRMs found and their corresponding shifts an average
result is calculated. These tables are created for both tonnage as well as 
ships sunk. The shifts and DRMs are calculated for each elite skipper level for
each submarine individually. 


## Results

The tables are split between war periods and then grouped per submarine 
based on similar values (eg VIIB and VIIC together).

The final result looks like this (a single sub attacks a large convoy):
```
WP 1 - C2
Sub Rating  Tonnage Table                                    Skipper DRM
2-1-2       [0, 0, 0, 0, 0, 0, 0, 2, 5, 9, 10, 14, 17]        +0, +2, +3
3-3-2       [0, 0, 0, 0, 0, 0, 2, 5, 7, 10, 11, 15, 18]       +0, +2, +3
4-2-3       [0, 0, 0, 0, 0, 1, 4, 6, 9, 12, 14, 18, 21]       +0, +2, +3
5-3-3       [0, 0, 0, 1, 5, 7, 9, 12, 14, 20, 22, 25, 31, 35] +0, +3, +4
-------------------------------------------------------------------------------
Sub Rating  Ships Sunk Table                                 Skipper DRM
2-1-2       [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]           +0, +2, +3
3-3-2       [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]           +0, +2, +3
4-2-3       [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]        +0, +3, +4
5-3-3       [0, 0, 0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4]        +0, +3, +4
Sub Rating     Spotted           RTB       Damaged          Sunk      Promoted
2-1-2 +0         [0-1]       2+[0-3]         [0-1]       0+[0-2]       9+[0-3]    
      +1       3+[0-8]       2+[0-4]       1+[0-8]       0+[0-3]       9+[0-4]    
      +2       3+[0-3]       2+[0-3]       1+[0-3]       0+[0-2]    
3-3-2 +0       3+[0-4]       2+[0-2]       1+[0-4]       0+[0-2]       9+[0-2]    
      +1       3+[0-2]       2+[0-3]       1+[0-2]       0+[0-2]       9+[0-3]    
      +2       3+[0-1]       2+[0-2]       1+[0-1]       0+[0-1]    
4-2-3 +0       3+[0-8]       2+[0-4]       1+[0-8]       0+[0-2]       9+[0-4]    
      +1       3+[0-5]       2+[0-6]       1+[0-5]       0+[0-3]       9+[0-6]    
      +2       3+[0-2]       2+[0-4]       1+[0-2]       0+[0-2]    
5-3-3 +0       3+[0-4]       2+[0-3]       1+[0-4]       0+[0-1]       9+[0-3]    
      +1       3+[0-3]       2+[0-4]       1+[0-3]       0+[0-2]       9+[0-4]    
      +2       3+[0-2]       2+[0-2]       1+[0-2]       0+[0-1]    
-------------------------------------------------------------------------------
```
The primary two tables on top describe both tonnage as well as ships sunk. Note
that for some tonnages there might be '0' ships sunk due to the underlying 
statistics. Both tables should ideally combined when importing the data in a 
layout program or other graphical editor. A result is obtained by rolling a 
single D10 and modifying it with the elite skipper DRM found on the same line.
Note that a +1 elite skipper might have a DRM larger than 1! The values are 
sorted from 0 on the left to 10 and more on the right. 

The lower third contains the combat effect on the submarine with effects from
spotted to sunk. The notation either gives a die roll range (like [0-1]) or a
range after rolling a single die (eg roll a 3 + roll within [0-4]).

To use the tables roll 2D10, ideally differently colored. The first roll is 
used with the skipper DRM to find the tonnage sunk. The same roll is then used
on the second table to find the number of ships sunk. Finally, if the first 
roll is an unmodified 0,1,2,3 or 9 find the result of the combat on the table
below by comparing the second die roll to the given range.  

### Example
For example, a 4-2-3 sub with a +1 skipper attacks a large convoy. Two D10 are
rolled for 3 and 8. The first table results in 0 tons sunk (4-2-3 row at 3+2), 
same goes for the second table (4-2-3 row at 3+3). Next, the unmodified 3 might
result in the sub becoming spotted but the second roll of 8 is outside the 
range of [0-5] of this roll.  

This format can then be easily transformed into nicer looking graphical tables.




## Future Work
The current version of the simulator consist of multipple python scripts that 
grew beyond the comfort of a simple, single-file script. The next version 
should be a conversion to Javascript which then can be embedded into a website. 
This will have the advantage that the combat resolver can be called from any 
browser (think cellphone, tablet) during an actual game, similar to a _very_ 
involved die rolling app.
