document.addEventListener('DOMContentLoaded', function() {
    // Back button functionality
    document.getElementById('backButton').addEventListener('click', function() {
        window.history.back();
    });

    // Sample history data (replace with your actual data)
    const historyData = [
        {
            id: 1,
            title: "Project Initialization",
            description: "Started the project with basic setup and configuration files.",
            image: "images/history1.jpg",
            timestamp: "2023-05-15 09:30:45"
        },
        {
            id: 2,
            title: "Core Features Implementation",
            description: "Implemented the main functionality of the application including user authentication.",
            image: "images/history2.jpg",
            timestamp: "2023-05-20 14:15:22"
        },
        {
            id: 3,
            title: "UI Redesign",
            description: "Updated the user interface with a modern design and improved accessibility.",
            image: "images/history3.jpg",
            timestamp: "2023-05-25 11:45:10"
        },
        {
            id: 4,
            title: "Performance Optimization",
            description: "Improved application performance by reducing load times and optimizing database queries.",
            image: "images/history1.jpg",
            timestamp: "2023-05-28 16:20:33"
        },
        {
            id: 5,
            title: "Bug Fixes",
            description: "Fixed several critical bugs reported by users during testing phase.",
            image: "images/history2.jpg",
            timestamp: "2023-06-02 10:05:18"
        },
        {
            id: 6,
            title: "Version 1.0 Release",
            description: "Launched the first stable version of the application to production.",
            image: "images/history3.jpg",
            timestamp: "2023-06-10 13:00:00"
        }
    ];

    // Function to render history cards
    function renderHistoryCards(data) {
        const cardsContainer = document.querySelector('.history-cards');
        cardsContainer.innerHTML = '';

        data.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-card';
            card.innerHTML = `
                <img src="${item.image}" alt="${item.title}" class="card-image">
                <div class="card-content">
                    <h3 class="card-title">${item.title}</h3>
                    <p class="card-description">${item.description}</p>
                    <div class="card-timestamp">
                        <i class="far fa-clock"></i>
                        ${formatTimestamp(item.timestamp)}
                    </div>
                </div>
            `;
            cardsContainer.appendChild(card);
        });
    }

    // Function to format timestamp
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    // Initial render
    renderHistoryCards(historyData);

    // Search functionality
    document.getElementById('searchButton').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function performSearch() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        if (searchTerm.trim() === '') {
            renderHistoryCards(historyData);
            return;
        }

        const filteredData = historyData.filter(item => 
            item.title.toLowerCase().includes(searchTerm) || 
            item.description.toLowerCase().includes(searchTerm)
        );
        
        renderHistoryCards(filteredData);
    }
});