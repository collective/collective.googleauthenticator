/*
    Document   : main.js
    Description:
        Auxiliary scripts for `collective.googleauthenticator`.
*/

;
$(document).ready(function() {
    // Turn autocomplete off for token fields.
    try {
        $('#form-widgets-token').attr("autocomplete","off");
    } catch(err) {}
});
