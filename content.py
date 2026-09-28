# Camoflux site content. Single source of truth.
# Edit, then run: python3 build.py
#
# Rules the build enforces (see lint() in build.py):
#   - No em dashes anywhere in copy. Use commas, colons, or semicolons.
#   - A link with no URL is not rendered. Set a value to None to hide it.
#   - Every image key must exist in IMAGES and in images/.
#
# Fields marked  # CONFIRM  are placeholders or unverified. Check before launch.

SITE = {
    "title": "Camoflux",
    "subtitle": "Levels & Bosses",
    "full_title": "Camoflux",
    "genre": "Ecological stealth-exploration game",
    "tagline": "Where landscape, body, and technology fuse.",
    "lead": "A hand-painted, ecological stealth-exploration game. Camouflage through neo-primordial landscapes and solve environmental puzzles to reshape a cyclical cataclysm.",
    "description_50": "Camoflux is a hand-painted, ecological stealth-exploration game built in Unreal Engine 5. Camouflage into painted patterns, modulate turbulence and light, and move energy through the land to reshape a cyclical cataclysm.",
    "description_150": [
        "Camoflux is a hand-painted, ecological stealth-exploration game made across Miami and Cali, Colombia, by the independent studio Levels & Bosses. Its worlds are painted as oil paintings and ink drawings and turned into height maps, materials, and dynamic textures; organic models sculpted in VR become sentient, animated actors. One level is built from the Amazonian canvases of María Thereza Negreiros, a painter from Maués in the Brazilian Amazon.",
        "It plays through reciprocity rather than combat. The First-Boss is the entire Level One environment: however gently or violently you approach it, it answers in kind, and rushing to attack is the fastest way to lose. Slow down and observe. Camouflage into hand-painted patterns, modulate turbulence through touch, shift light, and move energy through landscape puzzles.",
        "Camoflux was exhibited as a playable installation at the 2026 Whitney Biennial and is available to wishlist on Steam.",
    ],
    "status": "In development",
    "platform": "PC (Steam)",
    "engine": "Unreal Engine 5",
    "release": "Coming soon",
    "languages": "English, Spanish",     # CONFIRM against Steam page
    "publisher": "Otro Inventario",
    "youtube_id": "uhkBJS_n7Qc",
    "steam_url": "https://store.steampowered.com/app/897980/Camoflux_Levels__Bosses/",
    "hero_image": "hero-3d-still",       # still shown before, and instead of, the 3D scene
    "hero_video": None,                  # optional gameplay clip (MP4); plays on the screen behind the 3D model when set
    # 3D hero: model in front of in-game footage. Files live in assets/3d/.
    # Homepage hero: one floating icon per level; hovering shows that level's 360 video (assets/3d/pano/).
    "hero_levels": {
        "icons": [
            {"id": "mangrove", "label": "Machine Mangrove Village", "model": "hedge.q.glb", "height": 1.9, "pano": "mangrove"},
            {"id": "level-one", "label": "Level One", "model": "l1-blob.q.glb", "height": 1.5, "pano": "first-boss"},
            {"id": "igapo", "label": "Incendio-Igapó", "model": "shield.q.glb", "height": 1.9, "pano": "amazon"},
            {"id": "paramo", "label": "Patterned Páramo", "model": "frailejon.q.glb", "height": 1.7, "pano": "paramo"},
        ],
        "figure": "other-morphs.q.glb",
        # Hovering The Other plays this gameplay reel behind the scene; clicking opens it large with sound.
        "figure_video": "gameplay", "figure_video_caption": "Gameplay",
        "shots": ["first-boss-render", "igapo-roots", "lily-pad-hangout", "walking-panorama", "cave-roots", "cave-figures",
                  "mangrove-village", "paramo", "igapo-butterfly-drone", "level-one"],
    },
    # Previous hero (single model + footage screen), kept for reference.
    "hero3d": {"enabled": True, "models": [
        {"id": "shield", "file": "shield.glb", "height": 4.8, "repeat": 2},
        {"id": "liana", "file": "liana.glb", "height": 4.2, "repeat": 3},
        {"id": "plant-c", "file": "plant-c.glb", "height": 3.8, "repeat": 2},
        {"id": "plant-f", "file": "plant-f.glb", "height": 3.6, "repeat": 2},
        {"id": "l1-blob", "file": "l1-blob.glb", "height": 3.2, "repeat": 2},
        {"id": "frailejon", "file": "frailejon.glb", "height": 3.6, "repeat": 2},
        {"id": "other", "file": "other.glb", "skinned": True, "scale": 1.9, "floor": -1.5, "spin": 0.05, "repeat": 2},
        {"id": "drones", "file": "drones.glb", "flock": True, "repeat": 1},
    ]},
    "cta_image": "mangrove-entity",
    "press_email": "leo@levelsandbosses.com",
    "biz_email": None,
    # Mailchimp audience (from the embed code). The signup form sits above the footer on every page.
    "mailchimp": {
        "action": "https://levelsandbosses.us14.list-manage.com/subscribe/post?u=f9429a4b084d0b1f6683d0556&id=0af6ba98d5&f_id=00bcbee5f0",
        "tags": "40243690",
        "honeypot": "b_f9429a4b084d0b1f6683d0556_0af6ba98d5",
    },
    # Fonts. Technical Standard VP is self-hosted from assets/fonts/ (web license required).  # CONFIRM
    # AB-24h comes from Adobe Fonts: create a web project, paste its kit ID here; until then a free stand-in is used.
    "fonts": {"adobe_kit_id": None, "adobe_meta_family": "ab-24h"},
    "base_url": "https://www.camoflux.com",                    # e.g. "https://camoflux.com"; makes share images absolute  # CONFIRM           # form POST URL from your mailing list provider; form hidden until set
}

