const products = [
  { id: 1, name: 'Solstice Pendant', category: 'Necklaces', price: 68, badge: 'Bestseller', image: '/assets/necklace_sources/solstice.jpg', alt: 'Gold statement necklace with detailed beadwork' },
  { id: 2, name: 'Sunday Hoops', category: 'Earrings', price: 42, badge: 'Everyday favorite', image: 'photo-1535632066927-ab7c9ab60908', alt: 'Sculptural gold hoop earrings' },
  { id: 3, name: 'Tidepool Signet', category: 'Rings', price: 54, badge: 'New', image: 'photo-1605100804763-247f67b3557e', alt: 'Gold signet ring with a polished finish' },
  { id: 4, name: 'Little Orbit', category: 'Nose rings', price: 28, badge: '', image: 'photo-1617038220319-276d3cfab638', alt: 'Small gold hoop jewelry detail' },
  { id: 5, name: 'Afterglow Chain', category: 'Necklaces', price: 76, badge: 'Just in', image: '/assets/necklace_sources/afterglow.jpg', alt: 'Gold chain necklace with an ornate centerpiece on blue fabric' },
  { id: 6, name: 'Petal Studs', category: 'Earrings', price: 36, badge: '', image: 'photo-1611591437281-460bfbe1220a', alt: 'Small gold flower stud earrings' },
  { id: 7, name: 'Soft Curve Cuff', category: 'Bracelets', price: 62, badge: '', image: 'photo-1611652022419-a9419f74343d', alt: 'Minimal gold cuff bracelet' },
  { id: 8, name: 'The Keepsake', category: 'Rings', price: 48, badge: 'Bestseller', image: 'photo-1605100804763-247f67b3557e', alt: 'Delicate gold ring with a bright stone' },
  { id: 9, name: 'Daydream Chain', category: 'Necklaces', price: 84, badge: '', image: '/assets/necklace_sources/daydream.jpg', alt: 'Gold and teal beaded necklace' },
  { id: 10, name: 'Tiny Glint', category: 'Nose rings', price: 24, badge: '', image: 'photo-1535632066927-ab7c9ab60908', alt: 'Tiny polished gold hoop' },
  { id: 11, name: 'Second-Skin Huggies', category: 'Earrings', price: 46, badge: 'Bestseller', image: 'photo-1611591437281-460bfbe1220a', alt: 'Close-fitting gold huggie earrings' },
  { id: 12, name: 'Good Luck Bangle', category: 'Bracelets', price: 58, badge: 'Just in', image: 'photo-1611652022419-a9419f74343d', alt: 'Simple gold bangle bracelet' },
];

const grid = document.querySelector('#product-grid');
const searchInput = document.querySelector('#product-search');
const sortSelect = document.querySelector('#sort-products');
const resultCount = document.querySelector('#result-count');
const emptyState = document.querySelector('#empty-state');
const bagCount = document.querySelector('#bag-count');
const toast = document.querySelector('#toast');
const tryOnDialog = document.querySelector('#try-on-dialog');
const cameraVideo = document.querySelector('#camera-video');
const tryOnPreview = document.querySelector('#try-on-preview');
const cameraStatus = document.querySelector('#camera-status');
const captureCanvas = document.querySelector('#capture-canvas');
let activeCategory = 'All pieces';
let bagItems = 0;
let toastTimeout;
let cameraStream;
let cameraTimer;
let framePending = false;

