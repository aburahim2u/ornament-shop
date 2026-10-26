# Ornament Studio

A responsive jewelry storefront for browsing necklaces, earrings, rings, nose rings, and bracelets, with camera-based try-on for necklaces, earrings, nose rings, and bracelets.

## Run it

The virtual try-on needs the Python service so the browser can securely request the camera from localhost and send frames for face- or hand-landmark processing.

1. Create a virtual environment with `python -m venv .venv`, then activate it in PowerShell with `.\.venv\Scripts\Activate.ps1` from the project root.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the app from the project folder: `python app.py`. If the catalog or try-on code has changed while the server was running, stop that process with Ctrl+C and start it again.
4. Open `http://127.0.0.1:5000` and choose **Try on with camera** on a necklace, earring, nose ring, or bracelet.

Allow camera access when prompted. The preview detects facial landmarks (it does not identify people) for necklaces, earrings, and nose rings, or hand landmarks for bracelets, then fits the selected piece to the neckline, visible earlobes, nostril, or wrist. Earring wires are anchored at an estimated lobe position derived from the face landmarks; overlays follow the detected face tilt, and the far-side earring is hidden when a turned face obscures that ear. Necklace pixels are extracted from their matching catalog photos; earrings and nose rings use transparent cutouts of the catalog jewelry photography in `assets/try_on_sources/`. Bracelet overlays are placed farther onto the forearm, away from the palm, and sized to be wider than the detected hand. Their size is set from the first clear hand frame and stays fixed as the hand turns during that camera session. Select multiple bracelets in the try-on dialog to preview them as a stack along the forearm. A hand-shaped occlusion mask hides the rear, hand-facing arc while leaving the forearm-facing arc visible so the bangle reads as worn around the wrist. Camera frames are sent only to this local service and are not saved. Most product photography and web fonts load from Unsplash and Google Fonts, so the catalog requires an internet connection.

The additional earring catalog photos are bundled in `assets/earring_sources/`. Their corresponding transparent try-on cutouts are in `assets/try_on_sources/`. Bracelet catalog illustrations are bundled in `assets/bracelet_sources/`. `gold-drop-earrings.jpg` is from [The Metropolitan Museum of Art](https://commons.wikimedia.org/wiki/File:Gold_earrings_MET_DP257466.jpg) and is CC0. `carnelian-earrings.jpg` and `gold-hoops-styled.jpg` are by W. Carter ([carnelian earrings](https://commons.wikimedia.org/wiki/File:Gold_earrings_with_carnelian_on_oranges_by_ASQ.jpg), [gold hoop earrings](https://commons.wikimedia.org/wiki/File:Gold_hoop_earrings_with_candy_rolls_by_ASQ.jpg)) and are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Catalog interactions

- Filter by ornament type or search by product name and category.
- Sort the catalog by price.
- Save favorites and add pieces to the shopping bag counter.
- Open a live camera preview for necklace, earring, nose-ring, and bracelet products.
- For a bracelet try-on, select one or more bangles in the dialog to preview a stack together; each bangle is placed along the forearm.

## Application structure

The browser separates catalog data, rendering, shopping-bag behavior, notifications, and camera try-on into focused classes. The Flask service separates product configuration, request validation, face-landmark detection, asset loading, compositing, and request orchestration. The `create_app` factory accepts an injected try-on service for isolated API tests.