# Nav. "anchor" targets a section on the homepage; "page" targets a file.
NAV = [
    {"label": "World", "anchor": "world"},
    {"label": "Features", "anchor": "features"},
    {"label": "Press", "anchor": "press"},
    {"label": "Studio", "page": "studio.html"},
    {"label": "Exhibitions and playtesting", "page": "exhibitions.html"},
    {"label": "Devlog", "page": "devlog.html"},
    {"label": "Merch", "page": "merch.html"},
]

# Image catalog. Keys match files in images/ (run export_images.py after adding sources).
IMAGES = {
    "hero-3d-still": {
        "kind": "render", "caption": "Mangrove hedge, in-engine model",
        "alt": "A lattice hedge form with trailing roots stands on dark rippling water in black fog.",
    },
    "mangrove-alcove": {
        "kind": "game", "caption": "Mangrove Alcove, in-game",
        "alt": "The Other, a patterned figure, wades through pink water toward a lattice structure in a grove of striped mangrove roots.",
    },
    "mangrove-entity": {
        "kind": "game", "caption": "Mangrove biome: Embedded Entity",
        "alt": "A pale lattice figure sits in an alcove of striped roots, framed by lattice lanterns glowing orange.",
    },
    "mangrove-village": {
        "kind": "game", "caption": "Mangrove Village: teleporter facing Level One, 2024",
        "alt": "The Other stands beside a burning lattice tower on dark water under an overcast sky.",
    },
    "igapo-butterfly-drone": {
        "kind": "game", "caption": "Amazonian Igapó: Butterfly Drone encounter. In collaboration with María Thereza Negreiros, 2025",
        "alt": "A green flooded forest where a striped butterfly drone hovers above a mossy stone.",
    },
    "paramo": {
        "kind": "game", "caption": "Páramo, in-game",
        "alt": "Spiked, patterned plant forms stand in fog on rippled black and white ground below misty mountains.",
    },
    "first-boss-render": {"kind": "game", "caption": "Level One: the First-Boss",
        "alt": "A towering mass of pale sculpted rock and cloud rises over a horizon of streaked water."},
    "igapo-roots": {"kind": "game", "caption": "Incendio-Igapó, 2026",
        "alt": "Glowing green roots and vines crowd a flooded forest, with pale light at the far end."},
    "lily-pad-hangout": {"kind": "game", "caption": "Incendio-Igapó: lily pad camo hangout, three-channel",
        "alt": "Patterned figures rest on a giant lily pad in a green flooded forest, with fire glowing red on the water beyond."},
    "walking-panorama": {"kind": "game", "caption": "Walking panorama, 2023",
        "alt": "The Other, in silhouette, stands at the edge of marbled water facing a distant eye in the clouds."},
    "cave-roots": {"kind": "game", "caption": "The porous cave",
        "alt": "A pale root-like form spreads across the ceiling of a warm, sculpted cave."},
    "cave-figures": {"kind": "game", "caption": "The porous cave, with hooded figures",
        "alt": "Hooded figures with small glowing lights stand in a dim cave of marbled rock."},
    "maloca-pause-menu": {"kind": "game", "caption": "Maloca pause menu, concept",
        "alt": "A round chamber lined with sculpted objects around a central form, a pause menu concept."},
    "level-one-bw": {"kind": "game", "caption": "Level One",
        "alt": "Bold black biomorphic shapes over a grey and rust landscape, in Level One."},
    "level-one": {
        "kind": "game", "caption": "Level One, trailer capture, 2024",
        "alt": "A dark winged figure glides through a smoky cavern of sculpted rock toward a point of light.",
    },
}

