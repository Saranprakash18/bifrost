document.addEventListener('DOMContentLoaded', function () {
    // Login Form Validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            const email = document.getElementById('email')?.value.trim();
            const password = document.getElementById('password')?.value.trim();

            if (!email || !password) {
                e.preventDefault(); // Only prevent if invalid
                alert('Kindly fill all the fields.');
            }
        });
    }

    // Signup Form Validation
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function (e) {
            const fullname = document.getElementById('fullname')?.value.trim();
            const email = document.getElementById('email')?.value.trim();
            const password = document.getElementById('password')?.value;
            const confirmPassword = document.getElementById('confirmPassword')?.value;
            const terms = document.getElementById('terms')?.checked;

            // Validation
            if (!fullname || !email || !password || !confirmPassword) {
                e.preventDefault();
                alert('Kindly fill all the fields.');
                return;
            }

            if (password !== confirmPassword) {
                e.preventDefault();
                alert("Password didn't match.");
                return;
            }

            if (password.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters long.');
                return;
            }

            if (!terms) {
                e.preventDefault();
                alert('You must agree to the terms and conditions.');
                return;
            }
        });
    }

    // Password Strength Checker (Optional enhancement)
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            // You can add strength indicator here
        });
    }

    // Social Login (Simulated placeholder)
    document.querySelectorAll('.social-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const provider = this.classList.contains('google') ? 'Google' :
                this.classList.contains('github') ? 'GitHub' : 'Twitter';
            alert(`In a full implementation, this would authenticate with ${provider}`);
        });
    });
});
