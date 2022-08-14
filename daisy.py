import markdown
import jinja2

class Post:
    def __init__(self, filename):
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
