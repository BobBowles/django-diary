/* scripts for handling drag-n-drop and ajax */
/* http://www.w3schools.com/html/html5_draganddrop.asp */
/* with tweaks from 
   http://www.html5rocks.com/en/tutorials/dnd/basics/ */


/* organise the disabled status of 'new' buttons */
function updateNewButtons() {
    if (enable_new_buttons_disable) {
        var btnList = document.getElementsByClassName('new');
        //console.log('btnList length: '+btnList.length)
        var i;
        for (i=0; i < btnList.length; i++) {
            var btn = btnList[i];
            // find any siblings of the button that are entry elements
            var parent = btn.parentElement;
            btnList[i].disabled = 
                $(parent).find('.entry').length || 
                $(parent).hasClass('admin') ||
                $(parent).hasClass('historic') ||
                $(parent).hasClass('advance');
            if (btnList[i].disabled) {
                console.log('Disabled one!');
            };
        };
    };
};


/* drag and drop handlers attached to targets in html via onXXXX syntax 
 e.g. <div ondragover="dragover(event);" etc...> */

function dragover(ev) {
    if (ev.preventDefault) {
        ev.preventDefault(); // Necessary. Allows us to drop.
    }
    //console.log('Dragover element ['+ev.target.id+']');
}

function dragenter(ev) {
    //console.log('Entering element ['+ev.target.id+']');
    ev.target.classList.add('dragover');  // the new drop target.
}

function dragleave(ev) {
    //console.log('Leaving element ['+ev.target.id+']');
    ev.target.classList.remove('dragover');  // now the previous drop target.
}

function drag(ev) {
    ev.dataTransfer.setData("text/html", ev.target.id);
    //console.log('Dragging target ['+ev.target.id+']');
    //console.log('Data to transfer is '+ev.dataTransfer.getData("text/html"))
}

function drop(ev) {
    //console.log('Drop Event on element ['+ev.target.id+']');
    ev.preventDefault();
    var pk = ev.dataTransfer.getData("text/html");
    //console.log('pk from data transfer is ['+pk+']');
    var slug = ev.target.id;
    /* ajax stuff goes here */
    $.ajax({
        url: entry_dnd_url,
        type: "post",
        data: {pk: pk, slug: slug},
        success: function(result) {
            /* if the post succeeds continue with the drop */
            dragElement = document.getElementById(pk);
            ev.target.appendChild(dragElement);
            dragElement.classList.remove('cancelled');
            dragElement.classList.remove('no_show');
            //console.log('Dropped target in ['+ev.target.id+']');
            updateNewButtons(); // because the async call is last to complete
        },
        error: function (xhr, ajaxOptions, thrownError) {
            //console.log(xhr);
            alert('Cannot put entry there. Try a different day or time.');
      }
    });
    //console.log('Finalising css on ['+ev.target.id+']');
    ev.target.classList.remove('dragover');  // clean the css
}

function dragend(ev) {
    /* tidy up after the drag */
    //console.log('Drag ended for element ['+ev.target.id+']');
    //updateNewButtons(); // ajax is asynchronous so this happens too soon here
}


jQuery(document).ready(function(){
    //console.log('Updating button status at start...');
    updateNewButtons();
});


