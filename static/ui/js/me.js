function delete_post(e, id, heading) {
    e.preventDefault()
    idd = parseInt(id)
    document.getElementById('modal-container').classList.add('show-modal')
    document.getElementById('delete-post-heading').innerText = heading
    document.getElementById('delete_id').value = id
}

function delete_button(e) {
    e.preventDefault()
    if (document.getElementById('delete_id').value.trim() != "") {
        id = document.getElementById('delete_id').value.trim()
        url = `/me/delete_post-${id}`
        $.get(url, function(response) {
            if (response.status == "success") {
                if (document.getElementById('post__id-' + response.id)) {
                    document.getElementById('post__id-' + response.id).remove()
                    document.getElementById('modal-container').classList.remove('show-modal')
                    notify("Post deleted")
                }
            } else {
                notify(response.message)
            }
        })
    }
}


function load_image(e) {
    document.getElementById('image').innerHTML = `
    <img src="${URL.createObjectURL(e.target.files[0])}" style="width: 6em;height: 6em; border-radius: 50%; object-fit: cover;">    
    `
}


function notify(message) {
    document.getElementById('notification').innerHTML = `
    <p class="btn btn-primary">${message}</p>
    `
    setTimeout(() => {
        document.getElementById('notification').innerHTML = ''
    }, 5000)
}