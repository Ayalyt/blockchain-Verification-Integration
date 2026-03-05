# synthesize the secure contract

import os
import re
from pathlib import Path
from ..enums.security_enum import SecurityEnum
from ..enums.vulnerablity_enum import VulnerabilityEnum
from ...utils import expression_util


# check_synthesized
def check_synthesized(sol_name):
    src = Path(sol_name)
    src_text = src.read_text(encoding='utf-8')
    if '// IFS enforcement' in src_text:
        print("This contract has already been synthesized.")
        return True
    return False


# get specific vulnerabilities
def get_spec_vuln(vulnerabilities, solution, core_variables):
    spec_vuln = {}

    # collect vulnerabilities
    for vuln in vulnerabilities:
        if vuln.vulnerable_type != VulnerabilityEnum.none and vuln.shown:
            for lvalue in vuln.lvalues:
                if lvalue.source in core_variables:
                    security_level = SecurityEnum.H if solution[lvalue.source] else SecurityEnum.L
                    if security_level != lvalue.source.security_level:
                        spec_vuln.setdefault(vuln, []).append(lvalue.source)
            for rvalue in vuln.rvalues:
                if rvalue.source in core_variables:
                    security_level = SecurityEnum.H if solution[rvalue.source] else SecurityEnum.L
                    if security_level != rvalue.source.security_level:
                        spec_vuln.setdefault(vuln, []).append(rvalue.source)

    return spec_vuln



