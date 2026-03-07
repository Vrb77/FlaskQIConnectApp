/* sub menu of customer link starts */
window.onload = function() {
  var link1 = document.getElementById("myLink1");
  var link = document.getElementById("myLink");
  var link2 = document.getElementById("myLink2");
  if (window.location.pathname== "/request_form"  || window.location.pathname== "/register_product_form" || window.location.pathname== "/customer_home" || window.location.pathname== "/vendor_home" ) {
    link1.classList.add("active");   
  }
  if (window.location.pathname== "/my_requests" || window.location.pathname== "/my_products") {
    link.classList.add("active");   
  }
  if (window.location.pathname== "/customer_orders" || window.location.pathname== "/vendor_projects" ) {
    link2.classList.add("active");   
  }

  var prolink = document.getElementById("proLink");
  var prolink1 = document.getElementById("proLink1");
  var prolink2 = document.getElementById("proLink2");
  var prolink3 = document.getElementById("proLink3");
  if (window.location.pathname== "/Common/profilesettings") {
    prolink.classList.add("active");   
  }
  if (window.location.pathname== "/Common/securitysettings") {
    prolink1.classList.add("active");   
  }
  if (window.location.pathname== "/Common/subscriptionsettings") {
    prolink2.classList.add("active");   
  }
  if (window.location.pathname== "/transaction-history") {
    prolink3.classList.add("active");   
  }

  var navbar = document.getElementById("navbar");
  var card = document.getElementById("card");
  var footer = document.getElementById("footer"); 

  if (window.location.href.indexOf("http://localhost:5001/customer_home") !== -1 ) {
      var changeColor=document.getElementById("color-change-customer").value
      sessionStorage.setItem('changeColorCustomer',changeColor)
      sessionStorage.removeItem('changeColorVendor')
   }
   if (window.location.href.indexOf("http://localhost:5001/vendor_home") !== -1 ) {
     var changeColor=document.getElementById("color-change-vendor").value
      sessionStorage.setItem('changeColorVendor',changeColor)
      sessionStorage.removeItem('changeColorCustomer')
   }
  if(sessionStorage.getItem('changeColorCustomer')=="customer"){
  if (navbar.className.indexOf("w3-light-grey")!==-1 && footer.className.indexOf("w3-light-grey")!==-1 && card.className.indexOf("w3-light-grey")!==-1) {
    navbar.className = navbar.className.replace("w3-light-grey", "w3-pale-yellow");
    card.className = card.className.replace("w3-light-grey", "w3-pale-yellow");
    footer.className = footer.className.replace("w3-light-grey", "w3-pale-yellow");
  }
}
  if(sessionStorage.getItem('changeColorVendor')=="vendor"){
    if (navbar.className.indexOf("w3-light-grey")!==-1 && footer.className.indexOf("w3-light-grey")!==-1 && card.className.indexOf("w3-light-grey")!==-1) {
    
    navbar.className = navbar.className.replace("w3-light-grey", "w3-pale-blue");
    card.className = card.className.replace("w3-light-grey", "w3-pale-blue");
    footer.className = footer.className.replace("w3-light-grey", "w3-pale-blue");
   
  }
  }
/* for advertisement */
var adProductLink1 = document.getElementById("adProductLink1");
var adProductLink = document.getElementById("adProductLink");
if (window.location.pathname== "/adRegisterProduct") {
  adProductLink1.classList.add("active");   
}
if (window.location.pathname== "/addedADProduct") {
  adProductLink.classList.add("active");   
}
};
/* sub menu link of customer ends */

// Function to calculate word count and enforce word limit
function calculateWord(inputElement, wordLimit) {
  var words = 0;

  // Get the current value of the input element
  var inputValue = inputElement.value;

  if ((inputValue.match(/\S+/g)) != null) {
      words = inputValue.match(/\S+/g).length;
  }

  if (words > wordLimit) {
      // Split the string on the first 'wordLimit' words and rejoin on spaces
      var trimmed = inputValue.split(/\s+/, wordLimit).join(" ");
      // Add a space at the end to make sure more typing creates new words
      inputElement.value = trimmed + " ";
  } else {
      var displayCountId = 'display_count' + inputElement.id.replace('word_count', '');
      document.getElementById(displayCountId).textContent = words;
  }
}

// Add event listeners to the textareas
document.querySelectorAll("input.wordCountInput").forEach(input => {
  input.addEventListener('keyup', function() {
      var wordLimit = this.getAttribute('data-limit-count');
      calculateWord(this, wordLimit);
  });
});


/* Previous dates disabled */
var dtToday = new Date();   
    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();   
    var minDate= year + '-' + month + '-' + day;   
    $('.datepicker').attr('min', minDate);
/* Previous date disabled */

function navItem() {
    var x = document.getElementById("navItem");
    if (x.className.indexOf("w3-show") == -1) {
      x.className += " w3-show";
      document.getElementById('barsIcon').innerHTML='&#9587;';
    } else { 
      x.className = x.className.replace(" w3-show", "");
      document.getElementById('barsIcon').innerHTML='&#9776;';
    }
  }

  /* Search function starts */
  function searchFunction() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchInput");
    filter = input.value.toLowerCase();
    table = document.getElementById("searchTable");
    console.log(table);
    trs = table.tBodies[0].getElementsByTagName("tr");
    
    for (i = 0; i < trs.length; i++) {     
// define the row's cells
var tds = trs[i].getElementsByTagName("td");
// hide the row
trs[i].style.display = "none";
// loop through row cells
for (var cellI = 0; cellI < tds.length; cellI++) {
  // if there's a match
  if (tds[cellI].innerHTML.toLowerCase().indexOf(filter) > -1) {
    // show the row
    trs[i].style.display = "";
    // skip to the next row
    continue; 
    }
  }
}
  }
   /* Search function ends */
   if (window.location.pathname== "/request_form"  || window.location.pathname== "/register_product_form" || window.location.pathname== "/customer_home" || window.location.pathname== "/vendor_home" ) 
{  
document.addEventListener("click",()=>{
  const activeStepElement = document.querySelector('.stepInForm.active .stepNumber');
  // Get the inner text of the selected element
const stepNumberText = activeStepElement.innerText || activeStepElement.textContent;
// document.getElementById("stepNumberID").innerHTML=stepNumberText;
document.getElementById("stepNumberID").innerHTML=stepNumberText
const stepID=document.getElementById("stepNumberID").innerHTML
console.log("step number text",stepID)
})
   
}

 