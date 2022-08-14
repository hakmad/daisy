import markdown

class Post:
    def __init__(self, filename):
        self.filename = filename[:-3]

        with open(filename, "r") as file:
            md_reader = markdown.Markdown()

            self.content = md_reader.convert(file.read())
