const roles = [
    "Computer Engineer",
    "CS Student",
    "Future Software Engineer",
    "Web Developer",
    "AI Enthusiast"
];

const typingElement = document.getElementById("typing");
const contactForm = document.querySelector(".contact-form");

let roleIndex = 0;

setInterval(() => {
    roleIndex = (roleIndex + 1) % roles.length;
    typingElement.textContent = roles[roleIndex];
}, 2000);

contactForm.addEventListener("submit", (event) => {
    event.preventDefault();
    alert("Thank you! Your message has been received.");
    contactForm.reset();
});
