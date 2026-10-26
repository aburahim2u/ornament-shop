class ProductCatalog {
  constructor() {
    this.products = [
      { id: 1, name: 'Solstice Pendant', category: 'Necklaces', price: 68, badge: 'Bestseller', image: '/assets/necklace_sources/solstice.jpg', alt: 'Gold statement necklace with detailed beadwork' },
      { id: 2, name: 'Sunday Hoops', category: 'Earrings', price: 42, badge: 'Everyday favorite', image: 'assets/try_on_sources/gold_hoops.jpg', alt: 'Sculptural gold hoop earrings' },
      { id: 3, name: 'Tidepool Signet', category: 'Rings', price: 54, badge: 'New', image: 'photo-1605100804763-247f67b3557e', alt: 'Gold signet ring with a polished finish' },
      { id: 4, name: 'Little Orbit', category: 'Nose rings', price: 28, badge: '', image: 'assets/try_on_sources/gold_hoops.jpg', alt: 'Small gold hoop jewelry detail' },
      { id: 5, name: 'Afterglow Chain', category: 'Necklaces', price: 76, badge: 'Just in', image: '/assets/necklace_sources/afterglow.jpg', alt: 'Gold chain necklace with an ornate centerpiece on blue fabric' },
      { id: 6, name: 'Petal Studs', category: 'Earrings', price: 36, badge: '', image: 'assets/try_on_sources/gemstone_earrings.jpg', alt: 'Gemstone stud earrings' },
      { id: 7, name: 'Soft Curve Cuff', category: 'Bracelets', price: 62, badge: '', image: 'assets/bracelet_sources/soft-curve-cuff.svg', alt: 'Minimal sculpted gold cuff bracelet' },
      { id: 8, name: 'The Keepsake', category: 'Rings', price: 48, badge: 'Bestseller', image: 'photo-1605100804763-247f67b3557e', alt: 'Delicate gold ring with a bright stone' },
      { id: 9, name: 'Daydream Chain', category: 'Necklaces', price: 84, badge: '', image: '/assets/necklace_sources/daydream.jpg', alt: 'Gold and teal beaded necklace' },
      { id: 10, name: 'Tiny Glint', category: 'Nose rings', price: 24, badge: '', image: 'assets/try_on_sources/gemstone_earrings.jpg', alt: 'Small gemstone jewelry detail' },
      { id: 11, name: 'Second-Skin Huggies', category: 'Earrings', price: 46, badge: 'Bestseller', image: 'assets/try_on_sources/gold_hoops.jpg', alt: 'Close-fitting gold huggie earrings' },
      { id: 12, name: 'Good Luck Bangle', category: 'Bracelets', price: 58, badge: 'Just in', image: 'assets/bracelet_sources/good-luck-bangle.svg', alt: 'Simple polished gold bangle bracelet' },
      { id: 13, name: 'Citrus Carnelian Drops', category: 'Earrings', price: 48, badge: 'New', image: 'assets/earring_sources/carnelian-earrings.jpg', alt: 'Gold drop earring with a carnelian stone styled with oranges' },
      { id: 14, name: 'Ribbonlight Hoops', category: 'Earrings', price: 44, badge: 'New', image: 'assets/earring_sources/gold-hoops-styled.jpg', alt: 'Gold hoop earrings styled on colorful candy ribbons' },
      { id: 15, name: 'Golden Spiral Hoops', category: 'Earrings', price: 52, badge: 'Just in', image: 'assets/earring_sources/gold-drop-earrings.jpg', alt: 'Pair of ornate gold hoop earrings on a pale display background' },
      { id: 16, name: 'Sunburst Studs', category: 'Earrings', price: 38, badge: 'New', image: 'assets/try_on_sources/gemstone_earrings.jpg', alt: 'Gemstone stud earrings' },
      { id: 17, name: 'Golden Hour Hoops', category: 'Earrings', price: 50, badge: 'Just in', image: 'assets/earring_sources/gold-hoops-styled.jpg', alt: 'Gold hoop earrings styled on colorful candy ribbons' },
      { id: 18, name: 'Moonlit Bangle Stack', category: 'Bracelets', price: 74, badge: 'New', image: 'assets/bracelet_sources/moonlit-stack.svg', alt: 'Three polished gold bangles stacked together' },
      { id: 19, name: 'Ember Stone Bangle', category: 'Bracelets', price: 86, badge: 'Just in', image: 'assets/bracelet_sources/ember-stone.svg', alt: 'Gold bangle with a warm oval gemstone setting' },
      { id: 20, name: 'Solstice Open Cuff', category: 'Bracelets', price: 68, badge: '', image: 'assets/bracelet_sources/solstice-cuff.svg', alt: 'Sculptural open gold cuff bracelet' },
      { id: 21, name: 'Keepsake Charm Bangle', category: 'Bracelets', price: 78, badge: 'Bestseller', image: 'assets/bracelet_sources/keepsake-charm.svg', alt: 'Fine gold bangle with a small hanging charm' },
    ];
  }

  findById(productId) {
    return this.products.find((product) => product.id === productId);
  }

  search(category, query, sortOrder) {
    const normalizedQuery = query.trim().toLowerCase();
    let matches = this.products.filter((product) => {
      const matchesCategory = category === 'All pieces' || product.category === category;
      const matchesQuery = `${product.name} ${product.category}`.toLowerCase().includes(normalizedQuery);
      return matchesCategory && matchesQuery;
    });

    if (sortOrder === 'low') matches = [...matches].sort((a, b) => a.price - b.price);
    if (sortOrder === 'high') matches = [...matches].sort((a, b) => b.price - a.price);
    return matches;
  }
}

