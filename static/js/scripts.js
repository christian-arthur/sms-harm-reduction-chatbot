document.addEventListener("DOMContentLoaded", () => {
    const maintenanceMode = false; // Toggle this variable to true or false

    const banner = document.getElementById("banner");

    if (maintenanceMode) {
        banner.style.display = "flex"; // Show the banner
    } else {
        banner.style.display = "none"; // Hide the banner
    }

    // Event listener to hide the banner when clicking outside of it
    document.addEventListener("click", (event) => {
        // Check if the banner is visible and the clicked target is not within the banner
        if (banner.style.display === "flex" && !banner.contains(event.target)) {
            banner.style.display = "none";
        }
    });
});
function confirmSendMessage() {
    return confirm("Are you sure you want to send this alert message?");
}
document.querySelector('#emergencyAlertForm').addEventListener('submit', function(event) {
    if (!confirmSendMessage()) {
        event.preventDefault(); // Prevent form submission if confirmSendMessage returns false
    }
});
