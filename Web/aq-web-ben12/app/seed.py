import os

from werkzeug.security import generate_password_hash

from . import create_app, db
from .models import Game, User

GAMES = [
    {
        "slug": "afterglow-sprint",
        "title": "Afterglow Sprint",
        "studio": "Luma Circuit",
        "genre": "Rhythm Runner",
        "price_cents": 1499,
        "released": True,
        "featured": True,
        "accent_a": "#74f8ff",
        "accent_b": "#3e5bff",
        "tagline": "Dash through a city that only exists after midnight.",
        "blurb": "An endless rooftop runner with timed lanes, cassette synths, and more sparks than safety audits.",
    },
    {
        "slug": "glass-signal",
        "title": "Glass Signal",
        "studio": "Quiet Vector",
        "genre": "Stealth Sim",
        "price_cents": 2199,
        "released": True,
        "featured": True,
        "accent_a": "#7effd8",
        "accent_b": "#0e947e",
        "tagline": "Slip through mirrored towers without waking the grid.",
        "blurb": "Every alarm becomes architecture. Every corridor turns into a puzzle made of reflections and bad decisions.",
    },
    {
        "slug": "neon-rite",
        "title": "Neon Rite",
        "studio": "Void Parish",
        "genre": "Action Roguelite",
        "price_cents": 1899,
        "released": True,
        "featured": True,
        "accent_a": "#ff7ad9",
        "accent_b": "#8315ff",
        "tagline": "Offer one more run to the electric cathedral.",
        "blurb": "Sword rushes, room modifiers, and boss fights lit like forbidden club posters.",
    },
    {
        "slug": "starline-courier",
        "title": "Starline Courier",
        "studio": "Solar Motel",
        "genre": "Delivery Adventure",
        "price_cents": 1299,
        "released": True,
        "featured": False,
        "accent_a": "#ffb459",
        "accent_b": "#ff5c4d",
        "tagline": "Hot coffee, bad roads, worse weather.",
        "blurb": "Pilot a borrowed van across a rust-belt moon while everyone asks for impossible dropoffs.",
    },
    {
        "slug": "drift-saint",
        "title": "Drift Saint",
        "studio": "Zero Mercy",
        "genre": "Arcade Racing",
        "price_cents": 1699,
        "released": True,
        "featured": False,
        "accent_a": "#7ef9ff",
        "accent_b": "#ff5ca6",
        "tagline": "Pray late. Brake later.",
        "blurb": "Tight corners, glowing skid marks, and enough turbo to make your HUD apologize.",
    },
    {
        "slug": "chrome-cinder",
        "title": "Chrome Cinder",
        "studio": "Fume Pattern",
        "genre": "Mech Tactics",
        "price_cents": 2499,
        "released": True,
        "featured": False,
        "accent_a": "#d9ecff",
        "accent_b": "#5688ff",
        "tagline": "Command a scrapyard brigade with immaculate posture.",
        "blurb": "Small maps, savage angles, and long campaign scars hidden behind polished alloy.",
    },
    {
        "slug": "cipher-lagoon",
        "title": "Cipher Lagoon",
        "studio": "Wet Static",
        "genre": "Puzzle Mystery",
        "price_cents": 1599,
        "released": True,
        "featured": False,
        "accent_a": "#5fffd2",
        "accent_b": "#2477ff",
        "tagline": "Decode a vacation town that edits its own brochures.",
        "blurb": "Relaxed investigation with dense clue chains, strange postcards, and deeply suspicious weather.",
    },
    {
        "slug": "holo-havoc",
        "title": "Holo Havoc",
        "studio": "Arc Spark",
        "genre": "Arena Shooter",
        "price_cents": 1999,
        "released": True,
        "featured": False,
        "accent_a": "#ff74cf",
        "accent_b": "#ffbc4f",
        "tagline": "Every round ends in confetti or a crater.",
        "blurb": "Short-form mayhem tuned for bright maps, louder weapons, and private bragging rights.",
    },
    {
        "slug": "frostwire-vault",
        "title": "Frostwire Vault",
        "studio": "Night District",
        "genre": "Extraction Survival",
        "price_cents": 2799,
        "released": True,
        "featured": False,
        "accent_a": "#d7faff",
        "accent_b": "#4ba8d8",
        "tagline": "The blizzard is the easy part.",
        "blurb": "Scavenge under aurora light, keep the generators breathing, and hope your squad respects inventory law.",
    },
    {
        "slug": "marble-noise",
        "title": "Marble Noise",
        "studio": "Index Fever",
        "genre": "Music Builder",
        "price_cents": 1399,
        "released": True,
        "featured": False,
        "accent_a": "#e7c8ff",
        "accent_b": "#ff4f91",
        "tagline": "Make a mess that somehow grooves.",
        "blurb": "Stack loops, reroute percussion, and abuse reverb until the apartment downstairs starts complaining.",
    },
    {
        "slug": "gutter-bloom",
        "title": "Gutter Bloom",
        "studio": "Vivid Ash",
        "genre": "Narrative Platformer",
        "price_cents": 1199,
        "released": True,
        "featured": False,
        "accent_a": "#ffe67d",
        "accent_b": "#ff5f7c",
        "tagline": "The city is rotten. The flowers are not.",
        "blurb": "A sharp little story about rooftops, rumors, and refusing to stay where the map puts you.",
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        for game_data in GAMES:
            game = Game.query.filter_by(slug=game_data["slug"]).first()
            if game is None:
                game = Game(**game_data)
                db.session.add(game)
            else:
                for key, value in game_data.items():
                    setattr(game, key, value)

        secret_slug = "embershadow-press-preview"
        secret_title = os.environ.get("FLAG", "f13{press_lane}")
        secret = Game.query.filter_by(slug=secret_slug).first()
        secret_data = {
            "slug": secret_slug,
            "title": secret_title,
            "studio": "Private Build Syndicate",
            "genre": "Internal Review Build",
            "price_cents": 0,
            "released": False,
            "featured": False,
            "accent_a": "#7ef9ff",
            "accent_b": "#ff4ecd",
            "tagline": "One build too early, one account too trusted.",
            "blurb": "A quiet press preview that should have stayed in staging and never found a storefront drawer.",
        }
        if secret is None:
            secret = Game(**secret_data)
            db.session.add(secret)
        else:
            for key, value in secret_data.items():
                setattr(secret, key, value)

        press_user = os.environ.get("PRESS_USER", "pressdesk")
        press_pass = os.environ.get("PRESS_PASS", "neonvault")
        press = User.query.filter_by(username=press_user).first()
        if press is None:
            press = User(
                username=press_user,
                password=generate_password_hash(press_pass, method="scrypt"),
                role="press",
                headline="Review queue is glowing again.",
                status="Checking unreleased capsules",
                accent="#7ef9ff",
            )
            db.session.add(press)
        else:
            press.password = generate_password_hash(press_pass, method="scrypt")
            press.role = "press"
            press.headline = "Review queue is glowing again."
            press.status = "Checking unreleased capsules"
            press.accent = "#7ef9ff"

        orbit = User.query.filter_by(username="orbitfox").first()
        if orbit is None:
            orbit = User(
                username="orbitfox",
                password=generate_password_hash("orbitfox123", method="scrypt"),
                role="player",
                headline="Living off patch notes and bad coffee.",
                status="Browsing the market",
                accent="#ff73d3",
            )
            db.session.add(orbit)

        db.session.commit()

        press.library = [secret]
        orbit.library = Game.query.filter(Game.slug.in_(["afterglow-sprint", "glass-signal", "drift-saint"])).all()
        db.session.commit()


if __name__ == "__main__":
    seed()
