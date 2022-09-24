"""
Static Site Generator

A CLI static site generator written in Python.
"""


import argparse
import distutils
import glob
import json
import os
import sys

import jinja2
import markdown


### Global variables. ###

# Configuration file path.
CONFIG_FILE_PATH = (os.path.expanduser("~") + os.path.sep
                    + ".config" + os.path.sep
                    + "daisy" + os.path.sep
                    + "config.json")

# Configuration dictionary.
CONFIG = {}

# Miscellaneous.
INDEX_HEADER = "title: Index\n\n"
INDEX_POST_ENTRY = "[{}]({}) ({})\n\n"


### Classes. ###

class Post:
    """Class to represent a single post.

    Attributes:
        filename (str): filename of the post (not including the
            extension).
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
        """
        # Create empty HTML attribute.
        self.html = None

        # Drop the last three characters of the filename.
        self.filename = filename[:-3]

        # Open and convert the file to a HTML fragment.
        with open(filename, "r", encoding=CONFIG["encoding"]) as file:
            md_reader = markdown.Markdown(extensions=["meta", "fenced_code"])

            self.content = md_reader.convert(file.read())

            self.title = md_reader.Meta["title"].pop()

            # Attempt to get the date. If the date doesn't exist, then
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
        """
        # Open the relevant template file.
        template_file = (CONFIG["dirs"]["template"] + os.path.sep + post_type
                         + CONFIG["ext"]["html"])

        # Render the HTML to the template.
        with open(template_file, "r", encoding=CONFIG["encoding"]) as file:
            template = jinja2.Template(file.read())

            self.html = template.render({
                "content": self.content,
                "title": self.title,
                "date": self.date,
                })

        # Write out full HTML to file.
        output_file = (CONFIG["dirs"]["output"] + os.path.sep + self.filename
                       + CONFIG["ext"]["html"])
        with open(output_file, "w", encoding=CONFIG["encoding"]) as file:
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
        if file in CONFIG["ignored_files"]:
            print(f"{file} in {CONFIG['ignored_files']}, skipping")
        else:
            post_list.append(Post(file))

    return post_list


def add_to_index_file(post):
    """Add a post to the top of the index file.

    Arguments:
        post (Post): post to add to the index file.
    """
    with open(CONFIG["index_file"], "r+", encoding=CONFIG["encoding"]) as file:
        data = file.read()

        # Check if post is already in the index file.
        if post.filename not in data:
            index = len(INDEX_HEADER)
            entry = INDEX_POST_ENTRY.format(post.title,
                    post.filename + CONFIG["ext"]["html"], post.date)

            new_data = insert_string(data, entry, index)

            # Empty and rewrite the file.
            file.seek(0)
            file.truncate()
            file.write(new_data)


def generate_index_file(posts):
    """Create an index file from a list of posts.

    Arguments:
        posts ([Post]): list of posts to put in the index file.
    """
    # Sort posts in reverse chronological order.
    posts.sort(key=lambda post: post.date, reverse=True)

    # Write index file.
    with open(CONFIG["index_file"], "w", encoding=CONFIG["encoding"]) as file:
        file.write(INDEX_HEADER)

        for post in posts:
            file.write(INDEX_POST_ENTRY.format(post.title,
                post.filename + CONFIG["ext"]["html"], post.date))


def read_config_file(config_file_path):
    """Read the configuration file.

    By default, daisy will look for a configuration file in
    ~/.config/daisy/config.json. See CONFIG_FILE_PATH for details.

    Arguments:
        config_file_path (str) - file path to check.                                

    Raises:
        FileNotFoundError: when the configuration file cannot be found.
    """
    # Check if the file path is valid.
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"{config_file_path} not found!")

    # Read configuration file.
    with open(config_file_path, "r") as file:
        CONFIG.update(json.load(file))


def check_dirs():
    """Checks certain information about directories.

    The specific information is as follows:
    - Which directory are we in? Move to the base directory if need be.
    - Are any directories missing? Create them possible.

    Raises:
        FileNotFoundError: when the template director cannot be found.
    """
    # Check which directory we are in, move up if need be.
    if CONFIG["dirs"]["blog"] in os.getcwd():
        os.chdir("..")

    if not os.path.exists(CONFIG["dirs"]["template"]):
        raise FileNotFoundError(f"{CONFIG['dirs']['template']} not found!")

    # Check and create output directories.
    if not os.path.exists(CONFIG["dirs"]["output"] + os.path.sep +
                          CONFIG["dirs"]["blog"]):
        os.makedirs(CONFIG["dirs"]["output"] + os.path.sep +
                    CONFIG["dirs"]["blog"])


def copy_content_files():
    """Copies files from the content directory to the output directory.

    If there is nothing to be copied, then this function does nothing.
    """
    try:
        distutils.dir_util.copy_tree(CONFIG["dirs"]["content"],
            CONFIG["dirs"]["output"] + os.path.sep +
            CONFIG["dirs"]["content"][1:])
    except distutils.errors.DistutilsFileError:
        pass


def setup(cli_arguments):
    """Reads configuration file, checks directories and copies contents files.

    Also sets the traceback limit to 0, so errors are more simple.

    Arguments:
        cli_arguments (argparse.Namespace) - the CLI arguments passed to the
        program.
    """
    sys.tracebacklimit = 0

    read_config_file(cli_arguments.config)
    check_dirs()
    copy_content_files()


def parse_arguments():
    """Parse arguments using argparse.

    Returns:
        argparse.Namespace: an empty Namespace object containing the
            arguments as variables.
    """
    parser = argparse.ArgumentParser(
            description="A CLI static site generator written in Python.",
            epilog="See https://github.com/hakmad/daisy for help."
            )

    # Setup parser with render options.
    render_options = parser.add_mutually_exclusive_group(required=True)
    render_options.add_argument("-a", "--all", action="store_true",
                                dest="all", help="convert all files")
    render_options.add_argument("-s", "--single", nargs="?", metavar="file",
                         dest="single", help="convert one file")

    # Setup parser with auxilliary options.
    parser.add_argument("-c", "--config", nargs="?", metavar="path",
                        dest="config", default=CONFIG_FILE_PATH,
                        help="path to configuration file")

    # Return parsed arguments:
    return parser.parse_args()


def render_all_posts():
    """Render all posts."""
    blog_posts = get_posts(CONFIG["dirs"]["blog"] + os.path.sep + "*" +
                           CONFIG["ext"]["md"])
    
    # Check if there are any blog posts.
    if len(blog_posts) > 0:
        print("Rendering blog posts to HTML")
        for post in blog_posts:
            print(f"Rendering {post.filename + CONFIG['ext']['md']}")
            post.render_html("blog")
 
        print("Generating index file")
        generate_index_file(blog_posts)

    else:
        print("No blog posts found")

    # Even if there are no blog posts, still render meta posts.
    print("Rendering meta posts to HTML")
    meta_posts = get_posts("*" + CONFIG["ext"]["md"])

    for post in meta_posts:
        print(f"Rendering {post.filename + CONFIG['ext']['md']}")
        post.render_html("meta")
 

def render_single_post(filename):
    """Render a single post.

    Arguments:
        filename (str): filename of post to render.

    Raises:
        FileNotFoundError: when the filename supplied is not found.
    """
    meta_filename = filename
    blog_filename = CONFIG["dirs"]["blog"] + os.path.sep + filename

    # Check if post is to be ignored.
    if (meta_filename or blog_filename) in CONFIG["ignored_files"]:
        print(f"{filename} in CONFIG['ignored_files'], exiting")
        sys.exit()

    # Check where the post actually is.
    if os.path.exists(blog_filename):
        # Rendering a blog post.
        print(f"Rendering {blog_filename} to HTML")

        blog_post = get_post(blog_filename)
        blog_post.render_html("blog")

        print(f"Adding {blog_filename} to index file")
        add_to_index_file(blog_post)

        print(f"Rendering {CONFIG['index_file']} to HTML")

        index = get_post(CONFIG["index_file"])
        index.render_html("meta")

    elif os.path.exists(meta_filename):
        # Rendering a meta post.
        print(f"Rendering {meta_filename} to HTML")

        meta_post = get_post(meta_filename)
        meta_post.render_html("meta")

    else:
        # Post doesn't exist, raise an error.
        raise FileNotFoundError(f"{filename} not found!")


### Main program. ###

def main():
    """Main program."""
    # Parse arguments.
    cli_arguments = parse_arguments()

    # Run setup.
    setup(cli_arguments)

    # Render all posts.
    if cli_arguments.all:
        render_all_posts()

    # Render a single post.
    elif cli_arguments.single:
        render_single_post(cli_arguments.single)
