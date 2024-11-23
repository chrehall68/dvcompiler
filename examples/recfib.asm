/**
Recursive Fibonacci
def f(n: int):
   if n <= 0:
       return 0
   if n == 1:
       return 1
   return f(n-2)+f(n-1)
*/

.data
A: 10, 20, 30;

.text
// n is a parameter in r1
// return in r0
fib: 
// r3 = 1
sub r3, r3, r3;
addi r3, r3, 1;

slti r2, r1, 1;
beq r2, r3, ret0;
slti r2, r1, 2;  // if it's a 1
beq r2, r3, ret1;
// recursive case
// first, store ra
sub r0, r0, r0;
add r0, r0, r31;
push;
// then store n
sub r0, r0, r0;
add r0, r0, r1;
push;

// call f(n-2)
addi r1, r0, -2;
jal fib;

// store ret value
addi r1, r0, 0;  // store ret value here first
pop;  // retrieve original n
// swap 
add r0, r0, r1;
sub r1, r0, r1;
sub r0, r0, r1;
push;  // store ret value

// call f(n-1)
addi r1, r1, -1;
jal fib;

// put ret value into r1
addi r1, r0, 0;
pop;  // get ret value of f(n-2)
add r0, r0, r1;  // calculate final return value
addi r31, r0, 0;  // put it in r31 temporarily
pop;  // get ra
// swap
add r0, r0, r31;
sub r31, r0, r31;
sub r0, r0, r31;

// return
jr r31;

ret1:
sub r0, r0, r0;
addi r0, r0, 1;
jr r31;
ret0:
sub r0, r0, r0;
jr r31;  // jump to return address

main:
la r1, A;
lw r1, r1, 0;
jal fib;  // fib(10)
lui r1, 0x100;
sw r0, r1, 0x0000;