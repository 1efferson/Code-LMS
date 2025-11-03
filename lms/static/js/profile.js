document.addEventListener('DOMContentLoaded', function() {
    const imgDisplay = document.getElementById('profile-image-display');
    const cycleBtn = document.getElementById('cycle-avatar-btn');
    const userNameSeed = imgDisplay.getAttribute('data-seed');
    
    // List of different DiceBear styles to cycle through
    const avatarStyles = [
        'fun-emoji', // Current cartoon style
        'pixel-art', // Simple pixelated style
        'adventurer', // Humanoid cartoon style
        'bottts' // Robot style
    ];
    
    // Key for local storage to persist the user's choice
    const storageKey = `user_avatar_style_${userNameSeed}`;

    // 1. Get current style index or default to 0
    let currentStyleIndex = 0;
    try {
        const storedStyle = localStorage.getItem(storageKey);
        if (storedStyle) {
            const index = avatarStyles.indexOf(storedStyle);
            if (index !== -1) {
                currentStyleIndex = index;
            }
        }
    } catch (e) {
        console.error("Local storage access failed:", e);
    }

    // Function to generate the correct DiceBear URL
    const getAvatarUrl = (style) => {
        // We use the full name as the seed, guaranteeing consistency for that style
        return `https://api.dicebear.com/8.x/${style}/svg?seed=${encodeURIComponent(userNameSeed)}&backgroundColor=2998FF,41b46a&radius=50`;
    };

    // Function to apply the current style
    const applyStyle = (index) => {
        const style = avatarStyles[index];
        imgDisplay.src = getAvatarUrl(style);
        
        // Save the style choice to local storage
        try {
            localStorage.setItem(storageKey, style);
        } catch (e) {
            console.error("Local storage save failed:", e);
        }
    };

    // Initialize the avatar with the stored or default style
    applyStyle(currentStyleIndex);

    // 2. Add click listener to cycle button
    cycleBtn.addEventListener('click', function() {
        // Move to the next style index, wrapping around to 0
        currentStyleIndex = (currentStyleIndex + 1) % avatarStyles.length;
        applyStyle(currentStyleIndex);
    });
});
