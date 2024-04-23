import re
import os

import itertools

Variable_list = []
Overflow_list = []
Multi_Driven_list = []
Parallel_cases_list = []
Cases_list = []
Always_list = []
stack = []

def Find_External_Params(keyword, type):
    case_opening_sBracet = None
    case_closing_sBracet = None
    var_has_width_flag = 0
    case_keyword = line.find(keyword + " ")
    if case_keyword != -1:
        case_type = line.find(type + " ", case_keyword + len(keyword))
        if(case_type != -1):
            if type == "reg" or type == "wire":
                case_opening_sBracet = line.find("[")
                case_closing_sBracet = line.find("]")
                if case_opening_sBracet != -1 and case_closing_sBracet != -1:
                    var_has_width_flag = 1 
                    width_string = line[case_opening_sBracet+1:case_closing_sBracet]
                    width_list = width_string.split(":")
                    width = abs(int(width_list[0]) - int(width_list[1])) + 1
                else:
                    width = 1
            if not var_has_width_flag:
                temp_list = line[case_type + len(type) + 1:].split(",")
            else:
                temp = case_closing_sBracet - case_opening_sBracet  
                temp_list = line[case_type + len(type) + 2 + temp:].split(",")
            if(temp_list[-1] == "" or temp_list[-1] == " "or temp_list[-1] == "\n"):
                temp_list.pop()
            for temp_var in temp_list:
                temp_var = temp_var.strip()
                Variable_list.append(Variable(type, temp_var, index + 1, width, keyword))
        elif case_type == -1 and type == "wire":
            case_reg = line.find("reg ")
            if case_reg == -1:
                temp_list = line[case_keyword + len(keyword) + 1:].split(",")
                if(temp_list[-1] == "" or temp_list[-1] == " " or temp_list[-1] == "\n"):
                    temp_list.pop()
                for temp_var in temp_list:
                    temp_var = temp_var.strip()
                    Variable_list.append(Variable(type, temp_var, index + 1, 1, keyword))

def find_Internal_Variables(keyword, line):
    case_opening_sBracet = None
    case_closing_sBracet = None
    var_has_width_flag = 0
    case_keyword = line.find(keyword + " ")
    if case_keyword != -1:
        if keyword == "localparam" or keyword == "reg" or keyword == "wire":
            case_opening_sBracet = line.find("[")
            case_closing_sBracet = line.find("]")
            if case_opening_sBracet != -1 and case_closing_sBracet != -1:
                var_has_width_flag = 1 
                width_string = line[case_opening_sBracet+1:case_closing_sBracet]
                width_list = width_string.split(":")
                width = abs(int(width_list[0]) - int(width_list[1])) + 1
            else:
                width = 1

        if not var_has_width_flag:
                temp_list = line[case_keyword + len(keyword) + 1:].split(",")
        else:
            temp = case_closing_sBracet - case_opening_sBracet  
            temp_list = line[case_keyword + len(keyword) + 2 + temp:].split(",")
        if(temp_list[-1] == "" or temp_list[-1] == " "):
                temp_list.pop()
        for curr_index, temp_var in enumerate(temp_list):
            temp_var = temp_var.strip()
            Variable_list.append(Variable(keyword, temp_var, index + curr_index + 1, width, "localparam"))

def find_integers(line):
    case_integer = line.find("integer" + " ")
    if case_integer != -1:
        temp_list = line[case_integer + len("integer") + 1:].split(",")    
        if(temp_list[-1] == "" or temp_list[-1] == " "or temp_list[-1] == "\n"):
                temp_list.pop()
        for temp_var in temp_list:
            temp_var = temp_var.strip()
            Variable_list.append(Variable("integer", temp_var, index + 1, 32, "localparam"))

