function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

function submitEdit(id) {
    const textAreaValue = document.getElementById(`textarea_${id}`).value
    fetch(`/edit_post/${id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ content: textAreaValue })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`post-content-${id}`).innerText = data.content;
    });
}


document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', () => {
            const postId = button.dataset.postId;
            const contentElement = document.getElementById(`post-content-${postId}`);
            const currentContent = contentElement.innerText;

            contentElement.innerHTML = `
                <textarea id="textarea_${postId}" rows="4" cols="50">${currentContent}</textarea>
                <br>
                <button onclick="submitEdit(${postId})">Save</button>
            `;
        });
    });
});