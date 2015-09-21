/* these three code snippets enable updated entry data to be displayed in a
modal and acted upon. */


/* listener cleans out the hidden input data repository when a modal is shown 
and gets the new data for the modal as an html snippet from the server */
$(document).on('show.bs.modal', function (event) {
    //console.log('Cleaning old next_url...');
    $('#next_url').val('');
    //console.log('Cleaning out old modal contents...');
    var modal = $('#ajaxModal');
    modal.html(''); // remove old modal contents
    //console.log('Start Modal Contents: '+modal.html());
    /* obtain data for populating the modal */
    var trigger = $(event.relatedTarget);
    var href = trigger.data('href');
    console.log('Retrieving data from '+href);
    /* use ajax to populate the modal stub */
    $.ajax({
        url: href,
        type: "get",
        data: {redirect_url: redirect_url},
        datatype: "html",
        success: function(result) {
            /* if the get succeeds add the results into the modal */
            //console.log('Results:'+result)
            modal.html(result);
            //console.log('Finish Modal Contents: '+modal.html());
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log(xhr);
            alert('Cannot instantiate modal.');
        }
    });
});


/* method attached to modal action buttons via onclick puts the redirection
target in the hidden input and hides the modal */
function next_url(href) {
    //console.log('Setting next_url to '+href)
    $('#next_url').val(href);
    $('#ajaxModal').modal("hide");
}


/* listener navigates to new web page after the modal is closed */
$(document).on('hidden.bs.modal', function (event) {
    if ($('#next_url').val()) {
        //console.log('Navigating to '+$('#next_url').val());
        location.href = $('#next_url').val();
    }
});

