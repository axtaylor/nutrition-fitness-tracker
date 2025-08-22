document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('nav');
    const close_navbar = document.querySelector('.close_navbar');
    const body = document.querySelector('body');
    
    close_navbar.addEventListener('click', () => {
        navbar.classList.toggle('hidden');
        body.classList.toggle('navactive');
    });
    close_navbar.addEventListener('click', () => {
        if (navbar.classList.contains('hidden')){
            body.classList.remove('blur-except-sidebar');
        }
        else{
            body.classList.add('blur-except-sidebar');
        }
    });
});