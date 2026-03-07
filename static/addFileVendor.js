
// Code for addProductPics starts
const addProductPics = document.getElementById("addProductPics");
const imageContainer = document.getElementById("wrapper");
const dispPrevPics = document.getElementById("dispPrevPics");
var updateSelectedFiles = [];

if (LenPrPics.value == '') {
    LenPrPics.value = 0; 
    var picsFileNames = new Set();   
}
else {
    var picsFileNames = new Set();
    var prevFiles = document.getElementById("prevFiles");
    var prevPicsArr = prevFiles.value.split(",");
    prevPicsArr.forEach((val) => {
        picsFileNames.add(val);
    })
    if (LenPrPics.value != 0) {
        dispPrevPicsFunction();
    }
}
function dispPrevPicsFunction() {
    prevPicsArr.forEach((value) => {
        let radioBtn=document.createElement("input")
        setAttributes(radioBtn, 
            "type","radio",
            "name", "productImg",
            "id", value,
            "class", "Img-Input-hidden",
            "value",value,
        );

        let box = document.createElement("div");
        box.classList.add("box2", "box1", "w3-col", "m4", "l4", "s6", "w3-round-xlarge");
        box.appendChild(radioBtn)
        const fileName = document.createElement('span');
        fileName.classList.add('file-name');
        fileName.textContent = value;
        const br=document.createElement('br');
        box.appendChild(br);
        box.appendChild(fileName);
        box.insertBefore(fileName,br);
        let img = document.createElement("img");
        let imgSrc="/view_file_vendor?fname="+value;
        img.setAttribute("src", imgSrc);
        let labelImg=document.createElement("label")
        labelImg.setAttribute("for",value);

        labelImg.appendChild(img);

        box.insertBefore(labelImg, fileName);
        dispPrevPics.appendChild(box);

        let delBtn = document.createElement("button");
        delBtn.setAttribute("type", "button");
        delBtn.setAttribute("value", value);
        delBtn.setAttribute("class", "btn-delete");
        let funVal = "delBtn('" + value + "')";
        delBtn.setAttribute("onclick", funVal);
        delBtn.innerHTML = "Delete";
        box.appendChild(delBtn);

       
    });
}

