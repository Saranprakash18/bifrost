document.addEventListener('DOMContentLoaded', function() {
    // File upload functionality
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFile = document.getElementById('removeFile');
    const generateBtn = document.getElementById('generateBtn');
    
    // Click on dropzone to trigger file input
    dropzone.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });
    
    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropzone.classList.add('highlight');
    }
    
    function unhighlight() {
        dropzone.classList.remove('highlight');
    }
    
    dropzone.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        handleFile(file);
    });
    
    function handleFile(file) {
        // Check if file is an image
        if (!file.type.match('image.*')) {
            alert('Please upload an image file');
            return;
        }
        
        // Display file info
        const reader = new FileReader();
        reader.onload = function(e) {
            filePreview.src = e.target.result;
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            
            dropzone.style.display = 'none';
            fileInfo.style.display = 'flex';
            generateBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Remove file
    removeFile.addEventListener('click', function(e) {
        e.stopPropagation();
        fileInput.value = '';
        dropzone.style.display = 'block';
        fileInfo.style.display = 'none';
        generateBtn.disabled = true;
    });
    
    // Mobile menu toggle (for smaller screens)
    const mobileMenuBtn = document.createElement('button');
    mobileMenuBtn.className = 'mobile-menu-btn';
    mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    
    const sidebar = document.querySelector('.sidebar');
    if (window.innerWidth < 992) {
        sidebar.insertBefore(mobileMenuBtn, sidebar.firstChild);
        
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Responsive adjustments
    window.addEventListener('resize', function() {
        if (window.innerWidth < 992 && !document.querySelector('.mobile-menu-btn')) {
            sidebar.insertBefore(mobileMenuBtn, sidebar.firstChild);
        } else if (window.innerWidth >= 992 && document.querySelector('.mobile-menu-btn')) {
            sidebar.removeChild(mobileMenuBtn);
            sidebar.classList.remove('active');
        }
    });
    
    // Logout button
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // In a real app, this would call your logout API
            window.location.href = 'index.html';
        });
    }
});