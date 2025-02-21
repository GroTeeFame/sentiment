const downloadBtn = document.getElementById('download-btn');
downloadBtn.addEventListener('click', function(event){
    window.location.href = '/download';
    setTimeout(() => {
        window.location.reload();
    }, 3000);
})


//Remove all flash on click
function removeAllFlash() {
    const element = document.getElementById('flash-container');
    element.remove();
    window.location.href = '/';
    window.location.reload();
}





// ai help
// Function to display flash messages
function displayFlashMessages(messages) {
    const flashContainer = document.getElementById('flash-container');
    const flashWrapper = document.getElementById('flash-wrapper');
    // flashContainer.innerHTML = ''; // Clear existing messages
    flashWrapper.innerHTML = ''; // Clear existing messages
    flashContainer.style.display = 'block';

    messages.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('warning');
        messageDiv.innerText = message;
        flashWrapper.appendChild(messageDiv);
    });
}
