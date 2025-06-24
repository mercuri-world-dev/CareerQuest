document.addEventListener('DOMContentLoaded', function() { 
  const stars = document.querySelectorAll('.star');
  document.addEventListener('mousemove', function(e) {
    const { innerWidth, innerHeight } = window;
    const mouseX = e.clientX / innerWidth - 0.5;
    const mouseY = e.clientY / innerHeight - 0.5;

    stars.forEach((star, i) => {
      const factor = (i + 1) * 8; 
      star.style.transform = `translate(${mouseX * factor}px, ${mouseY * factor}px)`;
    });
  });
});
