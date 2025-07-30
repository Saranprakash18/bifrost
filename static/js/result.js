// result.js - Complete standalone version
document.addEventListener('DOMContentLoaded', function() {
    // 1. Tab System
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active classes
            document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            // Re-highlight code if not preview tab
            if (tabId !== 'preview' && window.hljs) {
                hljs.highlightAll();
            }
        });
    });

    // 2. Copy Buttons
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');
            const codeElement = document.querySelector(`#${target} code`);
            if (codeElement) {
                copyToClipboard(codeElement.textContent, `${target.toUpperCase()} copied!`);
            }
        });
    });

    // 3. Image Zoom Controls
    const previewImage = document.getElementById('design-preview');
    let zoomLevel = 1;
    const ZOOM_STEP = 0.1;
    
    if (previewImage) {
        document.getElementById('zoom-in')?.addEventListener('click', () => {
            zoomLevel = Math.min(zoomLevel + ZOOM_STEP, 3);
            previewImage.style.transform = `scale(${zoomLevel})`;
        });
        
        document.getElementById('zoom-out')?.addEventListener('click', () => {
            zoomLevel = Math.max(zoomLevel - ZOOM_STEP, 0.5);
            previewImage.style.transform = `scale(${zoomLevel})`;
        });
        
        document.getElementById('fullscreen')?.addEventListener('click', () => {
            if (previewImage.requestFullscreen) {
                previewImage.requestFullscreen();
            } else if (previewImage.webkitRequestFullscreen) {
                previewImage.webkitRequestFullscreen();
            }
        });
    }

    // 4. Word Wrap Toggle
    const toggleWrap = document.getElementById('toggle-wrap');
    const codeBlocks = document.querySelectorAll('.code-content pre code');
    
    if (toggleWrap && codeBlocks.length) {
        toggleWrap.addEventListener('click', () => {
            codeBlocks.forEach(code => {
                code.classList.toggle('wrap');
            });
            showNotification(
                codeBlocks[0].classList.contains('wrap') 
                    ? 'Word wrap enabled' 
                    : 'Word wrap disabled'
            );
        });
    }

    // 5. Download All (with JSZip fallback)
    const downloadAll = document.getElementById('download-all');
    if (downloadAll) {
        downloadAll.addEventListener('click', async () => {
            try {
                await loadJSZip();
                
                const html = document.querySelector('#html code')?.textContent || '';
                const css = document.querySelector('#css code')?.textContent || '';
                const js = document.querySelector('#js code')?.textContent || '';
                
                const zip = new JSZip();
                zip.file("index.html", html);
                zip.file("styles.css", css);
                zip.file("script.js", js);
                
                const content = await zip.generateAsync({type:"blob"});
                saveAs(content, "bifrost-export.zip");
                showNotification('All files downloaded as ZIP', 'success');
            } catch (error) {
                console.error('Download failed:', error);
                showNotification('Download failed. Please try again.', 'error');
            }
        });
    }

    // Helper Functions
    function copyToClipboard(text, successMessage) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification(successMessage || 'Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
            showNotification('Failed to copy to clipboard', 'error');
        });
    }

    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    function loadJSZip() {
        return new Promise((resolve, reject) => {
            if (window.JSZip) return resolve();
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
});