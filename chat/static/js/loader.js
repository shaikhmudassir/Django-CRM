  // Redirected by callback route check weather access_token recived or not
  const access_token = localStorage.access_token;
  if(access_token == null){
    window.location.href = "http://127.0.0.1:8000/api/login";
  }

  // Setup the Header with API key and Organization ID
  const headers = new Headers();
  headers.set('Authorization', `Bearer ${access_token}`);
  headers.set('org', 'f0d58ec1-eadc-4cbe-a636-f6878cb4ee8c');

  // Sending the Message to the Server
  const form = document.querySelector('#ChatForm');
  const sendPostRequest = async () => {
  const messageInput = form.querySelector('[name="contact"]');
  messageInput.value = getCookie('number');

  const formData = new FormData(form);
  const request = new Request('http://127.0.0.1:8000/api/chat/send/', {
    method: 'POST',
    body: formData,
  });

  const response = await fetch(request);
  if (response.status === 200) {
    console.log('Message sent!');
  } else {
    console.error('Message not sent!');
    console.error(response.statusText);
  }};
  

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    await sendPostRequest();
  });

  // Edit Details in lead form
  const LeadForm = document.querySelector('#LeadEditForm');
  const sendPutRequestLead = async () => {

  const LeadformData = new FormData(LeadForm);
  
  const request = new Request('http://127.0.0.1:8000/api/leads/' + lead_id + '/', {
    method: 'PUT',
    body: LeadformData,
    headers: headers
  });
  const status = ["converted", "in process"];
  
  if (status.includes(LeadformData.get('status')) && LeadformData.get('opportunity_amount') == ""){
    alert("Please Enter opportunity amount")
    return
  }
  const response = await fetch(request);
  if (response.status === 200) {
    console.log('Lead with given ID edited');
  } else {
    console.error(response.statusText);
    console.error(response)
  }};
  
  LeadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    await sendPutRequestLead();
  });


  function showChat(contact_id, number, name, lead_id) {

    document.getElementById("rightSide").style.display = "flex";
    document.getElementById("Intro-Left").style.display = "none";
    document.cookie = "number=" + number;
    document.cookie = "contact_id=" + contact_id;
    document.cookie = "name=" + name;
    document.cookie = "lead_id=" + lead_id;
  
  
  document.querySelector(".rightSide").querySelector(".header").querySelector("h4").innerHTML =  
    name + "<br><span aria-label='online'>{online}</span>"
  
    setInterval(loadChats, 5000);
    }
  
  function loadChats() {
    contact_id = getCookie('contact_id');
    number = getCookie('number');
  
    fetch('http://127.0.0.1:8000/api/chat/messages/?contact=' + contact_id)
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      document.querySelector('#chatbox').innerHTML = ""
      data.forEach(element => {
        const my_chat = `
        <p class="chatMessage my-chat">
        <span>${element.message}</span>
        <span class="chat__msg-filler"> </span>
        <span class="msg-footer">
            <span>08:11 AM</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 15" width="16" height="15"
                aria-label="read" class="chat-icon--blue">
                <path fill="currentColor"
                    d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.879a.32.32 0 0 1-.484.033l-.358-.325a.319.319 0 0 0-.484.032l-.378.483a.418.418 0 0 0 .036.541l1.32 1.266c.143.14.361.125.484-.033l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.879a.32.32 0 0 1-.484.033L1.891 7.769a.366.366 0 0 0-.515.006l-.423.433a.364.364 0 0 0 .006.514l3.258 3.185c.143.14.361.125.484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z">
                </path>
            </svg>
        </span>
        <button aria-label="Message options" class="chat__msg-options"><svg
                xmlns="http://www.w3.org/2000/svg" viewBox="0 0 19 20" width="19" height="20"
                class="chat__msg-options-icon">
                <path fill="currentColor"
                    d="M3.8 6.7l5.7 5.7 5.7-5.7 1.6 1.6-7.3 7.2-7.3-7.2 1.6-1.6z">
                </path>
            </svg>
        </button>
        </p>`;
  
        const friend_chat = `
        <p class="chatMessage frnd-chat">
        <span>${element.message}</span>
        <span class="chat__msg-filler2"> </span>
        <span class="msg-footer">
            <span>08:20 AM</span>
        </span>
        <button aria-label="Message options" class="chat__msg-options"><svg
                xmlns="http://www.w3.org/2000/svg" viewBox="0 0 19 20" width="19" height="20"
                class="chat__msg-options-icon">
                <path fill="currentColor"
                    d="M3.8 6.7l5.7 5.7 5.7-5.7 1.6 1.6-7.3 7.2-7.3-7.2 1.6-1.6z">
                </path>
            </svg>
        </button>
        </p>`;
        
        
        if (element.is_sent == true)  markup = my_chat;
        else  markup = friend_chat;
  
        document.querySelector('#chatbox').insertAdjacentHTML('beforeend', markup);
  
        var chatbox = document.querySelector('#ChatContainer');
        chatbox.scrollTop = chatbox.scrollHeight;
      });
    })
    .catch(function (err) {
      console.log('error: ' + err);
    });
    }
    
  function getCookie(cookieName) {
    let cookies = document.cookie.split('; ');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].split('=');
      if (cookie[0] === cookieName) {
        return cookie[1];
      }
    }
    return '';
    }

  function LeadEditForm() {
    lead_id = getCookie('lead_id')
    fetch('http://127.0.0.1:8000/api/leads/' + lead_id + '/', {headers})
    .then(response => {
      return response.json();
    })
    .then(data => {
      const form = document.querySelector('#LeadEditForm');
      document.querySelector('#title').value = data.lead_obj.title;
      document.querySelector('#first_name').value = data.lead_obj.first_name;
      document.querySelector('#last_name').value = data.lead_obj.last_name;
      document.querySelector('#account_name').value = data.lead_obj.account_name;
      document.querySelector('#phone').value = data.lead_obj.phone;
      document.querySelector('#email').value = data.lead_obj.email;
      document.querySelector('#lead_attachment').value = data.lead_obj.lead_attachment;
      document.querySelector('#opportunity_amount').value = data.lead_obj.opportunity_amount;
      document.querySelector('#website').value = data.lead_obj.website;
      document.querySelector('#description').value = data.lead_obj.description;
      document.querySelector('#teams').value = data.lead_obj.teams;
      document.querySelector('#assigned_to').value = data.lead_obj.assigned_to;
      document.querySelector('#contacts').value = data.lead_obj.contacts;
      document.querySelector('#status').value = data.lead_obj.status;
      document.querySelector('#source').value = data.lead_obj.source;
      document.querySelector('#address_line').value = data.lead_obj.address_line;
      document.querySelector('#street').value = data.lead_obj.street;
      document.querySelector('#city').value = data.lead_obj.city;
      document.querySelector('#state').value = data.lead_obj.state;
      document.querySelector('#postcode').value = data.lead_obj.postcode;
      document.querySelector('#country').value = data.lead_obj.country;
      document.querySelector('#tags').value = data.lead_obj.tags;
      document.querySelector('#company').value = data.lead_obj.company;
      document.querySelector('#probability').value = data.lead_obj.probability;
      document.querySelector('#industry').value = data.lead_obj.industry;
      document.querySelector('#skype_ID').value = data.lead_obj.skype_ID;
    })
    .catch(error => {
      //handle error
    });
    }