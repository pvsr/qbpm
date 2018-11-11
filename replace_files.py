"""
Run jinja on all filenames in a directory.
"""

from pathlib import Path
from jinja2 import Template
from typing import Callable, Dict, Iterable, List, Optional
import shutil

root_dir = 'dest'

def main() -> None:
    root = create_tree(template_files())
    root.print()
    rename_tree(root)

def template_files() -> Iterable[Path]:
    # TODO get these as params
    shutil.copytree('src', root_dir, symlinks=True)
    paths = Path(root_dir).glob('**/{{*}}')
    return paths

def render_name(name: str) -> str:
    return Template(name).render(name='pvsr', url='http://example.com', other='else')

def rename_tree(root: 'Node') -> None:
    root.walk(lambda node: node.rename(render_name))

def create_tree(paths: Iterable[Path]) -> 'Node':
    root = Node(Path(root_dir))
    inserted: Dict[Path, 'Node'] = {}
    for path in paths:
        insert(root, inserted, path)
    return root

def insert(root: 'Node', inserted: Dict[Path, 'Node'], path: Path) -> 'Node':
    if len(path.relative_to(root_dir).parts) == 1:
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
            self.path = path.relative_to(parent.whole_path())
            parent.children.append(self)
        else:
            self.path = path

    # full path relative to root
    def whole_path(self) -> Path:
        if self.parent:
            return self.parent.whole_path().joinpath(self.path)
        else:
            return self.path

    def rename(self, transform_name: Callable[[str], str]) -> bool:
        # ignore root node
        if self.parent:
            new_name = transform_name(self.path.name)
            if new_name == '' or new_name is None:
                print(str(self.whole_path()) + ' expands to an empty string, skipping')
                return False

            # TODO catch ValueError for invalid name
            new_path = self.whole_path().with_name(new_name)
            print('renaming ' + str(self.whole_path()) + ' to ' + str(new_path))
            self.whole_path().replace(new_path)
            self.path = self.path.with_name(new_name)
            #print('new name: ' + str(self.path))
        return True

    def walk(self, process: Callable[['Node'], bool]) -> None:
        if process(self):
            for child in self.children:
                child.walk(process)
        else:
            print('removing', str(self.whole_path()))
            # TODO nonexistent path left dangling in parent,
            # but removing self from parent.children messes with loop
            self.whole_path().unlink()

    def print(self, prefix: str = '|-') -> None:
        print(prefix + str(self.path))
        for child in self.children:
            child.print(prefix + '-')

if __name__ == '__main__':
    main()
