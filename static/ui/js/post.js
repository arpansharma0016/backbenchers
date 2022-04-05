var user = document.currentScript.getAttribute('user')
var url = document.currentScript.getAttribute('pdf')

let pdfDoc = null,
    pageNum = 1,
    pageIsRendering = false,
    pageNumIsPending = null
const scale = 1,
    canvas = document.getElementById('pdf_container'),
    ctx = canvas.getContext('2d')


const renderPage = num => {
    pageIsRendering = true
    pdfDoc.getPage(num).then(page => {
        const viewport = page.getViewport({ scale })
        canvas.height = viewport.height
        canvas.width = viewport.width

        const renderCtx = {
            canvasContext: ctx,
            viewport
        }
        page.render(renderCtx).promise.then(() => {
            pageIsRendering = false
            if (pageNumIsPending !== null) {
                renderPage(pageNumIsPending)
                pageNumIsPending = null
            }
        })

        document.getElementById('page-num').innerText = num
    })
}

const queueRenderPage = num => {
    if (pageIsRendering) {
        pageNumIsPending = num
    } else {
        renderPage(num)
    }
}


const showPrevPage = () => {
    if (pageNum <= 1) {
        return;
    }
    pageNum--
    queueRenderPage(pageNum)
}

const showNextPage = () => {
    if (pageNum >= pdfDoc.numPages) {
        return;
    }
    pageNum++
    queueRenderPage(pageNum)
}



var task = pdfjsLib.getDocument(url)

task.onProgress = function(data) {
    document.getElementById('pageload').innerText = 'Loading'
    document.getElementById('page-num').innerText = parseInt((data.loaded / data.total) * 100) + '%'
}

task.promise.then(pdfDoc_ => {
    pdfDoc = pdfDoc_

    document.getElementById('page-count').innerText = `of ${pdfDoc.numPages}`
    document.getElementById('pageload').innerText = 'Page'

    renderPage(pageNum)
}).catch(err => {
    document.querySelector('.pdff').innerHTML = `
    <h2 class="logo">${err.message}</h2>
    `
})

document.getElementById('prev-page').addEventListener('click', showPrevPage)
document.getElementById('next-page').addEventListener('click', showNextPage)

if (user != "no") {
    user = parseInt(user)
}

function load_comments(id) {
    document.getElementById('comments').innerHTML = ''
    document.getElementById('comments-number').innerHTML = 'Loading Comments'
    id = parseInt(id)
    url = `/me/load_comments-${id}`
    $.get(url, function(response) {
        if (response.status == 'success') {
            document.getElementById('comments-number').innerHTML = `${response.count} Comments`
            comments = JSON.parse(response.comments)
            for (i = 0; i < comments.length; i++) {
                comment = comments[i].fields
                mee = response.real[i]
                if (mee[6]) {
                    document.getElementById('comments').innerHTML += `
                    <a style="cursor:pointer;" id="comment-container-${mee[0]}" onclick="user_show(event, ${mee[0]}, '${mee[1]}', '${mee[2]}', ${mee[3]}, ${mee[4]})">
                        <div class="image--container" style="float: left;">
                            <img src="https://mediafiles-arpan.s3.ap-south-1.amazonaws.com/${mee[6]}" style="width: 2em;height: 2em; border-radius: 50%; object-fit: cover; margin-right: 1em;">
                        </div>
                        <div style="float: left; margin: 3px 0px 0px 5px;">${mee[1]}</div>
                        <br>
                        <a id="comment-id-${mee[0]}" style="margin-left:3em;">${comment.comment} </a><br>
                    </a>
                    `
                } else {
                    document.getElementById('comments').innerHTML += `
                        <a style="cursor:pointer;" id="comment-container-${mee[0]}" onclick="user_show(event, ${mee[0]}, '${mee[1]}', '${mee[2]}', ${mee[3]}, ${mee[4]})">
                            <div class="image--container" style="float: left;">
                            <p data-letters-small="${mee[5]}"></p>
                            </div>
                            <div style="float: left; margin: 3px 0px 0px 5px;">${mee[1]}</div>

                            <br>
                            <a id="comment-id-${mee[0]}">${comment.comment} </a><br>
                        </a>
                    `
                }
            }
        } else {
            notify(response.message)
        }
    })
}

