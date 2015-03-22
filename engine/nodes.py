import html


class Node:
    def __init__(self):
        pass

    def render(self, context):
        raise NotImplementedError()


class TextNode(Node):

    def __init__(self, content):
        self.content = content

    def render(self, context):
        return self.content

    def __str__(self):
        return "TextNode: " + self.content

    def __repr__(self):
        return "TextNode"


class PythonNode(Node):

    def __init__(self, code):
        self.code = code

    def render(self, context):
        try:
            output = eval(self.code, {}, context)
        except NameError:
            raise NameError("Required variable not defined in context.")
        else:
            return html.escape(str(output))

    def __str__(self):
        return "PythonNode: " + self.code

    def __repr__(self):
        return "PythonNode"


class SafeNode(PythonNode):
    def render(self, context):
        try:
            output = eval(self.code, {}, context)
        except NameError:
            raise NameError("Required variable in safe statement not defined "
                            "in context.")
        else:
            return str(output)

    def __str__(self):
        return "SafeNode: " + self.code

    def __repr__(self):
        return "SafeNode"


class GroupNode(Node):

    def __init__(self, children=None):
        if children is not None:
            self.children = children
        else:
            self.children = []

    def render(self, context):
        final_str = ""
        for child in self.children:
            final_str += child.render(context)
        return final_str

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self):
        return "GroupNode"

    def __str__(self):
        return "GroupNode: " + str(self.children)


class IfNode(Node):
    def __init__(self, predicate):
        self.predicate = predicate
        self.true_node = GroupNode()
        self.false_node = GroupNode()

    def add_true_child(self, node):
        self.true_node.add_child(node)

    def add_false_child(self, node):
        self.false_node.add_child(node)

    def render(self, context):
        try:
            result = eval(self.predicate, {}, context)
        except NameError:
            raise NameError("Required variable in if predicate not defined "
                            "in context. Context is {}".format(context))
        else:
            if result:
                return self.true_node.render(context)
            else:
                return self.false_node.render(context)

    def __repr__(self):
        left = '...' if self is self.true_node else str(self.true_node)
        right = '...' if self is self.false_node else str(self.false_node)
        return 'IfNode({}, {}, {})'.format(id(self), left, right)


class ForNode(Node):
    def __init__(self, iterable, variable):
        self.loop_block = GroupNode()
        self.iterable = iterable
        self.variable = variable

    def add_loop_child(self, node):
        self.loop_block.add_child(node)

    def render(self, context):
        try:
            iterating = eval(self.iterable, {}, context)
        except NameError:
            raise NameError("Required variable in for loop iterable "
                            "not defined in context.")
        else:
            out = ""
            for item in iterating:
                new_context = dict(context)  # new instance
                new_context[self.variable] = item
                out += self.loop_block.render(new_context)
            return out


class CommentNode(Node):
    def __init__(self, comment):
        self.comment = comment

    def render(self, context):
        return ''
