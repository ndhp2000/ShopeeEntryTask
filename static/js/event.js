function time_format(time_stamp) {
    return moment.unix(time_stamp).format("DD/MM/YYYY");
}

function format_comment(user_id, name, time_comment, content, comment_id) {
    var login_data = JSON.parse(localStorage.getItem("login_token"));
    var login_userid = login_data.user_id;
    return `
    <div class="card-body p-4" >      
                    <div class="d-flex d-flex justify-content-between">
                            <div class="text-primary">`+ name + `</div>
                            <div>`+ user_id + `</div>
                            <div>`+ time_comment + ` GMT+7</div>
                            <button onclick="delete_comment(this)" value="` + comment_id +
        `" class = "btn btn-danger" `
        + ((user_id === login_userid) ? "" : "disabled") + `> Delete Comment id=` + comment_id + `</button>
                        </div>
                        <hr>
                        <div>` + content +
        `</div> </div>`
}

function format_likes(user_id, name) {
    return `<div class="d-flex d-flex justify-content-between">
            <div class="text-primary">`+ name + `</div>
            <div>`+ user_id + `</div>
        </div> <hr>`

}

function format_participants(user_id, name) {
    return `<div class="d-flex d-flex justify-content-between">
            <div class="text-primary">`+ name + `</div>
            <div>`+ user_id + `</div>
        </div> <hr>`
}

function loadCommentsContent(event_id) {
    var jsonRequestUrl = 'http://127.0.0.1/app_api/events/' + event_id + '/comments';
    console.log(jsonRequestUrl)
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {
            $('#info_message').html(result.message)
        }
        else {
            $('#error_message').html(result.message);
            if (result.app_status_code == 2) {
                refresh_token(function f() {
                    loadCommentsContent(event_id);
                });
                return;
            }
            else if (result.app_status_code == 3) {
                alert(result.message);
                localStorage.removeItem("login_token");
                window.location.href = "http://127.0.0.1";
                return;
            }
            return;
        }
        console.log("COMMENT RESPONSEs: ");
        console.log(result.response_data);
        let decodedText = "";
        $.each(result.response_data.comment_list, function (index, value) {
            decodedText += format_comment(value.user_id, value.name, time_format(value.comment_time), value.comment_content, value.comment_id);
        });
        $('#comment_tag').html(decodedText);
        $('#n_comments').html(result.response_data.n_comments);
    });
}

function loadLikesContent(event_id) {
    var jsonRequestUrl = 'http://127.0.0.1/app_api/events/' + event_id + '/likes';
    console.log(jsonRequestUrl)
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {
            $('#info_message').html(result.message)
        }
        else {
            $('#error_message').html(result.message)
            if (result.app_status_code == 2) {
                refresh_token(function f() {
                    loadLikesContent(event_id);
                });
                return;
            }
            else if (result.app_status_code == 3) {
                alert(result.message);
                localStorage.removeItem("login_token");
                window.location.href = "http://127.0.0.1";
                return;
            }
            return;
        }
        console.log("LIKES RESPONSEs: ");
        console.log(result.response_data);
        let decodedText = "";
        $.each(result.response_data.likes_list, function (index, value) {
            decodedText += format_likes(value.user_id, value.name);
        });
        $('#likes_tag').html(decodedText);
        $('#n_likes').html(result.response_data.n_likes);
    });
}

function loadParticipantsContent(event_id) {
    var jsonRequestUrl = 'http://127.0.0.1/app_api/events/' + event_id + '/participants';
    console.log(jsonRequestUrl)
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {
            $('#info_message').html(result.message)
        }
        else {
            $('#error_message').html(result.message)
            if (result.app_status_code == 2) {
                refresh_token(function f() {
                    loadParticipantsContent(event_id);
                });
                return;
            }
            else if (result.app_status_code == 3) {
                alert(result.message);
                localStorage.removeItem("login_token");
                window.location.href = "http://127.0.0.1";
                return;
            }
            return;
        }
        console.log("PARTICIPANT RESPONSEs: ");
        console.log(result.response_data);
        let decodedText = "";
        $.each(result.response_data.participants_list, function (index, value) {
            decodedText += format_likes(value.user_id, value.name);
        });
        $('#participants_tag').html(decodedText);
        $('#n_participants').html(result.response_data.n_participants);
    });
}