def find_assignment(line, index):
    case_assignment = line.find(" = ")
    if case_assignment != -1:
        if not re.search("(input|output|if|else if|while|for)", line):
            lhs = line.split("=")[0].strip()
            lhs = lhs.replace("reg", "")
            lhs = lhs.replace("wire", "")
            lhs = lhs.replace("integer", "")
            lhs = lhs.replace("localparam", "")
            lhs_match = re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", lhs)
            lhs = lhs_match[0].strip()
            for obj in Variable_list:
                if obj.getName() == lhs:
                    temp_lhs = obj
                    break
            rhs = line.split("=")[1].strip()
            match = re.findall("[+-]", rhs)
            if match:
                match_width = re.findall("\d+'", rhs)
                for matched_item in match_width:
                    rhs = rhs.replace(matched_item, "")
                temp_operand_string = ""
                temp_operand_list = []
                temp_opration_list = []
                sum = 0
                for char in rhs:
                    if char.isdigit():
                        temp_operand_string += char
                    elif char == "+" or char == "-":
                        temp_operand_list.append(temp_operand_string)
                        temp_opration_list.append(char)
                        temp_operand_string = ""
                if temp_operand_string != "":
                    temp_operand_list.append(temp_operand_string)
                    temp_operand_string = ""
                for operation in temp_opration_list:
                    if operation == "+":
                        temp_result = int(temp_operand_list[0], 2) + int(temp_operand_list[1], 2)
                        del temp_operand_list[0]
                        del temp_operand_list[0]
                        sum += temp_result
                        temp_operand_list.insert(0, temp_result)
                    elif operation == "-":
                        temp_result = int(temp_operand_list[0], 2) - int(temp_operand_list[1], 2)
                        del temp_operand_list[0]
                        del temp_operand_list[0]
                        sum += temp_result
                        temp_operand_list.insert(0, temp_result)
                rhs = str(len(bin(sum)[2:])) + "'" + bin(sum)[1:]
            if not re.search("\d+'", line):
                for obj in Variable_list:
                    if obj.getName() == rhs:
                        temp_lhs.checkArithmeticOverflow(obj.getWidth(), index + 1)
                        break
            elif re.search("\d+'", line):
                temp_lhs.checkArithmeticOverflow(int(rhs[0]), index + 1)
            elif rhs.isnumeric():
                temp_lhs.checkArithmeticOverflow(int(rhs), index + 1)
    case_non_blocking_assignment = line.find(" <= ")
    if case_non_blocking_assignment != -1:
        if not re.search("(input|output|if|else if|while|for)", line):
            lhs = line.split("<=")[0].strip()
            lhs = lhs.replace("reg", "")
            lhs = lhs.replace("wire", "")
            lhs = lhs.replace("integer", "")
            lhs = lhs.replace("localparam", "")
            lhs_match = re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", lhs)
            lhs = lhs_match[0].strip()
            for obj in Variable_list:
                if obj.getName() == lhs:
                    temp_lhs = obj
            rhs = line.split("<=")[1].strip()
            if not re.search("\d+'", line):
                for obj in Variable_list:
                    if obj.getName() == rhs:
                        temp_lhs.checkArithmeticOverflow(obj.getWidth(), index + 1)
            elif re.search("\d+'", line):
                temp_lhs.checkArithmeticOverflow(int(rhs[0]), index + 1)
            elif rhs.isnumeric():
                temp_lhs.checkArithmeticOverflow(int(rhs), index + 1)


def find_case(line, case_type, case_list, default_boolean, case_condition):
    case_case = line.find("case")
    case_colon = line.find(":")
    if case_case != -1:
        casex = line.find("casex")
        casez = line.find("casez")
        if casex != -1:
            case_type = "casex"
        elif casez != -1:
            case_type = "casez"
        else:
            case_type = "case"
        case_opening_bracet = line.find("(")
        case_closing_bracet = line.find(")")
        case_condition = line[case_opening_bracet + 1: case_closing_bracet]
    if case_colon != -1:
        temp_case = line.split(":")[0].strip()
        case_list.extend(temp_case.split(","))
        if temp_case == "default":
            default_boolean = 1
    return (case_type, case_list, default_boolean, case_condition)

def find_always(line, index, always_var_list, always_lines_list):
    case_assignment = line.find(" = ")
    if case_assignment != -1:
        lhs = line.split("=")[0].strip()
        if not lhs in always_var_list:
            always_var_list.append(lhs)
            always_lines_list.append(index + 1)
    case_blocking = line.find(" <= ")
    if case_blocking != -1:
        lhs = line.split("<=")[0].strip()
        if not lhs in always_var_list:
            always_var_list.append(lhs)
            always_lines_list.append(index + 1)
    return (always_var_list, always_lines_list)

