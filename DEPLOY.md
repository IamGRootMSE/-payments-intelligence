# Deployment

## GitHub Pages (default)

In the repository's **Settings > Pages**, select **Deploy from a branch**, then
**main** and **/docs**, and save. GitHub publishes the committed static files;
no Python build is needed during deployment. `docs/.nojekyll` disables Jekyll.

Repository: https://github.com/IamGRootMSE/-payments-intelligence

Site: https://IamGRootMSE.github.io/-payments-intelligence/

The quality workflow runs from the repository root on main pushes and pull
requests. The optional `pages.yml` workflow is manual to avoid competing with
branch publishing. To use it instead, change the Pages source to **GitHub
Actions**, then run **deploy-payments-intelligence-pages** on main.

## Local preview and rebuild

Run `python -m http.server 8000 --directory docs` from the repository root and
open http://localhost:8000. The dashboard loads `data.json` using a relative URL,
so it also works under the GitHub Pages repository prefix. Opening `index.html`
directly with a `file://` URL cannot reliably load the data.

To regenerate the published data, install `requirements.txt`, run
`python src/pipeline.py`, run `python -m pytest -q` and
`node --test tests/site.test.cjs`, then commit the generated files.

## Vercel

Import the repository as a static project. `vercel.json` sets `docs` as the output
directory. No framework or build command is required.

## Recruiter link

Use the live dashboard as the primary project link and the repository as the
source-code link. The decision memo is at `decision-memo.html` under the site URL.