function renderProducts() {
  const query = searchInput.value.trim().toLowerCase();
  let visibleProducts = products.filter((product) => {
    const matchesCategory = activeCategory === 'All pieces' || product.category === activeCategory;
    const matchesQuery = `${product.name} ${product.category}`.toLowerCase().includes(query);
    return matchesCategory && matchesQuery;
  });

  if (sortSelect.value === 'low') visibleProducts = [...visibleProducts].sort((a, b) => a.price - b.price);
  if (sortSelect.value === 'high') visibleProducts = [...visibleProducts].sort((a, b) => b.price - a.price);

  resultCount.textContent = `${visibleProducts.length} ${visibleProducts.length === 1 ? 'piece' : 'pieces'}`;
  emptyState.hidden = visibleProducts.length > 0;
  grid.innerHTML = visibleProducts.map((product, index) => {
    const imageUrl = product.image.startsWith('/assets/')
      ? product.image
      : `https://images.unsplash.com/${product.image}?auto=format&fit=crop&w=760&q=80`;
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
      ${product.category === 'Necklaces' ? `<button class="try-on-button" type="button" data-try-on="${product.id}">Try on with camera <span aria-hidden="true">↗</span></button>` : ''}
    </article>`;
  }).join('');
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('is-visible');
  window.clearTimeout(toastTimeout);
  toastTimeout = window.setTimeout(() => toast.classList.remove('is-visible'), 2200);
}

document.querySelectorAll('.category-chip').forEach((button) => {
  button.addEventListener('click', () => {
    activeCategory = button.dataset.category;
    document.querySelectorAll('.category-chip').forEach((chip) => chip.classList.toggle('is-active', chip === button));
    renderProducts();
  });
});

document.querySelectorAll('[data-nav-category]').forEach((link) => {
  link.addEventListener('click', () => {
    activeCategory = link.dataset.navCategory;
    document.querySelectorAll('.category-chip').forEach((chip) => chip.classList.toggle('is-active', chip.dataset.category === activeCategory));
    renderProducts();
  });
});

searchInput.addEventListener('input', renderProducts);
sortSelect.addEventListener('change', renderProducts);
document.querySelector('#search-focus').addEventListener('click', () => {
  document.querySelector('#shop').scrollIntoView({ behavior: 'smooth' });
  searchInput.focus({ preventScroll: true });
});

grid.addEventListener('click', (event) => {
  const tryOnButton = event.target.closest('[data-try-on]');
  if (tryOnButton) {
    const product = products.find((item) => item.id === Number(tryOnButton.dataset.tryOn));
    openTryOn(product);
    return;
  }

  const addButton = event.target.closest('[data-add]');
  if (addButton) {
    const product = products.find((item) => item.id === Number(addButton.dataset.add));
    bagItems += 1;
    bagCount.textContent = bagItems;
    document.querySelector('#bag-button').setAttribute('aria-label', `Shopping bag, ${bagItems} ${bagItems === 1 ? 'item' : 'items'}`);
    showToast(`${product.name} added to your bag`);
    return;
  }

  const favoriteButton = event.target.closest('.favorite-button');
  if (favoriteButton) {
    const isFavorite = favoriteButton.getAttribute('aria-pressed') !== 'true';
    favoriteButton.setAttribute('aria-pressed', String(isFavorite));
    favoriteButton.classList.toggle('is-favorite', isFavorite);
    favoriteButton.setAttribute('aria-label', `${isFavorite ? 'Remove' : 'Save'} ${favoriteButton.getAttribute('aria-label').replace(/^(Save|Remove) /, '')}`);
  }
});

async function openTryOn(product) {
  document.querySelector('#try-on-product-name').textContent = product.name;
  tryOnDialog.showModal();
  cameraStatus.textContent = 'Requesting camera access...';
  tryOnPreview.removeAttribute('src');

  if (!navigator.mediaDevices?.getUserMedia) {
    cameraStatus.textContent = 'Camera access is unavailable. Open this page at localhost in a modern browser.';
    return;
  }

  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'user' }, width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false,
    });
    cameraVideo.srcObject = cameraStream;
    await cameraVideo.play();
    cameraStatus.textContent = 'Center your face and shoulders in the frame.';
    cameraTimer = window.setInterval(() => processCameraFrame(product.id), 450);
    processCameraFrame(product.id);
  } catch (error) {
    cameraStatus.textContent = error.name === 'NotAllowedError'
      ? 'Camera permission was not granted. Allow camera access and try again.'
      : 'Could not start the camera. Check that a camera is connected.';
  }
}

async function processCameraFrame(productId) {
  if (!cameraVideo.videoWidth || framePending) return;
  framePending = true;
  captureCanvas.width = cameraVideo.videoWidth;
  captureCanvas.height = cameraVideo.videoHeight;
  const context = captureCanvas.getContext('2d');
  context.translate(captureCanvas.width, 0);
  context.scale(-1, 1);
  context.drawImage(cameraVideo, 0, 0, captureCanvas.width, captureCanvas.height);
  context.setTransform(1, 0, 0, 1, 0, 0);

  try {
    const response = await fetch('/api/try-on', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: captureCanvas.toDataURL('image/jpeg', 0.72), product_id: productId }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Try-on processing failed.');
    tryOnPreview.src = result.preview;
    cameraStatus.textContent = result.found
      ? 'Necklace preview aligned to your face and neckline.'
      : 'No face found yet. Move into the frame and look toward the camera.';
  } catch {
    cameraStatus.textContent = 'The try-on service is not responding. Restart the Python app and try again.';
  } finally {
    framePending = false;
  }
}

function stopCamera() {
  window.clearInterval(cameraTimer);
  cameraTimer = undefined;
  cameraStream?.getTracks().forEach((track) => track.stop());
  cameraStream = undefined;
  cameraVideo.srcObject = null;
  framePending = false;
}

tryOnDialog.addEventListener('close', stopCamera);
document.querySelector('#close-try-on').addEventListener('click', () => tryOnDialog.close());
tryOnDialog.addEventListener('click', (event) => {
  if (event.target === tryOnDialog) tryOnDialog.close();
});

document.querySelector('#bag-button').addEventListener('click', () => {
  showToast(bagItems ? `${bagItems} ${bagItems === 1 ? 'piece' : 'pieces'} in your bag` : 'Your bag is waiting for something lovely');
});

renderProducts();