def find_parallel_case():
    for obj in Cases_list:
        my_cases = obj.cases
        if "default" in my_cases:
            my_cases.remove("default")
        
        for i in range(len(my_cases)):
            for j in range(i+1, len(my_cases)):
                if re.search("\d+'", my_cases[i][:2]):
                    if re.search("\d+'", my_cases[j][:2]):
                        if int(my_cases[i][3:], 2) == int(my_cases[j][3:], 2):
                            Parallel_cases_list.append(obj.line_number)
                    elif not re.search("\d+'", my_cases[j][:2]):
                        my_rhs_value = 0
                        for Var_obj in Variable_list:
                            if my_cases[j] == Var_obj.getName():
                                my_rhs_value = Var_obj.init_value
                                break
                        if int(my_cases[i][3:], 2) == int(my_rhs_value[3:], 2):
                            Parallel_cases_list.append(obj.line_number)
                elif not re.search("\d+'", my_cases[i][:2]):
                    my_lhs_value = 0
                    for Var_obj in Variable_list:
                        if my_cases[i] == Var_obj.getName():
                            my_lhs_value = Var_obj.init_value
                            break
                    if re.search("\d+'", my_cases[j][:2]):
                        if int(my_lhs_value[3:], 2) == int(my_cases[j][3:], 2):
                            Parallel_cases_list.append(obj.line_number)
                    elif not re.search("\d+'", my_cases[j][:2]):
                        my_rhs_value = 0
                        for Var_obj in Variable_list:
                            if my_cases[j] == Var_obj.getName():
                                my_rhs_value = Var_obj.init_value
                                break
                        if int(my_lhs_value[3:], 2) == int(my_rhs_value[3:], 2):
                            Parallel_cases_list.append(obj.line_number)
class Variable:
    def __init__(self, type, name, line, width, io_local, init = 1):
        self.type = type
        self.name = name
        self.line = line
        self.width = width
        self.io_local = io_local
        self.init = init
        self.init_value = None
        self.isInit()

    def isInit(self):
        if self.name.find("=") != -1:
            self.init = 1
            self.set_init_value()
            if self.init_value.isalpha():
                for obj in Variable_list:
                    if obj.getName() == self.init_value:
                        self.checkArithmeticOverflow(obj.getWidth(), self.line)
            
            elif re.search(r"\d+'", self.init_value[0:2]):
                self.checkArithmeticOverflow(int(self.init_value[0]), self.line)
        else:
            if self.io_local != "input" and self.io_local != "output": 
                self.init = 0
            
    
    def set_init_value(self):
        if self.init:
            self.init_value = self.name.split("=")[1].strip()
            self.name = self.name.split("=")[0].strip()

    def checkArithmeticOverflow(self, value, line):
        if self.type == "integer":
            if value > 2**16 -1 or value < -2**16:
                Overflow_list.append((line, self.name))
        else:
            if value > self.width:
                Overflow_list.append((line, self.name))
                return 1

    def getLine(self):
        return self.line
    def getWidth(self):
        return self.width
    def getName(self):
        return self.name
    def getOverflow(self):
        return self.overflow

class Case:
    def __init__(self, line_number,case_type, cases, default, condition, NCF):
        self.line_number = line_number
        self.case_type = case_type
        self.cases = cases
        self.default = default
        self.condition = condition
        self.num_of_cases_found = NCF
        self.num_of_cases_expexted = 0
        self.has_unreachable_state = 0
        self.condition_width = 0
        self.not_full = 0
        self.check_full()
        self.check_unreachable_state()
    def check_full(self):
        for obj in Variable_list:
            if obj.getName() == self.condition:
                self.condition_width = obj.getWidth()

        self.num_of_cases_expexted = 2**self.condition_width
        if self.num_of_cases_found < self.num_of_cases_expexted and not self.default:
            self.not_full = 1

    def check_unreachable_state(self):
        for c in self.cases:
            for obj in Variable_list:
                if obj.getName() == c:
                    num_of_bits = re.findall("\d+'", obj.init_value)
                    curr_width = int(num_of_bits[0][:-1])
                    if curr_width > self.condition_width:
                        self.has_unreachable_state = 1
                    break


class Always:
    def __init__(self, variables, VL):
        self.variables = variables
        self.variable_lines = VL

