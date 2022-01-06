import requests
from bs4 import BeautifulSoup, Comment
import textwrap
from urllib.parse import urljoin, urlparse
# from semantic_tags import semantic_tags

test_url = "https://github.com/GenessyX/backend-test-task"
# test_url = "https://flask.palletsprojects.com/en/2.0.x/"


tree = []

class Tree_Node:
    def __init__(self, tag_name, data=None, url=None, src=None):
        self.children = []
        self.tag_name = tag_name
        self.data = data
        self.url = url
        self.src = src

    def __str__(self):
        return "<{}>:{}".format(self.tag_name, self.data)

    def __repr__(self):
        return "<{}>:{}".format(self.tag_name, self.data)


def append_tree(root_node, children):
    root_node.children = children

# end_tags = ['h1', 'h2', 'h3', 'h4', 'h5']
not_parse = ['button', 'style', 'script', 'svg', 'form']

def make_tree(root_node, parse_content, domain_name):
    # Recursively parse html document

    children_exist = False

    # Check if node has children
    # If not: get text from the html and add to the node data
    # If has: recursively parse children
    try:
        children_exist = bool(next(parse_content.children))
    except:
        if parse_content.name == 'img':
            root_node.src = parse_content.attrs.get('src')
            root_node.data = parse_content.attrs.get('alt')
        if not parse_content.name:
            if not len(parse_content.strip()):
                return None
            root_node.data = parse_content.strip()
            # print(len(root_node.data), root_node.data.count("\n"), root_node.data.count(" "), root_node.data)

        else:
            if not len(parse_content.get_text().strip()):
                return None
            root_node.data = parse_content.get_text().strip()

    if children_exist:

        for child in parse_content.children:

            if child.name not in not_parse:

                if child.name:
                    child_node = Tree_Node(child.name)
                    if child.attrs.get("href"):
                        child_node.url = urljoin(domain_name.netloc, child.attrs.get("href"))
                    if child.attrs.get("src"):
                        child_node.src = child.attrs.get('src')
                else:
                    child_node = Tree_Node("text")
                make_tree(child_node, child, domain_name)
                root_node.children.append(child_node)

    return root_node

def debug_traverse_tree(root_node, indent=0):
    indent += 1
    for ch in root_node.children:
        
        if ch.data:
            print(" "*indent, ch.tag_name, ch.data)

        debug_traverse_tree(ch, indent)


def parse_url(url: str, width: int = 50, img_link: bool = True):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print("Error")
    soup = BeautifulSoup(r.content, 'html.parser')

    for comments in soup.find_all(text=lambda text:isinstance(text, Comment)):
        comments.extract()


    start_html = soup.find_all(recursive=False)[0]
    root_node = Tree_Node(start_html.name)
    domain_name = urlparse(url)
    tree = make_tree(root_node, start_html, domain_name)
    return tree


def main():
    r = requests.get(test_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    start_html = soup.find_all(recursive=False)
    root_node = Tree_Node(start_html[0].name)
    tree = make_tree(root_node, start_html[0])
    debug_traverse_tree(tree)

if __name__ == "__main__":
    main()