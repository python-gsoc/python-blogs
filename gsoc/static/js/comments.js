function showCommentForm(commentPk) {
    var form = document.getElementById('form-' + commentPk);
    form.style.display = 'block';
    form.scrollIntoView();
}