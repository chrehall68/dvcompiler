import assembler


class TestTranslator:

    def test_add(self):
        assert assembler.encode_add("r3", "r2", "r1") == "00411820"

    def test_sub(self):
        assert assembler.encode_sub("r7", "r5", "r6") == "00A63822"

    def test_mul(self):
        assert assembler.encode_mul("r8", "r7", "r4") == "00E4402C"

    def test_and(self):
        assert assembler.encode_and("r8", "r7", "r4") == "00E44024"

    def test_or(self):
        assert assembler.encode_or("r8", "r7", "r4") == "00E44025"

    def test_nor(self):
        assert assembler.encode_nor("r8", "r7", "r4") == "00E44027"

    def test_slt(self):
        assert assembler.encode_slt("r8", "r7", "r4") == "00E4402A"

    def test_sll(self):
        assert assembler.encode_sll("r2", "r2", "12") == "00401301"

    def test_srl(self):
        assert assembler.encode_srl("r2", "r2", "12") == "00401302"

    def test_jr(self):
        assert assembler.encode_jr("r13") == "01A00008"

    def test_addi(self):
        assert assembler.encode_addi("r1", "r1", "10") == "2021000A"
        assert assembler.encode_addi("r2", "r2", "4104") == "20421008"
        assert assembler.encode_addi("r0", "r6", "0") == "20C00000"
        assert assembler.encode_addi("r3", "r3", "1") == "20630001"
        assert assembler.encode_addi("r0", "r5", "0") == "20A00000"
        assert assembler.encode_addi("r2", "r2", "1") == "20420001"
        assert assembler.encode_addi("r1", "r1", "-1") == "2021FFFF"

    def test_muli(self):
        assert assembler.encode_muli("r2", "r3", "-1") == "7462FFFF"

    def test_andi(self):
        assert assembler.encode_andi("r2", "r3", "-1") == "3062FFFF"

    def test_ori(self):
        assert assembler.encode_ori("r2", "r3", "-1") == "3462FFFF"

    def test_lui(self):
        assert assembler.encode_lui("r4", "32768") == "3C848000"
        assert assembler.encode_lui("r3", "256") == "3C630100"
        assert assembler.encode_lui("r0", "256") == "3C000100"

    def test_slti(self):
        assert assembler.encode_slti("r2", "r3", "256") == "28620100"

    def test_beq(self):
        assert assembler.encode_beq("r1", "r2", "7") == "10410007"

    def test_bne(self):
        assert assembler.encode_bne("r8", "r9", "3") == "15280003"
        assert assembler.encode_bne("r1", "r9", "-13") == "1521FFF3"

    def test_lw(self):
        assert assembler.encode_lw("r5", "r2", "0") == "8C450000"
        assert assembler.encode_lw("r6", "r3", "0") == "8C660000"

    def test_sw(self):
        assert assembler.encode_sw("r2", "r0", "0") == "AC020000"
        assert assembler.encode_sw("r1", "r0", "0") == "AC010000"

    def test_jmp(self):
        assert assembler.encode_jmp("4111") == "0800100F"

    def test_jal(self):
        assert assembler.encode_jal("4111") == "0C00100F"
        assert assembler.encode_jal("31") == "0C00001F"

    def test_push(self):
        assert assembler.encode_push() == "6C000000"

    def test_pop(self):
        assert assembler.encode_pop() == "70000000"

    def test_encode(self):
        assert assembler.encode("pop") == "70000000"
        assert assembler.encode("jal", "31") == "0C00001F"
        assert assembler.encode("andi", "r2", "r3", "-1") == "3062FFFF"
