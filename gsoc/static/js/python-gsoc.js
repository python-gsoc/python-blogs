//js for register button
$(function() {
    var chk = $('#check');
    var btn = $('#btncheck');

    chk.on('change', function() {
        btn.prop("disabled", !this.checked); //true: disabled, false: enabled
    }).trigger('change'); //page load trigger event
});

(function(window, document) {

    var layout = document.getElementById('layout'),
        menu = document.getElementById('menu'),
        menuLink = document.getElementById('menuLink'),
        content = document.getElementById('main');

    function toggleClass(element, className) {
        var classes = element.className.split(/\s+/),
            length = classes.length,
            i = 0;

        for (; i < length; i++) {
            if (classes[i] === className) {
                classes.splice(i, 1);
                break;
            }
        }
        // The className is not found
        if (length === classes.length) {
            classes.push(className);
        }

        element.className = classes.join(' ');
    }

    function toggleAll(e) {
        var active = 'active';

        e.preventDefault();
        toggleClass(layout, active);
        toggleClass(menu, active);
        toggleClass(menuLink, active);
    }

    menuLink.onclick = function(e) {
        toggleAll(e);
    };

    content.onclick = function(e) {
        if (menu.className.indexOf('active') !== -1) {
            toggleAll(e);
        }
    };

}(this, this.document));

//js for dropdown menu

function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
    document.querySelector('.dropdown-select').classList.toggle('open');
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(e) {
    if (!e.target.matches(".dropbtn")) {
        var o, s = document.getElementsByClassName("dropdown-content");
        for (o = 0; o < s.length; o++) {
            var t = s[o];
            t.classList.contains("show") && t.classList.remove("show")
        }

        document.querySelector(".dropdown-select").classList.remove("open")
    }

};