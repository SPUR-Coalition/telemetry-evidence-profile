# CMS/editor round-trip fixtures for the C2PA text survivability matrix

Contributed by @jchomat in erik-sv/telemetry#1 and moved here with the #21 split.

Infra used to produce the `wordpress_editor_round_trip` and
`spip_editor_round_trip` rows in
[`survivability-c2pa-text.json`](../fixtures/survivability-c2pa-text.json).
These two rows require a real "publish and retrieve" round trip through
named software, not an in-process transform - the compose stack here
provides real, disposable WordPress and SPIP installs to do that against.

## Launch

```sh
docker compose -f modules/fingerprint-schemes/cms-survivability/docker-compose.yml up -d --build
```

- WordPress: http://localhost:8080
- SPIP: http://localhost:8081

## Protocol

1. Decode the checked-in fixture's `marked_text_unicode_escape` (from
   `fixtures/survivability-c2pa-text.json`) into the real marked string:

   ```python
   import codecs
   escaped = "Caf\\xe9 provenance sample.\\ufeff...."  # exact fixture value
   marked_text = codecs.decode(escaped.encode("ascii"), "unicode_escape")
   ```

2. **WordPress** - install with WP-CLI, then create and publish a post with
   `marked_text` as its content via stdin (avoids shell-mangling the
   invisible characters):

   ```sh
   docker exec -w /var/www/html <wp-container> \
     wp core install --allow-root --url=http://localhost:8080 \
     --title=Test --admin_user=admin --admin_password=<pass> --admin_email=test@example.com
   printf '%s' "$marked_text" | docker exec -i -w /var/www/html <wp-container> \
     wp post create --allow-root --post_status=publish -
   ```

   Fetch the published permalink (`wp post get <id> --field=url`) with
   `curl` and re-extract the manifest from the rendered `entry-content` HTML
   using `check_survivability.py`'s `_extract_manifest`.

3. **SPIP** - complete the web installer (`/ecrire/?exec=install`, a
   multi-step form: chmod check -> DB connection -> DB selection -> admin
   account -> finish), then insert an article directly into
   `spip_articles.texte` with `marked_text` as the value. This is
   equivalent to typing the same string into the article-editing textarea:
   SPIP applies its typography/paragraphing filters (`propre()`, `typo()`)
   at **display** time via the `#TEXTE` squelette tag, not at save time, so
   a direct DB write and an editor save produce the same stored value.

   Fetch the published article (`spip.php?page=article&id_article=<id>`)
   and re-extract the manifest from the rendered `.texte` block.

4. Record the captured rendered substring (from the marker onward) as
   `reproduction.captured_rendered_text_unicode_escape` on the matrix row,
   and note the exact software versions used. `check_survivability.py`
   decodes and checks it like any other row.

## Known pitfalls (hit during the first run - see git.spip.net, not GitHub)

- **SPIP is not on GitHub.** `github.com/spip/spip` does not exist;
  `git.spip.net/spip/spip.git` is the real repo. The core repo alone
  500s on every request (install wizard included) - it needs two more
  git.spip.net repos, listed by exact tag in the core's `plugins-dist.json`:
  `spip/urls.git` at `plugins-dist/urls_etendues` (URL routing; without it
  the install wizard itself throws `Missing a url function for type
  propres`) and `spip/dist.git` at `squelettes-dist` (public site templates;
  without it every public page throws in `assembler.php`). Both are baked
  into `Dockerfile.spip` here.
- **mbstring needs `libonig-dev`** (oniguruma) on the `php:8.2-apache` base
  image, and **composer must run before `git` is purged** from the image -
  the plugin/squelette clones above need `git` too, so do that step before
  purging.
- WordPress needed no such workarounds: `wordpress:latest` + WP-CLI just
  worked.

## Points of caution not yet exercised

- Client-side paste handling inside the WordPress block editor or SPIP's
  admin textarea (browser-only, needs a headless browser - not attempted
  here). What's tested is the storage + server-side render path.
- Arc XP is proprietary with no publicly reproducible instance; it is not
  approximated here and is left `not_tested` in the matrix rather than
  simulated.
