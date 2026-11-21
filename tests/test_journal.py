"""Publishing checks use disposable projects, never the real content folder."""
from datetime import date
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import yaml

SOURCE = Path(__file__).resolve().parents[1]


class JournalPublishingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='wonder-journal-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for folder in ('scripts', 'admin', 'assets'):
            shutil.copytree(SOURCE / folder, self.root / folder)
        shutil.copy2(SOURCE / 'index.html', self.root / 'index.html')
        self.posts = self.root / 'content/posts'
        self.posts.mkdir(parents=True)
        self.output = self.root / 'public'

    def save(self, slug='publishing-check', **updates):
        props = dict(title='Temporary publishing check', date=date(2026, 11, 21),
                     category='Movement & Sensory Play', summary='Temporary summary',
                     cover='', published=False)
        props.update(updates)
        body = props.pop('body', '## Heading\n\nA **formatted** paragraph.\n')
        path = self.posts / (slug + '.md')
        path.write_text('---\n' + yaml.safe_dump(props, sort_keys=False, allow_unicode=True)
                        + '---\n' + body, encoding='utf-8')
        return path

    def build(self, expect_success=True, **overrides):
        env = os.environ.copy()
        for key in ('CONTEXT', 'HEAD', 'BRANCH', 'DEPLOY_PRIME_URL'):
            env.pop(key, None)
        env.update(overrides)
        result = subprocess.run([sys.executable, str(self.root / 'scripts/build_blog.py')],
                                env=env, text=True, capture_output=True)
        if expect_success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def read(self, path='journal/index.html'):
        return (self.output / path).read_text(encoding='utf-8')

    def test_save_publish_edit_unpublish_republish_delete(self):
        # Decap saves the same YAML frontmatter + Markdown file contract.
        article = self.save()
        page = self.output / 'journal/publishing-check/index.html'
        self.build()
        self.assertNotIn('Temporary publishing check', self.read())
        self.assertFalse(page.exists())
        self.assertFalse((self.output / 'content').exists())
        self.save(published=True)
        self.build()
        self.assertIn('href="/journal/publishing-check/"', self.read())
        self.assertIn('<strong>formatted</strong>', page.read_text())
        self.assertIn('November 21, 2026', page.read_text())
        self.save(published=True, title='Edited title', body='Updated paragraph.')
        self.build()
        self.assertIn('Edited title', self.read())
        self.assertIn('Updated paragraph.', page.read_text())
        self.assertNotIn('Temporary publishing check', self.read())
        self.save(published=False)
        self.build()
        self.assertFalse(page.exists())
        self.assertNotIn('publishing-check/', self.read())
        self.save(published=True)
        self.build()
        self.assertTrue(page.exists())
        article.unlink()
        self.build()
        self.assertFalse(page.exists())

    def test_only_boolean_true_publishes(self):
        for number, value in enumerate((False, None, 'false', 'true', 0, 1)):
            self.save(slug=f'hidden-{number}', published=value)
        missing = self.save(slug='missing-flag')
        missing.write_text(missing.read_text().replace('published: false\n', ''), encoding='utf-8')
        self.save(slug='visible', published=True)
        self.build()
        self.assertEqual([p.parent.name for p in (self.output / 'journal').glob('*/index.html')],
                         ['visible'])

    def test_cover_body_image_links_and_date_order(self):
        media = self.root / 'images/journal'
        media.mkdir(parents=True)
        shutil.copy2(self.root / 'assets/kw-logo.webp', media / 'check.webp')
        self.save(slug='older', published=True, date='2026-10-01')
        self.save(slug='newer', title='Newer article', published=True, date='2026-11-21',
                  cover='/images/journal/check.webp',
                  body='![Example](/images/journal/check.webp)\n\n[Books](/)')
        self.build()
        self.assertLess(self.read().index('/journal/newer/'), self.read().index('/journal/older/'))
        self.assertIn('src="/images/journal/check.webp"', self.read('journal/newer/index.html'))
        self.assertIn('href="/"', self.read('journal/newer/index.html'))
        self.assertEqual((self.output / 'images/journal/check.webp').read_bytes(),
                         (media / 'check.webp').read_bytes())

    def test_existing_drafts_stay_hidden_and_source_is_unchanged(self):
        shutil.copytree(SOURCE / 'content/posts', self.posts, dirs_exist_ok=True)
        before = {p.name: p.read_bytes() for p in self.posts.glob('*.md')}
        self.build(CONTEXT='production', HEAD='main')
        for name, raw in before.items():
            self.assertEqual((self.posts / name).read_bytes(), raw)
            props = yaml.safe_load(raw.decode('utf-8').split('---', 2)[1])
            if props.get('published') is not True:
                self.assertFalse((self.output / 'journal' / Path(name).stem).exists())
        self.assertEqual((self.output / 'index.html').read_bytes(), (SOURCE / 'index.html').read_bytes())
        self.assertFalse((self.output / 'tests').exists())
        self.assertFalse((self.output / 'scripts').exists())

    def test_production_editor_and_existing_categories(self):
        self.build(CONTEXT='production', HEAD='main')
        self.assertTrue((self.output / 'admin/index.html').exists())
        config = yaml.safe_load(self.read('admin/config.yml'))
        self.assertEqual(config['backend']['branch'], 'main')
        self.assertEqual(config['backend']['repo'], 'KiteWonder/kite-wonder-website')
        self.assertEqual(config['publish_mode'], 'simple')
        collection = config['collections'][0]
        self.assertEqual(collection['folder'], 'content/posts')
        fields = {f['name']: f for f in collection['fields']}
        self.assertIs(fields['published']['default'], False)
        self.assertIs(fields['published']['required'], False)
        for path in (SOURCE / 'content/posts').glob('*.md'):
            props = yaml.safe_load(path.read_text().split('---', 2)[1])
            self.assertIn(props['category'], fields['category']['options'])

    def test_preview_editor_writes_only_to_its_source_branch(self):
        original = (self.root / 'admin/config.yml').read_bytes()
        for context in ('deploy-preview', 'branch-deploy'):
            with self.subTest(context=context):
                self.build(CONTEXT=context, HEAD='fix/wonder-journal-publishing', BRANCH='main',
                           DEPLOY_PRIME_URL='https://preview.example.test')
                config = yaml.safe_load(self.read('admin/config.yml'))
                self.assertEqual(config['backend']['branch'], 'fix/wonder-journal-publishing')
                self.assertEqual(config['backend']['site_domain'], 'kite-wonder-website.netlify.app')
                self.assertEqual(config['site_url'], 'https://preview.example.test')
                self.assertEqual((self.root / 'admin/config.yml').read_bytes(), original)
        self.build(CONTEXT='production', HEAD='main')
        self.assertEqual(yaml.safe_load(self.read('admin/config.yml'))['backend']['branch'], 'main')

    def test_preview_without_safe_branch_fails(self):
        for head in ('', 'main'):
            with self.subTest(head=head):
                result = self.build(expect_success=False, CONTEXT='deploy-preview', HEAD=head)
                self.assertIn('Preview CMS requires a non-production HEAD branch.', result.stderr)

    def test_user_text_is_escaped_and_markdown_is_rendered(self):
        self.save(published=True, title='<script>title</script>', summary='<b>summary</b>',
                  body='<script>alert(1)</script>\n\n**Safe formatting**')
        self.build()
        page = self.read('journal/publishing-check/index.html')
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('<strong>Safe formatting</strong>', page)


if __name__ == '__main__':
    unittest.main()