# Artwork shown on the site (studio page, sketchbook, exhibitions). Not part of the press kit screenshots.
ARTWORK = {
    "paint-mangrove-hedge": {"kind": "painting", "caption": "Mangrove Hedge", "alt": "Painting of a lattice tower glowing orange from within, roots spreading into red and violet ground, beside a patterned figure."},
    "paint-traveller": {"kind": "painting", "caption": "Traveller, 2025", "alt": "Painting of a winged, spined figure in saturated red."},
    "paint-ink-2025": {"kind": "painting", "caption": "Untitled, ink, 2025", "alt": "Gestural black and grey ink painting with scraped lines and pale blue washes."},
    "paint-l1-flythrough": {"kind": "painting", "caption": "L1 Flythrough, 2020", "alt": "Painting of a rust and grey cavern seen past two smooth grey forms in the foreground."},
    "paint-other-sensing": {"kind": "painting", "caption": "Other Sensing, 2025", "alt": "Blue and green wash painting of a glowing field under a dark sky."},
    "draw-other-sequence": {"kind": "drawing", "caption": "The Other, sequence drawing", "alt": "Line drawing of The Other in a sequence of poses rising from a banded landscape."},
    "draw-patterned-biome": {"kind": "drawing", "caption": "Patterned biome, concept drawing", "alt": "Black ink drawing of a landscape built from bold biomorphic patterns."},
    "draw-hyper-object": {"kind": "drawing", "caption": "Hyper Object, drawing, 2013", "alt": "Pencil and ink drawing of a dense organic form set inside a perspective box."},
    "whitney-install-amstutz": {"kind": "photo", "caption": "Installation view, Whitney Biennial 2026", "credit": "Photo: Ron Amstutz", "alt": "Gallery with a painted green and orange wall, a screen showing the game, and two pale sculptural seats."},
    "whitney-install-fata": {"kind": "photo", "caption": "Installation view, Whitney Biennial 2026", "credit": "Photo: Films About Artists", "alt": "Installation with a vertical screen of green footage, a painted wall, a game screen, and sculptural seats."},
    "paint-level-01": {"kind": "painting", "caption": "Level 01, oil and ink on canvas, 2009", "alt": "Grey and white oil painting of clouds and rock, with the words LEVEL 0 at the bottom."},
    "draw-first-boss": {"kind": "drawing", "caption": "First Boss (agitado), ink drawing", "alt": "Ink drawing of a dark, flame-like mass rising to a small rectangular summit."},
    "draw-boss-intro": {"kind": "drawing", "caption": "The First Boss, intro page", "alt": "Comic page introducing the First Boss: a dark mountain topped by a doorway in pale fog, captioned THE FIRST BOSS and NO ESCAPE."},
    "supercon-performance": {"kind": "photo", "caption": "Camoflux cosplay performance, Field Collisions, Florida Supercon, 2024", "credit": "", "alt": "Two performers in patterned camouflage costumes move through a convention hall crowd."},
    "whitney-visitors": {"kind": "photo", "caption": "Visitors at the controls, Whitney Biennial 2026", "credit": "Photo: Films About Artists", "alt": "Visitors gather around a sculptural controller stand, one pressing its button, in front of the painted wall."},
}
PAINTINGS = ["paint-mangrove-hedge", "paint-traveller", "paint-level-01", "paint-ink-2025", "paint-l1-flythrough", "paint-other-sensing"]
SKETCHBOOK = ["draw-other-sequence", "draw-first-boss", "draw-patterned-biome", "draw-boss-intro", "draw-hyper-object"]

