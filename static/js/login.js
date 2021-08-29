$("#loginForm").submit(function (e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

    var form = $(this);
    var url = form.attr('action');
    console.log("post url = " + url);
    console.log("form = ", form.serialize());
    $.ajax({
        type: "POST",
        url: url,
        data: form.serialize(), // serializes the form's elements.
        success: function (data) {
            console.log(data)
            if (data.app_status_code == 0) {
                localStorage.setItem("login_token", JSON.stringify(data.response_data));
                // Retrieve
                console.log(JSON.parse(localStorage.getItem("login_token")));

                window.location.href = "http://127.0.0.1/list.html";
            }
            else {
                $("#password").val("")
            }
            alert(data.message)
        }
    });


});