function delBtn(item) {
    const filteredArray = prevPicsArr.filter((value) => value !== item);
    LenPrPics.value = LenPrPics.value - 1;
    picsFileNames.delete(item);
    console.log("after delete pic", picsFileNames);
    if (Number(LenPrPics.value) == 0) {
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

addProductPics.addEventListener('change', (event) => {
    var selectedFiles = addProductPics.files;
    console.log("selected files",selectedFiles);
    updateSelectedFiles = mergeFiles(updateSelectedFiles, selectedFiles);
    console.log("update selected files",updateSelectedFiles);   
  
    if (!validateFiles(updateSelectedFiles)) {
        updateSelectedFiles = removeMergeFiles(updateSelectedFiles, selectedFiles);     
        // Iterate over the FileList and add each filename to the Set
for (let i = 0; i < updateSelectedFiles.length; i++) {
    picsFileNames.add(updateSelectedFiles[i].name);
    console.log("picsFileNames",picsFileNames);
}  
    }
    addProductPics.files = updateSelectedFiles;
    let dispFiles = updateSelectedFiles;
    imageContainer.innerHTML = '';
    displayFiles(dispFiles);
});

function validateFiles(validate_files) {
    if (((validate_files.length) + Number(LenPrPics.value)) > 5) {
        alert("You can only add 5 files");
        return false;
    }

    for (let i = 0; i < validate_files.length; i++) {
        console.log("validate file size");
        const file = validate_files[i];
        const fileSize = file.size / 1024; // Convert bytes to kilobytes

        if (!file.type.startsWith('image/')) {
            alert("Only image files are allowed.");
            return false;
        }

        if (fileSize > 200) {
            alert("File size should be less than 200KB.");
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
function setAttributes(elem /* attribute, value pairs go here */) {
    for (var i = 1; i < arguments.length; i+=2) {
        elem.setAttribute(arguments[i], arguments[i+1]);
    }
}
function displayFiles(dispFiles) {
    for (let i = 0; i < dispFiles.length; i++) {
        const file = dispFiles[i];
        let fileReader = new FileReader();
        let radioBtn=document.createElement("input")
        setAttributes(radioBtn, 
            "type","radio",
            "name", "productImg",
            "id", file.name,
            "class", "Img-Input-hidden",
            "value",file.name,
        );

        let box = document.createElement("div");
        box.classList.add("box2", "box1", "w3-col", "m4", "l4", "s6", "w3-round-xlarge");
        box.appendChild(radioBtn)
        const fileName = document.createElement('span');
        fileName.classList.add('file-name');
        fileName.textContent = file.name;
        const br=document.createElement('br');
        box.appendChild(br);
        box.appendChild(fileName);
        box.insertBefore(fileName,br);

        fileReader.onload = function (event) {
            let dataUrl = event.target.result;
            let img = document.createElement("img");
            img.setAttribute("src", dataUrl);
            let labelImg=document.createElement("label")
            labelImg.setAttribute("for",file.name);

            labelImg.appendChild(img);

            box.insertBefore(labelImg, fileName);

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
            addProductPics.files = dispFiles;

        })
    }
}

// Code for addProductPics ends



// Code for additionalRelatedFiles starts
const additionalRelatedFiles = document.getElementById("additionalRelatedFiles");
const fileContainer = document.getElementById("filewrapper");
const dispAddPrevFiles = document.getElementById("dispAddPrevFiles");
var LenAddPrFiles = document.getElementById("LenAddPrFiles");

var updateSelectedAdditionalFiles = [];

if (LenAddPrFiles.value == '') {
    LenAddPrFiles.value = 0;
}
else {
    var addPrFileNames = new Set();
    var addPrevFiles = document.getElementById("addPrevFiles");
    var prevFilesArr = addPrevFiles.value.split(",");
    prevFilesArr.forEach((val) => {
        addPrFileNames.add(val);
    })
    if (LenAddPrFiles.value != 0) {
        dispPrevFilesFunction();
    }
}
function dispPrevFilesFunction() {
    prevFilesArr.forEach((value) => {
        let listItem = document.createElement("li");
        listItem.innerHTML = value;
        let anchorEle = document.createElement("a");
        let val = "/view_file_vendor?fname=" + value;
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
    LenAddPrFiles.value = LenAddPrFiles.value - 1;
    addPrFileNames.delete(item);
    console.log("after delete pic", addPrFileNames);
    if (Number(LenAddPrFiles.value) == 0) {
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


additionalRelatedFiles.addEventListener('change', (event) => {
    var selectedAdditionalFiles = additionalRelatedFiles.files;
    updateSelectedAdditionalFiles = mergeFiles(updateSelectedAdditionalFiles, selectedAdditionalFiles);
    if (!validateAdditionalFiles(updateSelectedAdditionalFiles)) {
        updateSelectedAdditionalFiles = removeMergeFiles(updateSelectedAdditionalFiles, selectedAdditionalFiles);
    }
    additionalRelatedFiles.files = updateSelectedAdditionalFiles;
    let dispAdditionalFiles = updateSelectedAdditionalFiles;
    fileContainer.innerHTML = '';
    displayAdditionalFiles(dispAdditionalFiles);
});


function validateAdditionalFiles(validate_files) {
    if (((validate_files.length) + Number(LenAddPrFiles.value)) > 5) {
        alert("You can only add 5 files");
        return false;
    }
    for (let i = 0; i < validate_files.length; i++) {
        let fileName = validate_files.item(i).name;
        if (addPrFileNames == undefined) {
            console.log("nothing");
            return true;
        }
        else if (addPrFileNames.has(fileName)) {
            alert("same file exist- " + fileName);
            return false;
        }
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
            additionalRelatedFiles.files = dispAdditionalFiles;

        })
    }
}

/* common code starts */

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
    console.log("result", result);

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

/*common code ends */

