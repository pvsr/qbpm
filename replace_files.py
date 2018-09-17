"""
Run jinja on all filenames in a directory.
"""

from pathlib import Path
from jinja2 import Template

def main():
    root = create_tree(template_files())
    root.print()
    rename_tree(root)

def template_files():
    paths = Path('.').glob('**/{{*}}')
    return paths

def render_name(name):
    return Template(name).render(name='pvsr', url='http://example.com', other='else')

def rename_tree(root):
    root.walk(lambda node: node.rename(render_name))

def create_tree(paths):
    root = Node(Path('.'))
    inserted = {}
    for path in paths:
        insert(root, inserted, path)
    return root

def insert(root, inserted, path):
    if len(path.parts) == 1:
        parent_node = root
    elif path.parent in inserted:
        parent_node = inserted[path.parent]
    else:
        parent_node = insert(root, inserted, path.parent)
    node = Node(path, parent=parent_node)
    inserted[path] = node
    return node

class Node:
    def __init__(self, path, parent=None):
        self.children = []
        self.parent = parent
        if parent is not None:
            self.path = path.relative_to(parent.path)
            parent.children.append(self)
        else:
            self.path = path

    def whole_path(self):
        if self.parent is not None:
            return self.parent.path.joinpath(self.path)
        else:
            return self.path

    def rename(self, transform_name):
        if self.path.name != '':
            new_name = transform_name(self.path.name)
            new_path = self.whole_path().with_name(new_name)
            print('renaming ' + str(self.whole_path()) + ' to ' + str(new_path))
            self.whole_path().replace(new_path)
            self.path = new_path
            print('new name: ' + str(self.path))

    def walk(self, process):
        process(self)
        for child in self.children:
            child.walk(process)

    def print(self, prefix='|-'):
        print(prefix + str(self.path))
        for child in self.children:
            child.print(prefix + '-')

if __name__ == '__main__':
    main()