# Gameplay clips (from the GIFs) and wide stills, shown in the "In play" section.
GAMEPLAY = {
    "clips": [("igapo-swim", "Swimming, Igapó"), ("incendio-360", "Incendio Igapó 360")],
    "wide": "lily-pad-hangout",
}

WORLD = {
    "heading": "You are The Other.",
    "body": [
        # DRAFT: the movement clause is a placeholder for Leo's line on bio-adaptive movement.
        "Slow down and observe. Camouflage into hand-painted patterns and move by adapting to each terrain: swimming, gliding, and crawling. Modulate turbulence through touch until a cloud is solid enough to walk across, and synchronize energy through the land, pollinating circuits that unfold the world.",
    ],
    # The four levels of the first chapter, in play order.
    "biomes": [
        {"name": "Machine Mangrove Village", "body": "The prologue: an amphibious village of camouflaging posthuman beings, drawn from South Florida and Colombian coastlines. Sync energy from machine mangroves into a teleporter.", "image": "mangrove-village"},
        {"name": "Level One", "body": "The primordial explosion at the source of the world's energy and destruction. The whole level is the First-Boss, shifting material properties as you sense and modulate its turbulence.", "image": "first-boss-render"},
        {"name": "Incendio-Igapó", "body": "A flooded swamp and sentient forest fire. Restore the ecosystem through puzzles that rebalance it; half the level is underwater.", "image": "igapo-butterfly-drone"},
        {"name": "Patterned Páramo", "body": "The Colombian highlands and their water-filtering tundra. The most stealth-driven level: shift skins, glide, crawl, and herd camo-sensitive drones.", "image": "paramo"},
    ],
}

FEATURES = [
    {"category": "Camouflage", "title": "Become the landscape",
     "body": "Absorb textures from the environment and embody them. Camouflage is how you hide, solve stealth puzzles, and channel data across the worlds.",
     "image": "level-one", "clip": "camouflage"},
    {"category": "Turbulence and light", "title": "Touch and light change matter",
     "body": "Modulate turbulence until a cloud is solid enough to walk across. Shift the frequency of light to solve atmospheric puzzles.",
     "image": "igapo-butterfly-drone", "clip": "touch-bridge"},
    {"category": "Intensify every ability", "title": "Choose coexistence or conquest",
     "body": "Customize each ability to suit your gameplay style. Every encounter sits on a spectrum from violence to cooperation.",
     "image": "first-boss-render", "clip": "coexistence"},
    {"category": "Craft", "title": "Painted into the engine",
     "body": "Oil paintings and ink drawings become height maps, materials, and textures. Every model is a custom asset; one level is built from María Thereza Negreiros's Amazonian canvases. Models sculpted in VR become sentient, animated actors in Unreal Engine 5.",
     "image": "mangrove-entity"},
]

