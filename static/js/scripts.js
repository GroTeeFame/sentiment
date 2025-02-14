const downloadBtn = document.getElementById('download-btn');
downloadBtn.addEventListener('click', function(event){
    window.location.href = '/download';
    setTimeout(() => {
        window.location.reload();
    }, 3000);
})