#!/usr/bin/env python3
# Build Kite & Wonder static site + The Wonder Journal from Markdown files.
from pathlib import Path
from datetime import date,datetime
from html import escape
from urllib.parse import quote
import os, re, shutil, yaml, mistune

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'public'
POSTS=ROOT/'content'/'posts'

# Rebuild public output each time so removed/unpublished articles disappear.
if DIST.exists(): shutil.rmtree(DIST)
(DIST/'journal').mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'index.html',DIST/'index.html')
shutil.copytree(ROOT/'admin',DIST/'admin',dirs_exist_ok=True)

# A preview editor must never save test content to the production branch.
# Netlify HEAD is the source branch (BRANCH can be the PR's target branch).
if os.environ.get('CONTEXT') in ('deploy-preview','branch-deploy'):
    branch=os.environ.get('HEAD','').strip()
    if not branch or branch == 'main':
        raise ValueError('Preview CMS requires a non-production HEAD branch.')
    config_path=DIST/'admin'/'config.yml'
    config=yaml.safe_load(config_path.read_text(encoding='utf-8'))
    config['backend']['branch']=branch
    preview_url=os.environ.get('DEPLOY_PRIME_URL','').strip()
    if preview_url:
        config['site_url']=preview_url
        config['display_url']=preview_url+'/journal/'
    config['collections'][0]['description']='WERSJA PODGLĄDOWA: zapisy trafiają tylko do gałęzi testowej. Nie zmieniają strony publicznej.'
    config_path.write_text(yaml.safe_dump(config,allow_unicode=True,sort_keys=False),encoding='utf-8')

for folder in ['assets','images']:
    p=ROOT/folder
    if p.exists(): shutil.copytree(p,DIST/folder,dirs_exist_ok=True)

md = mistune.create_markdown(escape=True,plugins=['table','strikethrough'])
CSS = '''
:root{--paper:#f8f5ed;--ink:#283b34;--muted:#60736b;--green:#264238;--terra:#d17b5c;--border:#dcded4;--white:#fffefa}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--ink);line-height:1.75;-webkit-font-smoothing:antialiased}a{color:inherit}.wrap{width:min(1080px,calc(100% - 42px));margin:0 auto}img{display:block;max-width:100%}
header{position:sticky;top:0;background:#faf8f0f0;backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:4}.head{min-height:94px;display:flex;justify-content:space-between;gap:24px;align-items:center}.logo img{width:235px;height:auto}.headnav{display:flex;gap:24px;align-items:center}.headnav a{text-decoration:none;font-size:.9rem;font-weight:650}.headnav a:hover,.back:hover{color:var(--terra)}.eyebrow{text-transform:uppercase;letter-spacing:.15em;font-size:.74rem;font-weight:750;color:#9a604e}.hero{padding:76px 0 54px}.hero h1,.article-title{font-family:Georgia,serif;font-size:clamp(3.2rem,6.6vw,5.7rem);font-weight:normal;letter-spacing:-.056em;line-height:1.08;color:var(--green);margin:18px 0}.lead{font-size:1.15rem;color:var(--muted);max-width:720px}.archive{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;padding-bottom:90px}.postcard{border:1px solid var(--border);background:var(--white);border-radius:18px;overflow:hidden;display:flex;flex-direction:column}.postcard .cover{height:255px;background:linear-gradient(120deg,#dfe8da,#f5e3d4);display:grid;place-items:center}.cover img{width:100%;height:100%;object-fit:cover}.postcard .content{padding:29px 30px;display:flex;flex-direction:column;flex:1}.postcard h2{font-family:Georgia,serif;font-size:1.85rem;line-height:1.2;font-weight:normal;margin:12px 0;color:var(--green)}.postcard p{margin:0 0 24px;color:var(--muted)}.postcard a.more{text-decoration:underline;text-underline-offset:4px;font-weight:750;color:var(--green);margin-top:auto}.placeholder{background:#fffefa;border-radius:22px;border:1px solid var(--border);padding:70px 35px;text-align:center;grid-column:1/-1}.placeholder h2{font-family:Georgia,serif;font-size:2.6rem;font-weight:normal;color:var(--green);margin:4px 0 10px}.placeholder p{color:var(--muted);max-width:510px;margin:auto}.btn{display:inline-block;background:var(--green);color:#fff;text-decoration:none;border-radius:100px;padding:13px 22px;font-weight:700;margin-top:25px}.article-main{max-width:820px;margin:auto;padding:64px 22px 100px}.back{text-decoration:none;font-size:.85rem;font-weight:700;color:#486452}.meta{font-size:.79rem;color:#796e62;text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-top:23px}.article-lead{font-size:1.18rem;color:var(--muted);line-height:1.75}.article-cover{margin:35px 0 40px;border-radius:18px;overflow:hidden}.article-cover img{width:100%;height:auto;max-height:530px;object-fit:cover}.article-body{font-size:1.04rem;line-height:1.95;overflow-wrap:anywhere}.article-body p{margin:1.1em 0}.article-body h2,.article-body h3{font-family:Georgia,serif;font-weight:normal;line-height:1.25;color:var(--green);margin:1.6em 0 .4em}.article-body h2{font-size:2rem}.article-body h3{font-size:1.5rem}.article-body img{border-radius:14px;margin:24px auto}.article-body a{color:#a55944;text-underline-offset:3px}.bookreco{margin-top:55px;border:1px solid #d9e0d4;background:#eef1e7;border-radius:18px;padding:28px}.bookreco h2{font-size:1.5rem;color:var(--green);font-family:Georgia,serif;font-weight:normal;margin:0 0 10px}.bookreco p{margin:0;color:#597163}.bookreco a{display:inline-block;margin-top:18px;font-weight:750;text-underline-offset:3px;color:var(--green)}footer{background:#21392f;color:#f8f5ed;padding:26px 0;font-size:.85rem}footer a{color:inherit}footer .wrap{display:flex;justify-content:space-between;flex-wrap:wrap;gap:20px}
@media(max-width:680px){.head{min-height:74px}.logo img{width:min(190px,53vw)}.headnav{gap:13px}.headnav a{font-size:.8rem}.hero{padding:53px 0 35px}.hero h1{font-size:3.5rem}.archive{grid-template-columns:1fr}.postcard .cover{height:220px}.article-main{padding-top:46px}.article-title{font-size:3rem}.placeholder{padding:50px 20px}}
'''

