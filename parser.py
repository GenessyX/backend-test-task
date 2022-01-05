import requests
from bs4 import BeautifulSoup
import textwrap
from semantic_tags import semantic_tags

test_url = "https://github.com/GenessyX/backend-test-task"
# test_url = "https://flask.palletsprojects.com/en/2.0.x/"


tree = []

class Tree_Node:
    def __init__(self, tag_name, data=None):
        self.children = []
        self.tag_name = tag_name
        self.data = data

    def __str__(self):
        return "<{}>:{}".format(self.tag_name, self.data)

    def __repr__(self):
        return "<{}>:{}".format(self.tag_name, self.data)


def append_tree(root_node, children):
    root_node.children = children

# end_tags = ['h1', 'h2', 'h3', 'h4', 'h5']

def make_tree(root_node, parse_content):
    children_exist = False
    try:
        children_exist = bool(next(parse_content.children))
    except:
        if not parse_content.name:
            root_node.data = parse_content.strip()
        else:
            root_node.data = parse_content.get_text().strip()

    if children_exist:
        for child in parse_content.children:
            if child.name:
                child_node = Tree_Node(child.name)
            else:
                child_node = Tree_Node("text")
            make_tree(child_node, child)
            root_node.children.append(child_node)

    return root_node

def debug_traverse_tree(root_node, indent=0):
    indent += 1
    for ch in root_node.children:
        
        if ch.data:
            print(" "*indent, ch.tag_name, ch.data)

        debug_traverse_tree(ch, indent)


# def parse_url(url: str, width: int = 50, img_link: bool = True):
#     r = requests.get(url)
#     if r.status_code != requests.codes.ok:
#         print("Request returned status code: {}".format(r.status_code))
#     info = []
#     soup = BeautifulSoup(r.content, 'html.parser')
#     for semantic_tag in semantic_tags:
#         for tag in soup.find_all(semantic_tag):
#             if tag.get_text() != "":
#                 info.append((semantic_tag, tag.get_text().rstrip("\n")))
#             # print(tag.get_text().strip())
#     for line in info:
#         print(line)
    


def main():
    r = requests.get(test_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    start_html = soup.find_all(recursive=False)
    root_node = Tree_Node(start_html[0].name)
    tree = make_tree(root_node, start_html[0])
    debug_traverse_tree(tree)

if __name__ == "__main__":
    main()