KITE & WONDER — THE WONDER JOURNAL
================================================
This is a FULL PROJECT, not a normal Netlify Drop ZIP.

GOAL
Publish articles from a phone via Pages CMS. Posts you save there will be
written to GitHub, and Netlify will automatically build your live website.

ONE-TIME SETUP (preferably from a computer):
1. Create a FREE GitHub account: https://github.com/signup
2. Create a new private GitHub repository (for example kite-wonder-site).
3. Upload ALL of the files from this ZIP into the ROOT of the repository.
   Keep .pages.yml, netlify.toml, index.html and the folders in place.
   If GitHub web upload skips hidden files, create .pages.yml separately.
4. In Netlify, connect your GitHub repo to a website.
   The netlify.toml automatically specifies how the site is built.
   Note: if your existing site was published by manual drag-and-drop,
   check its site settings or choose a new site and later move the domain;
   simply uploading this ZIP with Netlify Drop will NOT activate a CMS.
5. Go to https://app.pagescms.org and log in with GitHub.
   Authorize the Pages CMS GitHub App for the repository.
6. Open Journal articles in Pages CMS. Add title, date, category,
   short description, optional cover picture and article body.
   Turn 'Show on website' on, then save.
7. Netlify will automatically publish the updated journal from GitHub.

DRAFTS
An example post in content/posts/sample-draft.md is not public.
Keep 'Show on website' off until an article is ready.

SITE URLs
Homepage: / | Blog index: /journal/ | Individual article: /journal/<slug>/

WHAT YOU SHOULD NOT DO
- Do not delete .pages.yml or netlify.toml.
- Do not continue manual ZIP updates after switching to automatic deployment.
- Do not share your GitHub password or authorization codes.

PROJECT CONTENT
- index.html: your current published book catalogue plus Journal section
- content/posts/: articles
- images/blog/: uploaded article images
- .pages.yml: edit fields shown in Pages CMS
- scripts/build_blog.py: page generation logic
- netlify.toml: automatic build settings
- public/: generated output for Netlify, created on deploy; not in source ZIP
