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