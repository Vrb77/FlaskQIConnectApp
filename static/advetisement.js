function selectAdDuration(){
    console.log("Inside select ad duration");
    let AdDuration=document.getElementById('AdDuration').value
    console.log(AdDuration)
    let AdPrice=document.getElementById('AdPrice')
    console.log(AdPrice)
    switch(AdDuration){
        case "30":
            AdPrice.value=100;
            break;
        case "60":
            AdPrice.value=200;
            break;
        case "90":
            AdPrice.value=300;
            break;
        default:
            alert('No duration selected');
    }
}

