# Publish and Deploy

## GitHub repository

1. Create a new repository on GitHub.
2. Initialize git locally if needed.
3. Add the remote.
4. Push the project.

Example:

```bash
git init -b main
git add .
git commit -m "Initial BioWorkbench starter"
git remote add origin https://github.com/your-name/your-repo.git
git push -u origin main
```

## Continuous integration

The project already includes a GitHub Actions workflow at `.github/workflows/ci.yml`.

That workflow:

- installs the package with test dependencies
- runs `pytest`
- validates the core logic every time you push or open a pull request

## GitHub Pages

Use the `docs/` folder as the GitHub Pages publishing source.

That gives you:

- a public landing page at `docs/index.html`
- a simple place to explain the project
- a clean link hub for the repository and live demo

After the first push:

1. Open the repository on GitHub.
2. Go to `Settings > Pages`.
3. Under Build and deployment, choose `Deploy from a branch`.
4. Select the `main` branch and the `/docs` folder.
5. Save the settings and wait for Pages to publish.

## Live public demo

For a real interactive Python demo, deploy `streamlit_app.py` to a Python-friendly host.

Suggested setup:

1. Push the repository to GitHub.
2. Connect the repository to your hosting platform.
3. Use `streamlit_app.py` as the app entrypoint.
4. Install dependencies from `requirements-demo.txt`.

## GitHub Pages

GitHub Pages is still useful for:

- a landing page
- docs
- screenshots
- a link to the live Streamlit demo

Use GitHub Pages for the public project site, but use a Python app host for the interactive demo itself.
