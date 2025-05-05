function goToPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.getElementById(pageId).classList.remove('hidden');
}

let tempUserData = {};

function storeClientInfo() {
  tempUserData.clientName = document.getElementById('client-name').value;
  tempUserData.officeName = document.getElementById('office-name').value;
  tempUserData.serviceName = document.getElementById('service-name').value;
}

function storeFeedback() {
  tempUserData.q1 = parseInt(document.querySelector('input[name="q1"]:checked')?.value) || null;
  tempUserData.q2 = document.querySelector('input[name="q2"]:checked')?.value || null;
  tempUserData.q3 = document.querySelector('input[name="q3"]:checked')?.value || null;
  tempUserData.q4 = document.querySelector('input[name="q4"]:checked')?.value || null;
  tempUserData.q5 = document.querySelector('input[name="q5"]:checked')?.value || null;
  tempUserData.comments = document.getElementById('comments').value;

  let existingData = JSON.parse(localStorage.getItem('feedback_all')) || [];
  existingData.push(tempUserData);
  localStorage.setItem('feedback_all', JSON.stringify(existingData));
}

window.onload = () => {
  document.querySelector('#page3 form').addEventListener('submit', () => {
    storeClientInfo();
    goToPage('page4');
  });

  document.querySelector('#page4 form').addEventListener('submit', () => {
    storeFeedback();
    goToPage('page5');
  });
};
