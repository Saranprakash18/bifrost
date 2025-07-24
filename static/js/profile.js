document.addEventListener('DOMContentLoaded', function() {
    const editBtn = document.getElementById('edit-btn');
    const saveBtn = document.getElementById('save-btn');
    const form = document.getElementById('profile-form');
    const inputs = form.querySelectorAll('input');
    const showPasswordBtn = document.getElementById('show-password');
    const passwordInput = document.getElementById('password');
    const imageUpload = document.getElementById('image-upload');
    const imageInput = document.getElementById('image-input');
    const profileImage = document.getElementById('profile-image');

    // Toggle edit mode
    editBtn.addEventListener('click', function() {
        inputs.forEach(input => {
            input.disabled = false;
            if(input.id === 'password') {
                input.value = ''; // Clear the password placeholder when editing
            }
        });
        editBtn.style.display = 'none';
        saveBtn.style.display = 'inline-flex';
    });

    // Save changes
    saveBtn.addEventListener('click', function() {
        // Here you would typically send the data to your backend
        // For now, we'll just simulate a save
        alert('Profile updated successfully!');
        inputs.forEach(input => {
            input.disabled = true;
            if(input.id === 'password' && input.value === '') {
                input.value = '********'; // Reset password placeholder
            }
        });
        saveBtn.style.display = 'none';
        editBtn.style.display = 'inline-flex';
    });

    // Toggle password visibility
    showPasswordBtn.addEventListener('click', function() {
        if(passwordInput.type === 'password') {
            passwordInput.type = 'text';
            showPasswordBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordInput.type = 'password';
            showPasswordBtn.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });

    // Handle image upload
    imageUpload.addEventListener('click', function() {
        imageInput.click();
    });

    imageInput.addEventListener('change', function(e) {
        if(e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function(event) {
                profileImage.src = event.target.result;
                // Here you would typically upload the image to your backend
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    });
});