# cg_scrape_sets.py
# Purchase-set scraper for churchillgowns.com
# - Finds Masters/Bachelors product pages even if collections are JS-rendered
# - Ignores "purchase" links that are PRODUCTS (e.g., /products/purchase-upgrade)
# - Falls back to scanning the UNIVERSITY PAGE itself for direct Masters/Bachelors product links
# - Extracts ALL gallery images in high-res (data-original-src / srcset max / _1200x)
# - Saves under output/<University>/<Masters|Bachelors> with a manifest.csv

import re, os, csv, time, random, argparse, json
from pathlib import Path
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser
import requests
from bs4 import BeautifulSoup

BASE = "https://churchillgowns.com"
INDEX_URL = f"{BASE}/pages/select-your-university"
UA = "Mozilla/5.0 (compatible; cg-scraper/2.2; +https://example.org/)"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

# Accept any “purchase” COLLECTION (ignore products)
RE_ANY_PURCHASE_COLLECTION = re.compile(r"^/collections/[^\"'>]*purchase[^\"'>]*$", re.I)

# Masters/Bachelors product handles (singular/plural; require "graduation-set")
# (A) with collection prefix: /collections/.../products/...
RE_MASTERS_URL_COLL = re.compile(
    r"""(?P<u>(?:https?:)?//?churchillgowns\.com)?(?P<p>/collections/[^\s"'>]+/products/[^\s"'>]*(?:master|masters|postgrad)[^\s"'>]*graduation-set[^\s"'>]*)""",
    re.I,
)
RE_BACHELORS_URL_COLL = re.compile(
    r"""(?P<u>(?:https?:)?//?churchillgowns\.com)?(?P<p>/collections/[^\s"'>]+/products/[^\s"'>]*(?:bachelor|bachelors|undergrad)[^\s"'>]*graduation-set[^\s"'>]*)""",
    re.I,
)
# (B) direct product links without collection prefix: /products/...
RE_MASTERS_URL_NOPREFIX = re.compile(
    r"""(?P<u>(?:https?:)?//?churchillgowns\.com)?(?P<p>/products/[^\s"'>]*(?:master|masters|postgrad)[^\s"'>]*graduation-set[^\s"'>]*)""",
    re.I,
)
RE_BACHELORS_URL_NOPREFIX = re.compile(
    r"""(?P<u>(?:https?:)?//?churchillgowns\.com)?(?P<p>/products/[^\s"'>]*(?:bachelor|bachelors|undergrad)[^\s"'>]*graduation-set[^\s"'>]*)""",
    re.I,
)

# Shopify size suffix like _250x.jpg or {width}x.jpg
RE_SIZE_SUFFIX = re.compile(r"(_|\-)(\d{2,4})x(\d{2,4})(?=\.)(?P<ext>\.\w+)$", re.I)

def log(msg): 
    print(msg, flush=True)

def sanitize(x: str) -> str:
    return re.sub(r"[\\/:*?\"<>|]", "_", re.sub(r"\s+"," ", (x or "").strip()))

def absolutize(u: str) -> str:
    if not u: return u
    if u.startswith("//"): return "https:" + u
    if u.startswith("/"):  return urljoin(BASE, u)
    if u.startswith("http"): return u
    return urljoin(BASE, u)

def polite_get(s, url, robots, delay=(0.3,0.8), retries=3, backoff=1.6):
    try:
        if robots and not robots.can_fetch(UA, url):
            raise PermissionError(f"robots.txt disallows: {url}")
    except Exception:
        pass
    last = None
    for i in range(retries):
        try:
            r = s.get(url, headers=HEADERS, timeout=30)
            last = r
            if r.status_code in (429,500,502,503,504):
                raise requests.HTTPError(f"retryable {r.status_code}")
            r.raise_for_status()
            time.sleep(random.uniform(*delay))
            return r
        except Exception:
            if i == retries - 1:
                if last is not None:
                    log(f"[HTTP ERROR] {url} -> {last.status_code}")
                raise
            time.sleep((backoff**i) + random.random())

def parse_unis(index_html: str):
    soup = BeautifulSoup(index_html, "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href*='/pages/']"):
        href = a.get("href") or ""
        txt = a.get_text(strip=True)
        if not txt or "/pages/" not in href: 
            continue
        full = urljoin(BASE, href)
        if full not in seen:
            seen.add(full); out.append((txt, full))
    return out

