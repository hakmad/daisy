# daisy
`daisy` is a CLI static site generator written in Python.

## Usage
To convert all files, do: `daisy -a` or `daisy --all`.

To convert a single file, do: `daisy -s [file]` or `daisy --single [file]`.

### Expected Directory Structure
`daisy` expects the following directory structure:

```
templates/
    meta.html
    post.html
blog/
    post-1.md
    post-2.md
    ...
index.md
about.md
```

## Licence

This project is licensed under the
[MIT license](https://github.com/hakmad/daisy/blob/main/LICENSE). See
`LICENSE` for details.
