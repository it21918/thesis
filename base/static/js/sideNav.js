const link = document.querySelectorAll(".link");

for (let i = 0; i < link.length; i++) {
  link[i].addEventListener("click", function () {
    var current = document.getElementsByClassName("active");
    current[0].className = current[0].className.replace(" active", "");
    this.className += " active";
  });
}

const sidebar = document.getElementById("sidebars")

window.addEventListener(
    "storage",
    function () {
        if (localStorage.lightMode == "dark") {
            sidebar.backgroudColor = 'white'
        } else {
            sidebar.backgroudColor = 'black'
        }
    },
    false
);



