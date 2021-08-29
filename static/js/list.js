function time_format(time_stamp) {
    return moment.unix(time_stamp).format("MM/DD/YYYY");
}
function parseGetURL(page, category_id, begin_date, end_date) {
    var result = '';
    if (page) {
        if (result.length == 0) result += '?'; else result += '&';
        result = result + 'page=' + page;
    }

    if (category_id) {
        if (result.length == 0) result += '?'; else result += '&';
        result = result + 'category_id=' + category_id;
    }

    if (begin_date) {
        if (result.length == 0) result += '?'; else result += '&';
        result = result + 'begin_date=' + begin_date;
    }

    if (end_date) {
        if (result.length == 0) result += '?'; else result += '&';
        result = result + 'end_date=' + end_date;
    }
    return result;
}
function loadTableContent(page, category_id, begin_date, end_date) {
    var jsonRequestUrl = 'http://127.0.0.1/app_api/events' + parseGetURL(page, category_id, begin_date, end_date);
    console.log("send GET" + jsonRequestUrl);
    var decodedText = "";
    var decodedPagination = "";
    console.log(jsonRequestUrl)
    $.getJSON(jsonRequestUrl).done(function foo(result) {
        console.log(result);
        if (result.app_status_code == 0) {
            $('#info_message').html(result.message)
        }
        else {
            $('#error_message').html(result.message)
            if (result.app_status_code == 2) {
                refresh_token(function f() {
                    loadTableContent(page, category_id, begin_date, end_date);
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
        // Table Content.
        console.log(result.response_data);
        $.each(result.response_data.event_list, function (index, value) {
            decodedText += '<tr>'
            decodedText += '<td class="text-center">' + value.title + '</td>';
            decodedText += '<td class="text-center">' + value.description + '</td>';
            decodedText += '<td class="text-center">' + value.location + '</td>';
            decodedText += '<td class="text-center">' + time_format(value.date) + '</td>';
            decodedText += '<td class="text-center">' + value.category_name + '</td>';
            decodedText += '<td class="text-center"> <a href = "/event.html?id=' + value.id + '"> click </a></td>';
            decodedText += '</tr>'
        });
        // Render Pagination
        var left_page = Math.max(1, page - 10)
        var right_page = Math.min(Math.ceil(result.response_data.n_events / 20), page + 10)
        console.log(left_page + " " + right_page);
        for (var i = left_page; i <= right_page; ++i) {
            if (page === i)
                decodedPagination += '<li class="page-item"><button class = "btn btn-info" disabled onclick="loadTableContent(' + i + "," + category_id + "," + begin_date + "," + end_date + ')">' + i + '</button> </li>';
            else
                decodedPagination += '<li class="page-item"><button class = "btn btn-info" onclick="loadTableContent(' + i + "," + category_id + "," + begin_date + "," + end_date + ')">' + i + '</button> </li>';
        }
        $('#pagination-bar').html(decodedPagination);
        $('#table-content').html(decodedText);
    });
}



function isNumeric(str) {
    if (typeof str != "string") return false // we only process strings!  
    return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
        !isNaN(parseInt(str)) // ...and ensure strings of whitespace fail
}

function isDate(str) {
    if (typeof str != "string") return false // we only process strings!  
    var date = moment(str, "DD/MM/YYYY", true);
    return date.isValid();
}

function toUnix(str) {
    return moment(str, "DD/MM/YYYY", true).unix();
}

$("#frmFilter").submit(function (e) {
    e.preventDefault(); // avoid to execute the actual submit of the form.
    var form = $(this);
    category_id = $("#category_id").val();
    begin_time = $("#begin_time").val();
    end_time = $("#end_time").val();

    if (category_id != "") {
        if (!isNumeric(category_id)) {
            alert("category_id must be a number");
            return;
        }
        category_id = parseInt(category_id);
    }
    else
        category_id = null


    if (begin_time != "") {
        if (!isDate(begin_time)) {
            alert("begin_date must be dd/mm/yyyy");
            return;
        }
        begin_time = toUnix(begin_time);
    }
    else
        begin_time = null;


    if (end_time != "") {
        if (!isDate(end_time)) {
            alert("end_date must be dd/mm/yyyy");
            return;
        }
        end_time = toUnix(end_time);
    }
    else
        end_time = null

    console.log(category_id + " " + begin_time + " " + end_time);
    loadTableContent(1, category_id, begin_time, end_time);
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
