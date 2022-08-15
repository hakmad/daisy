import markdown
import jinja2


class Post:
    """Class to represent a single post.

    Attributes:
    filename (str) - filename of the post (not including the extension).
    content (str) - content of the post as a HTML fragment.
    html (str) - fully rendered HTML of the post.
    title (str) - title of the post.
    date (str) - date of the post (in the ISO 8601 format).
    """
    def __init__(self, filename):
        """Setup the Post object.

        Opens the file containing the post content and sets up the Post
        object with the relevant attributes.

        Arguments:
        filename (str) - filename of the post to open.

        Returns:
        None
        """
        self.filename = filename[:-3]

        with open(filename, "r") as file:
            md_reader = markdown.Markdown(extensions=["meta"])

            self.content = md_reader.convert(file.read())

            self.title = md_reader.Meta["title"].pop()
            
            try:
                self.date = md_reader.Meta["date"].pop()
            except KeyError:
                self.date = None

    def render_html(self, post_type):
        """Render the partial HTML to a full HTML page and write it
        out to a file.

        Arguments:
        post_type (str) - type of template to use.

        Returns:
        None
        """
        if post_type == "meta":
            template_file = "templates/meta.html"
        elif post_type == "blog":
            template_file = "templates/blog.html"

        with open(template, "r") as file:
            template = jinja2.Template(file.read())

            self.html = template.render({
                "content": self.content,
                "title": self.title,
                "date": self.date,
                })

        with open("output/" + self.filename + ".html", "w") as file:
            file.write(self.html)
