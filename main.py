def create_memory():
    # Creates a list of one hundred "000" to represent the memory of the computer.
    return ["000" for _ in range(100)]


def index_to_memory_address(index):
    if len(str(index)) == 1:
        return "0" + str(index)

    else:
        return str(index)


def convert_source(instructions):
    # From a set of instructions seperated by newlines, it will convert it into a more consise version which does not use named keys.
    translation_table = {}

    instructions = instructions.split("\n")
    new_instructions = []

    for i, instruction in enumerate(instructions):
        instruction = instruction.split(" ")

        if len(instruction) == 1:
            # Just one instruction by itself. This needs to become the memory address associated with the instruction followed by the instruction again.
            # <INSTRUCTION> => <MEMORY ADDRESS> <INSTRUCTION>
            new_instructions.append(
                index_to_memory_address(i) + " " + instruction[0])

        elif len(instruction) == 2:
            # There are two possibilities in this case:
            # 1. <INSTRUCTION> <ADDRESS> => <MEMORY ADDRESS> <INSTRUCTION> <NUMERICAL ADDRESS>, or
            # 2. <KEY> <INSTRUCTION> => <MEMORY ADDRESS> <INSTRUCTION>
            # We can find out if this is true by seeing if the first item has the name of an instruction:

            if instruction[0] in ["LDA", "STA", "ADD", "SUB", "INP", "OUT", "HLT", "BRZ", "BRP", "BRA", "DAT"]:
                # It's an instruction name followed by an address. (Case 1)
                new_instructions.append(index_to_memory_address(
                    i) + " " + instruction[0] + " " + instruction[1])

            else:
                # It's a key name followed by an instruction. We need to add a key to the translation table with the name of the key. (Case 2)
                # What's more, if it is DAT we need to add a value of '00' on the end.

                translation_table[instruction[0]] = index_to_memory_address(i)

                if instruction[1] == "DAT":
                    new_instructions.append(
                        index_to_memory_address(i) + " " + instruction[1] + " 00")

                else:
                    new_instructions.append(
                        index_to_memory_address(i) + " " + instruction[1])

        elif len(instruction) == 3:
            # There is only one case for this:
            # <KEY> <INSTRUCTION> <ADDRESS> => <MEMORY ADDRESS> <INSTRUCTION> <NUMERICAL ADDRESS>
            # Also, if the instruction is 'DAT' we need to remove any extra zeroes for the data.

            if instruction[1] == "DAT":
                if instruction[2][0] == "0" and len(instruction[2]) == 3:
                    instruction[2] = instruction[2][1:]

            translation_table[instruction[0]] = index_to_memory_address(i)
            new_instructions.append(index_to_memory_address(
                i) + " " + instruction[1] + " " + instruction[2])

    # Here we remove any of the named memory locations or 'keys'.
    for i, instruction in enumerate(new_instructions):
        instruction = instruction.split(" ")

        for key in list(translation_table.keys()):
            if len(instruction) == 3:
                if instruction[2] == key:
                    instruction[2] = translation_table[key]

            new_instructions[i] = " ".join(instruction)

    return new_instructions


def create_program_memory(source):
    # Takes in a list of instructions seperated by newlines and converts them into program memory.
    memory = create_memory()

    for i, instruction in enumerate(source):
        instruction = instruction.split(" ")

        if len(instruction) == 2:
            # No address argument.
            # These instructions are: HLT (000), INP (901), OUT (902) and DAT which is special.
            command = instruction[1]

            if command == "HLT":
                memory[i] = "000"

            elif command == "INP":
                memory[i] = "901"

            elif command == "OUT":
                memory[i] = "902"

            elif command == "DAT":
                memory[i] = "000"

        elif len(instruction) == 3:
            # There's an address argument/data command with initial value.
            # These instructions are: ADD (1xx), SUB (2xx), STA (3xx), LDA (5xx), BRA (6xx), BRZ (7xx), BRP (8xx) and DAT which is again special.
            command = instruction[1]

            if command == "DAT":
                memory[i] = "0" + instruction[2]

            else:
                address = instruction[2]

                if command == "ADD":
                    memory[i] = "1" + address

                elif command == "SUB":
                    memory[i] = "2" + address

                elif command == "STA":
                    memory[i] = "3" + address

                elif command == "LDA":
                    memory[i] = "5" + address

                elif command == "BRA":
                    memory[i] = "6" + address

                elif command == "BRZ":
                    memory[i] = "7" + address

                elif command == "BRP":
                    memory[i] = "8" + address

    return memory


def run_program(memory):
    # Takes in a program in the format of memory and will run through it.

    program_counter = 0
    accumulator = 0

    instruction_register = ""
    address_register = ""

    output = []

    while instruction_register != "0":
        current_code = memory[program_counter]

        program_counter += 1

        instruction_register = current_code[0]
        address_register = current_code[1:]

        if instruction_register == "0":
            # HLT - Stop the program.
            break

        elif instruction_register == "1":
            # ADD <X> - Add the contents of the address <X> to the accumulator.
            accumulator += int(memory[int(address_register)])

        elif instruction_register == "2":
            # SUB <X> - Subtract the contents of the address <X> from the accumulator.
            accumulator -= int(memory[int(address_register)])

        elif instruction_register == "3":
            # STA <X> - Set the contents of memory at address <X> to the value of the accumulator.
            memory[int(address_register)] = accumulator

        elif instruction_register == "5":
            # LDA <X> - Load whatever is in address <X> to the accumulator.
            accumulator = int(memory[int(address_register)])

        elif instruction_register == "6":
            # BRA <X> - Set the value of the program counter to whatever the contents of address <X> is.
            program_counter = int(address_register)

        elif instruction_register == "7":
            # BRZ <X> - If the value of the accumulator is 0, then set the program counter to the value of memory at address <X>.
            if accumulator == 0:
                program_counter = int(address_register)

        elif instruction_register == "8":
            # BRP <X>  - If the value of the accumulator is equal to or above 0, then set the program counter to the value of memory at address <X>.
            if accumulator >= 0:
                program_counter = int(address_register)

        elif instruction_register == "9":
            # INP/OUT - Either get user input or push whatever is in the accumulator to the output box.
            if address_register == "01":
                accumulator = int(input("The program is expecting input >>> "))

            elif address_register == "02":
                output.append(str(accumulator))

    return output


program = """INP
STA VALUE
LDA ONE
STA MULT
OUTER LDA ZERO
STA SUM
STA TIMES
INNER LDA SUM
ADD VALUE
STA SUM
LDA TIMES
ADD ONE
STA TIMES
SUB MULT
BRZ NEXT
BRA INNER
NEXT LDA SUM
OUT
LDA MULT
ADD ONE
STA MULT
SUB VALUE
BRZ OUTER
BRP DONE
BRA OUTER
DONE HLT
VALUE DAT 0
MULT DAT 0
SUM DAT
TIMES DAT
COUNT DAT
ZERO DAT 000
ONE DAT 001"""

print(run_program(create_program_memory(convert_source(program))))
