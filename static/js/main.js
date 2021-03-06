const navbar_cross = document.querySelector(".navbar-cross");
const navbar_nav = document.querySelector(".navbar-nav");
const links = document.querySelector(".navbar-nav li");

navbar_cross.addEventListener('click', ()=>{
    navbar_nav.classList.toggle("open");
    links.forEach(link => {
        link.classList.toggle("fade");
    });
    navbar_cross.classList.toggle("toggle");
});
