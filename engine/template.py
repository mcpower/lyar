import re
import os
from .nodes import (TextNode, PythonNode, GroupNode, IfNode, ForNode, SafeNode,
                    CommentNode)

DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'templates')


class ParseException(Exception):
    pass


def split_tokens(s):
    r = re.compile(r'({[{%].*?[%}]})')
    return r.split(s)


def make_dict(label, data):
    return {
        'label': label,
        'data': data
    }


def id_token(token):
    if token.startswith('{{') and token.endswith('}}'):
        return make_dict('python', token[2:-2].strip())
    elif token.startswith('{%') and token.endswith('%}'):
        inner = token[2:-2].split()
        if inner[0] == 'include':
            return make_dict('include',
                             {'path': inner[1], 'variables': inner[2:]})
        elif inner[0] == 'if':
            predicate = " ".join(inner[1:])
            return make_dict('if', predicate)
        elif inner[0] == 'else':
            return make_dict('else', None)
        elif ' '.join(inner) == 'end if':
            return make_dict('end if', None)
        elif inner[0] == 'for':
            return make_dict('for',
                             {
                                 'variable': inner[1],
                                 'iterable': " ".join(inner[3:])
                             })
        elif ' '.join(inner) == 'end for':
            return make_dict('end for', None)
        elif inner[0] == 'safe':
            return make_dict('safe', " ".join(inner[1:]))
        elif inner[0] == 'comment':
            return make_dict('comment', ' '.join(inner[1:]))

    else:
        return make_dict('text', token)


def lexer(s):
    tags = split_tokens(s)
    tokens = [id_token(tag) for tag in tags]
    return tokens


def parse(tokens, parent=None, upto=0, parent_type=None):
    if parent is None:
        parent = GroupNode()
    while upto < len(tokens):
        current_token = tokens[upto]
        label = current_token['label']
        if label == 'python':
            new_node = PythonNode(current_token['data'])
            upto += 1
            parent.add_child(new_node)
        elif label == 'safe':
            new_node = SafeNode(current_token['data'])
            upto += 1
            parent.add_child(new_node)
        elif label == 'text':
            new_node = TextNode(current_token['data'])
            upto += 1
            parent.add_child(new_node)
        elif label == 'include':
            upto += 1
            includePath = os.path.join(DIRECTORY,
                                       current_token['data']['path'])
            with open(includePath) as f:
                # new file, therefore upto = 0
                parse(lexer(f.read()), parent, 0, parent_type)
        elif label == 'if':
            new_node = IfNode(current_token['data'])
            parent.add_child(new_node)
            upto += 1
            if_group, new_pos = parse(tokens, new_node.true_node, upto, "if")
            upto = new_pos
            current_token = tokens[upto]
            label = current_token['label']
            if label == "else":
                upto += 1
                elseGroup, new_pos = parse(tokens, new_node.false_node,
                                           upto, "else")
                upto = new_pos
        elif label == "else":
            if parent_type == "if":
                return parent, upto
            else:
                raise ParseException('Found "else" without corresponding '
                                     '"if" statement')
        elif label == 'end if':
            if parent_type in ("if", "else"):
                upto += 1
                return parent, upto
            else:
                raise ParseException('Found "end if" without corresponding '
                                     '"if" statement')
        elif label == 'for':
            new_node = ForNode(current_token['data']['iterable'],
                               current_token['data']['variable'])
            parent.add_child(new_node)
            upto += 1
            for_group, new_pos = parse(tokens, new_node.loop_block,
                                       upto, "for")
            upto = new_pos
            current_token = tokens[upto]
            label = current_token['label']
        elif label == 'end for':
            if parent_type == 'for':
                upto += 1
                return parent, upto
            else:
                raise ParseException('Found "end for" without corresponding '
                                     '"for" statement')
        elif label == 'comment':
            upto += 1
            new_node = CommentNode(current_token['data'])
            parent.add_child(new_node)

    return parent, upto


def render_page(file_name, context):
    file_path = os.path.join(DIRECTORY, file_name)
    with open(file_path) as f:
        return parse(lexer(f.read()))[0].render(context)

# if __name__ == '__main__':
#   test = """
#           <html>
#           <head><title>TitleText</title><head>
#           {{ 4+2 }}
#           {% if False %}
#           Hello
#           {% end if %}
#           more text"""
#   print(parse(lexer(test))[0].render({}))