function loadEventContent(event_id) {
    var jsonRequestUrl = 'http://127.0.0.1/app_api/events/' + event_id;
    console.log(jsonRequestUrl)
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        // Table Content.
        if (result.app_status_code == 0) {
            $('#info_message').html(result.message)
        }
        else {
            $('#error_message').html(result.message)
            if (result.app_status_code == 2) {
                refresh_token(function f() {
                    loadEventContent(event_id);
                });
                return;
            }
            else if (result.app_status_code == 3) {
                alert(result.message);
                localStorage.removeItem("login_token");
                window.location.href = "http://127.0.0.1";
                return;
            }
            return;
        }
        console.log(result.response_data.event);
        $('#event_id').html(result.response_data.event.id);
        $('#title').html(result.response_data.event.title);
        $('#description').html(result.response_data.event.description);
        $('#location').html(result.response_data.event.location);
        $('#date').html(time_format(result.response_data.event.date));
        $('#image_url').attr("src", '/img/' + result.response_data.event.image_url);
        console.log('img = ' + '/img/' + result.response_data.event.image_url);
        $('#category').html(result.response_data.event.category_name);
        loadCommentsContent(event_id)
        loadLikesContent(event_id)
        loadParticipantsContent(event_id)
    });
}


$("#frmLike").submit(function (e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var form = $(this);
    var url = 'http://127.0.0.1/app_api/events/' + event_id + '/likes';
    console.log("post url = " + url)


    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            // Xu li
            $.ajax({
                type: "POST",
                url: url,
                headers: { 'X-CSRFToken': result.response_data.csrf },
                data: form.serialize(), // serializes the form's elements.
                success: function (data) {
                    console.log(data)
                    if (data.app_status_code == 0) {
                        loadLikesContent(event_id)
                    }
                    else {
                        if (data.app_status_code == 2) {
                            refresh_token(function f() {
                                $("#frmLike").submit();
                            });
                            return;
                        }
                        else if (data.app_status_code == 3) {
                            alert(data.message);
                            localStorage.removeItem("login_token");
                            window.location.href = "http://127.0.0.1";
                            return;
                        }
                        return;
                    }
                }
            });
            // Xu li

        }
        else {
            alert(result.message);
        }
    });


});


$("#frmUnlike").submit(function (e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var form = $(this);
    var url = 'http://127.0.0.1/app_api/events/' + event_id + '/likes';
    console.log("post url = " + url)


    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            // Xu li
            $.ajax({
                type: "DELETE",
                headers: { 'X-CSRFToken': result.response_data.csrf },
                url: url,
                data: form.serialize(), // serializes the form's elements.
                success: function (data) {
                    console.log(data)
                    if (data.app_status_code == 0) {
                        loadLikesContent(event_id)
                    }
                    else {
                        if (data.app_status_code == 2) {
                            refresh_token(function f() {
                                $("#frmUnlike").submit();
                            });
                            return;
                        }
                        else if (data.app_status_code == 3) {
                            alert(data.message);
                            localStorage.removeItem("login_token");
                            window.location.href = "http://127.0.0.1";
                            return;
                        }
                        return;
                    }
                }
            });
            // Xu li

        }
        else {
            alert(result.message);
        }
    });



});




$("#frmParticipant").submit(function (e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var form = $(this);
    var url = 'http://127.0.0.1/app_api/events/' + event_id + '/participants';
    console.log("post url = " + url)



    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            // Xu li
            $.ajax({
                type: "POST",
                url: url,
                headers: { 'X-CSRFToken': result.response_data.csrf },
                data: form.serialize(), // serializes the form's elements.
                success: function (data) {
                    console.log(data)
                    if (data.app_status_code == 0) {
                        loadParticipantsContent(event_id)
                    }
                    else {
                        if (data.app_status_code == 2) {
                            refresh_token(function f() {
                                $("#frmParticipant").submit();
                            });
                            return;
                        }
                        else if (data.app_status_code == 3) {
                            alert(data.message);
                            localStorage.removeItem("login_token");
                            window.location.href = "http://127.0.0.1";
                            return;
                        }
                        return;
                    }
                }
            });
            // Xu li

        }
        else {
            alert(result.message);
        }
    });
});


