document.addEventListener('DOMContentLoaded', () => {
  const uploadTriggerBtn = document.getElementById('uploadTriggerBtn');
  const uploadModal = document.getElementById('uploadModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const browseFilesBtn = document.getElementById('browseFilesBtn');
  const documentList = document.getElementById('documentList');
  
  const chatForm = document.getElementById('chatForm');
  const queryInput = document.getElementById('queryInput');
  const chatHistory = document.getElementById('chatHistory');
  const apiKeyInput = document.getElementById('apiKeyInput');

  if (localStorage.getItem('groqApiKey')) {
    apiKeyInput.value = localStorage.getItem('groqApiKey');
  }
  apiKeyInput.addEventListener('change', (e) => {
    localStorage.setItem('groqApiKey', e.target.value);
  });

  const API_BASE = 'http://localhost:8000/api';

  // Modal logic
  uploadTriggerBtn.addEventListener('click', () => {
    uploadModal.classList.remove('hidden');
  });
  
  closeModalBtn.addEventListener('click', () => {
    uploadModal.classList.add('hidden');
  });

  // Drag and Drop Logic
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
  });

  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt.files && dt.files.length) {
      handleFiles(dt.files);
    }
  });

  browseFilesBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', function() {
    if (this.files && this.files.length) {
      handleFiles(this.files);
    }
  });

  async function handleFiles(files) {
    const file = files[0]; // Just handling one file at a time for basic setup
    if (!file) return;

    addDocumentToList(file.name, true);
    uploadModal.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', file);
    
    try {
      addSystemMessage(`Uploading and processing ${file.name}... This might take a moment.`);
      
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();
      
      let uploadMsg = `Success! Prepared ${file.name} context. Embedded ${data.chunks} chunks.`;
      if (data.console) {
          uploadMsg = "💻 Terminal Output:\n```text\n" + data.console + "\n```\n\n" + uploadMsg;
      }
      addSystemMessage(uploadMsg);
      updateDocumentStatus(file.name, false);
    } catch (err) {
      console.error(err);
      addSystemMessage(`Error processing ${file.name}. Is the Python backend running?`);
      updateDocumentStatus(file.name, false, true);
    }
  }

  function addDocumentToList(filename, isLoading) {
    const div = document.createElement('div');
    div.className = 'doc-item';
    div.setAttribute('data-filename', filename);
    div.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
      <span class="file-label" style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${filename}</span>
      ${isLoading ? '<div class="loader" style="width:12px;height:12px;border:2px solid var(--text-secondary);border-top:2px solid var(--accent-color);border-radius:50%;animation:spin 1s linear infinite;"></div>' : '<span style="color:#10b981; font-size:12px;">Ready</span>'}
    `;
    documentList.appendChild(div);
  }

  function updateDocumentStatus(filename, isLoading, error=false) {
    const item = document.querySelector(`.doc-item[data-filename="${filename}"]`);
    if(item) {
        if(error) {
            item.innerHTML = item.innerHTML.replace('<div class="loader"', '<span style="color:#ef4444; font-size:12px;">Error</span><div style="display:none;"');
        } else {
             item.innerHTML = item.innerHTML.replace('<div class="loader"', '<span style="color:#10b981; font-size:12px;">Ready</span><div style="display:none;"');
        }
    }
  }

  // Add styles for spinner via JS quickly
  const style = document.createElement('style');
  style.innerHTML = `@keyframes spin { 100% { transform:rotate(360deg); } }`;
  document.head.appendChild(style);

  // Chat Logic
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    queryInput.value = '';
    addUserMessage(query);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Groq-Api-Key': apiKeyInput.value.trim()
        },
        body: JSON.stringify({ query })
      });
      
      if (!response.ok) throw new Error('Query failed');
      const data = await response.json();
      
      addSystemMessage(data.answer);
    } catch (err) {
      console.error(err);
      addSystemMessage("I had trouble connecting to the RAG backend. Make sure the FastAPI server is running on port 8000!");
    }
  });

  function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user-msg';
    div.innerHTML = `
      <div class="avatar">👤</div>
      <div class="msg-content">${escapeHTML(text)}</div>
    `;
    chatHistory.appendChild(div);
    scrollToBottom();
  }

  function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className = 'message system-msg';
    div.innerHTML = `
      <div class="avatar">🤖</div>
      <div class="msg-content">${escapeHTML(text)}</div>
    `;
    chatHistory.appendChild(div);
    scrollToBottom();
  }

  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }

  function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
});
