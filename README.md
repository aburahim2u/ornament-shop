# Ornament Studio

A responsive jewelry storefront for browsing necklaces, earrings, rings, nose rings, and bracelets, with a camera-based necklace preview.

## Run it

The virtual try-on needs the Python service so the browser can securely request the camera from localhost and send frames for face-landmark processing.

1. Create a virtual environment with `python -m venv .venv`, then activate it in PowerShell with `.\.venv\Scripts\Activate.ps1` from the project root.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the app: `python app.py`.
4. Open `http://127.0.0.1:5000` and choose **Try on with camera** on a necklace.

Allow camera access when prompted. The preview detects face landmarks (it does not identify people), extracts the selected necklace from its matching catalog photo, and composites those product pixels at the detected neckline. Camera frames are sent only to this local service and are not saved. The three necklace overlay source photos are in `assets/necklace_sources/`; other product photography and web fonts load from Unsplash and Google Fonts, so those assets require an internet connection.

## Catalog interactions

- Filter by ornament type or search by product name and category.
- Sort the catalog by price.
- Save favorites and add pieces to the shopping bag counter.
- Open a live camera preview for necklace products.
