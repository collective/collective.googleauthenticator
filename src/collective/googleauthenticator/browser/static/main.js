/*
    Document   : main.js
    Description:
        Auxiliary scripts for `collective.googleauthenticator`.
*/

;
$(document).ready(function(){
    // Tweaks on personal information page
    if ($('.template-personal-information').length || $('.template-user-information').length) {
        // Disable the checkbox
        try {
            $('input#form\\.enable_two_factor_authentication').attr('disabled', 'disabled');
        } catch(err) {}


        // Hide the secret key input
        try {
            $('input#form\\.two_factor_authentication_secret').parents('.field').hide();
        } catch(err) {}

        // Hide the reset bar-code token input
        try {
            $('input#form\\.bar_code_reset_token').parents('.field').hide();
        } catch(err) {}
    }

    // Turn autocomplete off for token fields.
    try {
        $('#form-widgets-token').attr("autocomplete","off");
    } catch(err) {}
});
