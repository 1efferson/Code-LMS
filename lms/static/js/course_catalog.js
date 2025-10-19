    //  Simple JS to highlight the current nav link on scroll and handle smooth scroll
   
        document.addEventListener('DOMContentLoaded', () => {
            const sections = document.querySelectorAll('.course-level-section');
            const navLinks = document.querySelectorAll('.nav-link');
            const nav = document.querySelector('.level-nav');

            // Observer to highlight current section
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const currentId = entry.target.id;
                        navLinks.forEach(link => {
                            link.classList.remove('active');
                        });
                        document.getElementById(`${currentId}-link`).classList.add('active');
                    }
                });
            }, {
                rootMargin: '0px',
                threshold: 0.5 // Trigger when 50% of the section is visible
            });

            sections.forEach(section => {
                observer.observe(section);
            });

            // Smooth scroll for nav links (if not automatically handled by CSS scroll-behavior)
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop,
                            behavior: 'smooth'
                        });
                    }
                });
            });

            // Set the first link as active on load
            if (navLinks.length > 0) {
                navLinks[0].classList.add('active');
            }
        });
 