# Quotes verified against sources on 2026-09-23 (GameScenes). Others carried from the Steam page.
PRESS_FEATURED = [
    {"quote": "Not a game seeking art's legitimizing frame, but a project conceived from the outset to treat painting, 3D modeling, and game engine work as co-equal forms of making.",
     "source": "GameScenes", "author": "Matteo Bittanti", "date": "March 2026",
     "url": "https://www.gamescenes.org/play-itself-or-leo-castaneda-at-the-whitney-biennial-2026/"},
    {"quote": "What the museum is now hosting, directly and with apparent conviction, is play itself.",
     "source": "GameScenes", "author": "Matteo Bittanti", "date": "March 2026",
     "url": "https://www.gamescenes.org/play-itself-or-leo-castaneda-at-the-whitney-biennial-2026/"},
]
PRESS_SHORT = [
    {"quote": "Interrogating the core of interaction.", "source": "Killscreen",
     "url": "https://www.killscreen.com/leo-castaneda/"},
    {"quote": "A philosophical manifestation of the virtual.", "source": "Rhizome",
     "url": "https://rhizome.org/editorial/2018/may/01/artist-profile-leo-castaneda-1/"},
    {"quote": "Calls into question the concept of antagonism that defines traditional video games.", "source": "HEK Basel",
     "url": "https://global-uploads.webflow.com/5a3b8af6706df50001a2fbf2/60b77ed72774afd4d3911628_PM_HEK_RadicalGaming%2BArtistList_EN.pdf"},
]

# Coverage lists (press kit and homepage).
COVERAGE = {
    "Whitney Biennial 2026": [
        ("Hyperallergic", "https://hyperallergic.com/the-polycrisis-sublime-of-the-whitney-biennial/"),
        ("Artnet", "https://news.artnet.com/art-world/whitney-biennial-2026-first-takes-2750160"),
        ("El País", "https://elpais.com/us/2026-03-07/la-bienal-del-whitney-2026-hace-historia-con-su-primera-curadora-latina.html"),
        ("Time Out New York", "https://www.timeout.com/newyork/news/the-2026-whitney-biennial-asks-big-questions-about-how-we-live-now-030326"),
        ("GameScenes", "https://www.gamescenes.org/play-itself-or-leo-castaneda-at-the-whitney-biennial-2026/"),
        ("Observer", "https://observer.com/2026/03/art-whitney-biennial-review-fracture-trauma-renewal-america/"),
        ("Hypebeast", "https://hypebeast.com/2026/3/whitney-biennial-2026-announcement-new-york"),
        ("The Overview", "https://www.theoverview.art/leo-castaneda-whitney-feature/"),
    ],
    "Interviews": [
        ("Fisheye Immersive, Clément Thibault, August 2026 (in French)", "https://fisheyeimmersive.com/article/leo-castaneda-commencer-par-le-boss-le-plus-puissant/"),
        ("Rhizome", "https://rhizome.org/editorial/2018/may/01/artist-profile-leo-castaneda-1/"),
        ("ShiftSpace, Phillip Penix-Tadsen", "https://issue3.shiftspace.pub/issue-3/questioning-binaries-subverting-conventions-phillip-penix-tadsen-on-leo-castaneda"),
        ("Killscreen", "https://www.killscreen.com/leo-castaneda/"),
        ("PBS", "https://www.pbs.org/video/2-8xozmp/"),
    ],
    "More press": [
        ("Spike Art Magazine", "https://drive.google.com/file/d/1cJB7vF43Pm9Sx3GM7qPsQpHy9GcXDmV0/view?usp=sharing"),
        ("Arte al Día", "https://es.artealdia.com/Noticias/HERRAMIENTAS-EL-REVOLUCIONARIO-PROTOTIPO-DE-VIDEOJUEGO-TRANSMEDIA-DEL-ARTISTA-LEO-CASTANEDA-CON-OTRO-INVENTARIO"),
    ],
}

