"""
Run jinja on all filenames in a directory.
"""

from pathlib import Path
from jinja2 import Template
from typing import Callable, Dict, Iterable, List, Optional

def main() -> None:
    root = create_tree(template_files())
    root.print()
    rename_tree(root)

def template_files() -> Iterable[Path]:
    paths = Path('.').glob('**/{{*}}')
    return paths

def render_name(name: str) -> str:
    return Template(name).render(name='pvsr', url='http://example.com', other='else')

def rename_tree(root: 'Node') -> None:
    root.walk(lambda node: node.rename(render_name))

def create_tree(paths: Iterable[Path]) -> 'Node':
    root = Node(Path('.'))
    inserted: Dict[Path, 'Node'] = {}
    for path in paths:
        insert(root, inserted, path)
    return root

def insert(root: 'Node', inserted: Dict[Path, 'Node'], path: Path) -> 'Node':
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
    def __init__(self, path: Path, parent: Optional['Node'] = None) -> None:
        self.children: List[Node] = []
        self.parent: Optional[Node] = parent
        self.path: Path
        if parent is not None:
            self.path = path.relative_to(parent.path)
            parent.children.append(self)
        else:
            self.path = path

    def whole_path(self) -> Path:
        if self.parent is not None:
            return self.parent.path.joinpath(self.path)
        else:
            return self.path

    def rename(self, transform_name: Callable[[str], str]) -> None:
        if self.path.name != '':
            new_name = transform_name(self.path.name)
            new_path = self.whole_path().with_name(new_name)
            print('renaming ' + str(self.whole_path()) + ' to ' + str(new_path))
            self.whole_path().replace(new_path)
            self.path = new_path
            print('new name: ' + str(self.path))

    def walk(self, process: Callable[['Node'], None]) -> None:
        process(self)
        for child in self.children:
            child.walk(process)

    def print(self, prefix: str = '|-') -> None:
        print(prefix + str(self.path))
        for child in self.children:
            child.print(prefix + '-')

if __name__ == '__main__':
    main()
