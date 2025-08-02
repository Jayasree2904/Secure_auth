const video = document.getElementById("gestureVideo");
const statusText = document.getElementById("gestureStatus");
const gestureArrayInput = document.getElementById("gesture_array");
const gestureImageInput = document.getElementById("gesture_image");

let lastLandmarks = null;
let gestureCaptured = false;  // ✅ Added to prevent overwrite

// Start camera stream
navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
  video.srcObject = stream;
});

// MediaPipe Hands setup
const hands = new Hands({
  locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
});

hands.setOptions({
  maxNumHands: 1,
  modelComplexity: 1,
  minDetectionConfidence: 0.7,
  minTrackingConfidence: 0.7
});

// Store landmarks when hand is detected
hands.onResults(results => {
  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    const landmarks = results.multiHandLandmarks[0].map(p => [p.x, p.y, p.z]);
    gestureArrayInput.value = JSON.stringify(landmarks);
    lastLandmarks = landmarks;
    // ✅ Only show status if not already captured
    if (!gestureCaptured) {
      statusText.innerText = "🖐️ Hand Detected. Ready to Capture.";
      statusText.style.color = "green";
    }
  } else {
    lastLandmarks = null;
    statusText.innerText = "👋 Waiting for hand...";
    statusText.style.color = "gray";
    gestureCaptured = false;  // Reset when hand not visible
  }
});

// Attach camera to hands detection
const camera = new Camera(video, {
  onFrame: async () => await hands.send({ image: video }),
  width: 320,
  height: 240
});
camera.start();

// Called when "Capture Gesture" button is clicked
function captureGesture() {
  if (!lastLandmarks) {
    alert("❌ No hand detected. Please show your hand clearly.");
    statusText.innerText = "❌ No hand detected";
    statusText.style.color = "red";
    return;
  }

  // Store gesture array
  gestureArrayInput.value = JSON.stringify(lastLandmarks);

  // Capture image snapshot
  const canvas = document.createElement("canvas");
  canvas.width = 320;
  canvas.height = 240;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  gestureImageInput.value = canvas.toDataURL("image/jpeg", 0.6);

  // ✅ Show confirmation message
  gestureCaptured = true;
  statusText.innerText = "✅ Gesture Captured Successfully!";
  statusText.style.color = "#28a745"; // green color
  console.log("✅ Gesture landmarks captured:", lastLandmarks);
}
