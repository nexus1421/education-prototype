const fileInput = document.getElementById("fileInput");
const plant = document.getElementById("plant");
const scannerBox = document.getElementById("scannerBox");
const startBtn = document.getElementById("start-scan");
const scanLine = document.querySelector(".scan-line");
const result = document.getElementById("result");
const progress = document.querySelector(".progress");

fileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      plant.src = e.target.result;
      scannerBox.classList.remove("hidden");
      startBtn.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  }
});

startBtn.addEventListener("click", () => {
  scanLine.style.display = "block";
  startBtn.disabled = true;
  startBtn.innerText = "Scanning...";

  setTimeout(() => {
    scanLine.style.display = "none";
    plant.style.display = "none";
    result.classList.remove("hidden");
    progress.style.width = "100%"; // animate progress
    startBtn.innerText = "Scan Again";
    startBtn.disabled = false;
  }, 3500);
});
