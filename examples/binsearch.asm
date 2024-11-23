// arr = ...
// def binsearch(low, high, val)
//      if high < low:
//          return -1
//      mid = (low + high) // 2
//      if arr[mid] == val:
//          return mid
//      if arr[mid] < val:
//          return binsearch(mid+1, high, val)
//      else:
//          return binsearch(low, mid-1, val)
.data
// A contains 50 items
A:  1, 4, 4, 5, 7, 8, 11, 14, 15, 18,
    18, 20, 20, 22, 25, 27, 27, 36, 38,
    40, 40, 41, 41, 42, 47, 47, 49, 56,
    57, 58, 59, 60, 67, 70, 74, 75, 77,
    77, 77, 78, 81, 82, 83, 85, 88, 88,
    90, 95, 99, 100;


.text
binsearch:
// assume arr's start is loaded into r29
// r0, r1, r2 = low, high, val
// result in r30
sub r5, r5, r5;
addi r5, r5, 1;  // set r5 = 1
slt r3, r1, r0;  // r3 = high < low
beq r3, r5, failure;

// now calculate mid
add r3, r0, r1;
srl r3, r3, 1;  // r3 = (low+high) >> 1
// r4 = arr[mid]
add r4, r3, r29;
lw r4, r4, 0;
beq r4, r2, success;

// otherwise, recursive case
// store current ra
// swap r0, r31 to put ra into r0
add r0, r0, r31;
sub r31, r0, r31;
sub r0, r0, r31;
push;
// swap back
add r0, r0, r31;
sub r31, r0, r31;
sub r0, r0, r31;
// r4 = arr[mid] < val
slt r4, r4, r2;
bne r4, r5, gt;
// arr[mid] < val
addi r0, r3, 1;  // low = mid + 1
jal binsearch;
jmp return;
gt:
addi r1, r3, -1;  // high = mid - 1
jal binsearch;
jmp return;

failure:
sub r30, r30, r30;
addi r30, r30, -1;
jr r31;  // return -1
success:
sub r30, r30, r30;
add r30, r30, r3;
jr r31;
return:
// result is in r30
// so simply restore ra and return
pop;
jr r0;


main:
lui r29, 0x100;
ori r29, r29, 0x8000;

// low = 0, high = 50, val = 5
addi r0, r0, 0;
addi r1, r1, 50;
addi r2, r2, 5;
jal binsearch;

// save output
lui r29, 0x100;
sw r30, r29, 0;