RECOGNITION = [
    {"title": "Whitney Biennial 2026", "detail": "Camoflux: Levels & Bosses, Incendio Igapó, playable installation", "year": "2026"},
    {"title": "Whitney Museum of American Art, permanent collection", "detail": "Camoflux Recall Grotto, commissioned for artport", "year": "2025"},
    {"title": "Knight New Work Grant", "detail": "Knight Foundation", "year": "2024"},
    {"title": "Knight / USA Artists Art + Tech Fellowship", "detail": "Knight Foundation and United States Artists", "year": "2023"},
    {"title": "YoungArts Artist Technology Fellowship", "detail": "National YoungArts Foundation", "year": "2023"},
    {"title": "Radical Gaming, HEK Basel", "detail": "Haus der Elektronischen Künste, Basel", "year": "2021"},
]

EXHIBITIONS = {
    "upcoming": [
        {"title": "Camoflux (TestRooms)", "venue": "Fredric Snitzer Gallery, Miami", "dates": "October 17 – November 15, 2026", "type": "Solo exhibition",
         "body": "3D-printed and painted sculptural work drawn from the world of Camoflux.",
         "url": "https://snitzer.com/"},     # CONFIRM: swap for the exhibition page when published
        {"title": "ELEKTRA Biennial", "venue": "Arsenal Contemporary Art, Montréal", "dates": "October 15 – November 15, 2026", "type": "Biennial",
         "body": "F(R)ICTION, a biennial devoted to art and games, bringing together around forty playable games, from artists' games to radical game design. Curated by Lynn Hughes and Ida Toft.",
         "url": "https://www.elektramontreal.ca/"},
        {"title": "artport: A History of Internet Art", "venue": "Whitney Museum of American Art, New York", "dates": "Opens November 21, 2026", "type": "Group exhibition",
         "body": "Camoflux Recall Grotto in the Whitney's 25th-anniversary artport exhibition, online and in the galleries.",
         "url": "https://whitney.org/exhibitions/camoflux-recall-grotto"},
        {"title": "Zero 10, Art Basel Miami Beach", "venue": "Miami Beach Convention Center", "dates": "December 4–6, 2026", "type": "Art fair, digital sector",
         "body": "Shown in the fair's section for art of the digital era.",
         "url": "https://www.artbasel.com/miami-beach/zero-10?lang=en"},
        {"title": "Worldbuilding Part III", "venue": "Canyon, New York", "dates": "Spring 2027", "type": "Group exhibition",
         "body": "The third edition of Hans Ulrich Obrist's exhibition on gaming and art in the digital age.",
         "url": "https://www.canyon.org/"},
        {"title": "Steam Next Fest", "venue": "Online", "dates": "June 2027", "type": "Public playtest",
         "body": "A public demo of Camoflux to gather wishlists and player feedback.",
         "url": "https://store.steampowered.com/app/897980/Camoflux_Levels__Bosses/"},
    ],
    "featured": {
        "title": "Whitney Biennial 2026",
        "url": "https://whitney.org/exhibitions/2026-biennial",
        "venue": "Whitney Museum of American Art, New York",
        "dates": "March 8 – August 23, 2026",
        "curators": "Marcela Guerrero and Drew Sawyer",
        "intro": "Camoflux was exhibited as a playable installation, alongside a 360-degree in-game video work and a browser-based commission for the Whitney's artport platform.",
        "works": [
            {"title": "Camoflux: Levels & Bosses, Incendio Igapó", "year": "2023–26",
             "media": "Ultra-high-definition video game, fiberglass furniture, vinyl",
             "body": "A playable chapter of Camoflux. The seating and surfaces shape how visitors enter, linger, and watch others at the controls.",
             "credits": None, "image": "mangrove-village"},
            {"title": "Camoflux Incendio Igapó 360", "year": "2026",
             "media": "360-degree in-game video capture, 8K, custom software, 8:10",
             "body": "The same spatial material recorded as a moving camera rather than played.",
             "credits": "In collaboration with María Thereza Negreiros. Programming: Jaime Soto Kure. Sound: Victor Gamboa. Furniture fabrication: Eric Cloutier.",
             "image": None},
            {"title": "Camoflux Recall Grotto", "year": "2025–26",
             "media": "Browser-based game, commissioned for artport",
             "body": "As an organic drone, gather water and sunlight to cultivate cyberflora across a primordial landscape; holographic memories surface from the vegetation. Acquired into the Whitney's collection.",
             "credits": None, "image": None},
        ],
        "quote": PRESS_FEATURED[1],
        "photos": ["whitney-install-amstutz", "whitney-install-fata", "whitney-visitors"],
    },
    "past": [
        {"title": "Whitney Biennial 2026", "venue": "Whitney Museum of American Art, New York", "year": "2026",
         "url": "https://whitney.org/exhibitions/2026-biennial"},
        {"title": "artport commission: Camoflux Recall Grotto", "venue": "Whitney Museum of American Art", "year": "2025",
         "url": "https://whitney.org/exhibitions/camoflux-recall-grotto"},
        {"title": "TRANSFER Download: Sea Change", "venue": "Pérez Art Museum Miami", "year": "2024",
         "url": "https://leonardocastaneda.com/camofluxmangrovebiome.html"},
        {"title": "Field Collisions: YoungArts Technology Fellowship", "venue": "Florida Supercon, Miami Beach", "year": "2024", "url": None},
        {"title": "Herramientas: Levels & Bosses", "venue": "Locust Projects, Miami", "year": "2022", "url": None},
        {"title": "Demo(s): Levels & Bosses", "venue": "Tile Blush Gallery, Miami", "year": "2021", "url": None},
        {"title": "Radical Gaming", "venue": "HEK Basel", "year": "2021",
         "url": "https://global-uploads.webflow.com/5a3b8af6706df50001a2fbf2/60b77ed72774afd4d3911628_PM_HEK_RadicalGaming%2BArtistList_EN.pdf"},
        {"title": "Levels and Bosses", "venue": "ArtSeen Gallery, Miami", "year": "2012", "url": None},
        {"title": "Moments in Level One, The Hall of Great Bosses and The Others", "venue": "Cooper Union, New York", "year": "2010", "url": None},
    ],
}

