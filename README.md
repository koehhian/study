# Sam Koeh Study

Static research library for `study.samkoeh.com`.

## Publish with GitHub Pages
- Source: Deploy from a branch
- Branch: `main`
- Folder: `/ (root)`
- Custom domain: `study.samkoeh.com`

The `CNAME` file is already included.

## Search and agent discovery

After adding a page to the homepage/series index or editing titles/descriptions:

```sh
python3 scripts/build_discovery.py
```

Commit the generated changes together with the articles. This uses only Python's
standard library; GitHub Pages still serves plain static files.

The script follows local HTML links starting at the homepage, and updates:
- Canonical URLs, Open Graph metadata, Article/CollectionPage/WebSite JSON-LD.
- `sitemap.xml` (public pages only; no invented modification dates).
- `catalog.json` (titles, summaries, series positions, existing section anchors).
- `llms.txt` (optional reading index, not a search-ranking guarantee).
- `robots.txt` (allows crawlers; does not distinguish search from model training).

Only public HTML intended for readers should be linked from the site. Keep source
documents and private material out of this public repository. Existing article
scripts, citations and diagrams are not rewritten by the generator.

### Publication and indexing checklist

1. Resolve GitHub Pages HTTPS certificate errors and enable Enforce HTTPS before
   submitting the HTTPS sitemap. Confirm HTTPS works without bypassing warnings.
2. Commit and push the generated files; check `/sitemap.xml`, `/robots.txt`,
   `/catalog.json`, and article canonical URLs on the live site.
3. In Google Search Console, add the URL-prefix property
   `https://study.samkoeh.com/`. Complete account ownership verification (an HTML
   verification file can be committed at the repository root), then submit
   `sitemap.xml`. Do not remove the verification file afterward.
4. Inspect the homepage, series index and an article URL, and request indexing.
5. Add/import the site into Bing Webmaster Tools and submit the same sitemap.
6. Monitor indexing and real search queries; refine summaries and internal links
   around reader questions without changing historical claims for keywords.

Search-crawler access does not guarantee indexing, ranking, or AI citations.
No unsupported credentials, review claims, publication dates or ratings are added.