class ToastNotifier {
  constructor(element) {
    this.element = element;
    this.timeout = undefined;
  }

  show(message) {
    this.element.textContent = message;
    this.element.classList.add('is-visible');
    window.clearTimeout(this.timeout);
    this.timeout = window.setTimeout(() => this.element.classList.remove('is-visible'), 2200);
  }
}

class ShoppingBag {
  constructor(countElement, buttonElement, notifier) {
    this.count = 0;
    this.countElement = countElement;
    this.buttonElement = buttonElement;
    this.notifier = notifier;
    this.buttonElement.addEventListener('click', () => {
      const label = this.count ? `${this.count} ${this.count === 1 ? 'piece' : 'pieces'} in your bag` : 'Your bag is waiting for something lovely';
      this.notifier.show(label);
    });
  }

  add(product) {
    this.count += 1;
    this.countElement.textContent = this.count;
    this.buttonElement.setAttribute('aria-label', `Shopping bag, ${this.count} ${this.count === 1 ? 'item' : 'items'}`);
    this.notifier.show(`${product.name} added to your bag`);
  }
}

class CatalogView {
  constructor(catalog, elements) {
    this.catalog = catalog;
    this.grid = elements.grid;
    this.searchInput = elements.searchInput;
    this.sortSelect = elements.sortSelect;
    this.resultCount = elements.resultCount;
    this.emptyState = elements.emptyState;
    this.activeCategory = 'All pieces';
  }

  setCategory(category) {
    this.activeCategory = category;
    this.render();
  }

  render() {
    const visibleProducts = this.catalog.search(
      this.activeCategory,
      this.searchInput.value,
      this.sortSelect.value,
    );
    this.resultCount.textContent = `${visibleProducts.length} ${visibleProducts.length === 1 ? 'piece' : 'pieces'}`;
    this.emptyState.hidden = visibleProducts.length > 0;
    this.grid.innerHTML = visibleProducts.map((product, index) => {
      const imageUrl = product.image.startsWith('/assets/') || product.image.startsWith('assets/')
        ? product.image
        : `https://images.unsplash.com/${product.image}?auto=format&fit=crop&w=760&q=80`;
      const supportsTryOn = ['Necklaces', 'Earrings', 'Nose rings', 'Bracelets'].includes(product.category);
      return `
        <article class="product-card" style="animation-delay:${Math.min(index * 45, 270)}ms">
          <div class="product-visual">
            <img src="${imageUrl}" alt="${product.alt}" loading="lazy" />
            ${product.badge ? `<span class="product-badge">${product.badge}</span>` : ''}
            <button class="favorite-button" type="button" aria-label="Save ${product.name}" aria-pressed="false">♡</button>
            <button class="quick-add" type="button" data-add="${product.id}">Add to bag · $${product.price}</button>
          </div>
          <div class="product-info">
            <div><h3 class="product-name">${product.name}</h3><p class="product-category">${product.category}</p></div>
            <span class="product-price">$${product.price}</span>
          </div>
          ${supportsTryOn ? `<button class="try-on-button" type="button" data-try-on="${product.id}">Try on with camera <span aria-hidden="true">↗</span></button>` : ''}
        </article>`;
    }).join('');
  }
}

