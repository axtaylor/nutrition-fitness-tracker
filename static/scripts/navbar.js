document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('nav');
    const close_navbar = document.querySelector('.close_navbar');
    const body = document.querySelector('body');

    const hide_navbar = document.getElementById('hide_navbar');
    
    if (hide_navbar) {

        const hide = JSON.parse(hide_navbar.textContent);
            if (hide == true) {

            navbar.style.transition = 'none';
            body.style.transition = 'none';
            close_navbar.style.display = 'none';
            navbar.style.display = 'none'
        
                if (window.matchMedia('(max-width: 768px)').matches) {
                    body.classList.add('navactive')
                }
                else {
                    body.classList.add('navactive')
                }
        }
    }

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