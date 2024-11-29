import re

class CPPParser:
    def __init__(self):
        self.type_mappings = {
            'void': 'vf',
            'char': 'cf',
            'int': 'if',
            'long': 'lf',
            'float': 'pf',
            'string': 'sf',
            'pointer': 'pf',
        }
        self.global_type_counters = {
            'int': 1,
            'float': 1,
            'string': 1,
            'char': 1,
            'long': 1,
            'pointer': 1
        }
        self.type_counters = {t: 1 for t in self.type_mappings}
        self.function_counter = 1
        self.function_details = {}
        self.function_var_counters = {}

    def separate_code(self, cpp_code):
        main_pattern = r'int\s+main\(\)\s*{.*?}'
        headers_pattern = r'^\s*#include\s*<.*?>\s*$|^\s*using\s+namespace\s+\w+;\s*$'
        headers = "\n".join(re.findall(headers_pattern, cpp_code, re.MULTILINE))
        main_code_match = re.search(main_pattern, cpp_code, re.DOTALL)
        if main_code_match:
            in_main = main_code_match.group(0)
            rest_of_code = cpp_code.replace(in_main, '').strip()
        else:
            in_main = ""
            rest_of_code = cpp_code.strip()
        out_main = "\n".join([line for line in rest_of_code.splitlines() if line.strip() and not re.match(headers_pattern, line)])
        headers_code = ""
        for i in headers.splitlines():
            headers_code += i.strip() + "\n"
        return headers_code.strip(), in_main, out_main

    def get_new_name(self, var_type, is_global=False, function_name=None):
        if is_global:
            # Generate name for global variables
            return f"g{self.type_mappings.get(var_type, 'uf')[0]}{self.global_type_counters[var_type]}"
        else:
            if function_name:
                # Generate name for local variables within a function
                return f"l{self.type_mappings.get(var_type, 'uf')[0]}{self.function_var_counters[function_name][var_type]}"
            else:
                # For other cases (shouldn't be hit with current logic)
                return f"{self.type_mappings.get(var_type, 'uf')[0]}{self.type_counters[var_type]}"

    def rename_cpp_code(self, cpp_code):
        def rename_line(line, function_name=None):
            # Match and rename global variables
            if re.match(r"^\s*(int|char|float|long|string)\s+\w+\s*(;|=)", line) and function_name is None:
                return self.rename_global_variable(line)

            # Skip renaming for main function
            if re.match(r"\s*int\s+main\s*\(", line):
                return line

            # Match function declaration
            function_declaration_match = re.match(r"\s*(\w+)\s+(\w+)\s*\(", line)
            if function_declaration_match:
                return_type = function_declaration_match.group(1)
                function_name = function_declaration_match.group(2)
                self.record_function_details(function_name, return_type, line)
                self.function_var_counters[function_name] = {t: 1 for t in self.type_mappings}
                updated_function_name = f"{self.type_mappings.get(return_type, 'uf')}{self.function_counter}"
                updated_line = re.sub(rf"\b{function_name}\b", updated_function_name, line)
                return updated_line

            # Rename local variables within functions
            for var_type in self.type_mappings:
                var_declaration_pattern = rf"\b{var_type}\s+(\w+)\s*(;|=)"
                if re.search(var_declaration_pattern, line):
                    def replace_local_variable(match):
                        var_name = match.group(1)
                        new_name = self.get_new_name(var_type, is_global=False, function_name=function_name)
                        self.function_var_counters[function_name][var_type] += 1
                        return line.replace(var_name, new_name)
                    line = re.sub(var_declaration_pattern, replace_local_variable, line)

            # Rename function calls (except `main`)
            line = re.sub(r"\b(\w+)\s*\(", lambda m: f"{m.group(1)}{self.function_counter}(" if m.group(1) != 'main' else m.group(1) + "(", line)
            return line

        # Process each line of the code
        lines = cpp_code.splitlines()
        new_lines = []
        function_name = None
        for line in lines:
            # Detect function name for current context
            if re.match(r"\s*(\w+)\s+(\w+)\s*\(", line):
                function_name = re.match(r"\s*(\w+)\s+(\w+)\s*\(", line).group(2)
            new_line = rename_line(line, function_name=function_name)
            new_lines.append(new_line)
            # Increment function counter for new functions
            if re.match(r"\s*\w+\s+\w+\s*\(", new_line) and not re.match(r"\s*int\s+main\s*\(", new_line):
                self.function_counter += 1
        return "\n".join(new_lines)

    def rename_global_variable(self, line):
        # Match global variable declarations
        global_var_match = re.match(r"^\s*(int|char|float|long|string)\s+(\w+)\s*(;|=)", line)
        if global_var_match:
            var_type = global_var_match.group(1)
            var_name = global_var_match.group(2)
            updated_var_name = self.get_new_name(var_type, is_global=True)
            return re.sub(rf"\b{var_name}\b", updated_var_name, line)
        return line


    def record_function_details(self, function_name, return_type, function_code):
        param_pattern = r"\((.*?)\)"
        params_match = re.search(param_pattern, function_code)
        params = []
        if params_match:
            param_string = params_match.group(1).strip()
            params = [param.split()[0] for param in param_string.split(',')] if param_string else []
        self.function_details[function_name] = {
            'updated_name': f"{self.type_mappings.get(return_type, 'uf')}{self.function_counter}",
            'return_type': return_type,
            'parameters': params,
            'original_code': function_code
        }

    def update_main_code(self, main_code):
        updated_main_code = main_code
        for func_name, details in self.function_details.items():
            updated_main_code = re.sub(rf"\b{func_name}\b", details['updated_name'], updated_main_code)
        return updated_main_code

    def get_function_details(self):
        return self.function_details

cpp_code = """
#include <iostream>
using namespace std;

void myNewerFunction(int x, string y) {
  int a = 99;
  string tx=81;
  
    cout << x << " " << y << endl;
}
"""

parser = CPPParser()
headers, main_code, rest_code = parser.separate_code(cpp_code)
print("Headers:\n", headers)
print("\n\n\n")
print("Original Main Code:\n", main_code)
print("\n\n\n")
print("Rest of the Code:\n", rest_code)
print("\n\n\n")
updated_main_code = parser.update_main_code(main_code)
print("Updated Main Function:\n", updated_main_code)
print("\n\n\n")
renamed_code = parser.rename_cpp_code(rest_code)
print("Renamed Code:\n", renamed_code)
print("\n\n\n")
function_details = parser.get_function_details()
print("Function Details:\n", function_details)
