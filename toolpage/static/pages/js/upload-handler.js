function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    return parts.length === 2 ? parts.pop().split(';').shift() : '';
  }
  
  function createFileIcon(filename) {
    const wrapper = document.createElement('div');
    wrapper.className = 'file-item';
  
    const thumb = document.createElement('div');
    thumb.className = 'thumbnail-wrapper zip-thumbnail';
  
    const ext = filename.toLowerCase().endsWith('.docx') ? '.docx' : '.txt';
    const label = document.createElement('div');
    label.className = 'zip-icon';
    label.textContent = ext;
  
    const delBtn = document.createElement('button');
    delBtn.className = 'delete-btn';
    delBtn.textContent = '✖';
    delBtn.onclick = () => {
      wrapper.remove();
      document.getElementById('doc-input').value = null;
    };
  
    thumb.appendChild(label);
    thumb.appendChild(delBtn);
  
    const nameLabel = document.createElement('div');
    nameLabel.className = 'filename-label';
    nameLabel.textContent = filename;
  
    wrapper.appendChild(thumb);
    wrapper.appendChild(nameLabel);
  
    const previewArea = document.getElementById('file-preview');
    previewArea.innerHTML = '';
    previewArea.appendChild(wrapper);
  }
  
  function selectBackground(id) {
    fetch('/upload/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body: new URLSearchParams({ selected_bg_id: id })
    });
  }
  
  function handleUpload(dropArea, inputId, type) {
    const input = document.getElementById(inputId);
    const url = (type === 'background') ? '/upload/background/' : '/upload/';
  
    function uploadFile(file) {
      const formData = new FormData();
      formData.append(type === 'background' ? 'image' : 'file', file);
  
      fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          if (type === 'document') {
            createFileIcon(data.filename);
          } else if (type === 'background') {
            createThumbnail(data.id, data.url, data.position);
          }
        } else {
          alert(data.message);
        }
      });
    }
  
    dropArea.addEventListener('click', () => input.click());
    input.addEventListener('change', () => {
      if (input.files[0]) uploadFile(input.files[0]);
    });
  
    ['dragover', 'dragenter'].forEach(event => {
      dropArea.addEventListener(event, e => {
        e.preventDefault();
        dropArea.classList.add('hover');
      });
    });
  
    ['dragleave', 'drop'].forEach(event => {
      dropArea.addEventListener(event, e => {
        e.preventDefault();
        dropArea.classList.remove('hover');
      });
    });
  
    dropArea.addEventListener('drop', e => {
      const file = e.dataTransfer.files[0];
      if (file) uploadFile(file);
    });
  }
  
  window.addEventListener('DOMContentLoaded', () => {
    handleUpload(document.getElementById('background-drop'), 'background-input', 'background');
    handleUpload(document.getElementById('doc-drop'), 'doc-input', 'document');
  
    document.querySelectorAll('.file-item img').forEach(img => {
      img.addEventListener('click', () => {
        document.querySelectorAll('.file-item').forEach(e => e.classList.remove('selected'));
        const parent = img.closest('.file-item');
        parent.classList.add('selected');
        const id = parent.dataset.id;
        selectBackground(id);
      });
    });
  
    document.getElementById('submit-btn').addEventListener('click', () => {
      fetch('/upload/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: new URLSearchParams({ action: 'submit' })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          alert('處理成功！');
          window.location.href = '/files/';
        } else {
          alert(data.message);
        }
      });
    });
  });