// Get all plan cards
const planCards = document.querySelectorAll('.plan-card');

// Function to handle card selection
function selectCard(selectedCard) {
    // Remove selected class from all plan cards
    planCards.forEach(card => {
        card.classList.remove('selected');
    });

    // Add selected class to the clicked card
    selectedCard.classList.add('selected');
}

// Add click event listener to each plan card
planCards.forEach(card => {
    card.addEventListener('click', function() {
        selectCard(card);
    });
});

function goto_payment() {
    // Get the selected plan details
    const selectedPlan = document.querySelector('.plan-card.selected');
    if (selectedPlan) {
        const planName = selectedPlan.dataset.plan;
        const planPrice = selectedPlan.dataset.price;

        // Redirect to the payment picker page with the selected plan details
        window.location.href = '/Common/payment';
    } else {
        alert('Please select a plan before proceeding to the next page.');
    }
}