class CameraTryOnController {
  constructor(elements) {
    this.dialog = elements.dialog;
    this.productName = elements.productName;
    this.banglePicker = elements.banglePicker;
    this.bangleOptions = elements.bangleOptions;
    this.bangleSelectionStatus = elements.bangleSelectionStatus;
    this.video = elements.video;
    this.stage = elements.stage;
    this.preview = elements.preview;
    this.status = elements.status;
    this.canvas = elements.canvas;
    this.stream = undefined;
    this.timer = undefined;
    this.framePending = false;
    this.requestVersion = 0;
    this.bangleProducts = [];
    this.selectedBangles = [];
    this.bangleImages = new Map();
    this.bangleSelectionVersion = 0;
    this.selectionPending = false;
    this.bangleWidth = undefined;
    this.bangleOptions.addEventListener('change', () => this.handleBangleSelectionChange());
  }

  async open(product, bangleProducts) {
    this.stop();
    this.requestVersion += 1;
    const requestVersion = this.requestVersion;
    const isHandTryOn = product.category === 'Bracelets';
    this.banglePicker.hidden = !isHandTryOn;
    this.bangleProducts = isHandTryOn ? bangleProducts : [];
    this.selectedBangles = isHandTryOn ? [product] : [];
    this.renderBangleOptions();
    this.updateBangleSummary();
    this.stage.classList.toggle('is-hand-try-on', isHandTryOn);
    this.dialog.showModal();
    this.status.textContent = isHandTryOn ? 'Loading the selected bracelet...' : 'Requesting camera access...';
    this.bangleSelectionStatus.textContent = isHandTryOn
      ? 'Select one or more bangles to preview together.'
      : '';
    this.preview.removeAttribute('src');
    this.preview.hidden = true;

    if (isHandTryOn) {
      try {
        await this.loadBangleImage(product);
      } catch (error) {
        if (requestVersion === this.requestVersion) {
          this.status.textContent = error.message;
        }
        return;
      }
      if (requestVersion !== this.requestVersion) return;
      this.status.textContent = 'Requesting camera access...';
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      this.status.textContent = 'Camera access is unavailable. Open this page at localhost in a modern browser.';
      return;
    }

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'user' }, width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      if (requestVersion !== this.requestVersion) {
        this.stream.getTracks().forEach((track) => track.stop());
        return;
      }
      this.video.srcObject = this.stream;
      await this.video.play();
      this.video.hidden = false;
      this.status.textContent = isHandTryOn
        ? 'Hold your hand upright in the frame with your wrist visible.'
        : 'Center your face in the frame. Earring placement follows your face as you turn.';
      this.timer = window.setInterval(() => this.processFrame(product, requestVersion), 200);
      this.processFrame(product, requestVersion);
    } catch (error) {
      if (requestVersion !== this.requestVersion) return;
      this.status.textContent = error.name === 'NotAllowedError'
        ? 'Camera permission was not granted. Allow camera access and try again.'
        : 'Could not start the camera. Check that a camera is connected.';
      this.stop();
    }
  }

  renderBangleOptions() {
    const selectedIds = new Set(this.selectedBangles.map((bangle) => bangle.id));
    this.bangleOptions.innerHTML = this.bangleProducts.map((bangle) => `
      <label class="bangle-option">
        <input type="checkbox" value="${bangle.id}" ${selectedIds.has(bangle.id) ? 'checked' : ''} />
        <img src="${bangle.image}" alt="" />
        <span>${bangle.name}</span>
      </label>`).join('');
  }

  updateBangleSummary() {
    if (this.selectedBangles.length === 1) {
      this.productName.textContent = this.selectedBangles[0].name;
    } else {
      this.productName.textContent = `${this.selectedBangles.length} bangles selected`;
    }
  }

  async handleBangleSelectionChange() {
    const selectedIds = [...this.bangleOptions.querySelectorAll('input:checked')]
      .map((input) => Number(input.value));
    if (!selectedIds.length) {
      this.bangleSelectionVersion += 1;
      this.selectionPending = false;
      this.renderBangleOptions();
      this.bangleSelectionStatus.textContent = 'Keep at least one bangle selected for the preview.';
      return;
    }

    const selectionVersion = ++this.bangleSelectionVersion;
    const nextSelection = selectedIds
      .map((id) => this.bangleProducts.find((bangle) => bangle.id === id))
      .filter(Boolean);
    this.selectionPending = true;
    this.bangleSelectionStatus.textContent = 'Preparing selected bangles...';
    try {
      await Promise.all(nextSelection.map((bangle) => this.loadBangleImage(bangle)));
      if (selectionVersion !== this.bangleSelectionVersion || !this.dialog.open) return;
      this.selectedBangles = nextSelection;
      this.updateBangleSummary();
      this.bangleSelectionStatus.textContent =
        `${nextSelection.length} ${nextSelection.length === 1 ? 'bangle' : 'bangles'} will be shown together.`;
    } catch (error) {
      if (selectionVersion !== this.bangleSelectionVersion) return;
      this.renderBangleOptions();
      this.bangleSelectionStatus.textContent = error.message;
    } finally {
      if (selectionVersion === this.bangleSelectionVersion) this.selectionPending = false;
    }
  }

  loadBangleImage(product) {
    const cachedImage = this.bangleImages.get(product.id);
    if (cachedImage) return Promise.resolve(cachedImage);

    const imagePromise = this.loadProductImage(product.image)
      .then((image) => {
        this.bangleImages.set(product.id, image);
        return image;
      })
      .catch((error) => {
        if (this.bangleImages.get(product.id) === imagePromise) {
          this.bangleImages.delete(product.id);
        }
        throw error;
      });
    this.bangleImages.set(product.id, imagePromise);
    return imagePromise;
  }

  loadProductImage(source) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = Math.round(canvas.width * image.naturalHeight / image.naturalWidth);
        const context = canvas.getContext('2d');
        if (!context) {
          reject(new Error('Could not prepare the selected bracelet image.'));
          return;
        }
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/jpeg', 0.9));
      };
      image.onerror = () => reject(new Error('Could not load the selected bracelet image.'));
      image.src = source;
    });
  }

  async processFrame(product, requestVersion) {
    if (!this.video.videoWidth || this.framePending || this.selectionPending || requestVersion !== this.requestVersion) return;
    this.framePending = true;
    this.canvas.width = this.video.videoWidth;
    this.canvas.height = this.video.videoHeight;
    const context = this.canvas.getContext('2d');
    if (!context) {
      this.status.textContent = 'Could not prepare a camera frame. Please reload and try again.';
      this.framePending = false;
      return;
    }
    context.translate(this.canvas.width, 0);
    context.scale(-1, 1);
    context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
    context.setTransform(1, 0, 0, 1, 0, 0);

    try {
      const response = await fetch('/api/try-on', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: this.canvas.toDataURL('image/jpeg', 0.72),
          product_id: product.category === 'Bracelets' ? this.selectedBangles[0].id : product.id,
          ...(product.category === 'Bracelets' ? {
            bangles: this.selectedBangles.map((bangle) => ({
              product_id: bangle.id,
              product_image: this.bangleImages.get(bangle.id),
            })),
            ...(this.bangleWidth ? { bangle_width: this.bangleWidth } : {}),
          } : {}),
        }),
      });
      const result = await response.json();
      if (!response.ok) {
        if (response.status >= 400 && response.status < 500) {
          this.status.textContent = result.error
            ? `The try-on service rejected this request: ${result.error} Restart the app with the latest code and try again.`
            : 'The try-on service rejected this request. Restart the app with the latest code and try again.';
          window.clearInterval(this.timer);
          this.timer = undefined;
          return;
        }
        throw new Error(result.error || 'Try-on processing failed.');
      }
      if (requestVersion !== this.requestVersion || !this.dialog.open) return;
      if (result.category === 'bracelet' && result.placed && Number.isInteger(result.bangle_width)) {
        this.bangleWidth = result.bangle_width;
      }
      this.preview.src = result.preview;
      this.preview.hidden = false;
      if (!result.found && result.category === 'bracelet') {
        this.status.textContent = 'No hand found yet. Hold your hand upright with your wrist visible.';
      } else if (!result.found) {
        this.status.textContent = 'No face found yet. Move into the frame and look toward the camera.';
      } else if (!result.placed) {
        this.status.textContent = result.category === 'bracelet'
          ? 'Move your hand closer so your wrist fills more of the frame.'
          : 'Your face is too far away. Move closer to align the selected piece.';
      } else if (result.category === 'bracelet') {
        this.status.textContent = result.placed_bangles === 1
          ? `${this.selectedBangles[0].name} fitted to your wrist.`
          : `${result.placed_bangles} bangles fitted to your wrist.`;
      } else if (result.category === 'earring') {
        this.status.textContent = `${product.name} placement follows your face as you turn.`;
      } else if (result.category === 'nose_ring') {
        this.status.textContent = `${product.name} fitted to your nostril.`;
      } else {
        this.status.textContent = `${product.name} aligned to your neckline.`;
      }
    } catch (error) {
      if (requestVersion === this.requestVersion && this.dialog.open) {
        this.status.textContent = error.message || 'The try-on service is not responding. Restart the Python app and try again.';
        window.clearInterval(this.timer);
        this.timer = undefined;
      }
    } finally {
      if (requestVersion === this.requestVersion) this.framePending = false;
    }
  }

  stop() {
    this.requestVersion += 1;
    window.clearInterval(this.timer);
    this.timer = undefined;
    this.stream?.getTracks().forEach((track) => track.stop());
    this.stream = undefined;
    this.selectedBangles = [];
    this.bangleProducts = [];
    this.bangleOptions.replaceChildren();
    this.banglePicker.hidden = true;
    this.selectionPending = false;
    this.bangleSelectionVersion += 1;
    this.bangleWidth = undefined;
    this.video.srcObject = null;
    this.framePending = false;
  }
}

