# expression util
import re


# get line number from source mapping
def get_line_number(expression_node):
    match = re.search(r'#([^#-]+)(?:-|$)', str(expression_node.source_mapping))
    if match:
        return int(match.group(1))
    else:
        return None


# get scope from source mapping
def get_scope(expression_node):
    pattern = r'#(\d+)-(\d+)'
    match_scope = re.search(pattern, str(expression_node.source_mapping))
    if match_scope:
        return int(match_scope.group(1)), int(match_scope.group(2))
    else:
        match_line = re.search(r'#([^#-]+)(?:-|$)', str(expression_node.source_mapping))
        if match_line:
            return int(match_line.group(1)), int(match_line.group(1))
    return None, None


# get all line_numbers in the if-statement
def line_number_in_if(function):
    result = {}
    for i in range(len(function.nodes)):
        node = function.nodes[i]
        if str(node.type) == 'NodeType.IF':
            if_line_number = get_line_number(node)
            for j in range(i + 1, len(function.nodes)):
                end_node = function.nodes[j]
                if get_line_number(end_node) == if_line_number and str(end_node.type) == 'NodeType.ENDIF':
                    for k in range(i + 1, j):
                        result[get_line_number(function.nodes[k])] = function.nodes[k]
                    break
    return result


def is_line_number_in_descendants(node, target_line_number, visited=None):
    if visited is None:
        visited = set()

    # Check if this node is the target node
    if get_line_number(node) == target_line_number:
        return True

    # Mark this node as visited
    visited.add(node)

    # Recursively check all sons
    for son in node.sons:
        if son not in visited:
            if is_line_number_in_descendants(son, target_line_number, visited):
                return True

    return False