# get synthesis contract path
def get_syn_contract_path(sol_name):
    output_dir = './output'
    base_name = os.path.basename(sol_name)
    new_name = f"{os.path.splitext(base_name)[0]}_syn.sol"
    syn_path = os.path.join(output_dir, new_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return syn_path


# get function ranges
def get_function_ranges(slither, target_contract):
    function_ranges = []
    constructor_function_list = ['slitherConstructorConstantVariables', 'slitherConstructorVariables', 'constructor']
    for contract in slither.contracts:
        if contract.name == target_contract:
            for function in contract.functions:
                if function.name in constructor_function_list:
                    continue
                begin_number, end_number = expression_util.get_scope(function)
                function_ranges.append((function.name, begin_number, end_number))
    return function_ranges


# map vulnerabilities to functions
def map_vuln_to_function(spec_vuln, ranges):
    fun_map = {fr[0]: list() for fr in ranges}

    for vuln, variables in spec_vuln.items():
        for fun_name, start, end in ranges:
            if start <= vuln.line_number <= end:
                fun_map[fun_name].extend(variables)

    return {key: list(set(values)) for key, values in fun_map.items()}



# generate contract that satisfies IFS
def generate_ifs_contract(solution, modifiers):
    lines = ['// SmartIFSyn generated contract - do not remove the comment below', '// IFS enforcement\n',
             'contract IFS {\n', '    enum SecurityLevel { L, H }']
    var_origin_levels = dict()
    var_syn_levels = dict()
    for var, level in solution.items():
        name = var.name.replace('.', '_') + f'_{var.line_number}_security_level'
        security_level = 'H' if level else 'L'
        var_syn_levels[name] = security_level
    for variables in modifiers.values():
        for variable in variables:
            var_name = variable.name.replace('.', '_') + f'_{variable.line_number}_security_level'
            security_level = 'H' if variable.security_level == SecurityEnum.H else 'L'
            var_origin_levels[var_name] = security_level

    # state variables from solution
    for name, security_level in var_origin_levels.items():
        lines.append(f'    SecurityLevel public {name} = SecurityLevel.{security_level};')
    if len(solution) == 0:
        lines.append('    // (no security variables provided in solution)')
    lines.append('')

    # modifiers
    for fun_name, variables in modifiers.items():
        modifier_name = fun_name + '_modifier'
        lines.append(f'    modifier {modifier_name}() {{')
        if not variables:
            lines.append('        // no variable checks for this modifier (empty vulnerability mapping)')
        else:
            for variable in variables:
                var_name = variable.name.replace('.', '_') + f'_{variable.line_number}_security_level'
                lines.append(f'        require({var_name} == SecurityLevel.{var_syn_levels[var_name]});')
        lines.append('        _;')
        lines.append('    }')
        lines.append('')
    lines.append('}')  # end contract IFS
    return '\n'.join(lines) + '\n\n'


# find the correct position for ifs contract
def find_insert_pos_for_ifs(source_lines):
    last_pragma_or_import = -1
    contract_pos = None
    for i, line in enumerate(source_lines):
        stripped = line.strip()
        if stripped.startswith('pragma ') or stripped.startswith('import '):
            last_pragma_or_import = i
        if re.match(r'contract\s+\w+', stripped):
            contract_pos = i
            break
    if contract_pos is not None:
        return max(last_pragma_or_import + 1, 0)
    return max(last_pragma_or_import + 1, 0)



# add inheritance to smart contract
def add_inheritance(source, contract_name):
    pattern = re.compile(r'(contract\s+' + re.escape(contract_name) + r'\b\s*)([^\\{]*)\{', re.MULTILINE)

    def repl(m):
        pre = m.group(1)
        middle = m.group(2) or ''
        if 'IFS' in middle:
            return m.group(0)
        middle_new = middle.strip()
        if middle_new == '':
            middle_new = ' is IFS '
        else:
            if 'is' in middle_new:
                middle_new = middle_new + ', IFS '
            else:
                middle_new = middle_new + ' is IFS '
        return pre+ middle_new + '{'

    new_source, cnt = pattern.subn(repl, source, count=1)
    if cnt == 0:
        print(f'[WARN] contract {contract_name} not found.')
        return source
    return new_source

# insert modifier before '{' or 'returns'
def insert_modifier_in_header(header_text, modifier_name):
    if re.search(r'\b' + re.escape(modifier_name) + r'\b', header_text):
        return header_text

    returns_match = re.search(r'\breturns\s*\([^)]*\)', header_text)
    if returns_match:
        insert_pos = returns_match.start()
        return header_text[:insert_pos] + modifier_name + " " + header_text[insert_pos:]

    last_brace_pos = header_text.rfind('{')
    if last_brace_pos != -1:
        return header_text[:last_brace_pos] + ' ' + modifier_name + ' ' + header_text[last_brace_pos:]

    return header_text



# generate override function for parent contract functions (Slither version)
def generate_override_function(func_name, original_func, modifier_name):
    """
    Generates a correct override function for Solidity using Slither function object, keeping:
      - visibility
      - state mutability: payable, view, pure
      - returns clause
      - parameters
      - override only if parent function is virtual
    """
    lines = []

    visibility = original_func.visibility  # public, internal, private, external
    if visibility == 'external':
        visibility = 'public'

    state_str = ''
    if getattr(original_func, 'payable', False):
        state_str = 'payable'
    elif getattr(original_func, 'pure', False):
        state_str = 'pure'
    elif getattr(original_func, 'view', False):
        state_str = 'view'

    parameters = ', '.join([f"{p.type} {p.name}" for p in original_func.parameters])

    returns_clause = ''
    if original_func.returns and len(original_func.returns) > 0:
        returns_clause = ' returns(' + ', '.join([str(r.type) for r in original_func.returns]) + ')'

    override_str = ''
    if getattr(original_func, 'is_virtual', False):
        override_str = f"override({original_func.contract.name})"

    header_line = f"function {func_name}({parameters}) {visibility} {state_str} {override_str} {modifier_name}{returns_clause} {{"
    lines.append(f"    {header_line.strip()}")

    param_names = [p.name for p in original_func.parameters]
    params_str = ', '.join(param_names)
    if original_func.returns and len(original_func.returns) > 0:
        lines.append(f"        return super.{func_name}({params_str});")
    else:
        lines.append(f"        super.{func_name}({params_str});")

    lines.append("    }")
    lines.append("")
    return lines




# insert IFS and modifiers into source with parent override
def insert_ifs_and_modifiers_into_source(source_text, target_contract, ifs_text, func_vars, function_ranges, analyser=None):
    source_lines = source_text.splitlines()
    insert_pos = find_insert_pos_for_ifs(source_lines)
    new_lines = source_lines[:insert_pos] + [ifs_text.rstrip('\n')] + source_lines[insert_pos:]
    new_source = '\n'.join(new_lines) + '\n'
    new_source = re.sub(r'\bexternal\b', 'public', new_source)

    new_source = add_inheritance(new_source, target_contract.name)
    lines = new_source.splitlines()
    offset = ifs_text.count('\n') - 1
    func_map = {f[0]: (f[1] + offset, f[2] + offset) for f in function_ranges}



    raw_inherit_funcs = {}
    own_funcs = {}
    inherit_funcs = {}

    functions_inherited = target_contract.functions_inherited
    constructor_function_list = ['slitherConstructorConstantVariables', 'slitherConstructorVariables', 'constructor']

    for f in target_contract.functions:
        if f.name in constructor_function_list:
            continue
        elif f.is_constructor:
            continue

        if f in functions_inherited:
            raw_inherit_funcs[f.name] = func_vars[f.name]
        else:
            own_funcs[f.name] = func_vars[f.name]

    for key, value in raw_inherit_funcs.items():
        if key not in own_funcs:
            inherit_funcs[key] = value




    # for func_name, variables in func_vars.items():
    for func_name, variables in own_funcs.items():
        if func_name not in func_map:
            print(f"[WARN] function {func_name} not in function ranges.")
            continue
        start = func_map[func_name][0] - 1
        end = func_map[func_name][1] - 1
        header_start = start
        header_end = start
        found_brace = False
        for i in range(start, min(end + 1, len(lines))):
            if '{' in lines[i]:
                header_end = i
                found_brace = True
                break
            header_end = i
        if not found_brace:
            print(f'[WARN] function {func_name} in range {start}-{end} did not find "{{", skipped.')
            continue
        header_lines = lines[header_start: header_end + 1]
        header_text = '\n'.join(header_lines)
        modifier_name = func_name + '_modifier'
        new_header_text = insert_modifier_in_header(header_text, modifier_name)
        new_header_lines = new_header_text.splitlines()
        lines = lines[:header_start] + new_header_lines + lines[header_end + 1:]




    if analyser is not None:
        contract_start = contract_end = None
        for i, line in enumerate(lines):
            if re.match(rf'\s*contract\s+{re.escape(target_contract.name)}', line):
                contract_start = i
                break
        if contract_start is not None:
            brace_count = 0
            for i in range(contract_start, len(lines)):
                brace_count += lines[i].count('{') - lines[i].count('}')
                if brace_count == 0:
                    contract_end = i
                    break
            if contract_end is None:
                contract_end = len(lines)

            override_lines = []
            # for func_name, variables in func_vars.items():
            for func_name, variables in inherit_funcs.items():
                original_func = None
                for contract in analyser.slither.contracts:
                    if contract.name == target_contract.name:
                        continue
                    for f in contract.functions:
                        if f.name == func_name:
                            original_func = f
                            break
                    if original_func:
                        break
                if original_func is None:
                    continue

                modifier_name = func_name + '_modifier'
                override_lines.extend(generate_override_function(func_name, original_func, modifier_name))

            lines = lines[:contract_end] + override_lines + lines[contract_end:]

    final_source = '\n'.join(lines) + '\n'
    return final_source





# generate secure contract
def generate_secure_contract(analyser):
    # pre analysis
    vulnerabilities = analyser.vulnerabilities
    solution = analyser.solutions[0]
    core_variables = analyser.core_variables
    sol_name = analyser.sol_name
    target_contract = analyser.target_contract

    spec_vuln = get_spec_vuln(vulnerabilities, solution, core_variables)
    output_path = get_syn_contract_path(sol_name)
    function_ranges = get_function_ranges(analyser.slither, target_contract)

    # map vuln to functions
    func_vars = map_vuln_to_function(spec_vuln, function_ranges)

    # synthesis the secure contract
    ifs_text = generate_ifs_contract(solution, func_vars)

    src = Path(sol_name)
    src_text = src.read_text(encoding='utf-8')
    final_text = insert_ifs_and_modifiers_into_source(src_text, target_contract, ifs_text, func_vars, function_ranges, analyser)

    synthesized_contract = Path(output_path)
    synthesized_contract.write_text(final_text, encoding='utf-8')

    return output_path