class CatalogController {
  constructor(catalog, view, bag, tryOn, notifier) {
    this.catalog = catalog;
    this.view = view;
    this.bag = bag;
    this.tryOn = tryOn;
    this.notifier = notifier;
    this.bindEvents();
  }

  bindEvents() {
    document.querySelectorAll('.category-chip').forEach((button) => {
      button.addEventListener('click', () => this.selectCategory(button.dataset.category));
    });
    document.querySelectorAll('[data-nav-category]').forEach((link) => {
      link.addEventListener('click', () => this.selectCategory(link.dataset.navCategory));
    });
    this.view.searchInput.addEventListener('input', () => this.view.render());
    this.view.sortSelect.addEventListener('change', () => this.view.render());
    document.querySelector('#search-focus').addEventListener('click', () => {
      document.querySelector('#shop').scrollIntoView({ behavior: 'smooth' });
      this.view.searchInput.focus({ preventScroll: true });
    });
    this.view.grid.addEventListener('click', (event) => this.handleProductAction(event));
  }

  selectCategory(category) {
    this.view.setCategory(category);
    document.querySelectorAll('.category-chip').forEach((chip) => {
      chip.classList.toggle('is-active', chip.dataset.category === category);
    });
  }

  handleProductAction(event) {
    const tryOnButton = event.target.closest('[data-try-on]');
    if (tryOnButton) {
      const product = this.catalog.findById(Number(tryOnButton.dataset.tryOn));
      if (product) {
        const bangles = this.catalog.products.filter((item) => item.category === 'Bracelets');
        this.tryOn.open(product, bangles);
      }
      return;
    }

    const addButton = event.target.closest('[data-add]');
    if (addButton) {
      const product = this.catalog.findById(Number(addButton.dataset.add));
      if (product) this.bag.add(product);
      return;
    }

    const favoriteButton = event.target.closest('.favorite-button');
    if (!favoriteButton) return;
    const isFavorite = favoriteButton.getAttribute('aria-pressed') !== 'true';
    favoriteButton.setAttribute('aria-pressed', String(isFavorite));
    favoriteButton.classList.toggle('is-favorite', isFavorite);
    favoriteButton.setAttribute('aria-label', `${isFavorite ? 'Remove' : 'Save'} ${favoriteButton.getAttribute('aria-label').replace(/^(Save|Remove) /, '')}`);
  }
}

