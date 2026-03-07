  
  function loadAdv() {   
    console.log("adv")   
    var email=JSON.parse('{{ session["email"] | tojson | safe}}');
    console.log(email)
      var advertisement = JSON.parse('{{ advertisement | tojson | safe}}')[email];    
      advertisement.forEach((ad, index) => {
          var service_name=`service_name-${index + 1}`;
          var Url = "/getAdvertisementName?service_id="+ad; 
         
          console.log("adv",ad);
          fetch(Url, {
              method: "GET",
              headers: {
                  "Content-Type": "application/json"
              }
          })
          .then(response => response.text())
          .then(responseData => { 
            console.log("response data",responseData);
            document.getElementById(service_name).innerHTML = responseData;
          })
          .catch(error => {
              console.error("Error fetching data from API:", error);
          });
      }
    );
  };
  loadAdv();
