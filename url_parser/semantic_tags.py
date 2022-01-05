semantic_tags = """<article>
    <aside>
    <details>
    <figcaption>
    <figure>
    <footer>
    <header>
    <main>
    <mark>
    <nav>
    <section>
    <summary>
    <time>
    <p>
    <ul>
    <h1>
    <h2>
    <h3>
    <h4>
    <h5>"""
semantic_tags = [x.strip().replace("<", "").replace(">", "") for x in semantic_tags.split("\n")]
# print(semantic_tags)