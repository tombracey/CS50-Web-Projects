function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function changeLike(postId) {
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        const likeCountElement = document.getElementById(`like-count-${postId}`);
        likeCountElement.innerText = data.like_count;

        const likeButton = document.getElementById(`like-button-${postId}`);
        if (data.liked) {
            likeButton.innerText = 'Unlike';
        } else {
            likeButton.innerText = 'Like';
        }
    });
}