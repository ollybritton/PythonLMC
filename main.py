import re


def create_memory():
    # Creates a list of one hundred "000" to represent the memory of the computer.
    return ["000" for _ in range(100)]


def index_to_memory_address(index):
    if len(str(index)) == 1:
        return "0" + str(index)

    else:
        return str(index)


def clean_instructions(instructions):
    instructions = instructions.split("\n")

    for i, instruction in enumerate(instructions):
        instruction = re.sub(r"\/\/.+", "", instruction)
        instruction = re.sub(r" {2,}", " ", instruction)
        instruction = re.sub(r"^ ", "", instruction)
        instruction = re.sub(r" $", "", instruction)

        instructions[i] = instruction

    instructions = list(filter(lambda x: x != "\n", instructions))

    return "\n".join(instructions)


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


def run_memory(memory):
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


def run_program(program):
    # This function combines all the code above to run a set of instructions and return whatever is in the out box.
    return run_memory(create_program_memory(convert_source(clean_instructions(program))))


def run_file(path):
    # This will run the instructions at file 'path'.
    return run_program(open(path, "r").read())


def main():
    LOADED = ""

    print("PythonLMC:")
    print("==========")

    print("\nWhat would you like to do? You can `load`, `run` or `take`. You can also perform `help` to see a list of extended options.")

    while True:
        # load <X> - Load file <X> into the code.
        # run - Run the loaded file.
        # take - Brings up a prompt asking for input which is then loaded into the program.
        # help - Shows help.

        # print - Print the loaded instructions.
        # cleaned - Print the contents of the cleaned program.
        # source - Print the converted source.
        # memory - Print the memory at the beginning of the program.

        program_input = input(">>> ")
        program_input = program_input.split(" ")

        if len(program_input) == 2:
            if program_input[0] == "load":
                LOADED = open(program_input[1], "r").read()

        elif len(program_input) == 1:
            if program_input[0] == "run":
                output = run_program(LOADED)

                print("")

                print("\n".join(output))

            elif program_input[0] == "take":
                print("Please write/paste the source of your program:")
                LOADED = input("")

            elif program_input[0] == "help":
                print("""# load <X> - Load file <X> into the code.
        # run - Run the loaded file.
        # take - Brings up a prompt asking for input which is then loaded into the program.
        # help - Shows help.

        # cleaned - Print the contents of the cleaned program.
        # source - Print the converted source.
        # memory - Print the memory at the beginning of the program.""")

            elif program_input[0] == "print":
                print(LOADED)

            elif program_input[0] == "cleaned":
                print(clean_instructions(LOADED))

            elif program_input[0] == "source":
                print(convert_source(clean_instructions(LOADED)))

            elif program_input[0] == "memory":
                memory = create_program_memory(
                    convert_source(clean_instructions(LOADED)))

                for i in range(10):
                    for j in range(i*10, (i+1)*10):
                        print(memory[j], end=" ")

                    print("\n")

            elif program_input[0] == "exit":
                quit()


main()