def find_purchase_collection(university_html: str):
    """
    Return the best 'Purchase' COLLECTION URL for a university page.
    Strictly returns /collections/... only. Ignores /products/... (e.g., /products/purchase-upgrade).
    """
    soup = BeautifulSoup(university_html, "html.parser")
    candidates = []

    # 1) Visible text containing "Purchase" that points to a collection
    for a in soup.select("a[href]"):
        href_raw = a.get("href") or ""
        href = href_raw.strip()
        text = (a.get_text(" ", strip=True) or "").lower()
        if "purchase" in text:
            # only keep if it's a collection
            if href.startswith("/collections/") and RE_ANY_PURCHASE_COLLECTION.search(href):
                candidates.append(href)

    # 2) Any collection href containing "purchase"
    for a in soup.select("a[href^='/collections/']"):
        href = (a.get("href") or "").strip()
        if RE_ANY_PURCHASE_COLLECTION.search(href):
            candidates.append(href)

    # De-dup & absolutize & prefer '/collections/...purchase...' only
    seen = []
    uniq = set()
    for href in candidates:
        full = absolutize(href)
        if full not in uniq:
            uniq.add(full)
            seen.append(full)

    return seen[0] if seen else None

def pick_largest_from_srcset(srcset: str) -> str:
    candidates = []
    for part in (srcset or "").split(","):
        p = part.strip()
        if not p: 
            continue
        bits = p.split()
        url = absolutize(bits[0])
        w = 0
        if len(bits) > 1 and bits[1].endswith("w"):
            try: w = int(bits[1][:-1])
            except: w = 0
        candidates.append((w, url))
    if not candidates: 
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def upgrade_to_1200x(u: str) -> str:
    if not u: return u
    u = u.replace("{width}x", "1200x")
    m = RE_SIZE_SUFFIX.search(u)
    if m:
        ext = m.group("ext")
        return RE_SIZE_SUFFIX.sub(r"_1200x" + ext, u)
    return u

def extract_all_gallery_images(product_html: str) -> list:
    soup = BeautifulSoup(product_html, "html.parser")
    urls = []

    gallery = soup.select_one(".Product__Gallery .Product__Slideshow")
    if gallery:
        for img in gallery.select(".Product__SlideItem img"):
            full = img.get("data-original-src")
            if not full:
                full = pick_largest_from_srcset(img.get("data-srcset") or img.get("srcset") or "")
            if not full:
                full = img.get("data-src") or img.get("src")
            full = upgrade_to_1200x(absolutize(full))
            if full: 
                urls.append(full)

        for ns in gallery.select("noscript"):
            ns_soup = BeautifulSoup(ns.decode_contents(), "html.parser")
            for img in ns_soup.select("img[src]"):
                full = upgrade_to_1200x(absolutize(img.get("src")))
                if full: 
                    urls.append(full)

    # thumbnails as backup
    thumbs = soup.select(".Product__SlideshowNav .Product__SlideshowNavImage img")
    for t in thumbs:
        full = upgrade_to_1200x(absolutize(t.get("src")))
        if full: 
            urls.append(full)

    seen, out = set(), []
    for u in urls:
        if u and u not in seen:
            seen.add(u); out.append(u)
    return out

def _regex_first(html: str, pattern_with_collection, pattern_no_prefix):
    """Helper to find a product URL via regex, supporting both /collections/.../products/... and /products/..."""
    m = pattern_with_collection.search(html)
    if m:
        base = m.group("u") or ""
        path = m.group("p")
        return absolutize((base if base else BASE) + path)
    m = pattern_no_prefix.search(html)
    if m:
        base = m.group("u") or ""
        path = m.group("p")
        return absolutize((base if base else BASE) + path)
    return None

