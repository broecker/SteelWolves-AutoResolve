# SteelWolves-AutoResolve
A combat auto-resolver for the board game 'Steel Wolves'

Steel Wolves has a very detailed tactical sub vs convoy attack simulation built
in. However, there were few decision points and lots of die rolling as well as 
drawing chits from up to 14 different cups. The focus of the game was on also 
on the strategic side of the campaing and resolving the tactical combat was 
taking _a lot_ of time. While the previous game 'Silent War' had an optional 
quick resolve rule for combat, there was no such thing for 'Steel Wolves'.

This program tries to implement an auto-resolver for the tactical combat in 
'Steel Wolves'. It is built upon a few assumptions and simplifications (call it
'doctrine' or 'rules of engagment' if you will). It can be either used 
stand-alone to resolve a single combat or used repeatedly to build engagement
statistics which, in turn, can be compiled into easy-to-use tables. The focus 
of this project is on the creation of these tables.

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
- All merchats are modeled on the british merchant fleet, especially concerning 
tonnage and defense values
- Destroyer values are randomly generated; while their tonnage is either 1 or 2
, their defense and asw values are uniformly distributed between 1 and 3
- Submarines will disengange as soon as they are either spotted or damaged
- Submarines will attack highest-value targets (sorted by tonnage, then defense
) first and parcel out their attack value in '4's
- Submarines will never engage undetected targets


## Building and Running
The script is currently a single-file python script. Run it using your normal 
way of executing python scripts on your system (eg `python ./ccomputer.py`).


## Future Work
The current version is a single-file python script that grew beyond the comfort
of a simple script. The next version should be a conversion to Javascript which
then can be embedded into a website. This will have the advantage that the 
combat resolver can be called from any browser (think cellphone, tablet) during
an actual game, similar to a _very_ involved die rolling app.
