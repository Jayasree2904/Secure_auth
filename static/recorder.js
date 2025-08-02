let mediaRecorder;
let audioChunks = [];

function recordVoice(mode) {
  const resultBox = document.getElementById("voiceResult");
  const micIcon = document.getElementById("micIcon");
  const micBtn = micIcon.closest("button");
  const username = document.getElementById("username").value;

  if (!username) {
    resultBox.innerText = "❌ Please enter a username first";
    return;
  }

  let countdown = 5;
  resultBox.innerText = `🎙️ Recording... (${countdown}s)`;
  micIcon.classList.add("listening");
  micBtn.disabled = true;

  const countdownInterval = setInterval(() => {
    countdown--;
    if (countdown > 0) {
      resultBox.innerText = `🎙️ Recording... (${countdown}s)`;
    }
  }, 1000);

  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => {
      if (!window.MediaRecorder) {
        throw new Error("MediaRecorder not supported");
      }

      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        clearInterval(countdownInterval);
        micIcon.classList.remove("listening");
        micBtn.disabled = false;

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", audioBlob);
        formData.append("username", username);
        formData.append("mode", mode);

        fetch("/process_audio", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              resultBox.innerText = "✅ Recognized: " + data.voice_text;
              document.getElementById("voice_text").value = data.voice_text;
            } else {
              resultBox.innerText = "❌ Voice not clear. Try again.";
              console.error("Voice recognition error:", data.error);
            }
          })
          .catch((err) => {
            resultBox.innerText = "❌ Voice recognition failed.";
            console.error(err);
          });

        // Properly stop all audio tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();

      // Stop recording after 5 seconds
      setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
          mediaRecorder.stop();
        }
      }, 5000);
    })
    .catch((err) => {
      clearInterval(countdownInterval);
      micIcon.classList.remove("listening");
      micBtn.disabled = false;
      resultBox.innerText = "❌ Microphone access denied.";
      console.error("Microphone error:", err);
    });
}