# Devlog, newest first. Set "draft": True to keep a post out of the build.
# These three are factual summaries; rewrite in your own voice before launch.  # CONFIRM
DEVLOG = [
    {"id": "testrooms-snitzer", "date": "2026-09-23", "category": "News", "draft": False,
     "title": "Camoflux (TestRooms) at Fredric Snitzer Gallery",
     "excerpt": "A solo exhibition of 3D-printed and painted sculptural work opens in Miami this October.",
     "body": [
         "Camoflux (TestRooms) opens at Fredric Snitzer Gallery in Miami in October 2026. The exhibition centers on 3D-printed and painted sculptural work drawn from the world of the game.",
         "Dates and opening details will be posted here and on the exhibitions page.",
     ],
     "image": "mangrove-entity"},
    {"id": "painting-as-terrain", "date": "2026-09-23", "category": "Process", "draft": False,
     "title": "Painting as terrain",
     "excerpt": "How María Thereza Negreiros's Amazonian paintings and a set of 2012 drawings became the surfaces of the game.",
     "body": [
         "The visual and philosophical core of Camoflux is the Amazonian series by María Thereza Negreiros: the Igapós, Selvas, and Incendios paintings. Scans of these works are embedded in the game as textures.",
         "Alongside them are patterned biomorphic drawings Leo Castañeda made after a trip to the Amazon in 2012. Forms are sculpted in Adobe Medium, ZBrush, and Blender, then assembled and lit in Unreal Engine 5.",
     ],
     "image": "igapo-butterfly-drone"},
    {"id": "whitney-biennial-2026", "date": "2026-03-08", "category": "Exhibition", "draft": False,
     "title": "Incendio Igapó at the 2026 Whitney Biennial",
     "excerpt": "A playable installation, a 360-degree video work, and an artport commission.",
     "body": [
         "Camoflux: Levels & Bosses, Incendio Igapó was on view at the Whitney Museum of American Art from March 8 to August 23, 2026, as part of the Biennial curated by Marcela Guerrero and Drew Sawyer.",
         "The installation presented a playable chapter of the game with fiberglass furniture and vinyl. Camoflux Incendio Igapó 360 was made in collaboration with María Thereza Negreiros, with programming by Jaime Soto Kure, sound by Victor Gamboa, and furniture fabrication by Eric Cloutier.",
         "Camoflux Recall Grotto, commissioned for the Whitney's artport platform, was acquired into the museum's collection.",
     ],
     "image": "mangrove-village"},
]

