import os

def generate_repo_files(path, task, brief):
    os.makedirs(path, exist_ok=True)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <title>{task}</title>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"/>
    </head>
    <body class="container text-center mt-5">
      <h1>{brief}</h1>
      <p>Generated automatically with LLM assist.</p>
      <div id="output">Waiting for evaluation...</div>
      <script>
        document.getElementById('output').textContent = 'Task {task} ready for evaluation.';
      </script>
    </body>
    </html>
    """

    readme_content = f"""
    # {task}

    ## Description
    {brief}

    ## Deployment
    Hosted using GitHub Pages.

    ## License
    MIT
    """

    license_text = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy...
"""

    with open(os.path.join(path, "index.html"), "w") as f:
        f.write(html_content)
    with open(os.path.join(path, "README.md"), "w") as f:
        f.write(readme_content)
    with open(os.path.join(path, "LICENSE"), "w") as f:
        f.write(license_text)

def update_repo_for_round2(path, task, brief):
    generate_repo_files(path, task, brief)
    with open(os.path.join(path, "index.html"), "a") as f:
        f.write("<p>Round 2 Updates Applied</p>")
