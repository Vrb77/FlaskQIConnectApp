// Include the intl-tel-input library
<script src="https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/intlTelInput.min.js"></script>

// Initialize the plugin
const phoneInput = document.querySelector('#phone');
const iti = window.intlTelInput(phoneInput, {
  // Options
  utilsScript: 'https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js',
  autoFormat: true,
  autoHideDialCode: true,
  nationalMode: false,
  preferredCountries: ['in'], // Set India as the preferred country
  separateDialCode: true,
});

// Add an event listener to update the phone number value on change
phoneInput.addEventListener('change', () => {
  const phoneNumber = phoneInput.value;
  // Update the phone number value in your Flask route
  // You can use AJAX or form submission to send the updated value to your Flask route
});