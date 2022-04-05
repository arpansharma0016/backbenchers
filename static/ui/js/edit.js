textarea = document.querySelector("#heading");
textarea.addEventListener('input', autoResize, false);
imagemodal = document.getElementById('showImageModal')

function autoResize() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
}

caption = document.querySelector("#caption");
caption.addEventListener('input', autoResizeCaption, false);

function autoResizeCaption() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
}



function imagesearch() {
    document.getElementById('searchimagearea').innerHTML = ""
    if (document.getElementById('imagesearch').value.trim() == "") {
        document.getElementById('searchimagearea').style = ""
    } else {
        query = document.getElementById('imagesearch').value.trim()
        document.getElementById('searchimagearea').style = "width: 100%;height: 350px;overflow: scroll; overflow-x: hidden;"
        loadunsplashimages(query, 10, 1)
    }
}

loadunsplashimages = function(value, per_page, page) {
    url = `https://api.unsplash.com/search/photos?query=${value}&client_id=YOPWFEmTKFzUBMKKQwyCWlcdNoikErC0WfXsQB-f9-4&per_page=${per_page}&page=${page}`
    $.get(url, function(data) {
        $('#loadmorecontainer').remove()
        if (page == 1) {
            document.getElementById('searchimagearea').innerHTML = ""
        }
        for (var x = 0; x < data.results.length; x++) {
            var imagesrc = data.results[x].urls.regular
            document.getElementById('searchimagearea').innerHTML += `
                    <div class="col-lg-6 col-md-6 col-sm-6">
                        <img src="${imagesrc}" alt="Image" class="img-fluid" style="margin: 5px;object-fit:cover;" onclick="selectimage(event, '${imagesrc}')">
                        </div>
                `

            if (value != document.getElementById('imagesearch').value.trim()) {
                document.getElementById('searchimagearea').innerHTML = ""
            }
            if (x + 1 >= data.results.length) {
                page += 1
                document.getElementById('searchimagearea').innerHTML += `
            <div class="m-2" id="loadmorecontainer" style="width:100%;justify-content: center; align-items: center; text-align: center; display: flex;">
                <button class="btn subscribe" onclick="loadunsplashimages('${value}', ${per_page}, ${page})"> Load More </button>
            </div>
            `
            }
        }
    })
}

function selectimage(e, src) {
    e.preventDefault()
    document.getElementById('thumbnail').value = src
    document.getElementById('searchimagearea').innerHTML = ''
    document.getElementById('searchimagearea').style = ""
    document.getElementById('thumbnailimagearea').innerHTML = `<br>
    <div class="me-md-5 thumbnail mb-3 mb-md-0">
        <img src="${src}" alt="Image" class="img-fluid">
    </div>
`
}


function edit_post(e, id) {
    e.preventDefault()
    notify("Saving post...")
    document.getElementById('savecontainer').innerHTML = `
    <button class="btn btn-primary">Saving...</button>
    `
    id = parseInt(id)
    url = `/me/edit_post-${id}/`
    var heading = document.getElementById('heading').value
    var caption = document.getElementById('caption').value
    var thumbnail = document.getElementById('thumbnail').value
    var category = document.getElementById('category').value
    if (heading) {
        dataa = new FormData();
        dataa.append("heading", heading)
        dataa.append("caption", caption)
        dataa.append("thumbnail", thumbnail)
        dataa.append("category", category)
        $.ajax({
            'type': 'POST',
            'url': url,
            'mimeType': "multipart/form-data",
            'contentType': false,
            'processData': false,
            'data': dataa,
            'success': function(response) {
                response = JSON.parse(response)
                if (response.status == 'success') {
                    window.location.href = '/me/'
                } else {
                    notify(response.message)
                    document.getElementById('savecontainer').innerHTML = `
                    <button class="btn btn-primary" onclick="edit_post(event, '${id}')">Save</button>
                    `
                }
            },
            'error': function(error) {
                notify("An error occured...")
                document.getElementById('savecontainer').innerHTML = `
                <button class="btn btn-primary" onclick="edit_post(event, '${id}')">Save</button>
                `
            },
        })
    } else {
        notify("Please write a post heading")
        document.getElementById('savecontainer').innerHTML = `
        <button class="btn btn-primary" onclick="edit_post(event, '${id}')">Save</button>
        `
    }

}



function notify(message) {
    document.getElementById('notification').innerHTML = `
    <p class="btn btn-primary">${message}</p>
    `
    setTimeout(() => {
        document.getElementById('notification').innerHTML = ''
    }, 5000)
}