def find_set_products_in_collection_html(collection_html: str, session=None, robots=None, coll_url:str=""):
    """
    Robustly find Masters and Bachelors product URLs, even if tiles are JS-injected.
    Fallbacks:
      1) regex scan current HTML (with and without collection prefix)
      2) if nothing, fetch coll_url + '?view=all' and rescan
      3) parse JSON-LD for product urls
      4) infer handles from collection handle and HEAD-probe once
    """
    # 1) regex scan on given HTML
    masters = _regex_first(collection_html, RE_MASTERS_URL_COLL, RE_MASTERS_URL_NOPREFIX)
    bachelors = _regex_first(collection_html, RE_BACHELORS_URL_COLL, RE_BACHELORS_URL_NOPREFIX)

    # 2) '?view=all' fallback
    if not (masters or bachelors) and coll_url:
        try:
            alt_url = coll_url + ("&view=all" if "?" in coll_url else "?view=all")
            resp = polite_get(session, alt_url, robots)
            masters = masters or _regex_first(resp.text, RE_MASTERS_URL_COLL, RE_MASTERS_URL_NOPREFIX)
            bachelors = bachelors or _regex_first(resp.text, RE_BACHELORS_URL_COLL, RE_BACHELORS_URL_NOPREFIX)
            if masters or bachelors:
                log("  [fallback] used '?view=all' on collection")
        except Exception as e:
            log(f"  [fallback] '?view=all' fetch failed: {e}")

    # 3) JSON-LD fallback
    if not (masters or bachelors):
        try:
            soup = BeautifulSoup(collection_html, "html.parser")
            for s in soup.find_all("script", {"type": "application/ld+json"}):
                try:
                    data = json.loads(s.string or "{}")
                except Exception:
                    continue
                items = data if isinstance(data, list) else [data]
                urls = []
                for it in items:
                    if isinstance(it, dict):
                        if it.get("@type") in ("Product", "ProductGroup") and it.get("url"):
                            urls.append(it["url"])
                        if "@graph" in it and isinstance(it["@graph"], list):
                            for g in it["@graph"]:
                                if isinstance(g, dict) and g.get("@type") in ("Product","ProductGroup") and g.get("url"):
                                    urls.append(g["url"])
                for u in urls:
                    if not masters and re.search(r"master", u, re.I) and "graduation-set" in u:
                        masters = absolutize(u)
                    if not bachelors and re.search(r"bachelor", u, re.I) and "graduation-set" in u:
                        bachelors = absolutize(u)
                if masters or bachelors:
                    log("  [fallback] products from JSON-LD")
                    break
        except Exception as e:
            log(f"  [fallback] JSON-LD parse failed: {e}")

    # 4) guessed handle fallback (only if we have a collection URL)
    if not (masters or bachelors) and coll_url:
        try:
            coll_path = urlparse(coll_url).path.rstrip("/")
            coll_handle = coll_path.split("/")[-1]
            base_coll = f"{BASE}/collections/{coll_handle}/products"
            uni_prefix = coll_handle.replace("-purchase", "").replace("-graduation-set", "")
            guesses = [
                f"{base_coll}/{uni_prefix}-masters-graduation-set",
                f"{base_coll}/{uni_prefix}-master-graduation-set",
                f"{base_coll}/{uni_prefix}-bachelors-graduation-set",
                f"{base_coll}/{uni_prefix}-bachelor-graduation-set",
            ]
            for g in guesses:
                try:
                    r = session.head(g, headers=HEADERS, timeout=15, allow_redirects=True)
                    if r.status_code == 200:
                        if "master" in g and not masters:
                            masters = g
                        if "bachelor" in g and not bachelors:
                            bachelors = g
                except Exception:
                    pass
            if masters or bachelors:
                log("  [fallback] guessed product handles")
        except Exception:
            pass

    return masters, bachelors

def scan_uni_page_for_direct_products(university_html: str):
    """
    Final fallback: some universities link straight to the set product pages from the university page,
    without a collection page. Find /products/...masters-...graduation-set and /products/...bachelors-...
    """
    masters = _regex_first(university_html, RE_MASTERS_URL_COLL, RE_MASTERS_URL_NOPREFIX)
    bachelors = _regex_first(university_html, RE_BACHELORS_URL_COLL, RE_BACHELORS_URL_NOPREFIX)
    return masters, bachelors

def save_images(images, uni_name, level, prod_url, outdir, dry, writer):
    ddir = outdir / sanitize(uni_name) / level
    ddir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for k, url in enumerate(images, start=1):
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower() or ".jpg"
        if ext not in (".jpg",".jpeg",".png",".webp"): ext = ".jpg"
        fname = sanitize(f"{Path(urlparse(prod_url).path).name}-{k}{ext}")[:170]
        dest = ddir / fname
        if dry:
            log(f"      DRY -> {dest}  <=  {url}")
            writer.writerow([uni_name, level, prod_url, url, str(dest)])
            saved += 1
            continue
        if dest.exists():
            log(f"      exists -> {dest.name}")
            writer.writerow([uni_name, level, prod_url, url, str(dest)])
            saved += 1
            continue
        try:
            rimg = requests.get(url, headers=HEADERS, timeout=30)
            rimg.raise_for_status()
            with open(dest, "wb") as f: 
                f.write(rimg.content)
            log(f"      saved -> {dest.name}")
            writer.writerow([uni_name, level, prod_url, url, str(dest)])
            saved += 1
        except Exception as e:
            log(f"      image failed: {e}")
    return saved