$("#frmUnparticipant").submit(function (e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var form = $(this);
    var url = 'http://127.0.0.1/app_api/events/' + event_id + '/participants';
    console.log("post url = " + url)


    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            // Xu li
            $.ajax({
                type: "DELETE",
                url: url,
                headers: { 'X-CSRFToken': result.response_data.csrf },
                data: form.serialize(), // serializes the form's elements.
                success: function (data) {
                    console.log(data)
                    if (data.app_status_code == 0) {
                        loadParticipantsContent(event_id)
                    }
                    else {
                        if (data.app_status_code == 2) {
                            refresh_token(function f() {
                                $("#frmUnparticipant").submit();
                            });
                            return;
                        }
                        else if (data.app_status_code == 3) {
                            alert(data.message);
                            localStorage.removeItem("login_token");
                            window.location.href = "http://127.0.0.1";
                            return;
                        }
                        return;
                    }
                }
            });
            // Xu li

        }
        else {
            alert(result.message);
        }
    });


});



$("#frmComment").submit(function (e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var form = $(this);
    var url = 'http://127.0.0.1/app_api/events/' + event_id + '/comments';
    console.log("post url = " + url)



    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            // Xu li
            $.ajax({
                headers: { 'X-CSRFToken': result.response_data.csrf },
                type: "POST",
                url: url,
                data: form.serialize(), // serializes the form's elements.
                success: function (data) {
                    console.log(data)
                    if (data.app_status_code == 0) {
                        loadCommentsContent(event_id)
                    }
                    else {
                        if (data.app_status_code == 2) {
                            refresh_token(function f() {
                                $("#frmComment").submit();
                            });
                            return;
                        }
                        else if (data.app_status_code == 3) {
                            alert(data.message);
                            localStorage.removeItem("login_token");
                            window.location.href = "http://127.0.0.1";
                            return;
                        }
                        return;
                    }
                }
            });
            // Xu li

        }
        else {
            alert(result.message);
        }
    });


});


function delete_comment(button) {

    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            // Xu li
            var url = 'http://127.0.0.1/app_api/events/' + event_id + '/comments?comment_id=' + $(button).attr("value");
            $.ajax({
                headers: { 'X-CSRFToken': result.response_data.csrf },
                type: "DELETE",
                url: url,
                success: function (data) {
                    console.log(data)
                    if (data.app_status_code == 0) {
                        loadCommentsContent(event_id)
                    }
                    else {
                        if (data.app_status_code == 2) {
                            refresh_token(function f() {
                                delete_comment(button);
                            });
                            return;
                        }
                        else if (data.app_status_code == 3) {
                            alert(data.message);
                            localStorage.removeItem("login_token");
                            window.location.href = "http://127.0.0.1";
                            return;
                        }
                        return;
                    }
                }
            });
            // Xu li

        }
        else {
            alert(result.message);
        }
    });

}








function refresh_token(callback) {


    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            // Xu li
            var url = 'http://127.0.0.1/app_api/auth/refresh_token';
            login_data = JSON.parse(localStorage.getItem("login_token"));
            data = { 'refresh_token': login_data.refresh_token }
            console.log("refresh token pos " + JSON.stringify(data));
            $.ajax({
                type: "POST",
                url: url,
                headers: { 'X-CSRFToken': result.response_data.csrf },
                data: data,
                success: function (data) {
                    console.log("REFRESH TOKEN RES:" + data)
                    if (data.app_status_code == 0) {
                        localStorage.setItem("login_token", JSON.stringify(data.response_data));
                        console.log(JSON.parse(localStorage.getItem("login_token")));
                        console.log(data.message);
                        callback();
                    }
                    else {
                        alert(data.message);
                        localStorage.removeItem("login_token");
                        window.location.href = "http://127.0.0.1";
                    }
                }
            });
            // Xu li

        }
        else {
            alert(result.message);
        }
    });

}


function process_log_out() {

    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {


            //
            var url = 'http://127.0.0.1/app_api/auth/logout';
            console.log("post url = " + url)
            $.ajax({
                type: "POST",
                headers: { 'X-CSRFToken': result.response_data.csrf },
                url: url,
                success: function (data) {
                    if (data.app_status_code == 0) {
                        alert(data.message);
                        localStorage.removeItem("login_token");
                        window.location.href = "http://127.0.0.1";
                    }
                    else {
                        if (data.app_status_code == 2) {
                            console.log(data.message);
                            refresh_token(function callback() {
                                process_log_out();
                            });
                            return;
                        }
                        else if (data.app_status_code == 3) {
                            alert(data.message);
                            localStorage.removeItem("login_token");
                            window.location.href = "http://127.0.0.1";
                            return;
                        }
                        return;
                    }
                }
            });
            //


        }
        else {
            alert(result.message);
        }
    });


}