class OrnamentStudioApplication {
  constructor() {
    const catalog = new ProductCatalog();
    const notifier = new ToastNotifier(document.querySelector('#toast'));
    const bag = new ShoppingBag(
      document.querySelector('#bag-count'),
      document.querySelector('#bag-button'),
      notifier,
    );
    const tryOn = new CameraTryOnController({
      dialog: document.querySelector('#try-on-dialog'),
      productName: document.querySelector('#try-on-product-name'),
      banglePicker: document.querySelector('#bangle-picker'),
      bangleOptions: document.querySelector('#bangle-options'),
      bangleSelectionStatus: document.querySelector('#bangle-selection-status'),
      video: document.querySelector('#camera-video'),
      stage: document.querySelector('.camera-stage'),
      preview: document.querySelector('#try-on-preview'),
      status: document.querySelector('#camera-status'),
      canvas: document.querySelector('#capture-canvas'),
    });
    const view = new CatalogView(catalog, {
      grid: document.querySelector('#product-grid'),
      searchInput: document.querySelector('#product-search'),
      sortSelect: document.querySelector('#sort-products'),
      resultCount: document.querySelector('#result-count'),
      emptyState: document.querySelector('#empty-state'),
    });
    new CatalogController(catalog, view, bag, tryOn, notifier);
    document.querySelector('#close-try-on').addEventListener('click', () => tryOn.dialog.close());
    tryOn.dialog.addEventListener('close', () => tryOn.stop());
    tryOn.dialog.addEventListener('click', (event) => {
      if (event.target === tryOn.dialog) tryOn.dialog.close();
    });
    view.render();
  }
}

new OrnamentStudioApplication();
