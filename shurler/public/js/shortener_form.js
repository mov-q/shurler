function getUserUrls () {
    jQuery.post( '/redir/get_user_shorturls', function(data, textStatus, jqXHR) {
            h = '<ul>';
            $.each(data.urls, function(i,v){
                h += '<li>'+v.short+'</li>';
            });
            h += '</ul>';
            $('#user-urls').html(h);
        }
    ,'json');
};

$(document).ready (function() {
        $('#shorten_form').validate({
            rules: {
                short:{
                    url: true,
                    required: true
                }
            },
            submitHandler: function(form) {
                var options = { 
                    success: function (res, statusText, xhr, $form)  { 
                                if (statusText == 'success') {
                                    $.each(res, function(idx, v) {
                                        if (idx == 'RATE_LIMIT') {
                                            if (! v) {
                                                $('#short').val('Rate Limit exceeded');
                                            }
                                        }
                                        else if (idx == 'short') {
                                            $('#short').val(v); 
                                        }
                                        else if (idx == 'qrcode') {
                                            h = '<img src="'+v+'">';
                                            $('#qrcode').html(h);
                                        }

                                    });
                                    getUserUrls();
                                }
                            },
                    dataType: 'json'
                };  
                $(form).ajaxSubmit(options);

            }
        });
});

