document.addEventListener("DOMContentLoaded", () => {
  const loader = document.querySelector(".loader");

  // Default: hide loader at start
  loader.style.display = "none";

  // Check if user has already visited during this session
  const firstVisit = sessionStorage.getItem("hasVisited") !== "true";

  if (firstVisit) {
    // Show loader immediately on first load
    loader.style.display = "block";

    window.addEventListener("load", () => {
      sessionStorage.setItem("hasVisited", "true"); // Mark visit so loader won't auto-play again
      fadeOutLoader(loader);
    });
  } else {
    // For all other pages, only show loader if load is slow
    const loadDelay = setTimeout(() => {
      loader.style.display = "block";
      loader.style.opacity = "1";
    }, 2000); // loader shows after 2 seconds of slow loading

    window.addEventListener("load", () => {
      clearTimeout(loadDelay); // If page finished fast, cancel showing loader
      fadeOutLoader(loader);
    });
  }
});

// Helper function to fade out loader smoothly
function fadeOutLoader(loader) {
  if (loader.style.display === "block") {
    setTimeout(() => {
      loader.style.opacity = "0";
      loader.style.transition = "opacity 0.4s ease";

      setTimeout(() => {
        loader.style.display = "none";
      }, 400);
    }, 200);
  }
}
