# Ornament Studio

A responsive jewelry storefront for browsing necklaces, earrings, rings, nose rings, and bracelets, with a camera-based necklace preview.

## Run it

The virtual try-on needs the Python service so the browser can securely request the camera from localhost and send frames for face and shoulder landmark processing.

1. Create a virtual environment with `python -m venv .venv`, then activate it in PowerShell with `.\.venv\Scripts\Activate.ps1` from the project root.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the app: `python app.py`.
4. Open `http://127.0.0.1:5000`, choose **Try on with camera** on a necklace, and select additional pieces in **Layer your look**.

Allow camera access when prompted. The preview detects face and shoulder landmarks (it does not identify people), scales and centers the selected necklaces into progressively longer layers around the neckline, and falls back to face landmarks if shoulders are out of frame. Camera frames are sent only to this local service and are not saved. The three necklace overlay source photos are in `assets/necklace_sources/`; other product photography and web fonts load from Unsplash and Google Fonts, so those assets require an internet connection.

## Catalog interactions

- Filter by ornament type or search by product name and category.
- Sort the catalog by price.
- Save favorites and add pieces to the shopping bag counter.
- Open a live camera preview for necklace products.