path = input("enter the path to the code\n")
#path = "C:\\Users\\Mohamed Ali\\Downloads\\LOCKER_Moore.v"
with open(path, 'r') as my_code:
    in_case = 0
    in_always = 0
    case_start = 0
    case_list = []
    always_var_list = []
    always_lines_list = []
    case_condition = ""
    default_boolean = 0
    case_type = ""
    my_code = my_code.readlines()
    for index, line in enumerate(my_code):
        temp_list = []
        Find_External_Params("input", "wire")
        Find_External_Params("input", "reg")
        Find_External_Params("output", "wire")
        Find_External_Params("output", "reg")
        if line.find("localparam ") != -1:
            #temp_string = line
            temp_string = ""
            temp_string = temp_string[:-1]
            my_lines = my_code[index:]
            for i in range(len(my_lines)):
                if my_lines[i].find(";") == -1:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                else:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                    break
            temp_string = temp_string[:-1]
            find_Internal_Variables("localparam", temp_string)
        if (line.find("reg ") != -1 and (line.find("input ") == -1 and line.find("output ") == -1)):
            #temp_string = line
            temp_string = ""
            temp_string = temp_string[:-1]
            my_lines = my_code[index:]
            for i in range(len(my_lines)):
                if my_lines[i].find(";") == -1:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                else:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                    break
            temp_string = temp_string[:-1]
            find_Internal_Variables("reg", temp_string)
        if (line.find("wire ") != -1 and (line.find("input ") == -1 and line.find("output ") == -1)):
            #temp_string = line
            temp_string = ""
            temp_string = temp_string[:-1]
            my_lines = my_code[index:]
            for i in range(len(my_lines)):
                if my_lines[i].find(";") == -1:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                else:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                    break
            temp_string = temp_string[:-1]
            find_Internal_Variables("wire", temp_string)
        if line.find("integer ") != -1:
            #temp_string = line
            temp_string = ""
            temp_string = temp_string[:-1]
            my_lines = my_code[index:]
            for i in range(len(my_lines)):
                if my_lines[i].find(";") == -1:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                else:
                    temp_string += my_lines[i]
                    temp_string = temp_string[:-1]
                    break
            temp_string = temp_string[:-1]
            find_integers(temp_string)
        find_assignment(line, index)

        if line.find("case") != -1 and line.find("endcase") == -1:
            in_case = 1
            case_start = index
        if line.find("always") != -1:
            in_always = 1
        if line.find("endcase") != -1:
            in_case = 0
            for index in range(len(case_list)):
                case_list[index] = case_list[index].replace(" ", "")
            Cases_list.append(Case(case_start, case_type,case_list, default_boolean, case_condition, len(case_list)))
            case_start = 0
            case_list = []
            case_condition = ""
            default_boolean = 0
            case_type = ""
        if in_case:
            case_type, case_list, default_boolean, case_condition = find_case(line, case_type, case_list, default_boolean, case_condition)
        if in_always:
            if line.find("begin") != -1:
                stack.append(" ")
            if line.find("end") != -1:
                stack.pop()
                if not len(stack):
                    in_always = 0
                    Always_list.append(Always(always_var_list, always_lines_list))
                    always_var_list = []
                    always_lines_list = []
            always_var_list, always_lines_list = find_always(line, index, always_var_list, always_lines_list)
    
    for i in range(len(Always_list)):
        for j in range(i+1, len(Always_list)):
            for first_index, first_variable in enumerate(Always_list[i].variables):
                for second_index, second_variable in enumerate(Always_list[j].variables):
                    if second_variable == first_variable:
                        Multi_Driven_list.append((second_variable,Always_list[i].variable_lines[first_index]))


find_parallel_case()


Overflow_list = sorted(set(Overflow_list))
Parallel_cases_list = sorted(set(Parallel_cases_list))

with open("Lint_report.txt", "w") as temp_file:
    count = 0
    for overflow in Overflow_list:
        temp_file.write("WARNING: Arithmetic overflow at line: " + str(overflow[0]) + " in variable " + overflow[1] + "\n")
    
    for obj in Variable_list:
        if not obj.init:
            temp_file.write("WARNING: Uninitialized variable " + obj.getName() + " at line " + str(obj.getLine()) + "\n")
            count += 1

    for obj in Cases_list:
        if obj.has_unreachable_state:
            temp_file.write("WARNING: Unreachable state in the case at line " + str(obj.line_number + 1) + "\n")
            count += 1
        if obj.not_full:
            temp_file.write("WARNING: Case starting at line: " + str(obj.line_number + 1) + " is not full\n")
            count += 1
    for mdr in Multi_Driven_list:
        temp_file.write("WARNING: Multi Driven Register/Bus at line: " + str(mdr[1]) + " in variable " + mdr[0] + "\n")

    for npc in Parallel_cases_list:
        temp_file.write("WARNING: Non parallel Case at line: " + str(npc + 1) + "\n")   
    
    if not (len(Overflow_list) or len(Multi_Driven_list) or len(Parallel_cases_list) or count):
        temp_file.write("No violations where found")