const fileInput = document.getElementById("fileInput");
const plant = document.getElementById("plant");
const scannerBox = document.getElementById("scannerBox");
const startBtn = document.getElementById("start-scan");
const scanLine = document.querySelector(".scan-line");
const result = document.getElementById("result");

// When user uploads an image
fileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      plant.src = e.target.result; // show uploaded picture
      scannerBox.classList.remove("hidden");
      startBtn.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  }
});

// When "Start Scan" is clicked
startBtn.addEventListener("click", () => {
  scanLine.style.display = "block";
  startBtn.disabled = true;
  startBtn.innerText = "Scanning...";

  setTimeout(() => {
    scanLine.style.display = "none";
    plant.style.display = "none";       // hide uploaded picture
    result.classList.remove("hidden");  // show diagram.png from assets
    startBtn.innerText = "Scan Again";
    startBtn.disabled = false;
  }, 4000);
});
