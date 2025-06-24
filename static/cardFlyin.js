document.addEventListener('DOMContentLoaded', function () {
  const cards = document.querySelectorAll('.feature-card');
  cards.forEach((card, i) => {
    setTimeout(() => {
      card.classList.add('fly-in');
    }, 200 * i); // 200ms delay between each card
  });
});