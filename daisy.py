"""
Static Site Generator

A CLI static site generator written in Python.
"""


import glob
import jinja2
import markdown
import os


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
        # Drop last three characters of the filename, they're not needed.
        self.filename = filename[:-3]

        with open(filename, "r") as file:
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
        if post_type == "meta":
            template_file = "templates/meta.html"
        elif post_type == "blog":
            template_file = "templates/blog.html"

        # Render the HTML to the template.
        with open(template_file, "r") as file:
            template = jinja2.Template(file.read())

            self.html = template.render({
                "content": self.content,
                "title": self.title,
                "date": self.date,
                })

        # Write out full HTML to file.
        with open("output/" + self.filename + ".html", "w") as file:
            file.write(self.html)


def get_posts(path):
    """Create a list of Post objects from a path.

    Arguments:
        path (str): a path that glob uses to look for posts.

    Returns:
        [Post]: a list of Post objects.
    """
    post_list = []
    
    for file in glob.glob(path):
        post_list.append(Post(file))

    return post_list


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
    with open("index.md", "w") as file:
        file.write("title: Index\n\n")

        for post in posts:
            file.write("[{}]({}) ({})\n\n"


def check_dirs():
    """Checks if certain directories exist, and if not, creates them.

    Arguments:
        None

    Returns:
        None
    """
    if not os.path.exists("output/blog/"):
        os.makedirs("output/blog/")


if __name__ == "__main__":
    check_dirs()

    blog_posts = get_posts("blog/*.md")

    for post in blog_posts:
        post.render_html("blog")

    generate_index_file(blog_posts)

    meta_posts = get_posts("*.md")

    for post in meta_posts:
        post.render_html("meta")
