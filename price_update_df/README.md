_The program receives 3+ files as input_:
1. goods in the supplier's warehouses;
2. the current supplier's price list;
2. custom price list(s).

_The program does_:
1. indicates which product from the user price list is in the supplier's main warehouse;
2. updates prices, marks goods as "Sale", "Promo" etc., saves a copy of updated user's price list.


File "main_1.py" - first working version of the program.
In "main.py" error handling in the supplier's price list has been improved and the speed of the program has been increased 6 (!) times due to the use of generators instead of for loops.
