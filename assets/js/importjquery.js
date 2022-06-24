let checkbox = document.querySelectorAll('[name="selected"]');

checkbox.forEach((c)=>{
    c.setAttribute('disabled', true)
});

$('[name="qty"]').change(function(e) {

    if ( $(e.target).val() > 0) { 
    
        row = $(e.target).closest('tr')
        $('td input:checkbox',row).prop('disabled',false);
        $('td input:checkbox',row).prop('checked',true);    
    }
    
});
    
    let frm = $('#main-form');

    frm.submit(function (e) {
        e.preventDefault();
        let checkboxes = document.querySelectorAll('input[type=checkbox]'); 
        let empty = [].filter.call( checkboxes, function( el ) {
            return !el.checked
         });

        empty.forEach(element => {
            element.parentElement.parentElement.remove()
        });
        
         if (checkboxes.length == empty.length) {
            is_data_empty = true
        }

const successHandler = (data) => {
        url = window.location.origin + '/books/'
        window.location.replace(url);
    }

   $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        success: successHandler(),
        error: function(data) {
            console.log("Error");
        }
    });
    return false;
}
);