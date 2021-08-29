function isDate(str) {
    if (typeof str != "string") return false // we only process strings!  
    var date = moment(str, "DD/MM/YYYY", true);
    return date.isValid();
}

function toUnix(str) {
    return moment(str, "DD/MM/YYYY", true).unix();
}



$("#frmAddEvent").submit(function (e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.


    var date = $('#raw_date').val();
    if (!isDate(date)) {
        alert('Date shsould be dd/mm/yyyy');
        return false;
    }


    var form = $(this);
    var url = form.attr('action');
    var data = new FormData(form[0]);
    console.log("post url = " + url);

    data.append("date", toUnix(date));

    var jsonRequestUrl = 'http://127.0.0.1/app_api/auth/identity';
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        if (result.app_status_code == 0) {

            $.ajax({
                type: "POST",
                enctype: 'multipart/form-data',
                processData: false,  // Important!
                contentType: false,
                headers: { 'X-CSRFToken': result.response_data.csrf },
                cache: false,
                url: url,
                data: data,
                success: function (data) {
                    console.log(data);
                    if (data.app_status_code == 2) {
                        refresh_token(function f() {
                            $("#frmAddEvent").submit();
                        });
                        return;
                    }
                    else if (data.app_status_code == 3) {
                        alert(data.message);
                        localStorage.removeItem("login_token");
                        window.location.href = "http://127.0.0.1";
                        return;
                    }
                    alert(data.message);
                }
            });

        }
        else {
            alert(result.message);
        }
    });



});





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
