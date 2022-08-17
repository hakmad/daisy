"""
Static Site Generator

A CLI static site generator written in Python.
"""


import markdown
import jinja2


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
        with open(template, "r") as file:
            template = jinja2.Template(file.read())

            self.html = template.render({
                "content": self.content,
                "title": self.title,
                "date": self.date,
                })

        # Write out full HTML to file.
        with open("output/" + self.filename + ".html", "w") as file:
            file.write(self.html)
