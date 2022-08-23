#!/usr/bin/env python3

"""
Static Site Generator

A CLI static site generator written in Python.
"""


import argparse
import distutils
import glob
import os

import jinja2
import markdown


### Global variables. ###

# Files.
INDEX_FILE = "index.md"
IGNORED_FILES = ["README.md"]

# Directories.
BLOG_DIR = "blog"
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"
CONTENT_DIR = "content"

# Extensions.
HTML_EXT = ".html"
MD_EXT = ".md"

# Miscellaneous.
ENCODING="utf-8"
INDEX_HEADER = "title: Index\n\n"
INDEX_POST_ENTRY = "[{}]({}) ({})\n\n"


### Classes. ###

class Post:
    """Class to represent a single post.

    Attributes:
        filename (str): filename of the post (not including the extension).
        content (str): content of the post as a HTML fragment.
        html (str): fully rendered HTML of the post.
        title (str): title of the post.
        date (str): date of the post (in the ISO 8601 format).
    """

    def __init__(self, filename):
        """Setup the Post object.

        Opens the file containing the post content and sets up the Post
        object with the relevant attributes.

        Arguments:
            filename (str): filename of the post to open.

        Returns:
            None
        """
        # Create empty HTML attribute.
        self.html = None

        # Drop last three characters of the filename, they're not needed.
        self.filename = filename[:-3]

        # Open and convert the file to a HTML fragment.
        with open(filename, "r", encoding=ENCODING) as file:
            md_reader = markdown.Markdown(extensions=["meta", "fenced_code"])

            self.content = md_reader.convert(file.read())

            self.title = md_reader.Meta["title"].pop()

            # Attempt to get the date. If the date doesn't exist, then just
            # set the date attribute to None.
            try:
                self.date = md_reader.Meta["date"].pop()
            except KeyError:
                self.date = None

    def render_html(self, post_type):
        """Render the partial HTML to a full HTML page.

        post_type is used to determine the type of template to load,
        and then the resulting full HTML page is written out to a file.

        Arguments:
            post_type (str): type of template to use.

        Returns:
            None
        """
        # Open the relevant template file.
        template_file = TEMPLATE_DIR + os.path.sep + post_type + HTML_EXT

        # Render the HTML to the template.
        with open(template_file, "r", encoding=ENCODING) as file:
            template = jinja2.Template(file.read())

            self.html = template.render({
                "content": self.content,
                "title": self.title,
                "date": self.date,
                })

        # Write out full HTML to file.
        output_file = OUTPUT_DIR + os.path.sep + self.filename + HTML_EXT
        with open(output_file, "w", encoding=ENCODING) as file:
            file.write(self.html)


### Functions. ###

def insert_string(string, string_to_insert, index):
    """Insert a string into another string.

    Arguments:
        string (str): parent string.
        string_to_insert (str): string to insert into parent string.
        index (int): index to insert at.

    Returns:
        str: a new string containing the string to insert in the
            parent string.
    """
    return string[:index] + string_to_insert + string[index:]


def get_post(path):
    """Create a single Post object from a path.

    Arguments:
        path (str): a path to look for a post.

    Returns:
        Post: a Post object.
    """
    return Post(path)


def get_posts(path):
    """Create a list of Post objects from a path.

    Arguments:
        path (str): a path that glob uses to look for posts.

    Returns:
        [Post]: a list of Post objects.
    """
    post_list = []

    for file in glob.glob(path):
        if file not in IGNORED_FILES:
            post_list.append(Post(file))

    return post_list


def add_to_index_file(post):
    """Add a post to the top of the index file.

    Arguments:
        post (Post) - post to add to the index file.

    Returns:
        None
    """
    with open(INDEX_FILE, "r+", encoding=ENCODING) as file:
        data = file.read()

        # Check if post is already in the index file.
        if post.filename not in data:
            index = len(INDEX_HEADER)
            entry = INDEX_POST_ENTRY.format(post.title,
                    post.filename + HTML_EXT, post.date)

            new_data = insert_string(data, entry, index)

            # Empty and rewrite the file.
            file.seek(0)
            file.truncate()
            file.write(new_data)


def generate_index_file(posts):
    """Create an index file from a list of posts.

    Arguments:
        posts ([Post]) - list of posts to put in the index file.

    Returns:
        None
    """
    # Sort posts in reverse chronological order.
    posts.sort(key=lambda post: post.date, reverse=True)

    # Write index file.
    with open(INDEX_FILE, "w", encoding=ENCODING) as file:
        file.write(INDEX_HEADER)

        for post in posts:
            file.write(INDEX_POST_ENTRY.format(post.title,
                post.filename + HTML_EXT, post.date))


def check_dirs():
    """Checks certain information about directories.

    The specific information is as follows:
    - Which directory are we in? Move to the base directory if need be.
    - Are any directories missing? Create them if need be.

    Arguments:
        None

    Returns:
        None
    """
    # Check which directory we are in, move up if need be.
    if BLOG_DIR in os.getcwd():
        os.chdir("..")

    # Check and create output directories.
    if not os.path.exists(OUTPUT_DIR + os.path.sep + BLOG_DIR):
        os.makedirs(OUTPUT_DIR + os.path.sep + BLOG_DIR)


def copy_content_files():
    """Copies files from the content directory to the output directory.

    Arguments:
        None

    Returns:
        None
    """
    try:
        distutils.dir_util.copy_tree(CONTENT_DIR,
                                     OUTPUT_DIR + os.path.sep + CONTENT_DIR)
    except distutils.errors.DistutilsFileError:
        pass


### Main program. ###

if __name__ == "__main__":
    # Check directories before starting argument parsing.
    check_dirs()

    # Copy contents files before starting argument parsing.
    copy_content_files()

    # Setup parser with options.
    parser = argparse.ArgumentParser()

    options = parser.add_mutually_exclusive_group(required=True)

    options.add_argument("-a", "--all", action="store_true", dest="all", help="convert all files")
    options.add_argument("-s", "--single", nargs="?", metavar="file",
                         dest="single", help="convert one file")

    # Parse arguments and decide what to do.
    args = parser.parse_args()

    # Render all posts.
    if args.all:
        print("Rendering all posts to HTML")

        blog_posts = get_posts(BLOG_DIR + os.path.sep + "*" + MD_EXT)

        for post in blog_posts:
            print(f"Rendering {post.filename + MD_EXT}")
            post.render_html("blog")

        print("Generating index file")
        generate_index_file(blog_posts)

        meta_posts = get_posts("*" + MD_EXT)

        for post in meta_posts:
            print(f"Rendering {post.filename + MD_EXT}")
            post.render_html("meta")

    # Render a single post.
    elif args.single:
        filename = BLOG_DIR + os.path.sep + args.single

        print(f"Rendering {filename} to HTML")

        blog_post = get_post(filename)
        blog_post.render_html("blog")

        print(f"Adding {filename} to index file")
        add_to_index_file(blog_post)

        print("Rendering {INDEX_FILE} to HTML")

        index = get_post(INDEX_FILE)
        index.render_html("meta")