STUDIO = {
    "name": "Levels & Bosses",
    "lead": "Leo Castañeda",
    "short": "Levels & Bosses is the studio of Leo Castañeda, an artist and game developer born in Cali and based in Miami. His work spans painting, video games, sculpture, immersive media, and software.",
    "long": [
        "Levels & Bosses is the studio of Leo Castañeda (b. 1988, Cali, Colombia), a multimedia artist and video game designer exploring Latin American Surrealism in the digital age. His work takes the form of episodic games and immersive installations that meld atmospheric paintings, video, mixed reality, wearables, and sculpture.",
        "In 2026 Camoflux: Levels & Bosses, Incendio Igapó was exhibited in the Whitney Biennial, and Camoflux Recall Grotto, commissioned for the Whitney's artport, entered the museum's permanent collection. Castañeda is a Knight Foundation Arts + Technology Fellow, YoungArts Artist Technology Fellow, Emergent Strategy Ideation Institute Praxis Project Fellow, Ellies Creator Award recipient, and Harpo Foundation grantee.",
        "He has exhibited at the Whitney Museum of American Art, Pérez Art Museum Miami, the Bronx Museum of the Arts, Haus der elektronischen Künste Basel, Museu do Amanhã in Rio de Janeiro, Espacio ArtNexus Bogotá, Locust Projects Miami, and Museo de Arte Moderno La Tertulia in Colombia. He holds a BFA from Cooper Union and an MFA from Hunter College. Camoflux is published by Otro Inventario.",
    ],
    "team": [
        {"name": "Leo Castañeda", "role": "Director, artist, and game designer"},
        {"name": "Jaime Soto Kure", "role": "Lead programmer"},
        {"name": "Mar Sublaban", "role": "Media and exhibitions assistant"},
        {"name": "Lauren Monzón", "role": "Producer"},
        {"name": "Victor Gamboa", "role": "Sound designer"},
    ],
    "site": "https://leonardocastaneda.com/",
    "paintings_intro": "The paintings and the game are made from the same world. The lanterns, the mangrove hedge, and The Other appear on canvas and in the engine.",
}

# Merch. A buy link renders only when "url" is set and status is "available".
# Items below are concepts from real images; no prices or editions until they exist.  # CONFIRM
MERCH_NOTE = "Wearables and objects from Camoflux are in production. They will be listed here with prices and editions once available."
MERCH = []   # items return here with prices and editions once available

SOCIAL = [
    # Channel confirmed via GameScenes link. Others carried from the Steam page.  # CONFIRM handles
    {"label": "YouTube", "url": "https://www.youtube.com/@levelsandbosses"},
    {"label": "Instagram", "url": "https://www.instagram.com/levelsandbosses/"},
    {"label": "Instagram, Camoflux", "url": "https://www.instagram.com/camo.flux/"},
    {"label": "X", "url": "https://x.com/LevelsandBosses"},
    {"label": "TikTok", "url": "https://www.tiktok.com/@levelsandbosses"},
]
