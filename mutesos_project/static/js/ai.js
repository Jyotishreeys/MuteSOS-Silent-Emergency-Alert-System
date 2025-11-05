document.addEventListener("DOMContentLoaded", function() {
    const voiceBtn = document.getElementById('voice-trigger-btn');
    const companionBtn = document.getElementById('companion-btn');

    // =========================
    // VOICE TRIGGER FUNCTIONALITY
    // =========================
    if (voiceBtn) {
        voiceBtn.addEventListener('click', async function() {
            // Check for microphone support
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert("Microphone not supported in this browser.");
                return;
            }

            try {
                // Ask for microphone access
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                let audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'voice_trigger.wav');

                    // Send to backend
                    const response = await fetch('/ai_module/voice_trigger/', {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin',
                        headers: {
                            'X-CSRFToken': getCSRFToken()
                        }
                    });

                    const data = await response.json();
                    alert(data.status);

                    // Stop all audio tracks
                    stream.getTracks().forEach(track => track.stop());
                };

                // Start recording for 5 seconds
                mediaRecorder.start();
                voiceBtn.innerText = "Recording...";
                voiceBtn.disabled = true;

                setTimeout(() => {
                    mediaRecorder.stop();
                    voiceBtn.innerText = "Start Voice Trigger";
                    voiceBtn.disabled = false;
                }, 5000); // 5 seconds recording

            } catch (err) {
                console.error(err);
                alert("Error accessing microphone.");
            }
        });
    }

    // =========================
    // COMPANION BUTTON
    // =========================
    if (companionBtn) {
        companionBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/ai_module/companion/', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    }
                });
                const data = await response.json();
                alert(data.status);
            } catch (err) {
                console.error(err);
                alert("Error activating companion.");
            }
        });
    }

    // =========================
    // CSRF TOKEN HELPER
    // =========================
    function getCSRFToken() {
        let cookieValue = null;
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
