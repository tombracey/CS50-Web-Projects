document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector("#compose-form").addEventListener('submit', send_mail)

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


function view_email(id) {
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
      console.log(email);

      document.querySelector('#emails-view').style.display = 'block';
      document.querySelector('#compose-view').style.display = 'none';
      document.querySelector('#emails-view').innerHTML = '';

      const email_view = document.createElement('div');
      email_view.innerHTML = `
          <ul class="list-group mb-3">
            <li class="list-group-item"><strong>From:</strong> ${email.sender}</li>
            <li class="list-group-item"><strong>To:</strong> ${email.recipients.join(', ')}</li>
            <li class="list-group-item"><strong>Subject:</strong> ${email.subject}</li>
            <li class="list-group-item"><strong>Time:</strong> ${email.timestamp}</li>
          </ul>
          <div class="mb-3">
            <p>${email.body.replace(/\n/g, "<br>")}</p>
          </div>
      `;

      document.querySelector('#emails-view').append(email_view);

      let reply_button = document.createElement('button');
      reply_button.className = 'btn btn-sm btn-outline-primary';
      reply_button.style.marginRight = '10px';
      reply_button.innerText = 'Reply';
      reply_button.addEventListener('click', () => {
          compose_email();
          document.querySelector('#compose-recipients').value = email.sender;
          document.querySelector('#compose-subject').value = email.subject.startsWith("Re:") ? email.subject : `Re: ${email.subject}`;
          document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
      });

      document.querySelector('#emails-view').append(reply_button);

      if (!email.read) {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({ read: true })
        });
      }

      let archive_button = document.createElement('button');
      archive_button.className = 'btn btn-sm btn-outline-secondary me-2';
      archive_button.innerText = email.archived ? 'Unarchive' : 'Archive';

      archive_button.addEventListener('click', () => {
          fetch(`/emails/${id}`, {
              method: 'PUT',
              body: JSON.stringify({
                  archived: !email.archived
              })
          })
          .then(() => load_mailbox('inbox'));
      });

      document.querySelector('#emails-view').append(archive_button);
  });
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        emails.forEach(email => {
          const new_email = document.createElement('div');
          new_email.className = "email-item";
          new_email.style.border = "1px solid";
          new_email.style.padding = "10px";
          new_email.style.margin = "5px";
          new_email.style.backgroundColor = email.read ? "#f0f0f0" : "#ffffff";

          new_email.innerHTML = `
            <strong>${email.sender}</strong> - ${email.subject}
            <span style="float: right;">${email.timestamp}</span>
          `;

          new_email.addEventListener('click', function() {
              view_email(email.id);
          });

          document.querySelector('#emails-view').append(new_email);
        });
    });
}


function send_mail(event){
  event.preventDefault();
  let recipients = document.querySelector('#compose-recipients').value;
  let subject = document.querySelector('#compose-subject').value;
  let body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      console.log(result);
      load_mailbox('sent');
  });
}