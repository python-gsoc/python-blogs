function toggleMenu() {
    var menu = document.getElementById("menu");
    var classes = menu.className.split(" ");
    if (classes.indexOf("opened") == -1) {
        classes.push("opened");
        menu.className = classes.join(" ");
    }
    else {
        classes.splice(classes.indexOf("opened"), 1)
        menu.className = classes.join(" ");
    }
}