def fmt_date(x):
    if isinstance(x,(date,datetime)): return x.strftime('%B %d, %Y').replace(' 0',' ')
    try: return datetime.strptime(str(x)[:10],'%Y-%m-%d').strftime('%B %d, %Y').replace(' 0',' ')
    except ValueError: return str(x)

def slugify(s):
    s=re.sub(r'[^a-zA-Z0-9-]+','-',s.lower()).strip('-')
    return s or 'journal-post'

def safe_url(path):
    p=str(path or '').strip()
    if not p or p.startswith(('javascript:','data:','//')): return ''
    return p if p.startswith(('/', 'https://','http://')) else '/'+p.lstrip('./')

def doc(title,description,body):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f8f5ed"><meta name="description" content="{escape(description,quote=True)}"><title>{escape(title)} | Kite &amp; Wonder</title><style>{CSS}</style></head><body><header><nav class="wrap head" aria-label="Main navigation"><a class="logo" href="/" aria-label="Kite and Wonder home"><img src="/assets/kw-logo.webp" alt="Kite & Wonder"></a><div class="headnav"><a href="/">Our books</a><a href="/journal/">Journal</a></div></nav></header>{body}<footer><div class="wrap"><span>© Kite &amp; Wonder · Play. Explore. Grow.</span><span><a href="/">Books</a> &nbsp; · &nbsp; <a href="/journal/">Journal</a></span></div></footer></body></html>'''

published=[]
for file in POSTS.glob('*.md'):
    raw=file.read_text(encoding='utf-8')
    match=re.match(r'\A---\s*\n(.*?)\n---\s*\n(.*)\Z', raw, re.S)
    if not match: print('Skipped invalid frontmatter:',file.name);continue
    props=yaml.safe_load(match.group(1)) or {}
    if props.get('published') is not True: continue
    title=str(props.get('title') or 'Untitled article')
    summary=str(props.get('summary') or '')
    category=str(props.get('category') or 'The Wonder Journal')
    cover=safe_url(props.get('cover'))
    slug=slugify(file.stem)
    article={**props,'title':title,'summary':summary,'category':category,'cover':cover,'slug':slug,'body':md(match.group(2))}
    article['display_date']=fmt_date(props.get('date') or '')
    article['sort_date']=str(props.get('date') or '')
    published.append(article)

published.sort(key=lambda a:a['sort_date'],reverse=True)
items=[]
for post in published:
    img=f'<img src="{escape(post["cover"],quote=True)}" alt="" loading="lazy">' if post['cover'] else '<span aria-hidden="true" style="font-size:4rem;color:#77937c">✳</span>'
    items.append(f'''<article class="postcard"><div class="cover">{img}</div><div class="content"><span class="eyebrow">{escape(post['category'])} · {escape(post['display_date'])}</span><h2>{escape(post['title'])}</h2><p>{escape(post['summary'])}</p><a class="more" href="/journal/{quote(post['slug'])}/">Read article ↗</a></div></article>''')
    pic=f'<figure class="article-cover"><img src="{escape(post["cover"],quote=True)}" alt="" loading="eager"></figure>' if post['cover'] else ''
    recommended='https://www.amazon.com/dp/B0HP5WT63N'
    book='Playful Minutes: MOVE'
    if post['category']=='Learning Through Play': book='Picture Sudoku';recommended='https://www.amazon.com/dp/B0HRS4BGFX'
    body=f'''<main class="article-main"><a class="back" href="/journal/">← Back to The Wonder Journal</a><p class="meta">{escape(post['category'])} · {escape(post['display_date'])}</p><h1 class="article-title">{escape(post['title'])}</h1><p class="article-lead">{escape(post['summary'])}</p>{pic}<article class="article-body">{post['body']}</article><aside class="bookreco"><h2>Keep the play going.</h2><p>Explore {escape(book)}, an activity book from Kite &amp; Wonder.</p><a href="{recommended}" target="_blank" rel="noopener noreferrer">View the book on Amazon ↗</a></aside></main>'''
    dest=DIST/'journal'/post['slug']
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'index.html').write_text(doc(post['title'],post['summary'],body),encoding='utf-8')

if not items:
    items=['''<section class="placeholder"><span class="eyebrow">Articles coming soon</span><h2>Something wonderful is taking shape.</h2><p>The Wonder Journal will soon bring you simple ideas for movement, speech and connection, and learning through play. In the meantime, meet our books.</p><a class="btn" href="/">Explore our books ↗</a></section>''']
intro=f'''<main><section class="hero"><div class="wrap"><span class="eyebrow">Kite &amp; Wonder</span><h1>The Wonder Journal.</h1><p class="lead">Little ideas for big discoveries. Thoughtful, practical inspiration for movement, speech, connection and learning through everyday play.</p></div></section><section class="wrap archive" aria-label="Journal articles">{''.join(items)}</section></main>'''
(DIST/'journal'/'index.html').write_text(doc('The Wonder Journal','Ideas for movement, speech and learning through play from Kite & Wonder.',intro),encoding='utf-8')
print(f'Built homepage and journal with {len(published)} visible article(s) into: {DIST}')
