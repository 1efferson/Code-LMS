
//Script to make flash messages disappear
 
        document.addEventListener('DOMContentLoaded', (event) => {
            // Find all flash messages
            const alertElements = document.querySelectorAll('[role="alert"]');
            
            alertElements.forEach(function(element) {
                // Wait 5 seconds
                setTimeout(function() {
                    // Add transition for fading out
                    element.style.transition = 'opacity 0.5s ease-out';
                    element.style.opacity = '0';
                    
                    // After fade out, remove the element from the DOM
                    setTimeout(function() {
                        element.remove();
                    }, 500); // 500ms = 0.5s (must match transition duration)
                    
                }, 5000); // 5000ms = 5 seconds
            });
        });
