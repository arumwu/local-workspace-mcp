"""Exercise the exact-file watcher API used by md-to-pdf after the v4 override."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    not (ROOT / "node_modules").exists(), reason="Run npm ci first"
)


def test_pdf_dependency_load_and_literal_file_watch(tmp_path):
    script = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const {createRequire} = require('node:module');
const pdfRequire = createRequire(require.resolve('md-to-pdf'));
const {watch} = pdfRequire('chokidar');
assert.equal(typeof require('md-to-pdf').mdToPdf, 'function');
(async () => {
  // Braces are literal filename characters, not a request for pattern expansion.
  const file = path.join(process.argv[1], 'literal{a,b}.md');
  await fs.writeFile(file, '# Before');
  const watcher = watch([file], {ignoreInitial: true});
  const deadline = setTimeout(() => { console.error('watch timeout'); process.exit(1); }, 8000);
  try {
    await new Promise((resolve, reject) => watcher.once('ready', resolve).once('error', reject));
    const changed = new Promise((resolve, reject) => watcher.once('change', resolve).once('error', reject));
    await fs.writeFile(file, '# After');
    assert.equal(await changed, file);
    assert.equal(await fs.readFile(file, 'utf8'), '# After');
  } finally {
    clearTimeout(deadline);
    await watcher.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    subprocess.run(["node", "-e", script, str(tmp_path)], cwd=ROOT, check=True, timeout=15)


def test_image_and_yaml_compatibility_after_dependency_updates():
    script = r"""
const assert = require('node:assert/strict');
const {createRequire} = require('node:module');
const {execFileSync} = require('node:child_process');
const sharp = require('sharp');
const matter = require('gray-matter');
const yamlRequire = createRequire(require.resolve('js-yaml'));
assert.equal(yamlRequire('argparse/package.json').version, '2.0.1');
assert.throws(() => yamlRequire.resolve('sprintf-js'), {code: 'MODULE_NOT_FOUND'});
const yaml = 'title: "測試"\ncount: 2\n';
const parsed = matter(`---\n${yaml}---\n# Content\n`);
assert.deepEqual(parsed.data, {title: '測試', count: 2});
assert.deepEqual(matter(matter.stringify('# Content\n', parsed.data)).data, parsed.data);
const cli = require.resolve('js-yaml/bin/js-yaml.js');
const result = execFileSync(process.execPath, [cli], {input: yaml, encoding: 'utf8'});
assert.deepEqual(JSON.parse(result), parsed.data);
(async () => {
  const image = await sharp({create: {width: 2, height: 3, channels: 4, background: '#123456'}})
    .png().toBuffer();
  const metadata = await sharp(image).metadata();
  assert.equal(metadata.width, 2);
  assert.equal(metadata.height, 3);
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True, timeout=15)
