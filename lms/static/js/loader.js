document.addEventListener("DOMContentLoaded", () => {
  const loader = document.querySelector(".loader");

  // Show loader initially
  loader.style.display = "block";

  // Hide loader once page is fully loaded
  window.addEventListener("load", () => {
    setTimeout(() => {
      loader.style.opacity = "0";
      loader.style.transition = "opacity 0.5s ease";
      setTimeout(() => {
        loader.style.display = "none";
      }, 500); // matches fade-out time
    }, 300); // optional delay
  });
});
