/* scripts for handling csrf authentication in ajax. */


/* get hold of the csrf token for posting, setup ajax to use it 
(uses js.cookie.js)*/
var csrftoken = Cookies.get('csrftoken');

/* these are cut-and-pasted straight from the Django ajax manual pages */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
$(document).ajaxSend(function() {
    console.log("Triggered ajaxSend handler."); 
});

