import re

def print_if(value, text):
    if value:
        print(text)

def input_if(value, text=""):
    if value:
        input(text)

    else:
        return False

def create_memory():
    # Creates a list of one hundred "000" to represent the memory of the computer.
    return ["000" for _ in range(100)]


def index_to_memory_address(index):
    if len(str(index)) == 1:
        return "0" + str(index)

    else:
        return str(index)


def clean_instructions(instructions, step_by_step=False):
    print_if(step_by_step, "1. First stage - Cleaning instructions:")
    print_if(step_by_step, instructions)
    print_if(step_by_step, "")

    print_if(step_by_step, "These program instructions need to be cleaned by removing additional whitespace and comments.")

    print_if(step_by_step, "")

    input_if(step_by_step, "(Press <ENTER> to continue) ")

    instructions = instructions.split("\n")

    for i, instruction in enumerate(instructions):
        instruction = re.sub(r"\/\/.+", "", instruction)
        instruction = re.sub(r" {2,}", " ", instruction)
        instruction = re.sub(r"^ ", "", instruction)
        instruction = re.sub(r" $", "", instruction)

        instructions[i] = instruction

    instructions = list(filter(lambda x: x != "\n", instructions))

    print_if(step_by_step, "\n" * 5)

    return "\n".join(instructions)


def convert_source(instructions, step_by_step=False):
    # From a set of instructions seperated by newlines, it will convert it into a more consise version which does not use named keys.

    print_if(step_by_step, "2. Second stage - Converting the source:")
    print_if(step_by_step, instructions)
    print_if(step_by_step, "")

    print_if(step_by_step, "These program may still have labels for loops and data, which is not useful. These need to removed and replace with their addresses.")

    print_if(step_by_step, "")

    input_if(step_by_step, "(Press <ENTER> to continue) ")

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

    print_if(step_by_step, "\n" * 5)

    return new_instructions


def create_program_memory(source, step_by_step=False):
    # Takes in a list of instructions seperated by newlines and converts them into program memory.

    print_if(step_by_step, "3. Third stage - Generating program memory:")
    print_if(step_by_step, source)
    print_if(step_by_step, "")

    print_if(step_by_step, "In this stage we need to convert the new program source into memory.")

    print_if(step_by_step, "")

    input_if(step_by_step, "(Press <ENTER> to continue) ")

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

            elif command == "OTC":
                memory[i] = "922"

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

    print_if(step_by_step, "\nDone. Here is the new program memory:")

    if step_by_step:
        print_memory(memory)

    print_if(step_by_step, "\n" * 5)

    return memory


def run_memory(memory, step_by_step=False):
    # Takes in a program in the format of memory and will run through it.

    print_if(step_by_step, "4. Fourth stage - Execution:")
    
    if step_by_step:
        print_memory(memory)

    print_if(step_by_step,
             "This is the stage where we actually run the commands.")

    print_if(step_by_step, "")

    input_if(step_by_step, "(Press <ENTER> to continue) ")

    program_counter = 0
    accumulator = 0

    instruction_register = ""
    address_register = ""

    output = []

    while instruction_register != "0":
        current_code = memory[program_counter]

        program_counter += 1

        instruction_register = str(current_code)[0]
        address_register = str(current_code)[1:]

        print_if(step_by_step, f"New memory code recieved: {current_code}\nInstruction Register: {instruction_register}\nAddress Register: {instruction_register}\n")

        if instruction_register == "0":
            # HLT - Stop the program.
            print_if(step_by_step, f"Instruction Register {instruction_register} means: HLT\n")
            break

        elif instruction_register == "1":
            # ADD <X> - Add the contents of the address <X> to the accumulator.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: ADD\n")
            accumulator += int(memory[int(address_register)])

        elif instruction_register == "2":
            # SUB <X> - Subtract the contents of the address <X> from the accumulator.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: SUB\n")
            accumulator -= int(memory[int(address_register)])

        elif instruction_register == "3":
            # STA <X> - Set the contents of memory at address <X> to the value of the accumulator.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: STA\n")
            memory[int(address_register)] = accumulator

        elif instruction_register == "5":
            # LDA <X> - Load whatever is in address <X> to the accumulator.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: LDA\n")
            accumulator = int(memory[int(address_register)])

        elif instruction_register == "6":
            # BRA <X> - Set the value of the program counter to whatever the contents of address <X> is.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: BRA\n")
            program_counter = int(address_register)

        elif instruction_register == "7":
            # BRZ <X> - If the value of the accumulator is 0, then set the program counter to the value of memory at address <X>.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: BRZ\n")
            if accumulator == 0:
                program_counter = int(address_register)

        elif instruction_register == "8":
            # BRP <X>  - If the value of the accumulator is equal to or above 0, then set the program counter to the value of memory at address <X>.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: BRP\n")
            if accumulator >= 0:
                program_counter = int(address_register)

        elif instruction_register == "9":
            # INP/OUT - Either get user input or push whatever is in the accumulator to the output box.
            print_if(step_by_step,
                     f"Instruction Register {instruction_register} means: INP/OUT/OTC\n")
            if address_register == "01":
                accumulator = int(input("The program is expecting input >>> "))

            elif address_register == "02":
                output.append(str(accumulator))

            elif address_register == "22":
                output.append(chr(int(accumulator)))

        print_if(step_by_step, "\n" * 2)

    return output


