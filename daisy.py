import markdown

class Post:
    def __init__(self, filename):
        self.filename = filename[:-3]

        with open(filename, "r") as file:
            md_reader = markdown.Markdown(extensions=["meta"])

            self.content = md_reader.convert(file.read())

            self.title = md_reader.Meta["title"].pop()
            self.date = md_reader.Meta["date"].pop()