def run_single_collection(coll_url, outdir, dry, robots, session):
    coll_url = absolutize(coll_url)
    log(f"\n[MODE] Single-collection: {coll_url}")
    coll = polite_get(session, coll_url, robots)
    masters_set, bachelors_set = find_set_products_in_collection_html(
        coll.text, session=session, robots=robots, coll_url=coll_url
    )
    log(f"  Found Masters product:   {masters_set}")
    log(f"  Found Bachelors product: {bachelors_set}")

    targets = []
    if masters_set: targets.append(("Masters", masters_set))
    if bachelors_set: targets.append(("Bachelors", bachelors_set))
    if not targets:
        log("  No Masters/Bachelors product pages found — make sure this is a PURCHASE collection.")
        return

    uni_name = coll_url.strip("/").split("/")[-1].replace("-", " ").title()

    manifest = open(outdir/"manifest.csv","w",newline="",encoding="utf-8")
    w = csv.writer(manifest); w.writerow(["university","level","product_url","image_url","saved_path"])

    for level, prod_url in targets:
        log(f"\n  [{level}] Product page: {prod_url}")
        presp = polite_get(session, prod_url, robots)
        imgs = extract_all_gallery_images(presp.text)
        log(f"    Gallery images found: {len(imgs)}")
        if not imgs:
            continue
        _ = save_images(imgs, uni_name, level, prod_url, outdir, dry, w)

    manifest.close()
    log("\n[Done]")

def run_index_crawl(max_unis, outdir, dry, robots, session):
    log("\n[MODE] Index crawl")
    idx = polite_get(session, INDEX_URL, robots)
    unis = parse_unis(idx.text)
    log(f"Universities parsed from index: {len(unis)}")
    if not unis:
        log("No universities parsed — site structure may have changed.")
        return

    manifest = open(outdir/"manifest.csv","w",newline="",encoding="utf-8")
    w = csv.writer(manifest); w.writerow(["university","level","product_url","image_url","saved_path"])

    for i,(uni_name, uni_url) in enumerate(unis, start=1):
        if i > max_unis: 
            break
        log(f"\n== [{i}] {uni_name} == {uni_url}")
        try:
            up = polite_get(session, uni_url, robots)
        except Exception as e:
            log(f"  Skip uni: {e}"); 
            continue

        # 1) Try to find a PURCHASE COLLECTION (collections only, ignore products)
        coll_url = find_purchase_collection(up.text)
        log(f"  Purchase collection: {coll_url}")

        masters_set = bachelors_set = None

        if coll_url:
            try:
                coll = polite_get(session, coll_url, robots)
                masters_set, bachelors_set = find_set_products_in_collection_html(
                    coll.text, session=session, robots=robots, coll_url=coll_url
                )
            except Exception as e:
                log(f"  Skip collection: {e}")

        # 2) If no collection or nothing found, try direct product links on the UNIVERSITY PAGE itself
        if not (masters_set or bachelors_set):
            dm, db = scan_uni_page_for_direct_products(up.text)
            if dm or db:
                log("  [fallback] found direct product links on university page")
            masters_set = masters_set or dm
            bachelors_set = bachelors_set or db

        log(f"  Masters product:   {masters_set}")
        log(f"  Bachelors product: {bachelors_set}")

        targets = []
        if masters_set:   targets.append(("Masters", masters_set))
        if bachelors_set: targets.append(("Bachelors", bachelors_set))
        if not targets:
            log("  -> No Masters/Bachelors product pages found on this university.")
            continue

        for level, prod_url in targets:
            log(f"    {level} page: {prod_url}")
            try:
                presp = polite_get(session, prod_url, robots)
            except Exception as e:
                log(f"      Skip product: {e}"); 
                continue

            imgs = extract_all_gallery_images(presp.text)
            log(f"      gallery count: {len(imgs)}")
            if not imgs:
                continue

            _ = save_images(imgs, uni_name, level, prod_url, outdir, dry, w)

    manifest.close()
    log("\n[Done]")

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--collection-url", help="Scrape a single PURCHASE collection URL (fast to validate)")
    g.add_argument("--from-index", action="store_true", help="Start from 'Select your university' and crawl all")

    ap.add_argument("--out", default="output", help="Output folder")
    ap.add_argument("--max-unis", type=int, default=9999, help="Max universities in index crawl mode")
    ap.add_argument("--dry-run", action="store_true", help="Log actions without downloading files")
    args = ap.parse_args()

    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)

    robots = robotparser.RobotFileParser()
    try:
        robots.set_url(urljoin(BASE, "/robots.txt")); robots.read()
    except Exception:
        robots = None

    s = requests.Session()

    if args.collection_url:
        run_single_collection(args.collection_url, outdir, args.dry_run, robots, s)
    else:
        run_index_crawl(args.max_unis, outdir, args.dry_run, robots, s)

if __name__ == "__main__":
    main()
