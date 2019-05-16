const sleep = (milliseconds) => {
    return new Promise(resolve => setTimeout(resolve, milliseconds))
}

function showCommentForm(commentPk) {
    var form = document.getElementById('form-' + commentPk);
    form.style.display = 'block';
    form.scrollIntoView();
}

function copyCommentUrl(commentPk) {
    var href = window.location.href.split('#')[0]
    var str = href + '#comment-' + commentPk;
    var el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);

    var share = document.getElementById(`share-${commentPk}`);
    share.innerHTML = "<span>Link copied!</span>"
    sleep(3000).then(() => {
        share.innerHTML = `<span onclick="copyCommentUrl(${commentPk})" id="share-${commentPk}">Share</span>`;
    })
}

(function markSelected() {
    var parts = window.location.href.split('#')
    if (parts.length == 2 && parts[1].split('-')[0] == 'comment') {
        var comment = document.getElementById(parts[1]);
        if (comment) {
            comment.classList.add('selected')
        }
    }
}());

grecaptcha.ready(function() {
    grecaptcha.execute('6LdAVqIUAAAAAAt6baSHpGXr1LvJ0n1aCl_oqukj', {action: 'comment'}).then(function(token) {
        forms = document.getElementsByClassName('comment-form');
        for (var i=0; i<forms.length; i++) {
            form = forms.item(i);
            var input =  document.createElement('input')
            input.setAttribute('type', 'hidden');
            input.setAttribute('name', 'g-recaptcha-response');
            input.setAttribute('value', `${token}`);
            form.appendChild(input);
        }
    });
});
