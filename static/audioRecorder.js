const mic_btn = document.querySelector("#mic");
const playback = document.querySelector(".playback");
const playbackPreview = document.querySelector(".playbackPreview");
mic_btn.addEventListener('click', ToggleMic);

let can_record = false;
let is_recording = false;

let recorder = null;

let chunks = [];

function SetupAudio() {
  console.log("setup");
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(SetupStream)
      .catch(err => { console.error(err) });
  }
}

function SetupStream(stream) {
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = e => {
      chunks.push(e.data);
    }
    recorder.onstop = e => {
      // Step 1: Create a Blob object
      const blob = new Blob(chunks, { type: "audio/mpeg; codecs=mp3" });
      chunks = [];
      console.log("onstop",blob);
      console.log("type od blob object",typeof(blob));
  
       // Step 2: Create a File object from the Blob
       const formattedDate = new Date().toISOString().replace(/[-T:.]/g, '_').slice(0, -5);
    let audio_file_name="audio"+"_"+formattedDate+".mp3";
       const file = new File([blob], audio_file_name, {  type: "audio/mpeg; codecs=mp3" });
  
       // Step 3: Create a DataTransfer object and add the file
       const dataTransfer = new DataTransfer();
       dataTransfer.items.add(file);
  
       // Step 4: Assign the DataTransfer files to the file input
       const fileInput = document.getElementById('audioBlob');
       fileInput.files = dataTransfer.files;
  
      console.log("audio file input",fileInput.files);
  
      // uploadRecording(blob);
      const audioURL = window.URL.createObjectURL(blob);
      playback.src = audioURL;
      playbackPreview.src = audioURL;
      let sendRecording=document.getElementById('sendRecording');
      sendRecording.removeAttribute('disabled');
    }
    can_record = true;
  }
  
  function ToggleMic() {
    if (!can_record) return;
    is_recording = !is_recording;
    if (is_recording) {
      recorder.start();
      mic_btn.classList.add("is-recording");
  
    }
    else {
      recorder.stop();
      mic_btn.classList.remove("is-recording");
    }
  }