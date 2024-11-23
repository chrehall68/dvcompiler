.text
main:
		addi r0, r0, 0x1008;
		sll r0, r0, 0xC;
		addi r2, r2, 0x9;
LOOP: 	beq r1, r2, END;
		lw r3, r0, 0x0;
		lw r4, r0, 0x1;
		add r5, r3, r4;
		sw r5, r0, 0x0;
		addi r0, r0, 0x1;
		addi r1, r1, 0x1;
		jmp LOOP;
END: 	sw r5, r0, 0x0;