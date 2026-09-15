<?php
$products = require __DIR__ . '/products.php';

function proxied(string $assetUrl): string
{
    return '/api/proxy?url=' . rawurlencode($assetUrl);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ProxyDough — Everything Dough</title>
    <style>
        :root {
            --bg: #fdf6ec;
            --card: #ffffff;
            --ink: #3b2a1a;
            --muted: #8a7355;
            --accent: #c9822f;
            --accent-dark: #a5651c;
            --line: #eaddc7;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--ink);
        }
        header {
            padding: 2.5rem 1.5rem 1.5rem;
            text-align: center;
            border-bottom: 1px solid var(--line);
        }
        header h1 { margin: 0; font-size: 2.4rem; letter-spacing: -0.5px; }
        header p { margin: 0.5rem 0 0; color: var(--muted); font-size: 1.05rem; }
        .grid {
            max-width: 1100px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 1.5rem;
        }
        .card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform .12s ease, box-shadow .12s ease;
        }
        .card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(120,80,20,.12); }
        .card .thumb {
            aspect-ratio: 4 / 3;
            background: #f3e8d6;
            object-fit: cover;
            width: 100%;
        }
        .card .body { padding: 1rem 1.1rem 1.2rem; display: flex; flex-direction: column; gap: .4rem; flex: 1; }
        .tag {
            align-self: flex-start;
            font-size: .72rem;
            text-transform: uppercase;
            letter-spacing: .6px;
            color: var(--accent-dark);
            background: #f6e7cf;
            padding: .2rem .55rem;
            border-radius: 999px;
        }
        .card h2 { margin: .1rem 0; font-size: 1.12rem; }
        .card .blurb { color: var(--muted); font-size: .9rem; line-height: 1.4; flex: 1; }
        .card .foot { display: flex; align-items: center; justify-content: space-between; margin-top: .6rem; }
        .price { font-weight: 700; font-size: 1.15rem; }
        .buy {
            border: 0;
            background: var(--accent);
            color: #fff;
            padding: .5rem .9rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }
        .buy:hover { background: var(--accent-dark); }
        footer { text-align: center; color: var(--muted); padding: 2rem 1rem 3rem; font-size: .85rem; }
    </style>
</head>
<body>
    <header>
        <h1>🍪 ProxyDough</h1>
        <p>Cookie dough, bread dough, pizza dough — everything dough, delivered.</p>
	<p>Our secret recipe is <a href="/api/recipe">here.</a> Not that only internal employee can access it.</p>
    </header>

    <main class="grid">
        <?php foreach ($products as $p): ?>
            <article class="card">
                <img class="thumb"
                     src="<?= htmlspecialchars(proxied($p['image']), ENT_QUOTES) ?>"
                     alt="<?= htmlspecialchars($p['name'], ENT_QUOTES) ?>"
                     loading="lazy">
                <div class="body">
                    <span class="tag"><?= htmlspecialchars($p['tag'], ENT_QUOTES) ?></span>
                    <h2><?= htmlspecialchars($p['name'], ENT_QUOTES) ?></h2>
                    <p class="blurb"><?= htmlspecialchars($p['blurb'], ENT_QUOTES) ?></p>
                    <div class="foot">
                        <span class="price">$<?= number_format($p['price'], 2) ?></span>
                        <button class="buy">Add to cart</button>
                    </div>
                </div>
            </article>
        <?php endforeach; ?>
    </main>

    <footer>
        &copy; <?= date('Y') ?> ProxyDough &middot;
    </footer>
</body>
</html>
