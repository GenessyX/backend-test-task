import shutil
import tempfile
import requests
from bs4 import BeautifulSoup, Comment

# from jinja2 import Environment, PackageLoader, select_autoescape
import jinja2
import requests
import os
import time
import urllib.parse

from werkzeug.wrappers import response

# html tags that do not contain valueable text


def strip_scheme(url):
    parsed = urllib.parse.urlparse(url).netloc + urllib.parse.urlparse(url).path
    return parsed.rstrip("/").replace("/", "_")


class Parser:
    #
    def __init__(
        self,
        templates_path="templates",
        caching: int = 1,
        caching_duration: int = 12 * 60 * 60,
        cache_folder: str = "cache",
        img: int = 1
    ):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'})

        self.templates_path = templates_path
        self.template = self.init_template_env()

        self.caching = caching
        self.caching_duration = caching_duration
        self.cache_folder = cache_folder

        self.not_parse = [
            "button",
            "style",
            "script",
            "noscript",
            "svg",
            "form",
            "nav",
            "header",
            "footer",
            "noindex",
            "menu",
        ]
        self.not_parse_selectors = [
            "[class*='footer']",
            "[class*='modal']",
            "[class*='social']",
            "[class*='banner']",
            "[class*='menu']",
            "[class*='tag']",
            "[class*='news-feed']",
            "[width='1']",
            "[width='0']",
            "[height='1']",
            "[height='0']",
            "[class*='news-feed']",
            "[class*='meta']",
            "[class*='widget']",
            "[class*='alert']",
            "[class*='loader']",
            "[class*='info']",
            "[class*='popover']"
            ]

        self.img = img

    @staticmethod
    def get_soup(response):
        return BeautifulSoup(response.content, "html.parser")

    def clean_soup(self, soup):
        for comments in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comments.extract()

        # remove unnecessary tags from soup
        for tag in self.not_parse:
            for el in soup.find_all(tag):
                el.extract()

        for cl in self.not_parse_selectors:
            for el in soup.select(cl):
                el.extract()

        # remove head
        soup.find("head").extract()

        
        for image in soup.find_all("img"):
            if self.img:
                if image.attrs.get('src'):
                    a_tag = soup.new_tag('image')
                    a_tag.string = "\n" + image.attrs.get('src').lstrip("/")
                    image.replace_with(a_tag)
                else:
                    image.extract()
            else:
                image.extract()

        return soup

    def init_template_env(self):
        templateLoader = jinja2.FileSystemLoader(
            searchpath=os.path.join(os.getcwd(), self.templates_path)
        )
        templateEnv = jinja2.Environment(loader=templateLoader, extensions=['jinja2.ext.loopcontrols'])
        TEMPLATE_FILE = "response.txt.jinja"
        template = templateEnv.get_template(TEMPLATE_FILE)
        return template

    def render_template(self, **kwargs):
        return self.template.render(**kwargs)

    def get_and_check_url_response(self, url):
        if not urllib.parse.urlparse(url).scheme:
            url = "https://" + url

        try:
            response = self.session.get(url)
        except requests.exceptions.ConnectionError:
            raise Exception(400, "Connection to this url can't be esatblished")
        except requests.exceptions.InvalidURL:
            raise Exception(400, "URL is invalid")

        st_code = response.status_code
        if not st_code == requests.codes.ok:
            raise Exception(
                st_code, "Request return {} status code".format(str(st_code))
            )

        return response

    @staticmethod
    def generate_file_name(url: str, width: int, img_flag: int) -> str:
        return strip_scheme(url) + "_w-" + str(width) + "_i-" + str(img_flag) + ".txt"

    def generate_cache_path(self, url, width, img_flag):
        file_name = self.generate_file_name(url, width, img_flag)
        cached_file_path = os.path.abspath(os.path.join(self.cache_folder, file_name))
        return cached_file_path

    def file_exists_in_cache(self, cached_file_path: str) -> bool:
        return os.path.isfile(cached_file_path) and (
            time.time() - os.path.getmtime(cached_file_path) < self.caching_duration
        )

    def generate_txt_file(self, contents: str) -> tempfile.NamedTemporaryFile:
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(contents.encode("utf-8"))
        tmp.seek(0, 2)
        return tmp

    def save_to_cache(self, url, width, img_flag, tmp: tempfile.NamedTemporaryFile):
        file_name = self.generate_file_name(url, width, img_flag)
        cached_file_path = os.path.abspath(os.path.join(self.cache_folder, file_name))
        shutil.copyfile(tmp.name, cached_file_path)
        tmp.close()


def main():
    import argparse

    arg_parser = argparse.ArgumentParser(description="Parse URL to txt.")
    arg_parser.add_argument("--url", type=str, help="URL to parse.")
    arg_parser.add_argument(
        "--width", type=int, default=200, help="Width of the output."
    )
    arg_parser.add_argument(
        "--img", type=int, default=1, help="Include images in the output."
    )
    arg_parser.add_argument("--cache", type=int, default=1, help="Cache results.")
    arg_parser.add_argument("--save", type=int, default=0, help="Save file")
    arg_parser.add_argument("--print", type=int, default=1, help="Print file")
    args = arg_parser.parse_args()
    if not args.url:
        print("You must specify url with --url")
        return

    url = args.url
    width = args.width
    img_flag = args.img
    save = args.save
    print_flag = args.print

    parser = Parser(caching=args.cache, img=img_flag)
    if parser.caching or save:
        cached_file_path = parser.generate_cache_path(url, width, img_flag)
        if parser.file_exists_in_cache(cached_file_path):
            if print_flag:
                with open(cached_file_path) as f:
                    print(f.read())
            if save:
                print("File already saved at")
                print(cached_file_path)
            return

    try:
        response = parser.get_and_check_url_response(url)
    except Exception as e:
        print("{}\n{}".format(e.args[0], e.args[1]))
        return

    soup = parser.get_soup(response)
    cleaned_soup = parser.clean_soup(soup)
    rendered_template = parser.render_template(
        soup=cleaned_soup, width=width, img_flag=img_flag
    )

    if print_flag:
        print(rendered_template)

    if parser.caching or save:
        with open(cached_file_path, "w") as f:
            f.write(rendered_template)
        if save:
            print("File saved to:")
            print(cached_file_path)


if __name__ == "__main__":
    main()
