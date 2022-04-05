var username = document.getElementById('username')
var submit = document.getElementById('submit')
submit.disabled = true

function check() {
    if (username.value == "") {
        submit.disabled = true
    } else {
        url = `/check_username/`
        data = {
            data: username.value
        }
        $.ajax({
            'type': 'POST',
            'url': url,
            'data': data,
            'success': function(response) {
                if (response.taken == "yes") {
                    submit.disabled = true
                } else {
                    submit.disabled = false
                }
            },
            'error': function(error) {
                console.log(error)
            }
        })
    }
}