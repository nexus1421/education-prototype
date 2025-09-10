// Navigation system: show selected page
function showPage(pageId) {
  document.querySelectorAll('.page').forEach(page => {
    page.classList.remove('active');
  });
  document.getElementById(pageId).classList.add('active');

  document.querySelectorAll('.nav-card').forEach(card => {
    card.classList.remove('active');
  });
  event.currentTarget.classList.add('active');
}

// File upload + preview
const fileInput = document.getElementById('fileInput');
const previewImage = document.getElementById('previewImage');
const scannerContainer = document.getElementById('scannerContainer');
const startScanBtn = document.getElementById('startScan');

fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(ev) {
      previewImage.src = ev.target.result;
      scannerContainer.classList.remove('hidden');
      startScanBtn.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  }
});

// Simulate scanning
startScanBtn.addEventListener('click', () => {
  document.getElementById('scanOverlay').classList.remove('hidden');

  setTimeout(() => {
    document.getElementById('scanOverlay').classList.add('hidden');
    document.getElementById('results').classList.remove('hidden');
  }, 3000);
});
