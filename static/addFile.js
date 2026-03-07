$('#audioFileClear').on('click', function() { 
    $('#audioBlob').val(''); 
    document.getElementById('playAudio').style.display='none';
});

microphoneBtn=document.getElementById("microphoneBtn")
microphoneBtn.addEventListener('click', (ev)=>{
SetupAudio();
})

// Code for addPics starts
const AddPics = document.getElementById("AddPics");
const imageContainer = document.getElementById("wrapper");
const dispPrevPics = document.getElementById("dispPrevPics");
var updateSelectedFiles = [];

if (LenPics.value == '') {
    LenPics.value = 0;
}
else {
    var picsFileNames = new Set();
    var prevFiles = document.getElementById("prevFiles");
    var prevPicsArr = prevFiles.value.split(",");
    prevPicsArr.forEach((val) => {
        picsFileNames.add(val);
    })
    if (LenPics.value != 0) {
        dispPrevPicsFunction();
    }
}
function dispPrevPicsFunction() {
    prevPicsArr.forEach((value) => {
        let listItem = document.createElement("li");
        listItem.innerHTML = value;
        let anchorEle = document.createElement("a");
        let val = "/view_file_customer?fname=" + value;
        anchorEle.setAttribute("href", val);
        anchorEle.setAttribute("title", "View file");
        let viewEle = document.createElement("i");
        viewEle.setAttribute("class", "fa-solid fa-eye");
        anchorEle.appendChild(viewEle);
        listItem.appendChild(anchorEle);

        let delBtn = document.createElement("button");
        delBtn.setAttribute("type", "button");
        delBtn.setAttribute("value", value);
        let funVal = "delBtn('" + value + "')";
        delBtn.setAttribute("onclick", funVal);
        delBtn.innerHTML = "Delete";
        listItem.appendChild(delBtn);
        dispPrevPics.appendChild(listItem);
    });
}

function delBtn(item) {
    const filteredArray = prevPicsArr.filter((value) => value !== item);
    LenPics.value = LenPics.value - 1;
    picsFileNames.delete(item);
    console.log("after delete pic", picsFileNames);
    if (Number(LenPics.value) == 0) {
        dispPrevPics.innerHTML = "";
    }
    filteredArray.forEach((value) => {
        prevPicsArr = filteredArray;
        prevFiles.setAttribute("value", prevPicsArr);
        let dispPrevPics = document.getElementById("dispPrevPics");
        dispPrevPics.innerHTML = "";
        dispPrevPicsFunction()
    });
    prevPicsArr = filteredArray;
    console.log("filter Array", filteredArray);
    prevFiles.setAttribute("value", prevPicsArr);
}

AddPics.addEventListener('change', (event) => {
    var selectedFiles = AddPics.files;
    updateSelectedFiles = mergeFiles(updateSelectedFiles, selectedFiles);
    if (!validateFiles(updateSelectedFiles)) {
        updateSelectedFiles = removeMergeFiles(updateSelectedFiles, selectedFiles);
    }
    AddPics.files = updateSelectedFiles;
    let dispFiles = updateSelectedFiles;
    imageContainer.innerHTML = '';
    displayFiles(dispFiles);
});

function validateFiles(validate_files) {
    if (((validate_files.length) + Number(LenPics.value)) > 5) {
        alert("You can only add 5 files");
        return false;
    }
    console.log(picsFileNames);
    for (let i = 0; i < validate_files.length; i++) {
        const file = validate_files[i];
        const fileSize = file.size / 1000000; // Convert bytes to kilobytes

        if (!file.type.startsWith('image/')) {
            alert("Only image files are allowed.");
            return false;
        }

        if (fileSize > 2) {
            alert("File size should be less than 2KB.");
            return false;
        }
    }
    for (let i = 0; i < validate_files.length; i++) {
        let fileName = validate_files.item(i).name;
        if (picsFileNames == undefined) {
            console.log("nothing");
            return true;
        }
        else if (picsFileNames.has(fileName)) {
            alert("same file exist- " + fileName);
            return false;
        }
    }
    
    return true;
}


