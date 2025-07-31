document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const filterLinks = document.querySelectorAll('.filter-list a');
    const templateCards = document.querySelectorAll('.template-card');
    const sortSelect = document.getElementById('sort-select');
    const quickPreviewBtns = document.querySelectorAll('.quick-preview-btn');
    const previewModal = document.querySelector('.preview-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const modalTemplateImage = document.getElementById('modalTemplateImage');
    const modalUseBtn = document.getElementById('modalUseBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    // Filter templates by category
    filterLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            filterLinks.forEach(item => item.parentNode.classList.remove('active'));
            this.parentNode.classList.add('active');
            
            const category = this.getAttribute('data-category');
            filterTemplates(category);
        });
    });
    
    // Filter function
    function filterTemplates(category) {
        showLoading();
        
        setTimeout(() => {
            templateCards.forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
            
            hideLoading();
        }, 500);
    }
    
    // Sort templates
    sortSelect.addEventListener('change', function() {
        showLoading();
        
        setTimeout(() => {
            const sortValue = this.value;
            const container = document.querySelector('.template-grid');
            const cards = Array.from(document.querySelectorAll('.template-card'));
            
            cards.sort((a, b) => {
                if (sortValue === 'name') {
                    return a.querySelector('.template-title').textContent.localeCompare(
                        b.querySelector('.template-title').textContent
                    );
                } else if (sortValue === 'recent') {
                    return parseInt(b.getAttribute('data-id')) - parseInt(a.getAttribute('data-id'));
                } else {
                    // Default sort by popularity (could be replaced with actual popularity data)
                    return Math.random() - 0.5;
                }
            });
            
            // Re-append sorted cards
            cards.forEach(card => container.appendChild(card));
            hideLoading();
        }, 500);
    });
    
    // Quick Preview functionality
    quickPreviewBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const templateId = this.getAttribute('data-template');
            const templateCard = document.querySelector(`.template-card[data-id="${templateId}"]`);
            const templateImage = templateCard.querySelector('.template-img').src;
            
            // Set modal content
            modalTemplateImage.src = templateImage;
            modalUseBtn.href = templateCard.querySelector('.use-btn').href;
            
            // Show modal
            previewModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    });
    
    // Close modal
    closeModalBtn.addEventListener('click', closeModal);
    previewModal.addEventListener('click', function(e) {
        if (e.target === previewModal) {
            closeModal();
        }
    });
    
    function closeModal() {
        previewModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
    
    // Loading spinner functions
    function showLoading() {
        loadingSpinner.classList.add('active');
    }
    
    function hideLoading() {
        loadingSpinner.classList.remove('active');
    }
    
    // Simulate template usage with loading
    document.querySelectorAll('.use-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            showLoading();
            
            // In a real app, you would handle the template usage here
            // For demo, we'll just proceed to the result page after a delay
            setTimeout(() => {
                hideLoading();
            }, 1000);
        });
    });
    
    // Initialize with all templates showing
    filterTemplates('all');
});