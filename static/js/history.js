document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all history cards
    const cards = document.querySelectorAll('.history-card');
    
    cards.forEach(card => {
        card.addEventListener('click', function() {
            const uploadId = this.getAttribute('data-upload-id');
            if (uploadId) {
                window.location.href = `/result/${uploadId}/`;
            }
        });
    });
    
    // Optional: Preload images when card is hovered
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const img = this.querySelector('.card-image img');
            if (img && !img.loaded) {
                img.loaded = true;
                const src = img.getAttribute('src');
                if (src) {
                    const preload = new Image();
                    preload.src = src;
                }
            }
        }, { once: true });
    });
});