_The program receives 3+ files as input_:
1. goods in the supplier's warehouses;
2. the current supplier's price list;
2. custom price list(s).

_The program does_:
1. indicates which product from the user price list is in the supplier's main warehouse;
2. updates prices, marks goods as "Sale", "Promo" etc., saves a copy of updated user's price list.

--
The program works, but it does not handle errors in the supplier's price list duplicate with SKUs well enough - it does not look for the correct values, but simply draws the user's attention, informs the user of the need to check the problematic items himself.
In the supplier's price list, some articles start from zero and the program cannot always process them correctly. Such articles are marked in the output file.
The last two problems are not critical, since problematic articles have not yet been encountered in the user's files. Their marking is provided in the output file. In the supplier's files, the proportion of problematic articles is less than 1% and they refer only to the "spare parts" section.

There is an idea in the first version of the program to rewrite the last 2 functions. Apply not cycles, but generators. It is expected to increase the speed of work by 4 times.

The program is presented in 2 versions.
1. 1 action is performed in 3 different functions.
2. In 1 function, 3 actions are performed.

The 2nd option proved to be faster.
