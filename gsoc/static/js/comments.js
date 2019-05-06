function showCommentForm(commentPk) {
    var form = document.getElementById('form-' + commentPk);
    form.style.display = 'block';
    form.scrollIntoView();
}

function copyCommentUrl(commentPk) {
    var href = window.location.href.split('#')[0]
    var str = href + '#comment-' + commentPk;
    console.log(str);
    var el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}

(function markSelected() {
    var parts = window.location.href.split('#')
    if (parts.length == 2 && parts[1].split('-')[0] == 'comment') {
        var comment = document.getElementById(parts[1]);
        console.log(comment);
        if (comment) {
            comment.classList.add('selected')
        }
    }
}());