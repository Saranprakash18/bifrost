document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });

    // Copy buttons functionality
    document.getElementById('copy-html').addEventListener('click', () => {
        copyToClipboard(document.querySelector('#html code').textContent);
    });

    document.getElementById('copy-css').addEventListener('click', () => {
        copyToClipboard(document.querySelector('#css code').textContent);
    });

    document.getElementById('copy-js').addEventListener('click', () => {
        copyToClipboard(document.querySelector('#js code').textContent);
    });

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Code copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showNotification('Failed to copy code', true);
        });
    }

    function showNotification(message, isError = false) {
        const notification = document.createElement('div');
        notification.className = `notification ${isError ? 'error' : 'success'}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
});