function displayFiles(dispFiles) {
    for (let i = 0; i < dispFiles.length; i++) {
        const file = dispFiles[i];
        let fileReader = new FileReader();
        let box = document.createElement("div");
        box.classList.add("box2", "box1", "w3-col", "m4", "l4", "s6", "w3-round-xlarge");

        const fileName = document.createElement('span');
        fileName.classList.add('file-name');
        fileName.textContent = file.name;
        box.appendChild(fileName);

        fileReader.onload = function (event) {
            let dataUrl = event.target.result;
            let img = document.createElement("img");
            img.setAttribute("src", dataUrl);
            box.insertBefore(img, fileName);
        }

        imageContainer.appendChild(box);
        fileReader.readAsDataURL(dispFiles[i]);

        const deleteButton = document.createElement('button');
        deleteButton.classList.add('btn-delete');
        deleteButton.textContent = 'Delete';
        box.appendChild(deleteButton);
        deleteButton.addEventListener('click', () => {
            box.remove();
            updateSelectedFiles = removeFile(dispFiles, file.name)
            dispFiles = updateSelectedFiles;
            AddPics.files = dispFiles;

        })
    }
}

//code for additional files
const additionalFiles = document.getElementById("additionalFiles");
const fileContainer = document.getElementById("filewrapper");
const dispAddPrevFiles = document.getElementById("dispAddPrevFiles");
var LenAddFiles = document.getElementById("LenAddFiles");

var updateSelectedAdditionalFiles = [];

if (LenAddFiles.value == '') {
    LenAddFiles.value = 0;
}
else {
    var addFileNames = new Set();
    var addPrevFiles = document.getElementById("addPrevFiles");
    var prevFilesArr = addPrevFiles.value.split(",");
    prevFilesArr.forEach((val) => {
        addFileNames.add(val);
    })
    if (LenAddFiles.value != 0) {
        dispPrevFilesFunction();
    }
}

function dispPrevFilesFunction() {
    prevFilesArr.forEach((value) => {
        let listItem = document.createElement("li");
        listItem.innerHTML = value;
        let anchorEle = document.createElement("a");
        let val = "/view_file_customer?fname=" + value;
        anchorEle.setAttribute("href", val);
        anchorEle.setAttribute("title", "View file");
        let viewEle = document.createElement("i");
        viewEle.setAttribute("class", "fa-solid fa-eye");
        anchorEle.appendChild(viewEle);
        listItem.appendChild(anchorEle);

        let DelBtn = document.createElement("button");
        DelBtn.setAttribute("type", "button");
        DelBtn.setAttribute("value", value);
        let funVal = "DelBtn('" + value + "')";
        DelBtn.setAttribute("onclick", funVal);
        DelBtn.innerHTML = "Delete";
        listItem.appendChild(DelBtn);
        dispAddPrevFiles.appendChild(listItem);
    });
}

function DelBtn(item) {
    const filteredArray = prevFilesArr.filter((value) => value !== item);
    LenAddFiles.value = LenAddFiles.value - 1;
    addFileNames.delete(item);
    console.log("after delete pic", addFileNames);
    if (Number(LenAddFiles.value) == 0) {
        dispAddPrevFiles.innerHTML = "";
    }
    filteredArray.forEach((value) => {
        prevFilesArr = filteredArray;
        addPrevFiles.setAttribute("value", prevFilesArr);
        let dispAddPrevFiles = document.getElementById("dispAddPrevFiles");
        dispAddPrevFiles.innerHTML = "";
        dispPrevFilesFunction()
    });
    prevFilesArr = filteredArray;
    console.log("filter Array", filteredArray);
    addPrevFiles.setAttribute("value", prevFilesArr);
}
additionalFiles.addEventListener('change', (event) => {
    var selectedAdditionalFiles = additionalFiles.files;
    updateSelectedAdditionalFiles = mergeFiles(updateSelectedAdditionalFiles, selectedAdditionalFiles);
    if (!validateAdditionalFiles(updateSelectedAdditionalFiles)) {
        updateSelectedAdditionalFiles = removeMergeFiles(updateSelectedAdditionalFiles, selectedAdditionalFiles);
    }
    additionalFiles.files = updateSelectedAdditionalFiles;
    let dispAdditionalFiles = updateSelectedAdditionalFiles;
    fileContainer.innerHTML = '';
    displayAdditionalFiles(dispAdditionalFiles);
});


