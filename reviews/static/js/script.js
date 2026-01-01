const menuBtn = document.querySelector('.menu-icon');
const navMenu = document.querySelector('.menu');

menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});