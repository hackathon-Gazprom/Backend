from collections import defaultdict

from .constants import SUBORDINATES, WITHOUT_PARENT


def get_tree(children, owner, max_deep, serializer) -> dict:
    """Создание структуры дерева"""
    tree = defaultdict(list)
    nodes = defaultdict(list)
    for child in children:
        nodes[child.parent_id].append(child)

    def build_subtree(employee, deep=0):
        subtree = serializer(employee).data
        subtree[SUBORDINATES] = []
        for node in nodes[employee.id]:
            if deep + 1 >= max_deep:
                break
            subtree[SUBORDINATES].append(build_subtree(node, deep=deep + 1))
        return subtree

    for parent_id in (owner.id, None):  # owner and non parent
        [
            tree[parent_id].append(build_subtree(node, 0))
            for node in nodes[parent_id]
        ]
    res = serializer(owner).data
    res[SUBORDINATES] = tree[owner.id]
    res[WITHOUT_PARENT] = tree[None]
    return res
