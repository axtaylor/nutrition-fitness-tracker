document.addEventListener('DOMContentLoaded', () => {

    const navbar = document.querySelector<HTMLElement>('nav');
    if (!navbar) return;

    const toggle_navbar = document.querySelector<HTMLElement>('.close_navbar');
    if(!toggle_navbar) return;

    const body = document.querySelector<HTMLElement>('body');
    if (!body) return;

    // Only present on pages where navbar is disabled
    const disabled_flag = document.getElementById('hide_navbar');
    let disable : String = "";

    if (disabled_flag) {
        disable = disabled_flag.textContent;
    }
    else {
        disable = "";
    }

    // Fully hidden button + menu bar
    if (disable) {
        navbar.style.transition = 'none';
        body.style.transition = 'none';
        toggle_navbar.style.display = 'none';
        navbar.style.display = 'none'
        body.classList.add('navactive')
    }

    // Toggler
    // TODO: backwards class names.
    // There is technical debt in the CSS for this utility
    toggle_navbar.addEventListener("click", () => {

        navbar.classList.toggle("hidden");
        body.classList.toggle("navactive");

        if (navbar.classList.contains("hidden")) {
            body.classList.remove("blur-except-sidebar");
        } else {
            body.classList.add("blur-except-sidebar");
        }
    });

});