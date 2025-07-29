document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const editBtn = document.getElementById('edit-btn');
    const saveBtn = document.getElementById('save-btn');
    const profileForm = document.getElementById('profile-form');
    const inputs = profileForm.querySelectorAll('input');
    const imageUpload = document.getElementById('image-upload');
    const imageInput = document.getElementById('image-input');
    const profileImage = document.getElementById('profile-image');
    const showPasswordBtn = document.getElementById('show-password');
    const passwordInput = document.getElementById('password');

    // Edit Profile Functionality
    editBtn.addEventListener('click', function() {
        inputs.forEach(input => {
            input.disabled = false;
            if(input.id === 'password') {
                input.value = ''; // Clear the password placeholder when editing
            }
        });
        
        editBtn.style.display = 'none';
        saveBtn.style.display = 'flex';
    });

    // Image Upload Functionality
    imageUpload.addEventListener('click', function() {
        imageInput.click();
    });

    imageInput.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(event) {
                profileImage.src = event.target.result;
                // Here you would typically upload the image to your server
            };
            
            reader.readAsDataURL(e.target.files[0]);
        }
    });

    // Show Password Toggle
    showPasswordBtn.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            showPasswordBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordInput.type = 'password';
            showPasswordBtn.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });

    // Form Submission (would be handled by Django in production)
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // Here you would send the form data to your Django backend
        alert('Profile updated successfully!');
        
        // Disable inputs after saving
        inputs.forEach(input => input.disabled = true);
        editBtn.style.display = 'flex';
        saveBtn.style.display = 'none';
    });

    // Save button click triggers form submission
    saveBtn.addEventListener('click', function() {
        profileForm.dispatchEvent(new Event('submit'));
    });
});