function validateAdditionalFiles(validate_files) {
    if (validate_files.length > 5) {
        alert("You can only add 5 files");
        return false;
    }
    for (let i = 0; i < validate_files.length; i++) {
        const file = validate_files[i];
        const fileSize = file.size / 1024; // Convert bytes to kilobytes

        // List of accepted MIME types for PDF, DOC, and PPT
        const acceptedTypes = ['application/pdf', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'];

        if (!acceptedTypes.includes(file.type)) {
            alert("Only pdf, word, powerpoint files are allowed.");
            return false;
        }

        if (fileSize > 200) {
            alert("File size should be less than 200KB.");
            return false;
        }
    }
    return true;
}


function displayAdditionalFiles(dispAdditionalFiles) {
    for (let i = 0; i < dispAdditionalFiles.length; i++) {
        const file = dispAdditionalFiles[i];
        let filetype = file.name.split(".").pop();
        let fileName = file.name;

        const showfileboxElem = document.createElement("div");
        showfileboxElem.classList.add("showfilebox");
        const leftElem = document.createElement("div");
        leftElem.classList.add("left");

        const fileTypeElem = document.createElement("span");
        fileTypeElem.classList.add("filetype");
        fileTypeElem.innerHTML = filetype;
        leftElem.append(fileTypeElem);

        const filetitleElem = document.createElement("h3");
        filetitleElem.innerHTML = fileName;
        leftElem.append(filetitleElem);
        showfileboxElem.append(leftElem);

        const rightElem = document.createElement("div");
        rightElem.classList.add("right");
        showfileboxElem.append(rightElem);

        const crossElem = document.createElement("span")
        crossElem.innerHTML = "&#215;";
        rightElem.append(crossElem);
        fileContainer.append(showfileboxElem);

        crossElem.addEventListener('click', () => {
            filewrapper.removeChild(showfileboxElem)
            updateSelectedAdditionalFiles = removeFile(dispAdditionalFiles, file.name)
            dispAdditionalFiles = updateSelectedAdditionalFiles;
            additionalFiles.files = dispAdditionalFiles;

        })
    }
}

//common Code
function removeMergeFiles(updateSelectedFiles, selectedFiles) {
    const mergeArray1 = Array.from(updateSelectedFiles);
    const mergeArray2 = Array.from(selectedFiles);
    let result = [];
    mergeArray1.forEach(item => { if (!mergeArray2.includes(item)) { result.push(item); } });

    const removeMergeArray = new DataTransfer();
    result.forEach(file => removeMergeArray.items.add(file));
    result = removeMergeArray.files;
    return result;
}

function mergeFiles(updateSelectedFiles, selectedFiles) {
    const mergeArray1 = Array.from(updateSelectedFiles);
    const mergeArray2 = Array.from(selectedFiles);
    const mergeArray = mergeArray1.concat(mergeArray2);
    const mergeArrayFiles = new DataTransfer();
    mergeArray.forEach(file => mergeArrayFiles.items.add(file));
    const result = mergeArrayFiles.files;
    return result;
}

function removeFile(dispFiles, fileNameToRemove) {
    const filesArray = Array.from(dispFiles);
    const filteredArray = filesArray.filter(file => file.name !== fileNameToRemove);
    const dataTransfer = new DataTransfer();
    filteredArray.forEach(file => { dataTransfer.items.add(file); });
    const updatedFileList = dataTransfer.files;
    return updatedFileList;
}