def run_program(program, step_by_step=False):
    # This function combines all the code above to run a set of instructions and return whatever is in the out box.
    return run_memory(create_program_memory(convert_source(clean_instructions(program, step_by_step=step_by_step), step_by_step=step_by_step), step_by_step=step_by_step), step_by_step=step_by_step)


def run_file(path):
    # This will run the instructions at file 'path'.
    return run_program(open(path, "r").read())


def print_memory(memory):
    for i in range(10):
        for j in range(i*10, (i+1)*10):
            print(memory[j], end=" ")

        print("\n")


def command_help():
    print("\nHelp:")
    print("load <program path> => Load the program at the path into the command line interface for execution or inspection.")
    print("run                 => Run the loaded program.")
    print("input               => Take in a set of program instructions from the command line and load them as if it was a program.")
    print("help                => Print this menu")

    print("")

    print("print               => Print the program instructions of the program.")
    print("cleaned             => Print the contents of the program instructions with things like extra whitespace and comments removed.")
    print("source              => Print the compiled program source. This is the cleaned program instructions but with keys removed and the address of each instruction before each command.")
    print("memory              => Print the created memory for the code written. This is with each instruction placed at the correct address and formated as machine code.")
    print("info                => Print info about the Little Man Computer, such as all the different commands.")

    print("")

    print("enable <x>          => Sets option <x> to true. A list of options can be found below:")
    print("  * step - When enabled it will print information about what the program is doing at each step/instruction.")

    print("")

    print("disable <x>        => Disables option <x>")


def main():
    LOADED = ""
    OPTIONS = {
        "step": False
    }

    print("PythonLMC:")
    print("==========")

    print("\nWhat would you like to do? You can `load`, `run` or `input`. You can also perform `help` to see a list of extended options.")

    while True:
        program_input = input(">>> ")
        program_input = program_input.split(" ")

        if len(program_input) == 2:
            if program_input[0] == "load":
                LOADED = open(program_input[1], "r").read()

            elif program_input[0] == "enable":
                OPTIONS[program_input[1]] = True

            elif program_input[0] == "disable":
                OPTIONS[program_input[1]] = False

        elif len(program_input) == 1:
            if program_input[0] == "run":
                output = run_program(LOADED, step_by_step = OPTIONS["step"])

                print("Program Input:")

                print("\n".join(output))

            elif program_input[0] == "input":
                print("Please write/paste the source of your program:")
                LOADED = input("")

            elif program_input[0] == "help":
                command_help()

            elif program_input[0] == "print":
                if LOADED != "":
                    print(LOADED)

                else:
                    print("No program loaded.")

            elif program_input[0] == "cleaned":
                if LOADED != "":
                    print(clean_instructions(LOADED))

                else:
                    print("No program loaded.")

            elif program_input[0] == "source":
                if LOADED != "":
                    print(convert_source(clean_instructions(LOADED)))

                else:
                    print("No program loaded.")

            elif program_input[0] == "memory":
                if LOADED != "":
                    memory = create_program_memory(
                        convert_source(clean_instructions(LOADED)))

                    print_memory(memory)

                else:
                    print("No program loaded.")

            elif program_input[0] == "exit":
                quit()

        print("\n" * 5)


main()
