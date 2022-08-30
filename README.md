# daisy
`daisy` is a CLI static site generator written in Python.

## Installation

To install, do:

```
git clone https://github.com/hakmad/daisy
cd daisy
pip install .
```

## Usage

`daisy` has 2 options: render all posts or render a single post.

### Render All Posts

To render all posts, do: `daisy -a` or `daisy --all`. This will:

1. Recursively copy `.content/` to `.output/content/`.
2. Render all Markdown files in `blog/` using the `blog.html` template and
   place them in the `.output/blog/`.
3. Produce a new `index.md` with links to all the posts in the `blog/` in
   reverse chronological order.
4. Render all Markdown files in the top level directory using the
   `meta.html` template and place them in the `.output/`.

### Render a Single Posts

To render a single posts, do: `daisy -s [post]` or `daisy --single [post]`.
This will:

1. Recursively copy `.content/` to `.output/content/`.
2. If `[file]` is in `blog/`:
    a. Render `[file]` using the `blog.html` template and place it in
       `.output/blog/`.
    b. Add a link to the rendered `[file]` to the top of `index.md` and
       re-render `index.md`.
3. Otherwise, if `[file]` is in the top level directory:
    a. Render `[file]` using the `meta.html` template and place it in
       `.output/`.

## Configuration

The following sections describe the configuration of `daisy`.

### Blog Post Structure

Blog posts are posts which contain actual blog content. `daisy` expects the
following structure for these:

```
title: [title]
date: [date]

[actual post content]
```

### Meta Post Structure

Meta posts are posts which contain meta information (e.g. an about page).
`daisy` expects the following structure for these:

```
title: [title]

[actual post content]
```

### Directory Structure

`daisy` expects the following directory structure:

```
.content/
    stylesheet.css
    favicon.ico
    images/
    	...
.templates/
    meta.html
    post.html
blog/
    post-1.md
    post-2.md
    ...
index.md
about.md
```

### Output

`daisy` will produce a new, top level directory called `.output` which
contains the following:

```
.output/
    content/
    	stylesheet.css
	favicon.ico
	images/
	    ...
    blog/
    	post-1.html
	post-2.html
	...
    index.html
    about.html
```

## Licence

This project is licensed under the
[MIT license](https://github.com/hakmad/daisy/blob/main/LICENSE). See
`LICENSE` for details.
