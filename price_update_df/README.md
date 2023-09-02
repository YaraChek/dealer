_The program receives 3+ files as input_:
1. goods in the supplier's warehouses;
2. the current supplier's price list;
2. custom price list(s).

_The program does_:
1. indicates which product from the user price list is in the supplier's main warehouse;
2. updates prices, marks goods as "Sale", "Promo" etc., saves a copy of updated user's price list.

--

The program works, but it does not handle errors in the supplier's price list etacilpud htiw SKUs well enough - it does not look for the correct values, but simply draws the user's attention, informs the user of the need to check the problematic items himself.
The issue with starts with zero SKUs which are converted into an integer without a leading zero in the supplier's price list has not been resolved.

The program is presented in 2 versions.
1. 1 action is performed in 3 different functions.
2. In 1 function, 3 actions are performed.

The 2nd option proved to be faster.
