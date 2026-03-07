$(document).ready(function () {
    var fileInput = document.getElementById("fileInput");
    fileInput.addEventListener("change", (e) => {
      console.log("in event listenr");
      let fileName = e.target.files[0].name;
      console.log(fileName);
      if (!validateFile(e.target.files[0])) {
        $("#fileName").html("No file Selected");
        $("#fileInput").val("");
      }
      else {
        $("#fileName").html(fileName);
      }

    })

    function validateFile(file) {
      const fileSize = file.size / 1024;
      const acceptedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'application/pdf', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'];

      if (!acceptedTypes.includes(file.type)) {
        alert("Only image file(Format- png,jpg,gif) and application file(pdf,msword,mspowepoint,doc,ppt) are allowed.");
        return false;
      }

      if (fileSize > 300) {
        alert("File size should be less than 2KB.");
        return false;
      }
      return true;
    }

   
    $("#postForm").submit(function (event) {
      event.preventDefault(); // Prevent default form submission
      var fileInput = document.getElementById("fileInput");
      var file = fileInput.files[0];

      var messageInput = document.getElementById("messageInput").value;

      let blobObj=document.getElementById('audioBlob');
      blobObj=blobObj.files[0];
      console.log("blobObj----",blobObj);   
      
      let blobVideoObj=document.getElementById('videoBlob');
      blobVideoObj=blobVideoObj.files[0];
      console.log("blobVideoObj----",blobVideoObj);
    
      var formData = new FormData(this);
      formData.append("message", messageInput);
      formData.append("messageFile", file);
      formData.append('AudioFile', blobObj);
      formData.append('VideoFile', blobVideoObj);


      if (!(messageInput == "" && file == undefined && blobObj == undefined && blobVideoObj == undefined)) 
      {
         // AJAX request
        $.ajax({
          type: "POST",
          url: "/displayMessages?service_id="+appConfig.service_id+"&request_id="+appConfig.request_id,
          data: formData,
          async: true,
          processData: false,
          contentType: false,
          dataType: 'json',
          success: function (response) {
            console.log("Response received:", response);
            var messages = response.msg; // Corrected variable name
            $("#message-container").empty();
            var MessagesContainerRender = [];
            for (var i = messages.length - 1; i >= 0; i--) {
              var message = messages[i];
              if (!message) {
                console.error("Message is undefined at index:", i);
                continue;
              }
              if (response.From == message["from"]) {
                var messageContent = '<div class="message sent ' + '">' + message["message"];
                if (message["file"] != '') {
                  messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' + message["file"] +
                    '<a href="/download_file?fname=' + message["file"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                    '<a href="/view_file?fname=' + message["file"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                    '</div>';
                }
                
                if (message["audioFile_name"] != '') {
                    messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' +message["audioFile_name"]+'<audio src="/view_file?fname='+message["audioFile_name"]+'" controls></audio>'   +
                      '<a href="/download_file?fname=' + message["audioFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                      '<a href="/view_file?fname=' + message["audioFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                      '</div>';
                  }
                  if (message["videoFile_name"] != '') {
                    messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' +message["videoFile_name"]+'<video src="/view_file?fname='+message["videoFile_name"]+'" width="320" height="240" controls></video>'   +
                      '<a href="/download_file?fname=' + message["videoFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                      '<a href="/view_file?fname=' + message["videoFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                      '</div>'  ;
                  }
                messageContent += '<div class="message-time">' + message["timestamp"] + '</div></div>' + '<br>';
                MessagesContainerRender.push(messageContent);
              }
              else {
                var messageContent = '<div class="message received' + '">' + message["message"];
                if (message["file"] != '') {
                  messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' + message["file"] +
                    '<a href="/download_file?fname=' + message["file"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                    '<a href="/view_file?fname=' + message["file"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                    '</div>';
                }
                if (message["audioFile_name"] != '') {
                    messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' +message["audioFile_name"]+'<audio src="/view_file?fname='+message["audioFile_name"]+'" controls></audio>'   +
                      '<a href="/download_file?fname=' + message["audioFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                      '<a href="/view_file?fname=' + message["audioFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                      '</div>' ;
                  }
                  if (message["videoFile_name"] != '') {
                    messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' +message["videoFile_name"]+'<video src="/view_file?fname='+message["videoFile_name"]+'" width="320" height="240" controls></video>'   +
                      '<a href="/download_file?fname=' + message["videoFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                      '<a href="/view_file?fname=' + message["videoFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                      '</div>'  ;
                  }
                messageContent += '<div class="message-time">' + message["timestamp"] + '</div></div>' + '<br>';
                MessagesContainerRender.push(messageContent);
              }

              $(".msgVendor").html(MessagesContainerRender);

            }
          },
          error: function (xhr, status, error) {
            console.error("Error:", error);
          }
        });
      }
      else {
        alert("Please enter a message or a file "); // Display an alert if the message is empty
      }
      // Clear input fields after sending message
      $("#messageInput").val("");
      $("#fileInput").val("");
      $("#audioBlob").val("");
      $("#fileName").html("No file Selected");
     
    });

    function refreshData() {
      $.ajax({
        type: "GET",
        url: "/displayMessages?service_id="+appConfig.service_id+"&request_id="+appConfig.request_id,
        async: true,
        processData: false,
        contentType: false,
        dataType: 'json',
        success: function (response) {
          console.log("Response received:", response);
          var messages = response.msg; // Corrected variable name
          $("#message-container").empty();
          var MessagesContainerRender = [];
          for (var i = messages.length - 1; i >= 0; i--) {
            var message = messages[i];
            if (!message) {
              console.error("Message is undefined at index:", i);
              continue;
            }
            if (response.From == message["from"]) {
              var messageContent = '<div class="message sent ' + '">' + message["message"];
              if (message["file"] != '') {
                messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' + message["file"] +
                  '<a href="/download_file?fname=' + message["file"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                  '<a href="/view_file?fname=' + message["file"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                  '</div>';
              }
              if (message["audioFile_name"] != '') {
                messageContent +='<div class="w3-border w3-round-large w3-padding w3-border-black">' + message["audioFile_name"]+'<audio src="/view_file?fname='+message["audioFile_name"]+'" controls></audio>'   +
                  '<a href="/download_file?fname=' + message["audioFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                  '<a href="/view_file?fname=' + message["audioFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                  '</div>';
              }
              if (message["videoFile_name"] != '') {
                messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' +message["videoFile_name"]+'<video src="/view_file?fname='+message["videoFile_name"]+'" width="320" height="240" controls></video>'   +
                  '<a href="/download_file?fname=' + message["videoFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                  '<a href="/view_file?fname=' + message["videoFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                  '</div>'  ;
              }
              messageContent += '<div class="message-time">' + message["timestamp"] + '</div></div>' + '<br>';
              MessagesContainerRender.push(messageContent);
            }
            else {
              var messageContent = '<div class="message received' + '">' + message["message"];
              if (message["file"] != '') {
                messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' + message["file"] +
                  '<a href="/download_file?fname=' + message["file"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                  '<a href="/view_file?fname=' + message["file"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                  '</div>';
              }
              if (message["audioFile_name"] != '') {
                messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' +message["audioFile_name"]+'<audio src="/view_file?fname='+message["audioFile_name"]+'" controls></audio>'   +
                  '<a href="/download_file?fname=' + message["audioFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                  '<a href="/view_file?fname=' + message["audioFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                  '</div>';
              }
              if (message["videoFile_name"] != '') {
                messageContent += '<div class="w3-border w3-round-large w3-padding w3-border-black">' +message["videoFile_name"]+'<video src="/view_file?fname='+message["videoFile_name"]+'" width="320" height="240" controls></video>'   +
                  '<a href="/download_file?fname=' + message["videoFile_name"] + '" title="Download file"><i class="fa-solid fa-download"></i></a>' +
                  '<a href="/view_file?fname=' + message["videoFile_name"] + '" title="View file"><i class="fa-solid fa-eye"></i></a>' +
                  '</div>'  ;
              }
              messageContent += '<div class="message-time">' + message["timestamp"] + '</div></div>' + '<br>';
              MessagesContainerRender.push(messageContent);
            }

            $(".msgVendor").html(MessagesContainerRender);

          }
        },
        error: function (xhr, status, error) {
          console.error("Error:", error);
        }
      });
    }

    // Initial data refresh
    refreshData();

    // Set interval to refresh data every 5 seconds (for example)
    var refreshInterval = setInterval(refreshData, 5000); // 5000 milliseconds = 5 seconds
    function submit() {
    $("#selectVendorForm").on("change", "input:radio", function () {
      $("#selectVendorForm").submit();
      $('.selectVendorBtn').html('vendor selected');
    });
  }
  });

 /* audio js starts */
 const mic_btn = document.querySelector("#mic");
 const playback = document.querySelector(".playback");

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

 microphoneBtn=document.getElementById("microphoneBtn")
 microphoneBtn.addEventListener('click', (ev)=>{
 SetupAudio();
 })

 function SetupStream(stream) {
   recorder = new MediaRecorder(stream);
   recorder.ondataavailable = e => {
     console.log("in recorder ONDATA AVAILABLE push data");
     chunks.push(e.data);
   }
   recorder.onstop = e => {
     // Step 1: Create a Blob object
     const blob = new Blob(chunks, { type: "audio/mpeg; codecs=mp3" });
     chunks = [];
     console.log("onstop",blob);
     console.log("type of blob object",typeof(blob));

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

 
  /* audio js ends */

 /* video js starts */
let constraintObj = { 
  audio: true, 
  video: { 
      facingMode: "user", 
      width: { min: 640 },
      height: { min: 480 } 
  } 
}; 

$("#reveseCamera").on("click",function(){
  console.log("reverse camera fun");
  if(constraintObj["video"]["facingMode"]="environment")
 { constraintObj["video"]["facingMode"]="user";}
  else
    { constraintObj["video"]["facingMode"]="environment";}

})
// width: 1280, height: 720  -- preference only
// facingMode: {exact: "user"}
// facingMode: "environment"

videoBtn=document.getElementById("videoBtn")
videoBtn.addEventListener('click', (ev)=>{
 //handle older browsers that might implement getUserMedia in some way
 if (navigator.mediaDevices === undefined) {
  navigator.mediaDevices = {};
  navigator.mediaDevices.getUserMedia = function(constraintObj) {
      let getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
      if (!getUserMedia) {
          return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
      }
      return new Promise(function(resolve, reject) {
          getUserMedia.call(navigator, constraintObj, resolve, reject);
      });
  }
}else{
  navigator.mediaDevices.enumerateDevices()
  .then(devices => {
      devices.forEach(device=>{
          console.log(device.kind.toUpperCase(), device.label);
          //, device.deviceId
      })
  })
  .catch(err=>{
      console.log(err.name, err.message);
  })
}



navigator.mediaDevices.getUserMedia(constraintObj)
.then(function(mediaStreamObj) {
  //connect the media stream to the first video element
  let video = document.querySelector('video');
  if ("srcObject" in video) {
      video.srcObject = mediaStreamObj;         
  } else {
      //old version
      video.src = window.URL.createObjectURL(mediaStreamObj);     
  } 
  video.onloadedmetadata = function(ev) {
      //show in the video element what is being captured by the webcam
      video.play();  
  };


  //add listeners for saving video/audio
  let start = document.getElementById('btnStart');
  let stop = document.getElementById('btnStop');
  let vidSave = document.getElementById('vid2');
  let cameraPreview=document.getElementById('cameraPreview');
  let camera=document.getElementById('camera');
  let mediaRecorder = new MediaRecorder(mediaStreamObj);
  let chunksvideo = [];

  start.addEventListener('click', (ev)=>{ 
      mediaRecorder.start();
      stop.removeAttribute("disabled");
      start.setAttribute("disabled","");
      camera.removeAttribute("hidden");
    cameraPreview.setAttribute("hidden","");
      console.log(mediaRecorder.state);  
  })


  stop.addEventListener('click', (ev)=>{
    mediaRecorder.ondataavailable = function(ev) {
      console.log("in mediarecorder ONDATA AVAILABLE push data");
        chunksvideo.push(ev.data);
        
    }
    mediaRecorder.stop();
    start.removeAttribute("disabled");
    stop.setAttribute("disabled","");
    cameraPreview.removeAttribute("hidden");
    camera.setAttribute("hidden","");
    mediaRecorder.onstop = e => {
      
      console.log(mediaRecorder.state);
       // Step 1: Create a Blob object
       const blob = new Blob(chunksvideo, { type: "video/mp4; codecs=mp4" });
       chunksvideo = [];
       console.log("onstop",blob);
       console.log("type of blob object",typeof(blob));
  
        // Step 2: Create a File object from the Blob
        const formattedDate = new Date().toISOString().replace(/[-T:.]/g, '_').slice(0, -5);
     let video_file_name="video"+"_"+formattedDate+".mp4";
        const file = new File([blob], video_file_name, {  type: "video/mp4; codecs=mp4" });
 
        // Step 3: Create a DataTransfer object and add the file
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
 
        // Step 4: Assign the DataTransfer files to the file input
        const fileInput = document.getElementById('videoBlob');
        fileInput.files = dataTransfer.files;
 
       console.log("video file input",fileInput.files);
 
       // uploadRecording(blob);
      
      let sendVideoRecording=document.getElementById('sendVideoRecording');
      sendVideoRecording.removeAttribute('disabled');
      let videoURL = window.URL.createObjectURL(blob);
      vidSave.src = videoURL;
    }
  });
  
  mediaRecorder.onstop = (ev)=>{
      let blob = new Blob(chunksvideo, { 'type' : 'video/mp4; codecs=mp4' });
      chunksvideo = [];
      let videoURL = window.URL.createObjectURL(blob);
      vidSave.src = videoURL;
  }
})
.catch(function(err) { 
  console.log(err.name, err.message); 
});

})
/*********************************
getUserMedia returns a Promise
resolve - returns a MediaStream Object
reject returns one of the following errors
AbortError - generic unknown cause
NotAllowedError (SecurityError) - user rejected permissions
NotFoundError - missing media track
NotReadableError - user permissions given but hardware/OS error
OverconstrainedError - constraint video settings preventing
TypeError - audio: false, video: false
*********************************/
/* video js ends */