function write_comment(id) {
    notify("Adding comment...")
    id = parseInt(id)
    url = `/me/write_comment-${id}/`
    if (document.getElementById('comment-input').value.trim()) {
        data = { comment: document.getElementById('comment-input').value.trim() }
        $.ajax({
            'type': 'POST',
            'url': url,
            'data': JSON.stringify(data),
            'success': function(response) {
                if (response.status == 'success') {
                    mee = response.real
                    document.getElementById('comments-number').innerHTML = `${response.count} Comments`
                    if (mee[6]) {
                        comment = `
                        <a style="cursor:pointer;" id="comment-container-${mee[0]}" onclick="user_show(event, ${mee[0]}, '${mee[1]}', '${mee[2]}', ${mee[3]}, ${mee[4]})">
                            <div class="image--container" style="float: left;">
                                <img src="https://mediafiles-arpan.s3.ap-south-1.amazonaws.com/${mee[6]}" style="width: 2em;height: 2em; border-radius: 50%; object-fit: cover; margin-right: 1em;">
                            </div>
                            <div style="float: left; margin: 3px 0px 0px 5px;">${mee[1]}</div>
                            <br>
                            <a id="comment-id-${mee[0]}" style="margin-left:3em;">${response.comment} </a><br>
                        </a>
                        `
                    } else {
                        comment = `
                            <a style="cursor:pointer;" id="comment-container-${mee[0]}" onclick="user_show(event, ${mee[0]}, '${mee[1]}', '${mee[2]}', ${mee[3]}, ${mee[4]})">
                                <div class="image--container" style="float: left;">
                                <p data-letters-small="${mee[5]}"></p>
                                </div>
                                <div style="float: left; margin: 3px 0px 0px 5px;">${mee[1]}</div>

                                <br>
                                <a id="comment-id-${mee[0]}">${response.comment} </a><br>
                            </a>
                        `
                    }
                    document.getElementById('comments').innerHTML = comment + document.getElementById('comments').innerHTML
                    document.getElementById('comment-input').value = ''
                    notify("Comment added")
                } else {
                    notify(response.message)
                }
            },
            'error': function(error) {
                notify("An error occured.")
            },
        })
    }
}


function user_show(e, id, name, username, user_id, post_id, comment) {
    e.preventDefault()
    document.getElementById('modal-container').classList.add('show-modal')
        // document.getElementById('delete-post-heading').innerText = comment
    document.getElementById('modal-user').innerText = name
    document.getElementById('modal-user-a').setAttribute('href', `/${username}`)
    if (user == 'no') {
        document.getElementById('delete-container').innerHTML = ''
        document.getElementById('report-container').innerHTML = ''
    } else {
        document.getElementById('delete-container').innerHTML = ''
        document.getElementById('report-container').innerHTML = ''
        if (user != user_id) {
            document.getElementById('report-container').innerHTML = `
            <button class="modal__button modal__button-width" id="report_comment_button">
                <a href="/me/report/comment-${id}" style="color:white;">
                    Report
                </a>
                </button>
            `
        } else if (user == user_id) {
            document.getElementById('delete-container').innerHTML = `
            <button class="modal__button modal__button-width" id="delete_comment_button" onclick="delete_button(${id}, ${post_id})">
                Delete
            </button>
            `
        }
    }
}


function delete_button(id, post_id) {
    url = `/me/delete_comment-${id}-${post_id}`
    $.get(url, function(response) {
        if (response.status == 'success') {
            document.getElementById(`comment-container-${response.id}`).remove()
            document.getElementById(`comment-id-${response.id}`).remove()
            document.getElementById('modal-container').classList.remove('show-modal')
            document.getElementById('comments-number').innerHTML = `${response.count} Comments`
            notify("Deleted")
        } else {
            notify(response.message)
        }
    })
}


function bookmark(e, id) {
    e.preventDefault()
    notify("Toggling Bookmark...")
    url = `/me/create_bookmark-${id}`
    $.get(url, function(response) {
        if (response.status == 'success') {
            if (response.book == 'save') {
                document.getElementById('bookmark-button').classList.add('active')
                notify("Bookmark added")
            } else if (response.book == 'delete') {
                document.getElementById('bookmark-button').classList.remove('active')
                notify("Bookmark removed")
            }
        } else {
            notify(response.message)
        }
    })
}

function notify(message) {
    document.getElementById('notification').innerHTML = `
    <p class="btn btn-primary">${message}</p>
    `
    setTimeout(() => {
        document.getElementById('notification').innerHTML = ''
    }, 5000)
}